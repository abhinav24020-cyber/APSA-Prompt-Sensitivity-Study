# Research Methodology: Adversarial Prompt Sensitivity Analysis

**Project Title:** Adversarial Prompt Sensitivity Analysis: Studying Maximum Output Changes from Minimal Prompt Perturbations  
**Author / Research Lead:** Academic AI Research Project  
**Version:** 1.0  
**Date:** September 2026  

---

## 1. Main Research Question

> **Primary Research Question:**  
> *How much can a Large Language Model's (LLM's) output change when its input prompt is modified by minimal, controlled perturbations, and what underlying factors (model architecture, task domain, perturbation type) govern this sensitivity?*

The goal of this study is to systematically discover and measure instances of **adversarial prompt fragility**—defined as scenarios where a minimal, semantics-preserving (or near-imperceptible) perturbation to an input prompt leads to a disproportionately large deviation or failure in the model's output.

---

## 2. Specific Research Questions & Hypotheses

### Research Question 1 (Perturbation Type Susceptibility)
- **RQ1:** Which category of minimal input perturbation (surface-level, lexical, syntactic, or structural/instructional) causes the highest mean and maximum output divergence across different LLMs?
- **Hypothesis 1 ($H_1$):** *Surface-level changes (e.g., capitalization, trailing whitespace, minor punctuation edits) will induce significantly higher output divergence in instruction-following reasoning tasks compared to standard QA, exposing brittle tokenization and prompt-parsing mechanisms.*

### Research Question 2 (Task Category Vulnerability)
- **RQ2:** How does prompt sensitivity vary across distinct task categories (e.g., deterministic reasoning, code generation, closed QA/extraction, open-ended summarization)?
- **Hypothesis 2 ($H_2$):** *Tasks with strict binary or structured output constraints (e.g., mathematical reasoning, JSON extraction, code execution) will exhibit a higher rate of catastrophic functional failure under minimal input edits than open-ended creative tasks.*

### Research Question 3 (Model Family & Scale Robustness)
- **RQ3:** Do larger parameter scales and specialized alignment paradigms (e.g., RLHF, RLAIF, chain-of-thought reasoning tuning) increase LLM robustness against minimal prompt perturbations?
- **Hypothesis 3 ($H_3$):** *Increased parameter scale correlates with lower average semantic output sensitivity across general tasks, but reasoning-focused architectures (e.g., models with explicit internal CoT) exhibit localized fragility spikes under instruction reordering due to disruption of intermediate activation pathways.*

### Research Question 4 (Scaling Law of Output Divergence)
- **RQ4:** What is the mathematical relationship between input perturbation distance $\epsilon$ and output divergence $\delta$? Does output divergence scale continuously or via non-linear phase transitions?
- **Hypothesis 4 ($H_4$):** *The relationship between input perturbation distance and semantic output distance follows a non-linear step-function (phase transition), where specific "critical perturbation tokens" trigger catastrophic output shifts despite falling within an overall minimal distance budget $\epsilon \le \epsilon_{\text{threshold}}$.*

### Research Question 5 (Adversarial Optimization Feasibility)
- **RQ5:** Can discrete search strategies (e.g., greedy token substitution, beam search) consistently identify worst-case input perturbations that yield significantly higher output divergence than random perturbations of equal input distance?
- **Hypothesis 5 ($H_5$):** *Targeted discrete perturbation optimization will discover adversarial prompt variants that produce $\ge 3\times$ greater output divergence than randomized edits of identical edit distance.*

---

## 3. Variables Framework

### 3.1 Independent Variables
1. **Perturbation Category ($T$)**: 9 discrete perturbation types (word substitutions, additions, deletions, synonym replacements, punctuation edits, capitalization changes, whitespace/formatting modifications, instruction reordering, template restructuring).
2. **Perturbation Budget ($\mathbf{\epsilon}$)**: Quantitative threshold constraint on maximum allowed edit distance (e.g., normalized edit distance $\le 0.10$ or character edit distance $\le 5$).
3. **Target LLM ($M$)**: Model instances across sizes, fine-tuning regimes, and providers.
4. **Task Category ($C$)**: Task domain (Reasoning, Code Generation, Closed QA / Extraction, Summarization / Open Generation).
5. **Decoding Configuration ($G$)**: Temperature $T \in \{0.0, 0.7\}$, Top-$p = 0.95$, Random Seed $S$.

