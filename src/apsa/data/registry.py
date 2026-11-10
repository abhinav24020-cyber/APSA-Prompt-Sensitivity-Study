"""Dataset registry: maps dataset names to loader classes."""

from .base_dataset import BaseDataset
from .baseline import BaselineCSVDataset
from .gsm8k import GSM8KDataset
from .math_dataset import MATHDataset
from .humaneval import HumanEvalDataset
from .mbpp import MBPPDataset
from .squad_v2 import SQuADv2Dataset
from .hotpotqa import HotpotQADataset
from .cnn_dailymail import CNNDailyMailDataset
from .xsum import XSumDataset

_REGISTRY: dict[str, type[BaseDataset]] = {
    "baseline":     BaselineCSVDataset,
    "gsm8k":        GSM8KDataset,
    "math":         MATHDataset,
    "humaneval":    HumanEvalDataset,
    "mbpp":         MBPPDataset,
    "squad_v2":     SQuADv2Dataset,
    "hotpotqa":     HotpotQADataset,
    "cnn_dailymail":CNNDailyMailDataset,
    "xsum":         XSumDataset,
}


def get_dataset(name: str) -> BaseDataset:
    """Return an instantiated dataset loader for the given name."""
    if name not in _REGISTRY:
        raise KeyError(f"Unknown dataset '{name}'. Available: {list(_REGISTRY)}")
    return _REGISTRY[name]()
