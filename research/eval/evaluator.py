"""Evaluator for the symbolic-regression cross-validation benchmark.

Reads the solution's `f(x)` implementation at `--solution`, evaluates MSE
on a held-out set of 500 CLEAN points drawn from the hidden target
function on x in [-5, 5]. Prints `METRIC=<mse>` on stdout.

The hidden target is fixed at evaluator-build time (not seen by
solutions). Training data (200 noisy points, sigma=0.05) is shipped
alongside this evaluator at `research/eval/data_train.npz` with arrays
`x_train` and `y_train`. Solutions fit on the training data and are
graded on the clean test set.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import numpy as np


# Hidden target function. Deliberately picked to be smooth, bounded, and
# learnable by polynomial-basis / smoothing-spline / small-NN solutions
# so the target MSE < 0.01 is achievable without memorising noise.
def _target(x: np.ndarray) -> np.ndarray:
    return np.sin(2.0 * x) + 0.3 * x


X_LOW, X_HIGH = -5.0, 5.0
N_TRAIN = 200
N_TEST = 500
NOISE_SIGMA = 0.05
TRAIN_SEED = 20260420


def _train_data() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(TRAIN_SEED)
    x = rng.uniform(X_LOW, X_HIGH, size=N_TRAIN)
    y = _target(x) + rng.normal(0.0, NOISE_SIGMA, size=N_TRAIN)
    return x, y


def _test_data(seed: int) -> tuple[np.ndarray, np.ndarray]:
    # Clean held-out test set. The x-locations are FIXED (same 500 points
    # every seed) so the metric is fully deterministic per solution — any
    # drift across seeds would indicate non-determinism in the solution
    # itself. The `seed` argument is accepted for API compatibility.
    del seed
    rng = np.random.default_rng(10_000)
    x = rng.uniform(X_LOW, X_HIGH, size=N_TEST)
    x.sort()
    y = _target(x)
    return x, y


def _load_solution(path: str):
    spec = importlib.util.spec_from_file_location("solution", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "f"):
        raise AttributeError(f"{path} must define a function `f(x)`")
    return module.f


def evaluate(solution_path: str, seed: int) -> float:
    f = _load_solution(solution_path)
    x_test, y_true = _test_data(seed)
    y_pred = np.asarray(f(x_test), dtype=float)
    if y_pred.shape != y_true.shape:
        raise ValueError(
            f"solution returned shape {y_pred.shape} but expected {y_true.shape}"
        )
    if not np.all(np.isfinite(y_pred)):
        return float("inf")
    return float(np.mean((y_pred - y_true) ** 2))


def _maybe_write_train_npz() -> None:
    out = Path(__file__).parent / "data_train.npz"
    if out.exists():
        return
    x, y = _train_data()
    np.savez(out, x_train=x, y_train=y)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solution")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument(
        "--emit-train",
        action="store_true",
        help="(re)generate research/eval/data_train.npz and exit.",
    )
    args = parser.parse_args()

    if args.emit_train:
        out = Path(__file__).parent / "data_train.npz"
        x, y = _train_data()
        np.savez(out, x_train=x, y_train=y)
        print(f"wrote {out}")
        return 0

    if not args.solution:
        parser.error("--solution is required unless --emit-train is passed")
    _maybe_write_train_npz()
    metric = evaluate(args.solution, args.seed)
    print(f"METRIC={metric:.6f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