### 3.2 Dependent Variables
1. **Input Distance Metrics**:
   - Syntactic Input Distance ($d_{\text{syn\_in}}$)
   - Lexical Input Distance ($d_{\text{lex\_in}}$)
   - Semantic Input Distance ($d_{\text{sem\_in}}$)
2. **Output Distance Metrics**:
   - Output Textual Distance ($d_{\text{text\_out}}$)
   - Output Semantic Distance ($d_{\text{sem\_out}}$)
   - Functional / Task-Level Output Change ($\Delta f_{\text{task}}$)

### 3.3 Control Variables
- **Prompt Template Baseline**: Standardized prompt formatting structure for each benchmark task.
- **System Prompt**: Kept identical across baseline and perturbed runs.
- **Maximum Output Tokens**: Fixed ceiling (`max_tokens = 1024`) across paired runs to avoid length-truncation artifacts.
- **Evaluation Environment**: Fixed software dependency versions and evaluation seeds.

---

## 4. Mathematical Formalization of the Optimization Objective

Let $\mathcal{X}$ denote the space of text prompt sequences.  
Let $X \in \mathcal{X}$ be an original input prompt string.

### 4.1 Input Perturbation Constraint Space
We define a multi-dimensional perturbation constraint vector $\mathbf{\epsilon} = (\epsilon_{\text{lex}}, \epsilon_{\text{sem}}, \epsilon_{\text{syn}})$. The set of valid minimal prompt perturbations $\mathcal{P}(X, \mathbf{\epsilon})$ is defined as:

$$\mathcal{P}(X, \mathbf{\epsilon}) = \left\{ X' \in \mathcal{X} \;\middle|\; d_{\text{lex\_in}}(X, X') \le \epsilon_{\text{lex}} \;\land\; d_{\text{sem\_in}}(X, X') \le \epsilon_{\text{sem}} \;\land\; d_{\text{syn\_in}}(X, X') \le \epsilon_{\text{syn}} \;\land\; X' \neq X \right\}$$

Where:
- $d_{\text{lex\_in}}(X, X') \in [0, 1]$ is the normalized character/word edit distance.
- $d_{\text{sem\_in}}(X, X') \in [0, 1]$ is the semantic input embedding distance: $1 - \cos(\mathbf{e}(X), \mathbf{e}(X'))$.
- $d_{\text{syn\_in}}(X, X') \ge 0$ is the normalized dependency tree edit distance.

### 4.2 Central Optimization Problem
For a given target LLM $M$ operating under generation parameters $\theta$, let $Y = M(X; \theta)$ denote the output generated for the original prompt $X$, and $Y' = M(X'; \theta)$ denote the output generated for the perturbed prompt $X'$.

The **Adversarial Prompt Sensitivity Maximization Problem** is mathematically formalized as:

$$\max_{X' \in \mathcal{P}(X, \mathbf{\epsilon})} D_{\text{out}}\left( M(X; \theta), M(X'; \theta) \right)$$

