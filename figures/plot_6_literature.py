"""
Plot 6: D5-Part 1 expanded literature validation.

Story: 17.5% support rate. 45% of articles pre-date 2020.
"""

import matplotlib.pyplot as plt
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plot_style import apply_style, HIGHLIGHT, MUTED, DARK, save_figure

apply_style()

decades = ["1990s", "2000s", "2010s", "2020s"]
counts = [113, 450, 1000, 1942]

fig, ax = plt.subplots(figsize=(4.5, 3.0))

x = np.arange(len(decades))
colors = [MUTED, MUTED, MUTED, HIGHLIGHT]

bars = ax.bar(x, counts, color=colors, edgecolor=DARK, linewidth=0.8, width=0.6)

for bar, count in zip(bars, counts):
    pct = count / sum(counts) * 100
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
            f"{count}\n({pct:.0f}%)", ha="center", fontsize=8, color=DARK)

ax.set_xticks(x)
ax.set_xticklabels(decades, fontsize=9)
ax.set_ylabel("Number of PubMed articles", fontsize=10)
ax.set_ylim(0, 2400)
ax.axhline(0, color=DARK, linewidth=0.5)

ax.axvspan(-0.5, 2.5, alpha=0.1, color=MUTED)
ax.text(1, 2200, "45% pre-date 2020\n(would be excluded\nby narrow filter)",
        ha="center", fontsize=8, color=DARK,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                  edgecolor=DARK, linewidth=0.5))

ax.set_title("Literature validation: 17.5% support rate over 190 drugs",
             fontsize=10, pad=8)
ax.set_xlabel("Publication decade", fontsize=10)

plt.tight_layout()
save_figure(fig, "figures/output/plot_6_literature.png")
plt.close(fig)
