import matplotlib.pyplot as plt
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from plot_style import apply_style, HIGHLIGHT, MUTED, DARK, save_figure

apply_style()

fig, (ax, ax_ex) = plt.subplots(2, 1, figsize=(7.0, 5.5),
                                  gridspec_kw={"height_ratios": [2.5, 1.0]})

categories = [
    "Graph path\n(structural)",
    "Pathway support\n(biological)",
    "Literature\n(external)",
    "ALL THREE\n(triangulated)",
]
percentages = [98, 74, 20, 14]
counts = [49, 37, 10, 7]

x = np.arange(len(categories))
colors = [MUTED, MUTED, MUTED, HIGHLIGHT]
bars = ax.bar(x, percentages, color=colors, edgecolor=DARK, linewidth=0.8, width=0.6)

for bar, pct, count in zip(bars, percentages, counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
            f"{pct}%\n(n={count}/50)", ha="center", fontsize=9, color=DARK)

ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=9)
ax.set_ylabel("% of top-50 novel predictions", fontsize=10)
ax.set_ylim(0, 120)
ax.axhline(0, color=DARK, linewidth=0.5)
ax.set_title("Multi-modal evidence triangulation for top-50 predictions",
             fontsize=10, pad=8)

# Exemplar box in DEDICATED bottom panel
ax_ex.axis("off")
exemplar_text = ("Fully-triangulated exemplar:  testosterone → ABCB1\n"
                 "• 3-hop graph path via CYP3A4 (metabolism)\n"
                 "• 27 significant PGx pathways containing ABCB1\n"
                 "• 10 PubMed articles co-mentioning testosterone and ABCB1 (2024-2026)")
ax_ex.text(0.5, 0.5, exemplar_text, fontsize=9, color=DARK,
           ha="center", va="center", transform=ax_ex.transAxes,
           bbox=dict(boxstyle="round,pad=0.5", facecolor="white",
                     edgecolor=DARK, linewidth=0.5))

plt.tight_layout()
save_figure(fig, "figures/output/plot_7_integrated.png")
plt.close(fig)
