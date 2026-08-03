import matplotlib.pyplot as plt
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from plot_style import apply_style, MUTED, HIGHLIGHT, DARK, FIG_SINGLE_COL, save_figure

apply_style()

regimes = ["default", "ambig_as_pos", "nonassoc_excluded"]
means = [0.0903, 0.0855, 0.0844]
sds =   [0.0198, 0.0111, 0.0116]

fig, ax = plt.subplots(figsize=FIG_SINGLE_COL)

x_pos = np.arange(len(regimes))
ax.bar(x_pos, means, yerr=sds, capsize=4,
       color=MUTED, edgecolor=DARK, linewidth=0.8,
       error_kw={"elinewidth": 0.8, "ecolor": DARK})

seed_values = {
    "default":           [0.0710, 0.0895, 0.1105],
    "ambig_as_pos":      [0.0745, 0.0910, 0.0910],
    "nonassoc_excluded": [0.0710, 0.0900, 0.0920],
}
for i, regime in enumerate(regimes):
    xs = [i + 0.15] * 3
    ys = seed_values[regime]
    ax.scatter(xs, ys, color=HIGHLIGHT, s=20, zorder=3, edgecolor="white", linewidth=0.5)

ax.set_xticks(x_pos)
ax.set_xticklabels(["Default", "Ambig as\npositive", "Non-assoc\nexcluded"], fontsize=9)
ax.set_ylabel("Filtered MRR", fontsize=10)
ax.set_ylim(0, 0.16)
ax.axhline(0, color=DARK, linewidth=0.5)

ax.set_title("Supervision regime shows no effect under multi-seed evaluation",
             fontsize=10, pad=8)

# Annotation OUTSIDE plot area (bottom, in figure coordinates)
fig.text(0.5, -0.03, "n=3 seeds per regime (42, 123, 2026); blue points = individual seed values",
         ha="center", fontsize=8, color=DARK)

plt.tight_layout()
save_figure(fig, "figures/output/plot_1_d1_regimes.png")
plt.close(fig)
