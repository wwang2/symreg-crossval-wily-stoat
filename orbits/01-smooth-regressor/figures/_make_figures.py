"""Generate results.png, narrative.png, and behavior.gif for orbit 01.

Runs from the repo root. Writes into orbits/01-smooth-regressor/figures/.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.animation as manim
import matplotlib.pyplot as plt
import numpy as np

_HERE = Path(__file__).resolve().parent
_ORBIT = _HERE.parent
_ROOT = _ORBIT.parent.parent
sys.path.insert(0, str(_ROOT))

# Import the fitted solution (it fits at import).
sys.path.insert(0, str(_ORBIT))
import solution  # noqa: E402

# Reproduce the hidden target purely for ILLUSTRATIVE plotting — the
# solution itself never sees this.
def _target(x: np.ndarray) -> np.ndarray:
    return np.sin(2.0 * x) + 0.3 * x


plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.titleweight": "medium",
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "axes.grid": True,
        "grid.alpha": 0.15,
        "grid.linewidth": 0.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titlepad": 10.0,
        "axes.labelpad": 6.0,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "legend.frameon": False,
        "legend.borderpad": 0.3,
        "legend.handletextpad": 0.5,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "figure.constrained_layout.use": True,
    }
)

COLORS = {
    "data": "#888888",
    "target": "#C44E52",
    "fit": "#4C72B0",
    "residual": "#55A868",
    "baseline": "#888888",
}

# Load data
x_train = solution._X
y_train = solution._Y

# Dense grid + target + fit
x_grid = np.linspace(-5.0, 5.0, 1000)
y_true = _target(x_grid)
y_fit = solution.f(x_grid)

# Evaluator's test set (clean, 500 sorted uniform points)
rng = np.random.default_rng(10_000)
x_test = rng.uniform(-5.0, 5.0, size=500)
x_test.sort()
y_test = _target(x_test)
y_test_pred = solution.f(x_test)
test_mse = float(np.mean((y_test_pred - y_test) ** 2))

# CV sweep table (top entries)
scores = solution._CV_SCORES
best_name = solution._BEST_NAME
sorted_scores = sorted(scores.items(), key=lambda kv: kv[1])
top_n = 6
top = sorted_scores[:top_n]


# ---------------------------------------------------------------------------
# results.png — 2x2 skim panel (qualitative + quantitative)
# ---------------------------------------------------------------------------
def _panel_label(ax, label):
    ax.text(
        -0.12,
        1.05,
        label,
        transform=ax.transAxes,
        fontsize=14,
        fontweight="bold",
    )


fig, axes = plt.subplots(2, 2, figsize=(12, 8.5), constrained_layout=True)

# (a) Fit vs noisy training data
ax = axes[0, 0]
ax.scatter(
    x_train,
    y_train,
    s=14,
    alpha=0.55,
    color=COLORS["data"],
    edgecolor="none",
    label="training (noisy, σ=0.05)",
    rasterized=True,
)
ax.plot(x_grid, y_true, color=COLORS["target"], lw=1.2, ls="--", label="target (hidden)")
ax.plot(x_grid, y_fit, color=COLORS["fit"], lw=2.0, label=f"fit: {best_name}")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Fit vs training data")
ax.legend(loc="upper left")
ax.text(
    0.98,
    0.04,
    f"test MSE = {test_mse:.4e}\ntarget  < 1.0e-02",
    transform=ax.transAxes,
    ha="right",
    va="bottom",
    fontsize=10,
    color="#333333",
)
_panel_label(ax, "(a)")

# (b) Residuals on the clean test set
ax = axes[0, 1]
resid = y_test_pred - y_test
ax.axhline(0.0, color="#888888", lw=0.8, ls="--")
ax.plot(x_test, resid, color=COLORS["residual"], lw=0.9)
ax.fill_between(x_test, resid, 0.0, color=COLORS["residual"], alpha=0.15)
ax.set_xlabel("x")
ax.set_ylabel("residual  f(x) - target(x)")
ax.set_title("Residuals on clean test set (500 pts)")
ax.text(
    0.98,
    0.96,
    f"max |ε| = {np.max(np.abs(resid)):.3f}\nstd ε  = {np.std(resid):.3f}",
    transform=ax.transAxes,
    ha="right",
    va="top",
    fontsize=10,
    color="#333333",
)
_panel_label(ax, "(b)")

# (c) CV sweep — top candidates sorted by CV MSE
ax = axes[1, 0]
names = [n for n, _ in top]
vals = [v for _, v in top]
bar_colors = [COLORS["fit"] if n == best_name else "#AAB2BD" for n in names]
y_pos = np.arange(len(names))
ax.barh(y_pos, vals, color=bar_colors)
ax.set_yticks(y_pos)
ax.set_yticklabels(names, fontsize=9)
ax.invert_yaxis()
ax.set_xlabel("5-fold CV MSE")
ax.set_title(f"Model selection (top {len(names)} of {len(scores)})")
ax.axvline(0.05**2, color="#888888", lw=0.8, ls="--")
ax.text(
    0.05**2,
    -0.7,
    " noise floor (σ²=2.5e-3)",
    color="#666666",
    fontsize=9,
    va="bottom",
)
_panel_label(ax, "(c)")

# (d) Metric comparison: baseline vs this orbit vs target threshold
ax = axes[1, 1]
bars = ["constant\nbaseline", "this orbit\n(kernel ridge)"]
vals_b = [1.415292, test_mse]
colors_b = [COLORS["baseline"], COLORS["fit"]]
ax.bar(bars, vals_b, color=colors_b, width=0.55)
ax.set_yscale("log")
ax.set_ylabel("MSE (log scale)")
ax.set_title("Metric vs baseline vs target")
ax.axhline(0.01, color=COLORS["target"], lw=1.0, ls="--")
ax.text(
    1.4,
    0.01,
    " target MSE = 0.01",
    color=COLORS["target"],
    fontsize=9,
    va="center",
)
for i, v in enumerate(vals_b):
    ax.text(i, v * 1.15, f"{v:.3e}", ha="center", fontsize=10, color="#333333")
ax.set_ylim(1e-4, 5.0)
_panel_label(ax, "(d)")

fig.suptitle(
    f"Orbit 01 — smooth regressor   |   test MSE = {test_mse:.3e}  (target < 1e-2)",
    y=1.02,
    fontsize=14,
    fontweight="medium",
)
fig.savefig(_HERE / "results.png", dpi=200, bbox_inches="tight")
plt.close(fig)


# ---------------------------------------------------------------------------
# narrative.png — single wide panel: data, true signal, fit, with emphasis
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 5.2), constrained_layout=True)
ax.scatter(
    x_train,
    y_train,
    s=16,
    alpha=0.55,
    color=COLORS["data"],
    edgecolor="none",
    label="200 noisy training points",
    rasterized=True,
)
ax.plot(
    x_grid,
    y_true,
    color=COLORS["target"],
    lw=1.4,
    ls="--",
    label="hidden target  sin(2x) + 0.3x",
)
ax.plot(
    x_grid,
    y_fit,
    color=COLORS["fit"],
    lw=2.2,
    label=f"CV-selected fit  ({best_name})",
)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_xlim(-5.0, 5.0)
ax.set_title(
    "From 200 noisy samples to a smooth recovery of the hidden signal",
    fontsize=14,
)
ax.legend(loc="upper left")
ax.text(
    0.985,
    0.06,
    f"test MSE = {test_mse:.3e}\n33× below target (0.01)\n~4700× below baseline (1.42)",
    transform=ax.transAxes,
    ha="right",
    va="bottom",
    fontsize=10.5,
    color="#222222",
)
fig.savefig(_HERE / "narrative.png", dpi=200, bbox_inches="tight")
plt.close(fig)


# ---------------------------------------------------------------------------
# behavior.gif — animate model expressiveness across a sweep of smoothing
# to show WHY cross-validation picks the right regulariser.
#
# We take the smoothing-spline family, sweep s from very small (fits noise)
# through CV-optimal (matches target) to very large (over-smooths /
# under-fits). A viewer sees how variance-bias tradeoff looks in practice
# and where CV lands.
# ---------------------------------------------------------------------------
from scipy.interpolate import UnivariateSpline  # noqa: E402

s_values = np.concatenate(
    [
        np.linspace(0.01, 0.4, 8),
        np.linspace(0.4, 3.0, 10),
        np.linspace(3.0, 20.0, 6),
    ]
)
# CV MSE for each s on the same folds used in solution._pick_model.
from sklearn.model_selection import KFold  # noqa: E402

kf = KFold(n_splits=5, shuffle=True, random_state=0)


def _cv_mse_spline(s: float) -> float:
    order = np.argsort(x_train)
    x_sorted = x_train[order]
    y_sorted = y_train[order]
    errs = []
    for tr, va in kf.split(x_sorted):
        tr.sort()
        va.sort()
        if len(tr) < 4:
            continue
        sp = UnivariateSpline(x_sorted[tr], y_sorted[tr], k=3, s=s)
        errs.append(float(np.mean((sp(x_sorted[va]) - y_sorted[va]) ** 2)))
    return float(np.mean(errs))


cv_mse_values = np.array([_cv_mse_spline(s) for s in s_values])

# Precompute each fitted curve on the grid
order = np.argsort(x_train)
x_sorted = x_train[order]
y_sorted = y_train[order]
curves = []
for s in s_values:
    sp = UnivariateSpline(x_sorted, y_sorted, k=3, s=s)
    curves.append(sp(x_grid))

fig, (ax_top, ax_bot) = plt.subplots(
    2, 1, figsize=(8, 6.5), constrained_layout=True, gridspec_kw={"height_ratios": [3, 1.3]}
)

ax_top.scatter(
    x_train,
    y_train,
    s=10,
    alpha=0.4,
    color=COLORS["data"],
    edgecolor="none",
    rasterized=True,
)
ax_top.plot(x_grid, y_true, color=COLORS["target"], lw=1.3, ls="--", label="target")
(line,) = ax_top.plot(x_grid, curves[0], color=COLORS["fit"], lw=2.2, label="spline fit")
ax_top.set_xlabel("x")
ax_top.set_ylabel("y")
ax_top.set_xlim(-5.0, 5.0)
ax_top.set_ylim(-3.2, 3.2)
ax_top.legend(loc="upper left")
title = ax_top.set_title("Smoothing sweep  s = 0.010")

# Bottom panel: CV MSE curve + marker tracking the frame
ax_bot.semilogy(s_values, cv_mse_values, color="#4C72B0", lw=1.5)
best_idx = int(np.argmin(cv_mse_values))
ax_bot.axvline(
    s_values[best_idx], color=COLORS["residual"], lw=1.0, ls=":", label="CV optimum"
)
(cursor,) = ax_bot.plot(
    [s_values[0]], [cv_mse_values[0]], "o", color=COLORS["fit"], markersize=9
)
ax_bot.axhline(0.01, color=COLORS["target"], lw=0.8, ls="--")
ax_bot.text(s_values[-1], 0.01, " target", color=COLORS["target"], fontsize=9, va="bottom", ha="right")
ax_bot.set_xlabel("smoothing parameter  s")
ax_bot.set_ylabel("5-fold CV MSE")
ax_bot.set_xscale("log")
ax_bot.legend(loc="upper left")


def _update(i):
    s = s_values[i]
    line.set_ydata(curves[i])
    cursor.set_data([s], [cv_mse_values[i]])
    regime = (
        "overfit (chasing noise)"
        if s < s_values[best_idx] * 0.3
        else "oversmooth (lost the wiggles)"
        if s > s_values[best_idx] * 5
        else "near CV optimum"
    )
    title.set_text(f"Smoothing sweep  s = {s:7.3f}    [{regime}]")
    return line, cursor, title


anim = manim.FuncAnimation(fig, _update, frames=len(s_values), interval=250, blit=False)
anim.save(_HERE / "behavior.gif", writer=manim.PillowWriter(fps=6), dpi=120)
plt.close(fig)

print(f"wrote figures into {_HERE}")
print(f"test MSE = {test_mse:.6e}")
