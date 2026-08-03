import matplotlib.pyplot as plt
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from plot_style import apply_style, HIGHLIGHT, MUTED, DARK, save_figure

apply_style()

fig, (ax_bar, ax_text) = plt.subplots(1, 2, figsize=(9.5, 4.0),
                                        gridspec_kw={"width_ratios": [1.0, 1.0]})

# Left panel: bar chart
categories = ["Model\nonly", "Common\nto both", "Baseline\nonly"]
counts = [43, 221, 399]
colors = [HIGHLIGHT, MUTED, MUTED]
bars = ax_bar.bar(range(len(categories)), counts,
                    color=colors, edgecolor=DARK, linewidth=0.8, width=0.6)
for bar, count in zip(bars, counts):
    ax_bar.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 15,
                f"{count}", ha="center", fontsize=11, color=DARK, fontweight="bold")

ax_bar.set_xticks(range(len(categories)))
ax_bar.set_xticklabels(categories, fontsize=9)
ax_bar.set_ylabel("Number of FDR-significant pathways", fontsize=10)
ax_bar.set_ylim(0, 500)
ax_bar.axhline(0, color=DARK, linewidth=0.5)

# Right panel: text block explaining model-only
ax_text.axis("off")
text = ("43 model-only pathways include:\n\n"
        "• Wnt / β-catenin signaling\n"
        "• Nuclear Receptor transcription\n"
        "• Interferon signaling\n"
        "• G-α (s) signalling events\n"
        "• Class B/2 Secretin receptors\n\n"
        "These are mechanism-specific pathways\n"
        "that pure degree selection misses.")
ax_text.text(0.05, 0.5, text, fontsize=10, color=DARK, verticalalignment="center",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="white",
                       edgecolor=DARK, linewidth=0.5))

fig.suptitle("Null enrichment: 43 pathways are model-specific",
             fontsize=11, y=0.98)

plt.tight_layout()
save_figure(fig, "figures/output/plot_5_null_enrichment.png")
plt.close(fig)
