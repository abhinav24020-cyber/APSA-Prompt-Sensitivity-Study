"""Global random seed management across all RNG libraries."""

import random


class SeedManager:
    """Set deterministic seeds across random, numpy, torch, and CUDA."""

    @staticmethod
    def set_global_seed(seed: int) -> None:
        """Apply ``seed`` to all known RNG libraries.

        Covers: random, numpy, torch (CPU + CUDA), and sets PYTHONHASHSEED.
        API-level seed parameters are passed separately per provider call.
        """
        import os
        os.environ["PYTHONHASHSEED"] = str(seed)
        random.seed(seed)
        try:
            import numpy as np
            np.random.seed(seed)
        except ImportError:
            pass
        try:
            import torch
            torch.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
        except ImportError:
            pass
