"""
Plot 8: Stage 4a intrinsic — relation importance.

Story: Model respects evidence grading. Clinical evidence gets highest weight.
"""

import matplotlib.pyplot as plt
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plot_style import apply_style, HIGHLIGHT, SECONDARY, MUTED, DARK, save_figure

apply_style()

relations = [
    "drug → gene\n[clinical]",
    "gene → drug\n[clinical]",
    "drug → gene\n[label]",
    "drug → gene\n[pathway]",
    "gene → drug\n[label]",
]
norms = [8.46, 5.15, 4.07, 3.63, 3.60]
tiers = ["clinical", "clinical", "label", "pathway", "label"]

fig, ax = plt.subplots(figsize=(5.5, 3.5))

tier_colors = {"clinical": HIGHLIGHT, "label": SECONDARY, "pathway": MUTED}
colors = [tier_colors[t] for t in tiers]

y_pos = np.arange(len(relations))
bars = ax.barh(y_pos, norms, color=colors, edgecolor=DARK, linewidth=0.8, height=0.7)

for bar, norm in zip(bars, norms):
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
            f"{norm:.2f}", va="center", fontsize=9, color=DARK)

ax.set_yticks(y_pos)
ax.set_yticklabels(relations, fontsize=9)
ax.invert_yaxis()

ax.set_xlabel("Mean Frobenius norm (across encoder layers)", fontsize=10)
ax.set_xlim(0, 10)
ax.axvline(0, color=DARK, linewidth=0.5)

ax.set_title("Model prioritises clinical evidence in learned weights",
             fontsize=10, pad=8)

from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=HIGHLIGHT, label="Clinical (highest tier)"),
    Patch(facecolor=SECONDARY, label="Label (regulatory)"),
    Patch(facecolor=MUTED, label="Pathway (curated)"),
]
ax.legend(handles=legend_elements, loc="lower right", frameon=False, fontsize=8)

plt.tight_layout()
save_figure(fig, "figures/output/plot_8_relation_importance.png")
plt.close(fig)
