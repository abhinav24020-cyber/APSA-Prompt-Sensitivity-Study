"""Single trial runner: one (prompt, model, perturbation) triple."""

import datetime
import logging
import os
import socket

# If offline or huggingface.co unreachable, enable offline mode to prevent slow retry delays
try:
    _s = socket.create_connection(("huggingface.co", 443), timeout=1.0)
    _s.close()
except OSError:
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

from apsa.config.experiment_config import ExperimentConfig
from apsa.config.schema import ModelConfig, PerturbationConfig
from apsa.data.base_dataset import DatasetItem
from apsa.execution.budget_enforcer import BudgetEnforcer
from apsa.metrics.functional.exact_match import ExactMatchEvaluator
from apsa.metrics.input_distance.lexical import LexicalDistanceCalculator
from apsa.metrics.sensitivity import SensitivityCalculator
from apsa.storage.schema import (
    EpsilonBudgetUsed,
    ExperimentRun,
    FunctionalMetrics,
    GenerationConfigSnapshot,
    InputDistanceMetrics,
    OutputDistanceMetrics,
)

logger = logging.getLogger(__name__)


def _has_network() -> bool:
    import socket
    try:
        s = socket.create_connection(("huggingface.co", 443), timeout=1.0)
        s.close()
        return True
    except OSError:
        return False


