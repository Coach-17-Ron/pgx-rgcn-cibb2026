import matplotlib.pyplot as plt
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from plot_style import apply_style, HIGHLIGHT, MUTED, DARK, save_figure

apply_style()

categories = ["Graph path\n(structural)", "Pathway support\n(biological)", "Literature\n(external)", "ALL THREE\n(triangulated)"]
percentages = [98, 74, 20, 14]
counts = [49, 37, 10, 7]

fig, ax = plt.subplots(figsize=(5.5, 3.5))
x = np.arange(len(categories))
colors = [MUTED, MUTED, MUTED, HIGHLIGHT]

bars = ax.bar(x, percentages, color=colors, edgecolor=DARK, linewidth=0.8, width=0.6)

for bar, pct, count in zip(bars, percentages, counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            f"{pct}%\n(n={count}/50)", ha="center", fontsize=8, color=DARK)

ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=9)
ax.set_ylabel("% of top-50 novel predictions", fontsize=10)
ax.set_ylim(0, 115)
ax.axhline(0, color=DARK, linewidth=0.5)

plt.tight_layout()
save_figure(fig, "figures/output/plot_7_integrated.png")
plt.close(fig)
