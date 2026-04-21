"""Orbit 01-smooth-regressor (replica r1)

Gaussian Process regression with an RBF kernel and a learned WhiteKernel
noise term. Hyperparameters (length-scale, signal amplitude, noise level)
are fit by maximising the marginal likelihood with multiple restarts.
5-fold cross-validation on the 200 noisy training points was used OFFLINE
to confirm the CV MSE tracks the Bayes-optimal limit sigma^2 = 0.0025
(see log.md). At inference time we only call .predict on a GP fit to the
full training set.

Fitting happens at module import so `f(x)` is a thin wrapper.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel


_DATA_PATH = Path(__file__).resolve().parents[2] / "research" / "eval" / "data_train.npz"


def _fit_gp() -> GaussianProcessRegressor:
    data = np.load(_DATA_PATH)
    x_train = np.asarray(data["x_train"], dtype=float).reshape(-1, 1)
    y_train = np.asarray(data["y_train"], dtype=float)

    # RBF kernel + explicit white-noise term. Bounds are set wide so the
    # marginal-likelihood optimiser can find the true (signal variance,
    # length-scale, noise) without us hand-picking them.
    kernel = (
        ConstantKernel(constant_value=1.0, constant_value_bounds=(1e-3, 1e3))
        * RBF(length_scale=1.0, length_scale_bounds=(1e-2, 1e2))
        + WhiteKernel(noise_level=0.0025, noise_level_bounds=(1e-6, 1e-1))
    )

    gp = GaussianProcessRegressor(
        kernel=kernel,
        alpha=0.0,  # noise handled by the WhiteKernel term
        normalize_y=True,
        n_restarts_optimizer=10,
        random_state=0,
    )
    gp.fit(x_train, y_train)
    return gp


_GP = _fit_gp()


def f(x: np.ndarray) -> np.ndarray:
    """Predict smooth target y at inputs x.

    Args:
        x: 1-D numpy array of query locations in [-5, 5].

    Returns:
        1-D numpy array of predictions, same shape as `x`.
    """
    x = np.asarray(x, dtype=float)
    return _GP.predict(x.reshape(-1, 1))
