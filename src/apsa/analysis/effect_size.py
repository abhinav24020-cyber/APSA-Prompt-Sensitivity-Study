"""Effect size estimators: Cliff's Delta and Cohen's d."""

from dataclasses import dataclass


@dataclass
class EffectSizeResult:
    cliffs_delta: float
    cohens_d: float
    magnitude: str   # "negligible" | "small" | "medium" | "large"


class EffectSizeCalculator:
    """Compute Cliff's Delta and Cohen's d for paired samples."""

    def compute(
        self,
        group_a: list[float],
        group_b: list[float],
    ) -> EffectSizeResult:
        # TODO: implement Cliff's Delta and Cohen's d
        raise NotImplementedError
