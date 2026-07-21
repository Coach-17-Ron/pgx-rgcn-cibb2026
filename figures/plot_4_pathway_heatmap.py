import matplotlib.pyplot as plt
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from plot_style import apply_style, HIGHLIGHT, LIGHT, save_figure

apply_style()

pathways = [
    "Paroxetine", "Etoposide", "Taxane", "Mitotane", "Carbamazepine",
    "Tacrolimus/Cyclosporine", "Erlotinib", "Verapamil", "Gefitinib", "Nilotinib",
]
configs = [
    "def-42", "def-123", "def-2026", "amb-42", "amb-123", "amb-2026",
    "non-42", "non-123", "non-2026", "b0-42", "b0-123", "b0-2026",
]
sig_matrix = np.ones((len(pathways), len(configs)))

fig, ax = plt.subplots(figsize=(6.5, 4.5))
cmap = plt.matplotlib.colors.ListedColormap([LIGHT, HIGHLIGHT])
ax.imshow(sig_matrix, cmap=cmap, aspect="auto", vmin=0, vmax=1)

ax.set_xticks(np.arange(len(configs)) - 0.5, minor=True)
ax.set_yticks(np.arange(len(pathways)) - 0.5, minor=True)
ax.grid(which="minor", color="white", linewidth=1)

ax.set_xticks(np.arange(len(configs)))
ax.set_yticks(np.arange(len(pathways)))
ax.set_xticklabels(configs, rotation=45, ha="right", fontsize=8)
ax.set_yticklabels([f"{p} pathway" for p in pathways], fontsize=9)
ax.set_xlabel("Configuration (regime-seed)", fontsize=10)

from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=HIGHLIGHT, edgecolor="none", label="FDR-significant (q<0.05)")]
ax.legend(handles=legend_elements, loc="upper center", bbox_to_anchor=(0.5, -0.20), frameon=False, fontsize=9)

plt.tight_layout()
save_figure(fig, "figures/output/plot_4_pathway_heatmap.png")
plt.close(fig)
