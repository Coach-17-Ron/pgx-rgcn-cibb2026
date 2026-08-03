"""Shared publication-quality plot styling module (v2 — generous spacing)."""

import matplotlib.pyplot as plt
from matplotlib import rcParams

PALETTE = {
    "blue":       "#0072B2",
    "vermillion": "#D55E00",
    "green":      "#009E73",
    "orange":     "#E69F00",
    "yellow":     "#F0E442",
    "sky":        "#56B4E9",
    "pink":       "#CC79A7",
    "grey":       "#999999",
    "dark_grey":  "#555555",
    "light_grey": "#CCCCCC",
    "black":      "#000000",
}

HIGHLIGHT = PALETTE["blue"]
SECONDARY = PALETTE["vermillion"]
MUTED = PALETTE["grey"]
LIGHT = PALETTE["light_grey"]
DARK = PALETTE["dark_grey"]


def apply_style():
    rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "figure.dpi": 100,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.2,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": True,
        "axes.spines.bottom": True,
        "axes.edgecolor": DARK,
        "axes.linewidth": 0.8,
        "xtick.color": DARK,
        "ytick.color": DARK,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "xtick.major.size": 4,
        "ytick.major.size": 4,
        "axes.grid": False,
        "grid.color": LIGHT,
        "grid.linewidth": 0.5,
        "grid.alpha": 0.5,
        "legend.frameon": False,
    })


# Bigger canvases (more room for annotations)
FIG_SINGLE_COL = (4.5, 3.5)
FIG_SINGLE_TALL = (4.5, 5.0)
FIG_DOUBLE_COL = (8.0, 4.5)
FIG_DOUBLE_WIDE = (8.5, 4.0)


def save_figure(fig, path, dpi=300):
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white", pad_inches=0.2)
    print(f"Saved: {path}")
