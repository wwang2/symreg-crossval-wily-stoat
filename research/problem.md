# Symbolic Regression with Cross-Validation

## Problem Statement

Given 200 noisy (x, y) data points sampled from an unknown function with
Gaussian noise (sigma = 0.05), find a function `f(x)` that best fits the
underlying signal. The inputs are drawn from the interval `x ∈ [-5, 5]`.

The ground-truth target function is chosen at evaluator-build time and
kept fixed in `research/eval/evaluator.py`. Solutions do NOT see the
target function — they only see the 200 noisy training points (available
as `research/eval/data_train.npz` with arrays `x_train`, `y_train`), and
must generalize to the held-out test set of 500 clean points that the
evaluator uses to score the solution.

## Solution Interface

Solution must be a Python file with a function

```python
def f(x: np.ndarray) -> np.ndarray:
    ...
```

that takes a 1-D numpy array and returns a 1-D numpy array of the same
shape. The solution lives at `orbits/<name>/solution.py`.

## Success Metric

Mean-squared error (MSE) on a held-out set of 500 clean points,
generated from the same hidden target function on `x ∈ [-5, 5]` (direction:
minimize). Target: **MSE < 0.01**. Evaluator reports
`METRIC=<mse>` on stdout and is deterministic given the seed.

## Cross-Validation Mode

`parallel_agents: 2` — each orbit is solved independently by two agents
(primary + one replica) on sibling branches. The replica-panel agent
cross-checks them before any winner is declared. This guards against
an individual agent memorising the noisy training data rather than the
underlying signal.

## Budget

Max 2 orbits.
