"""C_random: Random edit control baseline perturbation."""

import random
from apsa.perturbations.base_perturbation import BasePerturbation, PerturbationConfig


class RandomEditPerturbation(BasePerturbation):
    """Inserts arbitrary character/word edits within a small edit-distance budget.

    Used as the C_random control condition to differentiate targeted
    perturbation sensitivity from generic noise sensitivity.
    """

    @property
    def perturbation_type(self) -> str:
        return "random_edit"

    def _apply_transform(self, prompt: str, config: PerturbationConfig) -> str | None:
        rng = random.Random(config.seed)
        n_edits = config.params.get("n_edits", 2)
        ALPHABET = "abcdefghijklmnopqrstuvwxyz "

        chars = list(prompt)
        if len(chars) < 3:
            return None

        for _ in range(n_edits):
            if not chars:
                break
            op = rng.choice(["substitute", "insert", "delete"])
            pos = rng.randint(0, len(chars) - 1)

            if op == "substitute":
                chars[pos] = rng.choice(ALPHABET)
            elif op == "insert":
                chars.insert(pos, rng.choice(ALPHABET))
            elif op == "delete" and len(chars) > 1:
                chars.pop(pos)

        result = "".join(chars)
        return result if result != prompt else None