where $D_{\text{out}}(Y, Y')$ is a composite output divergence function:

$$D_{\text{out}}(Y, Y') = w_1 \cdot d_{\text{text\_out}}(Y, Y') + w_2 \cdot d_{\text{sem\_out}}(Y, Y') + w_3 \cdot \Delta f_{\text{task}}(Y, Y')$$

with non-negative weights $w_1, w_2, w_3 \ge 0$.

### 4.3 Sensitivity Coefficient Definition
To enable cross-task and cross-model comparison, we define the **Sensitivity Coefficient** $\mathcal{S}(X, X'; M)$ as:

$$\mathcal{S}(X, X'; M) = \frac{D_{\text{out}}\left( M(X; \theta), M(X'; \theta) \right)}{\max\left( \eta, \; d_{\text{input\_composite}}(X, X') \right)}$$

where $\eta > 0$ (e.g., $\eta = 10^{-4}$) is a small smoothing constant preventing division by zero, and:

$$d_{\text{input\_composite}}(X, X') = \alpha \cdot d_{\text{lex\_in}}(X, X') + \beta \cdot d_{\text{sem\_in}}(X, X') + \gamma \cdot d_{\text{syn\_in}}(X, X')$$

A high sensitivity coefficient $\mathcal{S} \gg 1.0$ indicates an adversarial vulnerability where an imperceptible change in prompt space leads to massive output divergence.

---

## 5. Experimental Conditions & Baselines

```
                                    +-----------------------+
                                    |  Original Prompt (X)  |
                                    +-----------+-----------+
                                                |
                      +-------------------------+-------------------------+
                      |                                                   |
          [Baseline Condition C0]                              [Treatment Conditions CT]
        Original Prompt Inferences                           Controlled Perturbation Pipeline
        - Deterministic (T = 0.0)                            - Lexical Edits
        - Stochastic (T = 0.7, N=5)                          - Surface / Formatting Edits
                      |                                      - Structural / Instruction Edits
                      v                                                   |
           Original Output Y = M(X)                                       v
                      |                                     Perturbed Prompt X' in P(X, eps)
                      |                                                   |
                      |                                                   v
                      |                                     Perturbed Output Y' = M(X')
                      |                                                   |
                      +-------------------------+-------------------------+
                                                |
                                                v
                               +---------------------------------+
                               | Comprehensive Metric Extraction |
                               |  - Syntactic Input Dist         |
                               |  - Lexical Input Dist           |
                               |  - Semantic Input Dist          |
                               |  - Textual Output Dist          |
                               |  - Semantic Output Dist         |
                               |  - Functional / Task Change     |
                               |  - Sensitivity Coeff S          |
                               +---------------------------------+
```

### 5.1 Experimental Conditions
1. **Baseline Condition ($C_0$)**: Evaluation of original unperturbed prompts $X$. Used to establish standard task accuracy and reference output $Y$.
2. **Random Edit Control ($C_{\text{random}}$)**: Insertion of arbitrary character/word edits of identical edit distance to differentiate targeted perturbation sensitivity from generic noise sensitivity.
3. **Treatment Groups ($C_{T_1} \dots C_{T_9}$)**: Systematic application of specific perturbation operators within the allowed budget $\mathbf{\epsilon}$.

---

## 6. Model Comparison Methodology

To evaluate model scale, architecture, and alignment effects, we select a representative matrix of LLMs across two deployment classes:

| Model ID | Provider / Paradigm | Parameter Scale | Context Window | Type |
| :--- | :--- | :--- | :--- | :--- |
| `llama-3.1-8b-instruct` | Meta / Open-Weights | 8B | 128k | Dense Instruct |
| `llama-3.1-70b-instruct` | Meta / Open-Weights | 70B | 128k | Dense Instruct |
| `qwen-2.5-7b-instruct` | Alibaba / Open-Weights | 7B | 128k | Dense Instruct |
| `qwen-2.5-coder-32b` | Alibaba / Open-Weights | 32B | 128k | Code Specialized |
| `mistral-7b-instruct-v0.3` | Mistral / Open-Weights | 7B | 32k | Dense Instruct |
| `gemini-1.5-flash` | Google / API | Undisclosed | 1M | Frontier Light |
| `gemini-1.5-pro` | Google / API | Undisclosed | 2M | Frontier Heavy |

### Protocol for Fair Model Comparison
- **Unified Prompt Wrapper**: A single unified API abstraction wraps local HuggingFace/vLLM instances and external APIs.
- **Fixed System Prompt**: Standardized across models: `"You are a precise academic assistant. Follow instructions exactly."`
- **Tokenizer Alignment**: Input edit distances are calculated at both the string level and the model-specific token level to account for vocabulary differences across tokenizers.

---

## 7. Task-Category Methodology

Experiments span 4 foundational NLP task domains, representing different points on the spectrum of determinism vs. creativity:

```
[Deterministic / Closed] <-------------------------------------> [Open-Ended / Generative]
  Math & Logic        Code Generation        Closed QA / Extraction       Summarization
  (Exact Match)       (Pass@1 / Unit Test)    (F1 / JSON Schema)           (Semantic BERTScore)
```

### 7.1 Task Categories & Benchmark Datasets

1. **Mathematical & Logical Reasoning (Deterministic)**
   - *Datasets*: GSM8K, MATH subset.
   - *Primary Output Metric*: Exact-Match (EM) on numerical answer, step-by-step reasoning divergence.
2. **Code Generation (Structured Execution)**
   - *Datasets*: HumanEval, MBPP.
   - *Primary Output Metric*: Pass@1 unit test execution pass rate, Abstract Syntax Tree (AST) edit distance.
3. **Closed QA & Structured Information Extraction (Constrained)**
   - *Datasets*: SQuAD v2.0, HotpotQA, Custom JSON extraction tasks.
   - *Primary Output Metric*: Token F1, Exact Match, JSON Schema validation success rate.
4. **Summarization & Open Text Generation (Unconstrained)**
   - *Datasets*: CNN/DailyMail subset, XSum.
   - *Primary Output Metric*: ROUGE-1/2/L, BERTScore F1, Sentence-Transformer Cosine Similarity.

---

## 8. Perturbation Methodology

We establish 9 granular perturbation operators, organized into 4 primary tiers:

```
                                  +------------------------------------+
                                  |     Perturbation Taxonomy (T)      |
                                  +-----------------+------------------+
                                                    |
         +--------------------+---------------------+---------------------+--------------------+
         |                    |                                           |                    |
         v                    v                                           v                    v
  [1. Surface / Format]  [2. Lexical Edits]                         [3. Syntactic Edits]  [4. Structural Edits]
  - Capitalization       - Synonym Replacement (WordNet/Embedding)  - Active/Passive      - Instruction Swap
  - Whitespace / Tabs    - Word Substitution                        - Clause Swap         - Context/Query Swap
  - Punctuation          - Word Addition / Deletion
```

### 8.1 Detailed Operator Definitions

1. **Capitalization Alterations ($T_{\text{cap}}$)**:
   - Convert keywords to lowercase, UPPERCASE, TitleCase, or sPoNgEbOb case.
2. **Whitespace & Formatting Modifications ($T_{\text{space}}$)**:
   - Inject double spaces, trailing spaces, newline replacements (`\n` vs `\n\n`), or tab insertions.
3. **Punctuation Changes ($T_{\text{punct}}$)**:
   - Add/remove trailing periods, alter quotes (`'` vs `"` vs `«»`), swap Oxford commas.
4. **Synonym Replacements ($T_{\text{synonym}}$)**:
   - Replace non-stopword nouns/verbs with nearest semantic neighbors using WordNet or embedding space ($\cos \ge 0.90$).
5. **Word Substitutions ($T_{\text{sub}}$)**:
   - Replace non-critical words with contextually plausible alternatives.
6. **Word Additions ($T_{\text{add}}$)**:
   - Insert low-information adverbs/adjectives (e.g., "please", "carefully", "simply", "basically").
7. **Word Deletions ($T_{\text{del}}$)**:
   - Remove non-essential tokens (e.g., removing articles "the", "a", or introductory politeness markers).
8. **Syntactic Rephrasing ($T_{\text{syntax}}$)**:
   - Convert active voice to passive voice (or vice versa), rephrase relative clauses.
9. **Instruction Reordering ($T_{\text{reorder}}$)**:
   - Permute multi-sentence prompts (e.g., swapping `[Context][Instruction]` to `[Instruction][Context]`).

---

## 9. Input Distance Methodology

We strictly differentiate three dimensions of input distance to isolate surface variations from semantic drift:

```
+-----------------------------------------------------------------------------------+
|                              INPUT DISTANCE METRICS                               |
+-----------------------------------------------------------------------------------+
|  1. Lexical Input Distance (d_lex_in)                                             |
|     - Normalized Character Levenshtein: EditCount(X, X') / max(|X|, |X'|)         |
|     - Normalized Word Levenshtein: WordEditCount(X, X') / max(|X_w|, |X'_w|)      |
|     - Jaccard Distance over Word 2-grams: 1 - |G(X) \cap G(X')| / |G(X) \cup G(X')|  |
+-----------------------------------------------------------------------------------+
|  2. Syntactic Input Distance (d_syn_in)                                           |
|     - Dependency Tree Edit Distance (TED): Cost of relabeling/inserting nodes    |
|       in spaCy dependency parse trees between X and X'.                           |
+-----------------------------------------------------------------------------------+
|  3. Semantic Input Distance (d_sem_in)                                            |
|     - Sentence Embedding Cosine Distance: 1 - cos( E(X), E(X') )                  |
|       using `all-mpnet-base-v2` / `text-embedding-3-large`.                       |
+-----------------------------------------------------------------------------------+
```

---

## 10. Output Distance & Divergence Methodology

Output changes are evaluated across three distinct operational levels:

### 10.1 Output Textual Distance ($d_{\text{text\_out}}$)
Measures surface token and character drift:
- **Normalized Character Levenshtein**: $\frac{\text{Levenshtein}(Y, Y')}{\max(|Y|, |Y'|)}$
- **ROUGE-1, ROUGE-2, ROUGE-L**: Measure $n$-gram overlap and longest common subsequence recall.
- **BLEU Score**: Precision-focused $n$-gram overlap metric.
- **Token Jaccard Distance**: $1 - \frac{|T(Y) \cap T(Y')|}{|T(Y) \cup T(Y')|}$.

### 10.2 Output Semantic Distance ($d_{\text{sem\_out}}$)
Measures underlying meaning shift regardless of surface phrasing:
- **BERTScore F1 Disparity**: $1 - \text{BERTScore}_{\text{F1}}(Y, Y')$ using RoBERTa-large backbones.
- **Embedding Vector Cosine Distance**: $1 - \cos\left(\mathbf{e}_{\text{out}}(Y), \mathbf{e}_{\text{out}}(Y')\right)$.
- **LLM-as-a-Judge Divergence Score**: Evaluates semantic contradiction or informational loss on a 1–5 scale using an independent judge model (`gpt-4o`).

### 10.3 Functional / Task-Level Output Change ($\Delta f_{\text{task}}$)
Measures strict task performance failure:
- **Exact Match (EM) Failure**: Binary indicator $\mathbb{I}\left[\text{Extract}(Y) \neq \text{Extract}(Y')\right]$ for math/QA tasks.
- **Code Execution Pass@1 Delta**: Binary indicator $\mathbb{I}\left[\text{Pass}(Y) \neq \text{Pass}(Y')\right]$ under test suites.
- **Schema Validation Failure**: Binary indicator $\mathbb{I}\left[\text{ValidJSON}(Y') = \text{False}\right]$ given a baseline valid JSON $Y$.

---

## 11. Confounding Factors & Mitigation Strategies

```
+--------------------------+------------------------------------+-------------------------------------------+
| Confounding Factor       | Potential Impact                   | Mitigation Strategy                       |
+--------------------------+------------------------------------+-------------------------------------------+
| LLM Stochasticity        | Non-zero output variance even with | Run N=5 iterations at T=0.7 to establish  |
|                          | unperturbed prompt X               | baseline variance sigma^2_self; compute   |
|                          |                                    | statistical significance relative to it.  |
+--------------------------+------------------------------------+-------------------------------------------+
| Temperature Configuration| Masks or amplifies perturbation    | Evaluate dual regimes: T=0.0 (pure        |
|                          | sensitivity                        | determinism) & T=0.7 (stochastic sampling)|
+--------------------------+------------------------------------+-------------------------------------------+
| Prompt Length            | Longer prompts inflate raw edit    | Normalize all edit distance metrics by    |
|                          | distance totals                    | string length (|X|); bin by token count.  |
+--------------------------+------------------------------------+-------------------------------------------+
| Output Length Disparity  | Asymmetric generation lengths skew | Use length-normalized text metrics and    |
|                          | edit metrics                       | embedding semantic similarity measures.   |
+--------------------------+------------------------------------+-------------------------------------------+
| Model Tokenizer Differences| 1 character edit may equal 0 vs 2  | Log distance at character, word, AND model|
|                          | tokens across different LLMs       | specific token ID level.                  |
+--------------------------+------------------------------------+-------------------------------------------+
```

---

## 12. Statistical Analysis Methodology

To ensure academic rigor and publication quality, data analysis follows this multi-stage statistical workflow:

### 12.1 Hypothesis Testing
- **Paired Non-Parametric Tests**: Because output distance distributions are typically right-skewed, we use the **Wilcoxon Signed-Rank Test** to compare paired output metrics between baseline $C_0$ and treatment $C_T$.
- **Multi-Group Variance Analysis**: Use the **Kruskal-Wallis H Test** to assess whether output divergence significantly differs across the 9 perturbation categories and 4 task domains.

### 12.2 Effect Size Estimation
- Calculate **Cliff’s Delta ($\delta$)** and **Cohen’s $d$** to quantify the magnitude of perturbation impact beyond simple $p$-value statistical significance.

### 12.3 Regression & Interaction Modeling
We specify a **Generalized Linear Mixed-Effects Model (GLMM)** to isolate independent effects and interaction terms:

$$D_{\text{out}} = \beta_0 + \beta_1 d_{\text{lex\_in}} + \beta_2 d_{\text{sem\_in}} + \beta_3 \text{Type} + \beta_4 \text{Task} + \beta_5 \text{Model} + (\text{Type} \times \text{Model}) + u_{\text{prompt}} + \epsilon$$

where $u_{\text{prompt}} \sim \mathcal{N}(0, \sigma_u^2)$ represents random intercepts for individual prompt topics.

### 12.4 Tail Risk & Sensitivity Distribution
We apply **Extreme Value Theory (EVT)** to model the upper 5th percentile of the Sensitivity Coefficient $\mathcal{S}$, isolating worst-case prompt fragility.

---

## 13. Reproducibility Requirements

To guarantee 100% reproducibility of all experimental findings:

1. **Version-Locked Model Checkpoints**: Exact model IDs (e.g., HuggingFace commit hashes, OpenAI/Gemini explicit snapshot dates).
2. **Environment Manifest**: Complete dependency freeze via `pyproject.toml` / `requirements.txt` with locked CUDA and PyTorch runtime versions.
3. **Random Seed Standardization**: All stochastic sampling runs fix `PYTHONHASHSEED`, `torch.manual_seed`, and API `seed` parameters to `42`.
4. **Structured Experiment Schema**: Every single inference run is serialized into an immutable JSONL line format (see Section 14).

---

## 14. Data Log Schema Specification

All experimental outputs will be logged to structured `.jsonl` files adhering to the following JSON schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AdversarialPromptExperimentRun",
  "type": "object",
  "required": [
    "experiment_id",
    "run_id",
    "timestamp",
    "model_name",
    "generation_config",
    "task_category",
    "original_prompt",
    "perturbed_prompt",
    "perturbation_type",
    "input_distance",
    "original_output",
    "perturbed_output",
    "output_distance",
    "exact_match_info"
  ],
  "properties": {
    "experiment_id": { "type": "string" },
    "run_id": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" },
    "model_name": { "type": "string" },
    "generation_config": {
      "type": "object",
      "properties": {
        "temperature": { "type": "number" },
        "top_p": { "type": "number" },
        "max_tokens": { "type": "integer" },
        "seed": { "type": "integer" }
      }
    },
    "task_category": { "type": "string" },
    "original_prompt": { "type": "string" },
    "perturbed_prompt": { "type": "string" },
    "perturbation_type": { "type": "string" },
    "input_distance": {
      "type": "object",
      "properties": {
        "lexical_char_levenshtein": { "type": "number" },
        "lexical_word_levenshtein": { "type": "number" },
        "syntactic_tree_edit_distance": { "type": "number" },
        "semantic_cosine_distance": { "type": "number" }
      }
    },
    "original_output": { "type": "string" },
    "perturbed_output": { "type": "string" },
    "output_distance": {
      "type": "object",
      "properties": {
        "textual_levenshtein": { "type": "number" },
        "rouge_l_f1": { "type": "number" },
        "bleu_score": { "type": "number" },
        "semantic_bertscore_f1": { "type": "number" },
        "semantic_embedding_cosine": { "type": "number" },
        "llm_judge_score_delta": { "type": "number" }
      }
    },
    "exact_match_info": {
      "type": "object",
      "properties": {
        "applicable": { "type": "boolean" },
        "original_match": { "type": "boolean" },
        "perturbed_match": { "type": "boolean" },
        "functional_failure_occurred": { "type": "boolean" }
      }
    },
    "sensitivity_coefficient": { "type": "number" }
  }
}
```
