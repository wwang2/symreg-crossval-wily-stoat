#!/usr/bin/env bash
# Reproduce orbit 01-smooth-regressor (replica r1).
# Fits GP-RBF on the 200 noisy training points and evaluates on 500 clean
# points. Deterministic.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

for SEED in 1 2 3; do
    python3 research/eval/evaluator.py \
        --solution orbits/01-smooth-regressor/solution.py \
        --seed "$SEED"
done
