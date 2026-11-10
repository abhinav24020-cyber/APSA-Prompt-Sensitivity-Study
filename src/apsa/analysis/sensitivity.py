import numpy as np
import scipy.stats as stats
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

@dataclass
class SensitivityRecord:
    experiment_id: str
    model: str
    task_category: str
    prompt_id: str
    perturbation_type: str
    
    d_input: float
    d_output: float
    d_semantic_input: Optional[float] = None
    
    # Optional task-level performance metrics
    original_output_correct: Optional[bool] = None
    perturbed_output_correct: Optional[bool] = None


class SensitivityAnalyzer:
    """Analyzes prompt sensitivity and output deviations across experimental records.
    
    Calculates primary sensitivity metrics such as:
    S = D_output / (D_input + eta)  [Smoothed Ratio]
    or
    S = D_output / max(eta, D_input) [Methodology Section 4.3 Definition]
    
    where eta (smoothing constant, default 1e-4) prevents division by zero.
    Note: eta is distinct from the epsilon perturbation budget (D_input <= epsilon).
    
    Also provides absolute, normalized, and aggregate output deviations subject to budgets.
    """
    
    def __init__(self, records: List[SensitivityRecord], epsilon: float = 1e-4, eta: Optional[float] = None):
        self.records = records
        self.eta = eta if eta is not None else epsilon
        self.epsilon = self.eta  # Backwards compatibility alias
        
    def calculate_sensitivity(self, record: SensitivityRecord, method: str = "ratio_smoothed") -> float:
        """Calculates sensitivity measure.
        
        Args:
            record: SensitivityRecord with d_input and d_output.
            method: 'ratio_smoothed' for D_out / (D_in + eta) (default),
                    'methodology_bounded' for D_out / max(eta, D_in) (Methodology Section 4.3).
        """
        if record.d_input < 0 or record.d_output < 0:
            raise ValueError(f"Distances must be non-negative, got d_input={record.d_input}, d_output={record.d_output}")
        if record.d_input == 0.0 and record.d_output == 0.0:
            return 0.0
        if method == "methodology_bounded":
            return record.d_output / max(self.eta, record.d_input)
        return record.d_output / (record.d_input + self.eta)

    def calculate_normalized_output_deviation(self, record: SensitivityRecord, max_possible_d_out: float = 1.0) -> float:
        """Calculates normalized output deviation against a theoretical maximum."""
        if max_possible_d_out <= 0:
            raise ValueError(f"max_possible_d_out must be positive, got {max_possible_d_out}")
        return min(1.0, max(0.0, record.d_output / max_possible_d_out))

    def output_deviation_per_unit_input_change(self, record: SensitivityRecord) -> float:
        """Alias for sensitivity: output deviation per unit of syntactic/lexical input change."""
        return self.calculate_sensitivity(record)

    # Aggregate statistical measurements
    
    def mean_output_deviation(self, records: Optional[List[SensitivityRecord]] = None) -> float:
        records = records if records is not None else self.records
        if not records: return 0.0
        return float(np.mean([r.d_output for r in records]))

    def median_output_deviation(self, records: Optional[List[SensitivityRecord]] = None) -> float:
        records = records if records is not None else self.records
        if not records: return 0.0
        return float(np.median([r.d_output for r in records]))
        
    def confidence_interval_output_deviation(self, records: Optional[List[SensitivityRecord]] = None, confidence: float = 0.95) -> Tuple[float, float]:
        """Calculates the confidence interval for the mean output deviation."""
        records = records if records is not None else self.records
        if not records: return (0.0, 0.0)
        data = [r.d_output for r in records]
        if len(data) == 1:
            return (float(data[0]), float(data[0]))
        mean = float(np.mean(data))
        sem = float(stats.sem(data))
        if sem == 0.0 or np.isnan(sem):
            return (mean, mean)
        # Using t-distribution
        margin = float(sem * stats.t.ppf((1 + confidence) / 2., len(data) - 1))
        return (mean - margin, mean + margin)
        
    def max_output_deviation_under_budget(
        self,
        semantic_budget: Optional[float] = None,
        lexical_budget: Optional[float] = None,
    ) -> float:
        """Finds max D_output subject to d_semantic_input <= semantic_budget and/or d_input <= lexical_budget.
        
        This aligns with the primary research objective:
        max D_output subject to D_input <= epsilon.
        """
        valid_records = self.records
        if semantic_budget is not None:
            valid_records = [
                r for r in valid_records
                if r.d_semantic_input is not None and r.d_semantic_input <= semantic_budget
            ]
        if lexical_budget is not None:
            valid_records = [r for r in valid_records if r.d_input <= lexical_budget]
        if not valid_records: return 0.0
        return max(r.d_output for r in valid_records)

    # Retrieval functions for edge cases and highest sensitivity categories
    
    def top_k_sensitivity_cases(self, k: int = 5) -> List[Tuple[SensitivityRecord, float]]:
        scored = [(r, self.calculate_sensitivity(r)) for r in self.records]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]

    def top_k_output_deviation_cases(self, k: int = 5) -> List[Tuple[SensitivityRecord, float]]:
        scored = [(r, r.d_output) for r in self.records]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]

    def _highest_sensitivity_per_group(self, key_func) -> Dict[str, float]:
        grouped = defaultdict(list)
        for r in self.records:
            grouped[key_func(r)].append(self.calculate_sensitivity(r))
        return {k: float(max(v)) for k, v in grouped.items()}

    def _mean_sensitivity_per_group(self, key_func) -> Dict[str, float]:
        grouped = defaultdict(list)
        for r in self.records:
            grouped[key_func(r)].append(self.calculate_sensitivity(r))
        return {k: float(np.mean(v)) for k, v in grouped.items()}

    def highest_sensitivity_per_model(self) -> Dict[str, float]:
        return self._highest_sensitivity_per_group(lambda r: r.model)

    def highest_sensitivity_per_task(self) -> Dict[str, float]:
        return self._highest_sensitivity_per_group(lambda r: r.task_category)
        
    def highest_sensitivity_per_perturbation(self) -> Dict[str, float]:
        return self._highest_sensitivity_per_group(lambda r: r.perturbation_type)
