import matplotlib.pyplot as plt
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from plot_style import apply_style, MUTED, DARK, FIG_SINGLE_COL, save_figure

apply_style()

labels = ["β = 0.10\n(with hub penalty)", "β = 0.00\n(no hub penalty)"]
means = [0.0903, 0.0821]
sds =   [0.0198, 0.0159]

fig, ax = plt.subplots(figsize=FIG_SINGLE_COL)

x_pos = np.arange(len(labels))
ax.bar(x_pos, means, yerr=sds, capsize=4,
       color=[MUTED, MUTED], edgecolor=DARK, linewidth=0.8,
       error_kw={"elinewidth": 0.8, "ecolor": DARK})

ax.set_xticks(x_pos)
ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel("Filtered MRR", fontsize=10)
ax.set_ylim(0, 0.16)
ax.axhline(0, color=DARK, linewidth=0.5)

ax.set_title("Hub penalty has no measurable effect", fontsize=10, pad=8)

fig.text(0.5, -0.03, f"Δ = {means[0]-means[1]:+.3f} MRR — within seed variance",
         ha="center", fontsize=8, color=DARK)

plt.tight_layout()
save_figure(fig, "figures/output/plot_2_d2_hub_penalty.png")
plt.close(fig)
