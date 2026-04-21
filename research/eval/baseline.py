"""Baseline solution: constant predictor (mean of training y).

Terrible fit by design — orbits must beat this easily.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

_DATA = np.load(Path(__file__).parent / "data_train.npz")
_Y_MEAN = float(np.mean(_DATA["y_train"]))


def f(x: np.ndarray) -> np.ndarray:
    return np.full_like(np.asarray(x, dtype=float), _Y_MEAN)