class TrialRunner:
    """Executes a single paired-comparison trial."""

    def __init__(self, config: ExperimentConfig) -> None:
        self._config = config
        self._lexical_calc = LexicalDistanceCalculator()
        self._budget_enforcer = BudgetEnforcer(config.epsilon_budget)
        self._exact_match = ExactMatchEvaluator()
        self._sensitivity_calc = SensitivityCalculator(
            config.metric_weights, config.composite_input_weights
        )
        self._providers: dict = {}
        self._embedder = None
        self._rouge_scorer = None

    def _get_provider(self, model_config: ModelConfig):
        if model_config.model_id not in self._providers:
            from apsa.providers.registry import get_provider
            self._providers[model_config.model_id] = get_provider(model_config)
        return self._providers[model_config.model_id]

    def _get_embedder(self):
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise RuntimeError(
                    "Semantic input distance requires sentence-transformers."
                ) from exc
            if not _has_network():
                os.environ["HF_HUB_OFFLINE"] = "1"
                os.environ["TRANSFORMERS_OFFLINE"] = "1"
            self._embedder = SentenceTransformer("all-MiniLM-L6-v2")
        return self._embedder

    def _compute_semantic_cosine(self, s1: str, s2: str) -> float:
        if s1 == s2:
            return 0.0
        embedder = self._get_embedder()
        if embedder is None:
            raise RuntimeError("Semantic input distance is unavailable; no fallback metric was substituted.")
        vecs = embedder.encode([s1, s2], normalize_embeddings=True, show_progress_bar=False)
        dot = sum(float(a) * float(b) for a, b in zip(vecs[0], vecs[1]))
        return max(0.0, min(1.0, 1.0 - dot))

    def _compute_textual_metrics(self, orig: str, pert: str):
        if orig == pert:
            return {
                "lev_norm": 0.0,
                "rouge1": 1.0,
                "rouge2": 1.0,
                "rougel": 1.0,
                "bleu": 1.0,
                "token_jaccard": 1.0,
            }

        lex = self._lexical_calc.compute(orig, pert)
        lev_norm = lex.char_levenshtein_normalized

        if self._rouge_scorer is None:
            from rouge_score import rouge_scorer
            self._rouge_scorer = rouge_scorer.RougeScorer(
                ["rouge1", "rouge2", "rougeL"], use_stemmer=False
            )
        scores = self._rouge_scorer.score(orig, pert)
        rouge1 = scores["rouge1"].fmeasure
        rouge2 = scores["rouge2"].fmeasure
        rougel = scores["rougeL"].fmeasure

        # Unigram BLEU
        orig_toks = orig.lower().split()
        pert_toks = pert.lower().split()
        bleu = 0.0
        if orig_toks and pert_toks:
            ref_counts: dict[str, int] = {}
            for t in orig_toks:
                ref_counts[t] = ref_counts.get(t, 0) + 1
            matches = 0
            for t in pert_toks:
                if ref_counts.get(t, 0) > 0:
                    matches += 1
                    ref_counts[t] -= 1
            precision = matches / len(pert_toks)
            bp = 1.0 if len(pert_toks) >= len(orig_toks) else len(pert_toks) / len(orig_toks)
            bleu = bp * precision

        # Token Jaccard
        s_orig = set(orig_toks)
        s_pert = set(pert_toks)
        union = s_orig | s_pert
        inter = s_orig & s_pert
        token_jaccard = len(inter) / len(union) if union else 1.0

        return {
            "lev_norm": round(lev_norm, 6),
            "rouge1": round(rouge1, 6),
            "rouge2": round(rouge2, 6),
            "rougel": round(rougel, 6),
            "bleu": round(bleu, 6),
            "token_jaccard": round(token_jaccard, 6),
        }

    def execute(
        self,
        run_id: str,
        item: DatasetItem,
        model_config: ModelConfig,
        perturbation_config: PerturbationConfig,
    ) -> ExperimentRun:
        """Run baseline and perturbed inference; compute all metrics."""
        logger.debug(f"[{run_id}] trial_started")

        # 1. Format baseline prompt
        from apsa.prompts.registry import get_formatter
        formatter = get_formatter(item.task_category)
        prompt_record = formatter.format(item, self._config.system_prompt)
        original_prompt = prompt_record.original_prompt

        # 2. Apply perturbation
        from apsa.perturbations.base_perturbation import PerturbationConfig as OperatorPertConfig
        from apsa.perturbations.registry import get_perturbation
        operator = get_perturbation(perturbation_config.type)
        pert_cfg = OperatorPertConfig(
            params=perturbation_config.params,
            seed=self._config.experiment.seed,
        )
        perturbation_record = operator.perturb(
            original_prompt,
            prompt_id=item.id,
            config=pert_cfg,
        )
        if perturbation_record is None:
            raise ValueError(
                f"Perturbation {perturbation_config.type!r} is not applicable "
                f"to dataset item {item.id!r}; no model request was made."
            )
        perturbed_prompt = perturbation_record.perturbed_prompt

        # 3. Measure and enforce available input budgets before model requests.
        lex_dist = self._lexical_calc.compute(original_prompt, perturbed_prompt)
        sem_cosine_in = self._compute_semantic_cosine(original_prompt, perturbed_prompt)
        if not self._budget_enforcer.is_within_budget(
            lexical_result=lex_dist,
            semantic_result={"cosine_distance": sem_cosine_in},
            original_prompt=original_prompt,
            perturbed_prompt=perturbed_prompt,
            run_id=run_id,
        ):
            raise ValueError(
                f"Perturbation {perturbation_record.perturbation_id!r} exceeds "
                "the configured lexical or semantic input budget; no model request was made."
            )

        # 4. Model inference setup
        from apsa.providers.base_provider import GenerationConfig, Message
        gen_config = GenerationConfig(
            temperature=self._config.generation.temperature_deterministic,
            top_p=self._config.generation.top_p,
            max_tokens=self._config.generation.max_tokens,
            seed=self._config.experiment.seed,
        )

        provider = self._get_provider(model_config)
        messages_orig = [
            Message(role="system", content=self._config.system_prompt),
            Message(role="user", content=original_prompt),
        ]
        messages_pert = [
            Message(role="system", content=self._config.system_prompt),
            Message(role="user", content=perturbed_prompt),
        ]

        # 5. Generate outputs
        orig_res = provider.generate(messages_orig, gen_config)
        pert_res = provider.generate(messages_pert, gen_config)
        orig_output = orig_res.output_text
        pert_output = pert_res.output_text

        # 6. Output distances and functional correctness
        text_m = self._compute_textual_metrics(orig_output, pert_output)
        sem_cosine_out = self._compute_semantic_cosine(orig_output, pert_output)

        func = self._exact_match.evaluate(
            orig_output, pert_output, item.gold_answer, item.task_category.value
        )

        # 7. Composite output divergence
        w = self._config.metric_weights
        textual_comp = 1.0 - text_m["rougel"]
        semantic_comp = sem_cosine_out
        functional_comp = 1.0 if func.functional_failure else 0.0
        d_out = (
            w.w1_textual * textual_comp
            + w.w2_semantic * semantic_comp
            + w.w3_functional * functional_comp
        )

        # 8. Sensitivity coefficient
        sensitivity = None
        sensitivity_unavailable_reason = None
        if self._config.composite_input_weights.gamma_syntactic == 0:
            sensitivity = self._sensitivity_calc.compute(
                d_out_composite=d_out,
                d_lex_in=lex_dist.char_levenshtein_normalized,
                d_sem_in=sem_cosine_in,
                d_syn_in=0.0,
            )
        else:
            sensitivity_unavailable_reason = (
                "Syntactic tree edit distance is not implemented and has a positive weight."
            )

        experiment_id = run_id.split("__")[0] if "__" in run_id else "apsa"

        return ExperimentRun(
            experiment_id=experiment_id,
            run_id=run_id,
            timestamp=datetime.datetime.now(datetime.UTC),
            condition="treatment" if perturbation_config.type != "random_edit" else "random_control",
            model_name=model_config.model_id,
            task_category=item.task_category.value,
            perturbation_type=perturbation_config.type,
            dataset_item_id=item.id,
            generation_config=GenerationConfigSnapshot(
                temperature=gen_config.temperature,
                top_p=gen_config.top_p,
                max_tokens=gen_config.max_tokens,
                seed=gen_config.seed,
            ),
            original_prompt=original_prompt,
            perturbed_prompt=perturbed_prompt,
            original_output=orig_output,
            perturbed_output=pert_output,
            original_token_count=orig_res.token_count,
            perturbed_token_count=pert_res.token_count,
            input_distance=InputDistanceMetrics(
                lexical_char_levenshtein=float(lex_dist.char_levenshtein),
                lexical_word_levenshtein=float(lex_dist.word_levenshtein),
                lexical_char_normalized=lex_dist.char_levenshtein_normalized,
                lexical_word_normalized=(
                    lex_dist.word_levenshtein
                    / max(len(original_prompt.split()), len(perturbed_prompt.split()), 1)
                ),
                semantic_cosine_distance=round(sem_cosine_in, 6),
            ),
            output_distance=OutputDistanceMetrics(
                textual_levenshtein=text_m["lev_norm"],
                rouge_1_f1=text_m["rouge1"],
                rouge_2_f1=text_m["rouge2"],
                rouge_l_f1=text_m["rougel"],
                bleu_score=text_m["bleu"],
                token_jaccard=text_m["token_jaccard"],
                semantic_embedding_cosine=round(sem_cosine_out, 6),
            ),
            functional_metrics=FunctionalMetrics(
                applicable=func.applicable,
                original_pass=func.original_pass,
                perturbed_pass=func.perturbed_pass,
                functional_failure=func.functional_failure,
            ),
            composite_output_divergence=round(d_out, 6),
            sensitivity_coefficient=sensitivity,
            original_latency_ms=orig_res.latency_ms,
            perturbed_latency_ms=pert_res.latency_ms,
            epsilon_budget_used=EpsilonBudgetUsed(
                lexical_char_normalized=lex_dist.char_levenshtein_normalized,
                semantic_cosine=round(sem_cosine_in, 6),
                lexical_word_normalized=(
                    lex_dist.word_levenshtein
                    / max(len(original_prompt.split()), len(perturbed_prompt.split()), 1)
                ),
            ),
            perturbation_id=perturbation_record.perturbation_id,
            perturbation_metadata=perturbation_record.metadata,
            semantic_risk_level=perturbation_record.semantic_risk_level.value,
            semantic_risk_reasons=perturbation_record.semantic_risk_reasons,
            sensitivity_unavailable_reason=sensitivity_unavailable_reason,
        )
