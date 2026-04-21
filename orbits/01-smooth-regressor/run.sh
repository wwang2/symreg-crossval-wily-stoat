#!/usr/bin/env bash
# Reproduce orbit 01 from scratch.
#
# - Fits solution.py on the frozen training data at research/eval/data_train.npz
#   (CV over GP + smoothing spline + RBF kernel ridge; model is selected
#   and refit at import time).
# - Runs the evaluator on 3 seeds.
# - Regenerates figures/{results.png, narrative.png, behavior.gif}.
#
# Run from the repo root (or a worktree checkout of orbit/01-smooth-regressor).

set -euo pipefail

SEEDS=(1 2 3)
SOL="orbits/01-smooth-regressor/solution.py"

for s in "${SEEDS[@]}"; do
    python3 research/eval/evaluator.py --solution "$SOL" --seed "$s"
done

python3 orbits/01-smooth-regressor/figures/_make_figures.py
