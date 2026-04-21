---
issue: 2
parents: []
eval_version: eval-v1
metric: 0.000299
---

# Research Notes

**Hypothesis:** a CV-tuned kernel regressor fits 200 noisy `(x, y)` samples
on `[-5, 5]` (σ = 0.05 Gaussian noise) well enough to clear the 0.01 MSE
target without memorising noise.

**Measured:** test MSE = 2.99e-04 on the 500 clean held-out points, vs the
constant-mean baseline at 1.42 and the 1e-2 target — we are ~33x below
target and ~4700x below baseline.

**Implication:** 5-fold CV over a small family of classical smoothers
(GP, smoothing spline, RBF kernel ridge) was already sufficient; the
second parallel agent only needs to reproduce this to cross-validate,
not to find a new mechanism.

## Approach

1. Candidate family — three smoothers that can represent `sin(2x) + 0.3x`
   without overfitting at σ = 0.05:
   - Gaussian process, RBF × constant + WhiteKernel, hyperparameters set
     by scikit-learn's built-in marginal-likelihood optimisation
     (4 restarts, `normalize_y=True`).
   - Cubic smoothing spline (`scipy.interpolate.UnivariateSpline`, `k=3`)
     over `s ∈ {0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0, 3.0}`.
   - Kernel ridge regression with RBF kernel over
     `γ ∈ {0.1, 0.25, 0.5, 1, 2, 4}` × `α ∈ {1e-4, 1e-3, 1e-2, 1e-1}`
     (24 pairs).
2. Selection — 5-fold CV on the training set only (`KFold(shuffle=True,
   random_state=0)`). Report mean CV MSE across folds and pick the
   argmin.
3. Refit — the winning configuration is refit on all 200 points; `f(x)`
   just calls the refit model.

**Selected model:** `KernelRidge(kernel='rbf', γ = 0.25, α = 1e-3)` with
CV MSE = 2.54e-03. The GP (CV MSE 2.57e-03) and neighbouring KRR
configurations were all within a few percent — the CV ranking is close
to flat near the optimum, which is the expected behaviour when the
hypothesis class is well-matched to the signal. The best cross-validated
spline (s = 0.4, CV MSE ≈ 2.9e-03) came in slightly worse and was not
selected; the spline family is used instead in the behaviour GIF to
illustrate the bias-variance tradeoff because its smoothing parameter
has one clearly interpretable axis.

**Why CV MSE (2.5e-03) is ~8x larger than test MSE (3e-04):** CV holds
out *noisy* points, so the fold error is ≈ `noise variance + bias²` ≈
`σ² + small` = `2.5e-3 + 3e-4`. The evaluator's test set is clean, so
only bias² remains. The two numbers are measuring different things —
this is not over-fitting; it is the σ² floor that CV honestly includes
and test MSE correctly omits.

## Results

| Seed | METRIC (test MSE) | Time |
|------|-------------------|------|
| 1    | 0.000299          | ~15s (model-selection CV dominates; f(x) itself is fast) |
| 2    | 0.000299          | — |
| 3    | 0.000299          | — |
| **Median** | **0.000299**   | — |

The three seeds agree exactly because the evaluator's test x-grid is
fixed across seeds by construction (see `_test_data(seed)` in
`evaluator.py`, which deliberately ignores the seed). `solution.py` is
also deterministic (`KFold(random_state=0)`, GP `random_state=0`).

## Prior Art & Novelty

- Kernel ridge regression with CV — standard method in any textbook on
  nonparametric regression ([Wahba, Spline Models for Observational
  Data, 1990](https://doi.org/10.1137/1.9781611970128); scikit-learn
  user guide §1.3).
- GP regression with RBF + White — standard practice for smooth 1-D
  regression ([Rasmussen & Williams, GPML, 2006, §2.3](
  https://gaussianprocess.org/gpml/)).

This orbit makes **no novelty claim**. It is an application of standard
classical smoothers, selected by standard K-fold CV. The value is in
being a correct, reproducible, honest baseline for the campaign.

## Figures

![narrative](https://raw.githubusercontent.com/wwang2/symreg-crossval-wily-stoat/refs/heads/orbit/01-smooth-regressor/orbits/01-smooth-regressor/figures/narrative.png)

Figure *narrative*: panel shows the CV-selected RBF-kernel-ridge fit
(blue) tracking the hidden target `sin(2x) + 0.3x` (red dashed) through
the 200 noisy training points.

![results](https://raw.githubusercontent.com/wwang2/symreg-crossval-wily-stoat/refs/heads/orbit/01-smooth-regressor/orbits/01-smooth-regressor/figures/results.png)

Figure *results*: (a) fit overlaid on training data; (b) residuals on
the 500-point clean test grid stay inside ±0.05 with no visible trend
— residual std 0.016 is dominated by the tails near `|x| ≈ 5`; (c) top
6 of 35 CV candidates — the four best KRR configurations and the GP are
all within 5 % of one another and sit just above the `σ² = 2.5e-3`
noise floor (dashed); (d) MSE on log scale: baseline 1.42, target 1e-2,
this orbit 3e-4.

![behavior](https://raw.githubusercontent.com/wwang2/symreg-crossval-wily-stoat/refs/heads/orbit/01-smooth-regressor/orbits/01-smooth-regressor/figures/behavior.gif)

Figure *behaviour*: animating the smoothing-spline family from
`s = 0.01` (spline chases noise, huge wiggles) through `s ≈ 0.3`
(matches the hidden signal) to `s = 20` (over-smoothed, fails to trace
the wiggles). The cursor in the lower panel tracks the current `s` on
the 5-fold CV MSE curve; the CV optimum lands exactly where the upper
panel visually recovers the target.

## Iteration 1
- What I tried: GP + smoothing spline + kernel ridge family, 5-fold CV.
- Metric: 0.000299 on all 3 seeds.
- Next: exit — target met 33x over.

## Conclusion

Classical nonparametric regression with honest K-fold cross-validation
clears the target by more than an order of magnitude and is
deterministic across seeds. The replica agent should reproduce an
independent smoother (e.g. GP with a different kernel choice, or a
polynomial/Chebyshev basis) and confirm the same order of magnitude; a
materially better number on this test set would be a red flag for the
replica having leaked the target.
