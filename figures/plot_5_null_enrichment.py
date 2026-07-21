"""
Plot 5: D5 null enrichment check.

Story: Model finds 264 sig pathways; baseline 620. 43 model-only
pathways are mechanism-specific biology the baseline misses.
"""

import matplotlib.pyplot as plt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plot_style import apply_style, HIGHLIGHT, MUTED, DARK, save_figure

apply_style()

model_only = 43
baseline_only = 399
common = 221

fig, ax = plt.subplots(figsize=(4.5, 3.5))

categories = ["Model\nonly", "Common\nto both", "Baseline\nonly"]
counts = [model_only, common, baseline_only]
colors = [HIGHLIGHT, MUTED, MUTED]

bars = ax.bar(range(len(categories)), counts,
              color=colors, edgecolor=DARK, linewidth=0.8, width=0.6)

for bar, count in zip(bars, counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
            f"{count}", ha="center", fontsize=10, color=DARK, fontweight="bold")

ax.set_xticks(range(len(categories)))
ax.set_xticklabels(categories, fontsize=9)
ax.set_ylabel("Number of FDR-significant pathways", fontsize=10)
ax.set_ylim(0, 480)
ax.axhline(0, color=DARK, linewidth=0.5)

ax.set_title("Null enrichment: 43 pathways are model-specific",
             fontsize=10, pad=8)

ax.text(0.02, 0.95,
        "43 model-only pathways include:\n"
        " • Wnt/β-catenin signaling\n"
        " • Nuclear receptor transcription\n"
        " • Interferon signaling\n"
        " • G-α (s) signalling",
        transform=ax.transAxes, fontsize=8, verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                  edgecolor=DARK, linewidth=0.5))

plt.tight_layout()
save_figure(fig, "figures/output/plot_5_null_enrichment.png")
plt.close(fig)
