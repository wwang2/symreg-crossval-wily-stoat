---
issue: 2
parents: []
eval_version: eval-v1
metric: 0.000278
---

# Research Notes — orbit/01-smooth-regressor (replica r1)

**Hypothesis:** A Gaussian-process regressor with an RBF kernel and a learned
white-noise term, trained only on the 200 noisy training points, will fit the
hidden smooth target well below the 0.01 MSE target.

**Measured:** test MSE = **0.000278** on the evaluator's 500 clean points
(deterministic across seeds 1, 2, 3). That is 36× below the 0.01 target and
only ~11% of the Bayes-optimal noise floor `σ² = 0.0025` (the best MSE any
regressor could achieve on *noisy* test data). On clean test data the MSE can
drop well below σ² because the GP posterior mean *averages out* the training
noise.

**Implication:** GP-RBF already solves this orbit; no refinement needed.

## Approach

* **Model:** `ConstantKernel · RBF + WhiteKernel` fit with
  `sklearn.gaussian_process.GaussianProcessRegressor`. `normalize_y=True`.
  Marginal-likelihood optimisation with `n_restarts_optimizer=10` handles the
  hyperparameters (signal amplitude, length-scale, noise level) — no manual
  grid search required.
* **Why GP over polynomial bases?** Marginal likelihood self-tunes model
  complexity. Chebyshev ridge required a K-fold sweep over degree and reached
  the same CV floor only at deg ≥ 13 — GP-RBF reaches it in one fit.
* **K-fold CV** on the training data (no test-set peek) was used to
  *confirm* the model was not under-fit or over-fit: 5-fold CV MSE =
  **0.00257 ± 0.00059**, which matches σ² = 0.0025 to within a noise-level
  sampling error. This is the signature of a well-calibrated fit — CV MSE
  hitting the irreducible noise floor means the model is explaining as much
  signal as is extractable from the noisy folds.

**Fitted kernel (full train):**
`1.47² · RBF(length_scale=1.26) + WhiteKernel(noise_level=0.00163)`.

The learned noise level 0.00163 is below the true 0.0025 = σ², because the
maximum-likelihood estimate under-estimates noise when the kernel can flex to
explain it. That is fine here: test-set MSE shows no sign of over-fit.

## Results

| Seed | Metric (MSE) |
|------|--------------|
| 1    | 0.000278     |
| 2    | 0.000278     |
| 3    | 0.000278     |
| **Mean** | **0.000278 ± 0.0 (deterministic)** |

The evaluator's test `x` grid is fixed (not seeded); the `seed` arg is kept
for API compatibility. So all three runs return identical metrics — this is
expected, not a bug.

### K-fold CV comparison (on training data only, 5-fold)

| Method                         | CV MSE (mean ± std) |
|--------------------------------|---------------------|
| Chebyshev deg 11 + RidgeCV     | 0.00433 ± 0.00073   |
| Chebyshev deg 13 + RidgeCV     | 0.00264 ± 0.00059   |
| Chebyshev deg 15 + RidgeCV     | 0.00259 ± 0.00065   |
| **GP-RBF (marg-lik tuned)**    | **0.00257 ± 0.00059** |
| Bayes-optimal floor σ²         | 0.00250             |

Once the model class is rich enough (deg ≥ 13, or GP-RBF), everyone hits the
σ² floor — the data carry no more information. That settles model-selection:
pick the method that *also* predicts well on clean points, which is GP-RBF.

### Test-set MSE

| Method                         | Test MSE on 500 clean points |
|--------------------------------|------------------------------|
| Constant baseline              | 1.462                        |
| Chebyshev deg 13 + RidgeCV     | 0.000318                     |
| **GP-RBF (this orbit)**        | **0.000278**                 |

GP-RBF and Chebyshev-13 are within a factor of 1.14 on clean test data;
either would pass the 0.01 target easily. GP-RBF wins on parsimony: one
`fit()` call, no degree sweep.

## Prior Art & Novelty

### What is already known
- Gaussian process regression with RBF kernel and white-noise term is the
  textbook approach for smooth 1-D nonparametric regression: Rasmussen &
  Williams (2006), *Gaussian Processes for Machine Learning*, MIT Press.
- Cross-validation for kernel/degree selection in nonparametric regression
  is standard (Hastie, Tibshirani, Friedman, *Elements of Statistical
  Learning*, Ch. 7).

### What this orbit adds
Nothing novel. This orbit applies known textbook methods to a benchmark
sanity-check problem. The value here is as a cross-validation replica — an
independent fit, on an independent branch, that confirms the primary orbit's
conclusion on an orbit the campaign deliberately designed to be easy.

### Honest positioning
Benchmark sanity-check. If GP-RBF *didn't* clear this by 30×, something
would be very wrong.

## Self-check against figure rubric

* `figures/results.png` — 2×2 multi-panel with `(a)`–`(d)` labels:
  - (a) CV MSE vs Chebyshev degree with GP reference line + σ² floor
  - (b) test-set MSE bar chart (constant / cheb-13 / GP-RBF) + target line
  - (c) GP posterior mean, ±2σ band, training points, true target
  - (d) residual vs truth, with ±2σ predictive band and ±σ noise scale
* `figures/narrative.png` — single-panel summary with fit, truth, band,
  monospace metric readout.
* `figures/behavior.gif` — GP learning curve: fits at N=5, 10, 20, …, 200,
  uncertainty band shrinks as N grows, MSE in the title reports the
  per-frame test MSE (1.47 → 0.04 → 0.0017 → 0.0003).
* All figures use the `research/style.md` rcParams block (viridis/muted
  palette, no boxed text, panel labels, constrained_layout).

## Conclusion

GP-RBF solves orbit 01-smooth-regressor with test MSE ≈ 2.8 × 10⁻⁴, ~36× below
the 0.01 target. K-fold CV corroborates the fit is calibrated at the noise
floor. Replica agrees with primary's expected approach.

## References

- Rasmussen, C. E. & Williams, C. K. I. (2006). *Gaussian Processes for
  Machine Learning.* MIT Press.
  [gaussianprocess.org/gpml](https://gaussianprocess.org/gpml/)
- Hastie, T., Tibshirani, R. & Friedman, J. (2009). *The Elements of
  Statistical Learning* (2nd ed.). Springer.

![results](https://raw.githubusercontent.com/wwang2/symreg-crossval-wily-stoat/refs/heads/orbit/01-smooth-regressor.r1/orbits/01-smooth-regressor/figures/results.png)

![narrative](https://raw.githubusercontent.com/wwang2/symreg-crossval-wily-stoat/refs/heads/orbit/01-smooth-regressor.r1/orbits/01-smooth-regressor/figures/narrative.png)

![behavior](https://raw.githubusercontent.com/wwang2/symreg-crossval-wily-stoat/refs/heads/orbit/01-smooth-regressor.r1/orbits/01-smooth-regressor/figures/behavior.gif)

## Iteration 1
- What I tried: GP-RBF with WhiteKernel, marginal-likelihood optimisation, `n_restarts_optimizer=10`, normalize_y=True.
- Metric: 0.000278 (test), 0.00257 ± 0.00059 (5-fold CV on training data)
- Next: exiting — target met by 36×, no refinement planned.
