"""
Shared publication-quality plot styling module.

Colorblind-friendly palette based on Wong (Nature Methods 2011) — the
standard for scientific figures. Adhere to this palette across all plots
for visual consistency.

Usage:
    from plot_style import apply_style, PALETTE, HIGHLIGHT, MUTED
    apply_style()
    ax.bar(x, y, color=HIGHLIGHT)  # main story
    ax.bar(x, y_other, color=MUTED)  # supporting context
"""

import matplotlib.pyplot as plt
from matplotlib import rcParams

# =========================================================
# COLORBLIND-FRIENDLY PALETTE (Wong 2011)
# =========================================================
# Ordered by "prominence" - use first colors for main data
PALETTE = {
    "blue":       "#0072B2",   # Strong blue - primary highlight
    "vermillion": "#D55E00",   # Warm red - secondary highlight
    "green":      "#009E73",   # Green - tertiary
    "orange":     "#E69F00",   # Orange
    "yellow":     "#F0E442",   # Yellow (use sparingly, low contrast)
    "sky":        "#56B4E9",   # Sky blue
    "pink":       "#CC79A7",   # Reddish purple
    "grey":       "#999999",   # Neutral grey
    "dark_grey":  "#555555",   # Dark grey
    "light_grey": "#CCCCCC",   # Light grey
    "black":      "#000000",
}

# Semantic aliases for the "highlight vs muted" pattern
HIGHLIGHT = PALETTE["blue"]        # For the main story data
SECONDARY = PALETTE["vermillion"]  # For a second story data
MUTED = PALETTE["grey"]            # For background/comparison data
LIGHT = PALETTE["light_grey"]      # For grid lines, subtle details
DARK = PALETTE["dark_grey"]        # For text, axes


def apply_style():
    """Apply publication-quality styling to matplotlib globally."""
    rcParams.update({
        # Font
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        
        # Figure quality
        "figure.dpi": 100,      # Screen preview
        "savefig.dpi": 300,     # Publication export
        "savefig.bbox": "tight",
        "savefig.transparent": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        
        # Remove chart junk
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": True,
        "axes.spines.bottom": True,
        "axes.edgecolor": DARK,
        "axes.linewidth": 0.8,
        
        # Ticks
        "xtick.color": DARK,
        "ytick.color": DARK,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "xtick.major.size": 4,
        "ytick.major.size": 4,
        
        # Grid - minimal
        "axes.grid": False,
        "grid.color": LIGHT,
        "grid.linewidth": 0.5,
        "grid.alpha": 0.5,
        
        # Legend
        "legend.frameon": False,
        "legend.borderpad": 0.5,
    })


# =========================================================
# STANDARD FIGURE SIZES (matches journal columns at 300 dpi)
# =========================================================
FIG_SINGLE_COL = (3.5, 2.6)     # 89 mm width, ~66mm height
FIG_SINGLE_TALL = (3.5, 4.0)    # 89 mm width, taller
FIG_DOUBLE_COL = (7.2, 4.0)     # 183 mm width, medium height
FIG_DOUBLE_WIDE = (7.2, 3.0)    # 183 mm width, low height


def save_figure(fig, path, dpi=300):
    """Save a figure with publication settings."""
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    print(f"Saved: {path}")
