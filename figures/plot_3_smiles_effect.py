import matplotlib.pyplot as plt
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from plot_style import apply_style, HIGHLIGHT, MUTED, DARK, FIG_DOUBLE_WIDE, save_figure

apply_style()

configs = ["default\nβ=0.10", "ambig_as_pos\nβ=0.10", "nonassoc_excl\nβ=0.10", "default\nβ=0.00"]
with_smiles_mean = [0.1109, 0.1012, 0.1031, 0.1035]
with_smiles_sd =   [0.0280, 0.0149, 0.0145, 0.0270]
without_smiles_mean = [0.0438, 0.0396, 0.0404, 0.0346]
without_smiles_sd =   [0.0100, 0.0138, 0.0075, 0.0011]

fig, ax = plt.subplots(figsize=FIG_DOUBLE_WIDE)
x = np.arange(len(configs))
width = 0.35

ax.bar(x - width/2, with_smiles_mean, width, yerr=with_smiles_sd, capsize=3,
       color=HIGHLIGHT, edgecolor=DARK, linewidth=0.8, label="With SMILES (n≈537)",
       error_kw={"elinewidth": 0.8, "ecolor": DARK})
ax.bar(x + width/2, without_smiles_mean, width, yerr=without_smiles_sd, capsize=3,
       color=MUTED, edgecolor=DARK, linewidth=0.8, label="Without SMILES (n≈214)",
       error_kw={"elinewidth": 0.8, "ecolor": DARK})

ax.set_xticks(x)
ax.set_xticklabels(configs, fontsize=9)
ax.set_ylabel("Filtered MRR", fontsize=10)
ax.set_ylim(0, 0.16)
ax.axhline(0, color=DARK, linewidth=0.5)
ax.legend(loc="upper right", frameon=False, fontsize=9)

plt.tight_layout()
save_figure(fig, "figures/output/plot_3_smiles_effect.png")
plt.close(fig)
