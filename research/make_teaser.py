"""Generate research/figures/teaser.png — shows the noisy training data.

Note: we do NOT reveal the hidden target curve here. The teaser is just
the 200 noisy points as they are given to solutions.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

here = Path(__file__).parent
data = np.load(here / "eval" / "data_train.npz")
x, y = data["x_train"], data["y_train"]

fig, ax = plt.subplots(figsize=(7, 4.2), dpi=150)
ax.scatter(x, y, s=16, c="#1f77b4", alpha=0.75, edgecolor="white", linewidth=0.4)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Symbolic regression: 200 noisy observations on x ∈ [-5, 5]")
ax.grid(alpha=0.25, linewidth=0.5)
ax.set_xlim(-5.2, 5.2)
fig.tight_layout()

out = here / "figures" / "teaser.png"
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"wrote {out}")
