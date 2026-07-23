"""
Build MSc Progress Presentation.

Generates MSc_Progress_Presentation.pptx following the approved outline:
- 25 main slides + 6 backup slides
- 8 embedded figures from figures/output/
- 16:9 widescreen format
- Clean Arial typography with Wong colorblind palette accents
- Speaker notes on each slide
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pathlib import Path

# ============================================================
# CONSTANTS
# ============================================================
FIG_DIR = Path("figures/output")
OUT_PATH = Path("presentation/MSc_Progress_Presentation.pptx")

# Wong colorblind-friendly palette (matching figures)
BLUE = RGBColor(0x00, 0x72, 0xB2)
VERMILLION = RGBColor(0xD5, 0x5E, 0x00)
GREEN = RGBColor(0x00, 0x9E, 0x73)
ORANGE = RGBColor(0xE6, 0x9F, 0x00)
GREY = RGBColor(0x66, 0x66, 0x66)
DARK = RGBColor(0x33, 0x33, 0x33)
LIGHT_GREY = RGBColor(0xE0, 0xE0, 0xE0)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

# 16:9 slide dimensions
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

# ============================================================
# HELPERS
# ============================================================
def set_bg_white(slide):
    """Set slide background white."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = WHITE


def add_title(slide, text, y=0.3, color=DARK, size=32, bold=True):
    """Add a title text box near the top of the slide."""
    tb = slide.shapes.add_textbox(Inches(0.5), Inches(y), Inches(12.3), Inches(0.9))
    tf = tb.text_frame
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = text
    run.font.name = "Arial"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return tb


def add_subtitle(slide, text, y=1.1, color=GREY, size=16):
    """Add a smaller subtitle under the main title."""
    tb = slide.shapes.add_textbox(Inches(0.5), Inches(y), Inches(12.3), Inches(0.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = text
    run.font.name = "Arial"
    run.font.size = Pt(size)
    run.font.color.rgb = color
    return tb


def add_body_text(slide, bullets, y=1.6, height=5.5, x=0.5, width=12.3, size=18,
                   color=DARK, bullet_char="•"):
    """
    Add a body text area with bulleted lines.
    bullets: list of (text, indent_level) tuples OR list of strings.
    """
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    
    for i, item in enumerate(bullets):
        if isinstance(item, tuple):
            text, level = item
        else:
            text, level = item, 0
        
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        
        # Indent
        p.level = level
        prefix = "    " * level + (bullet_char + " " if bullet_char else "")
        
        run = p.add_run()
        run.text = prefix + text
        run.font.name = "Arial"
        run.font.size = Pt(size - level * 2)  # Smaller for deeper levels
        run.font.color.rgb = color
        p.space_after = Pt(6)
    return tb


def add_image(slide, image_path, left, top, width, height=None):
    """Add an image to the slide."""
    if not Path(image_path).exists():
        print(f"WARNING: image not found: {image_path}")
        return None
    if height is not None:
        return slide.shapes.add_picture(str(image_path),
                                          Inches(left), Inches(top),
                                          width=Inches(width), height=Inches(height))
    return slide.shapes.add_picture(str(image_path),
                                      Inches(left), Inches(top),
                                      width=Inches(width))


def add_footer(slide, text="Kgabe R. Molepo (MLPKGA007) | MSc Progress | 24 July 2026"):
    """Add small footer text at bottom."""
    tb = slide.shapes.add_textbox(Inches(0.5), Inches(7.1), Inches(12.3), Inches(0.3))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = text
    run.font.name = "Arial"
    run.font.size = Pt(9)
    run.font.color.rgb = GREY


def add_slide_number(slide, num, total):
    """Add slide number at bottom right."""
    tb = slide.shapes.add_textbox(Inches(11.5), Inches(7.1), Inches(1.5), Inches(0.3))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    run = p.add_run()
    run.text = f"{num} / {total}"
    run.font.name = "Arial"
    run.font.size = Pt(9)
    run.font.color.rgb = GREY


def add_notes(slide, notes):
    """Add speaker notes."""
    notes_slide = slide.notes_slide
    notes_tf = notes_slide.notes_text_frame
    notes_tf.text = notes


def add_accent_bar(slide, y=0.15, height=0.05, color=BLUE):
    """Add a colored accent bar (visual continuity)."""
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                    Inches(0.5), Inches(y),
                                    Inches(12.3), Inches(height))
    bar.fill.solid()
    bar.fill.fore_color.rgb = color
    bar.line.fill.background()  # No border


# ============================================================
# BUILD PRESENTATION
# ============================================================
prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H

blank_layout = prs.slide_layouts[6]  # Blank

TOTAL = 31  # 25 main + 6 backup


def new_slide():
    slide = prs.slides.add_slide(blank_layout)
    set_bg_white(slide)
    return slide


# ============================================================
# SECTION 1: FRAMING (Slides 1-4)
# ============================================================

# ------ SLIDE 1: TITLE ------
s = new_slide()

# Big colored title area
title_bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                 Inches(0), Inches(2.0),
                                 Inches(13.333), Inches(3.5))
title_bar.fill.solid()
title_bar.fill.fore_color.rgb = BLUE
title_bar.line.fill.background()

# Main title
tb = s.shapes.add_textbox(Inches(0.75), Inches(2.4), Inches(11.8), Inches(2.5))
tf = tb.text_frame
tf.word_wrap = True
tf.vertical_anchor = MSO_ANCHOR.TOP

p = tf.paragraphs[0]
p.alignment = PP_ALIGN.LEFT
r = p.add_run()
r.text = "Interpretable Graph Neural Networks for Learning\nDrug-Gene Relationships and Inferring Phenotype\nOutcomes in Pharmacogenomics"
r.font.name = "Arial"
r.font.size = Pt(36)
r.font.bold = True
r.font.color.rgb = WHITE

# Presenter block below title bar
tb2 = s.shapes.add_textbox(Inches(0.75), Inches(5.7), Inches(11.8), Inches(1.5))
tf2 = tb2.text_frame

p = tf2.paragraphs[0]
r = p.add_run()
r.text = "Kgabe Ronald Molepo (MLPKGA007)"
r.font.name = "Arial"; r.font.size = Pt(22); r.font.bold = True; r.font.color.rgb = DARK

p = tf2.add_paragraph()
r = p.add_run()
r.text = "MSc Computational Health Informatics"
r.font.name = "Arial"; r.font.size = Pt(16); r.font.color.rgb = GREY

p = tf2.add_paragraph()
r = p.add_run()
r.text = "Supervisors: Hocine Bendou, Khuthala Mnika  |  University of Cape Town  |  24 July 2026"
r.font.name = "Arial"; r.font.size = Pt(14); r.font.color.rgb = GREY

add_notes(s, "Introduce yourself. Note this is a progress meeting, not a defence. "
              "You've completed all experimental work; today is about reviewing findings "
              "and confirming readiness to move into Part B writing.")

# ------ SLIDE 2: WHERE WE ARE ------
s = new_slide()
add_accent_bar(s)
add_title(s, "Where we are in the project")

bullets = [
    "✓  Part A submitted (November 2025)",
    "✓  All experimental deliverables complete",
    "📝  Part B writing phase beginning",
    "🎯  Today: report findings + confirm readiness to write",
]
add_body_text(s, bullets, y=1.8, size=22, bullet_char="")

# Add a subtle "December submission target" note
tb = s.shapes.add_textbox(Inches(0.5), Inches(5.5), Inches(12.3), Inches(1))
tf = tb.text_frame
p = tf.paragraphs[0]
r = p.add_run()
r.text = "Target: December 2026 submission  |  Currently 5-6 weeks ahead of Part A schedule"
r.font.name = "Arial"; r.font.size = Pt(16); r.font.italic = True; r.font.color.rgb = BLUE

add_footer(s)
add_slide_number(s, 2, TOTAL)
add_notes(s, "Set expectation this is a progress meeting, not a defence. "
              "You've done the work; you're asking for guidance on writing.")

# ------ SLIDE 3: PART A GAP RECAP ------
s = new_slide()
add_accent_bar(s)
add_title(s, "Recap: Part A identified a specific gap")
add_subtitle(s, "Five requirements that no prior pipeline had combined")

bullets = [
    "1.  Evidence-graded curated supervision (ClinPGx association tiers)",
    "2.  Ranking objective + hub-degree penalty + degree-aware sampling",
    "3.  Biologically-mediated drug-gene-phenotype propagation",
    "4.  Cold-drug evaluation with raw + filtered MRR",
    "5.  Coupled intrinsic + post-hoc interpretability + pathway contextualisation",
]
add_body_text(s, bullets, y=1.9, size=20, bullet_char="")

# Bottom quote
tb = s.shapes.add_textbox(Inches(0.5), Inches(5.7), Inches(12.3), Inches(1))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
r = p.add_run()
r.text = '"The contribution lies in combining all five within a single, reproducible pipeline applied to ClinPGx."'
r.font.name = "Arial"; r.font.size = Pt(14); r.font.italic = True; r.font.color.rgb = GREY

add_footer(s); add_slide_number(s, 3, TOTAL)
add_notes(s, "Set up the scoring framework. Everything that follows shows whether we met these 5 requirements.")

# ------ SLIDE 4: AIM AND OBJECTIVES ------
s = new_slide()
add_accent_bar(s)
add_title(s, "Overall aim + 5 objectives")

# Aim box
aim_shape = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                 Inches(0.5), Inches(1.5),
                                 Inches(12.3), Inches(1.3))
aim_shape.fill.solid()
aim_shape.fill.fore_color.rgb = LIGHT_GREY
aim_shape.line.fill.background()

tb = s.shapes.add_textbox(Inches(0.8), Inches(1.65), Inches(12), Inches(1.1))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
r = p.add_run()
r.text = "Aim: "
r.font.name = "Arial"; r.font.size = Pt(18); r.font.bold = True; r.font.color.rgb = DARK
r = p.add_run()
r.text = ("Evaluate whether R-GCN can rank drug-gene relationships for "
           "previously-unseen drugs on ClinPGx, and characterise what drives performance.")
r.font.name = "Arial"; r.font.size = Pt(16); r.font.color.rgb = DARK

# Objectives list
bullets = [
    "1.  Construct heterogeneous knowledge graph",
    "2.  Train evidence-aware R-GCN ranking model",
    "3.  Explore phenotype-contextualised propagation",
    "4.  Interpret ranked PGx relationships",
    "5.  Validate with biological pathways + literature",
]
add_body_text(s, bullets, y=3.2, size=20, bullet_char="")

add_footer(s); add_slide_number(s, 4, TOTAL)
add_notes(s, "State the aim clearly, then walk through the 5 objectives. "
              "Note that Objective 3 was reformulated due to data reality (we'll come to that).")


# ============================================================
# SECTION 2: METHODOLOGY (Slides 5-7)
# ============================================================

# ------ SLIDE 5: KG CONSTRUCTION ------
s = new_slide()
add_accent_bar(s)
add_title(s, "Knowledge graph construction (Objective 1)")
add_subtitle(s, "ClinPGx heterogeneous KG — evidence categories preserved")

# Left side: numbers
left_bullets = [
    ("38,955 nodes across 4 types:", 0),
    ("Drugs:  5,210", 1),
    ("Genes:  25,041", 1),
    ("Variants:  7,091", 1),
    ("Phenotypes:  1,613", 1),
    ("", 0),
    ("44,218 edges across 56 relations", 0),
    ("Drug-gene edges:  ~6,704", 1),
    ("Evidence types:  clinical / label / pathway / guideline", 1),
    ("Association types:  associated / not-associated / ambiguous", 1),
]
add_body_text(s, left_bullets, y=1.8, x=0.5, width=8.0, size=15, bullet_char="")

# Right side: mini schema diagram (text-based)
tb = s.shapes.add_textbox(Inches(8.8), Inches(1.9), Inches(4.0), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True

for label, color in [("Drugs", BLUE), ("Genes", VERMILLION), ("Variants", GREEN), ("Phenotypes", ORANGE)]:
    p = tf.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = f"◆  {label}"
    r.font.name = "Arial"; r.font.size = Pt(18); r.font.bold = True; r.font.color.rgb = color
    p.space_after = Pt(6)

add_footer(s); add_slide_number(s, 5, TOTAL)
add_notes(s, "First objective met by construction. Emphasise evidence typing — this is what makes "
              "R-GCN appropriate for the data.")

# ------ SLIDE 6: R-GCN ARCHITECTURE ------
s = new_slide()
add_accent_bar(s)
add_title(s, "R-GCN architecture + training (Objective 2)")
add_subtitle(s, "Evidence-aware relational GNN with pairwise ranking loss")

model_bullets = [
    "Model",
    ("2-layer R-GCN encoder with basis decomposition (8 bases)", 1),
    ("64-dimensional embeddings", 1),
    ("DistMult decoder for scoring", 1),
    ("Drug fingerprints (Morgan, 2048-dim) as input features", 1),
    ("", 0),
    "Training",
    ("Pairwise margin ranking loss", 1),
    ("Hub penalty (β = 0.10 default)", 1),
    ("Degree-aware negative sampling (deg^0.75)", 1),
    ("Evidence-graded supervision: only \"associated\" as positives", 1),
    ("", 0),
    "Compute",
    ("ilifu HPC | SLURM | Singularity | CPU (P100 GPU too old for PyTorch 2.10+cu128)", 1),
]

# Manual formatting for section headers
tb = s.shapes.add_textbox(Inches(0.5), Inches(1.8), Inches(12.3), Inches(5))
tf = tb.text_frame
tf.word_wrap = True

for item in model_bullets:
    if isinstance(item, tuple):
        text, level = item
    else:
        text, level = item, 0
    
    if tf.paragraphs[0].runs == []:
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    
    p.level = level
    if level == 0:
        # Section header
        r = p.add_run()
        r.text = text
        r.font.name = "Arial"; r.font.size = Pt(18); r.font.bold = True; r.font.color.rgb = BLUE
    else:
        r = p.add_run()
        r.text = "•  " + text
        r.font.name = "Arial"; r.font.size = Pt(14); r.font.color.rgb = DARK
    p.space_after = Pt(3)

add_footer(s); add_slide_number(s, 6, TOTAL)
add_notes(s, "Cover briefly. The interesting story is what came out of training, not the architecture itself. "
              "Mention that GPU-CPU decision was forced by ilifu hardware.")

# ------ SLIDE 7: EVALUATION PROTOCOL ------
s = new_slide()
add_accent_bar(s)
add_title(s, "Evaluation protocol")
add_subtitle(s, "Cold-drug ranking with multi-seed replication")

bullets = [
    "751 test drugs completely held out during training",
    "Message passing on training subgraph only (no leakage)",
    "Metrics: MRR + Hits@K, both raw AND filtered",
    "",
    "12 configurations tested:",
    ("3 supervision regimes × 3 seeds (42, 123, 2026) = 9 configs", 1),
    ("3 seeds at β = 0 (hub penalty ablation) = 3 configs", 1),
    "",
    "Every claim backed by multi-seed variance",
    ("Single-seed findings would be unreliable at this data scale", 1),
]
add_body_text(s, bullets, y=1.9, size=18)

add_footer(s); add_slide_number(s, 7, TOTAL)
add_notes(s, "Multi-seed discipline is a rigor point. Some published papers report single-seed. "
              "We don't. Every claim here has 3 seeds.")


# ============================================================
# SECTION 3: RESULTS (Slides 8-19)
# ============================================================

# ------ SLIDE 8: OBJECTIVES 1-2 STATUS ------
s = new_slide()
add_accent_bar(s)
add_title(s, "Objectives 1-2: Complete")

# Simple status table
bullets = [
    "Objective 1 — KG construction",
    ("38,955 nodes, 44,218 edges, 56 relations", 1),
    ("Split leakage audit: passed", 1),
    "",
    "Objective 2 — R-GCN training",
    ("12 configurations trained to convergence", 1),
    ("All checkpoints preserved, evaluation metrics logged", 1),
    ("Multi-seed variance computed for all", 1),
]

tb = s.shapes.add_textbox(Inches(0.5), Inches(2.0), Inches(12.3), Inches(4))
tf = tb.text_frame
tf.word_wrap = True

for i, item in enumerate(bullets):
    if isinstance(item, tuple):
        text, level = item
    else:
        text, level = item, 0
    
    if i == 0:
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    
    p.level = level
    if text and level == 0:
        r = p.add_run()
        r.text = "✓  " + text
        r.font.name = "Arial"; r.font.size = Pt(22); r.font.bold = True; r.font.color.rgb = GREEN
    elif text:
        r = p.add_run()
        r.text = text
        r.font.name = "Arial"; r.font.size = Pt(16); r.font.color.rgb = DARK
    p.space_after = Pt(6)

add_footer(s); add_slide_number(s, 8, TOTAL)
add_notes(s, "Quick transition slide. First two objectives are complete; results follow.")

# ------ SLIDE 9: D1 REGIME COMPARISON ------
s = new_slide()
add_accent_bar(s)
add_title(s, "D1 — Supervision regime shows no effect")
add_subtitle(s, "Three regimes × 3 seeds — differences within noise")

add_image(s, FIG_DIR / "plot_1_d1_regimes.png", left=2.5, top=1.7, width=8.0)

# Interpretation callout
tb = s.shapes.add_textbox(Inches(0.5), Inches(6.2), Inches(12.3), Inches(0.9))
tf = tb.text_frame
p = tf.paragraphs[0]
r = p.add_run()
r.text = "Interpretation:  "
r.font.name = "Arial"; r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = BLUE
r = p.add_run()
r.text = ("Regime choice doesn't matter. Null result but important — Part A's default "
           "regime is defensible.")
r.font.name = "Arial"; r.font.size = Pt(14); r.font.color.rgb = DARK

add_footer(s); add_slide_number(s, 9, TOTAL)
add_notes(s, "Emphasise the multi-seed rigor. Note that single-seed had suggested "
              "ambig_as_pos was better, but multi-seed revealed it wasn't.")

# ------ SLIDE 10: D2 HUB PENALTY ------
s = new_slide()
add_accent_bar(s)
add_title(s, "D2 — Hub penalty has no measurable effect")
add_subtitle(s, "β = 0.10 vs β = 0 — identical within variance")

add_image(s, FIG_DIR / "plot_2_d2_hub_penalty.png", left=2.5, top=1.7, width=8.0)

tb = s.shapes.add_textbox(Inches(0.5), Inches(6.2), Inches(12.3), Inches(0.9))
tf = tb.text_frame
p = tf.paragraphs[0]
r = p.add_run()
r.text = "Interpretation:  "
r.font.name = "Arial"; r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = BLUE
r = p.add_run()
r.text = ("Degree-aware negative sampling already handles hub bias. "
           "The hub penalty term is redundant.")
r.font.name = "Arial"; r.font.size = Pt(14); r.font.color.rgb = DARK

add_footer(s); add_slide_number(s, 10, TOTAL)
add_notes(s, "Second null result on methodological ablations. "
              "The pattern of D1+D2 is that method choice doesn't move the needle.")

# ------ SLIDE 11: D3 PHENOTYPE-RELEVANCE (HONEST REFRAME) ------
s = new_slide()
add_accent_bar(s)
add_title(s, "D3 — Phenotype-contextualised propagation, reformulated")
add_subtitle(s, "Objective 3 required reformulation due to data reality")

# Two-column layout
left_bullets = [
    "Part A commitment (Objective 3):",
    ("Predict drug → phenotype via biological reasoning through gene → variant intermediaries", 1),
    "",
    "Data reality:",
    ("ClinPGx has 0 direct drug-phenotype edges", 1),
    ("Cannot evaluate direct drug-phenotype ranking (no ground truth)", 1),
]
add_body_text(s, left_bullets, y=1.7, x=0.5, width=6.5, size=14, bullet_char="")

right_bullets = [
    "Reformulation:",
    ("Test whether model prioritises phenotype-relevant genes", 1),
    ("Genes with ≥1 gene-phenotype edge in ClinPGx (n=1,131)", 1),
    "",
    "Result:",
    ("Model filtered MRR ~0.10 on subset", 1),
    ("Matches gene-phenotype degree baseline (0.10)", 1),
    ("Consistent with D1/D2 pattern", 1),
]
add_body_text(s, right_bullets, y=1.7, x=7.2, width=5.7, size=14, bullet_char="")

# Direct callout at bottom
tb = s.shapes.add_textbox(Inches(0.5), Inches(6.4), Inches(12.3), Inches(0.9))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
r = p.add_run()
r.text = "Discussion point:  "
r.font.name = "Arial"; r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = VERMILLION
r = p.add_run()
r.text = ("Is this reformulation acceptable for the dissertation, or should we frame Objective 3 differently?")
r.font.name = "Arial"; r.font.size = Pt(14); r.font.color.rgb = DARK

add_footer(s); add_slide_number(s, 11, TOTAL)
add_notes(s, "Be direct. The reformulation was forced by data reality. Ask supervisor explicitly "
              "how to frame this in Part B.")

# ------ SLIDE 12: D4.1 RAW vs FILTERED ------
s = new_slide()
add_accent_bar(s)
add_title(s, "D4.1 — Filtered lifts MRR modestly")

bullets = [
    "Comparing raw vs filtered ranking protocol across 12 configurations:",
    "",
    ("Filtered MRR consistently ~0.012 higher than raw MRR", 0),
    ("Small, consistent effect from removing known positives", 0),
    "",
    "This sets up D4.3 — the substantive finding is coming.",
]
add_body_text(s, bullets, y=1.9, size=18)

add_footer(s); add_slide_number(s, 12, TOTAL)
add_notes(s, "Brief slide. The filtered-vs-raw effect is small. Move quickly to D4.3.")

# ------ SLIDE 13: D4.3 SMILES EFFECT (HERO) ------
s = new_slide()
add_accent_bar(s, color=VERMILLION)  # Highlight color for hero
add_title(s, "D4 — Chemical structure availability dominates")
add_subtitle(s, "The substantive positive finding")

add_image(s, FIG_DIR / "plot_3_smiles_effect.png", left=1.0, top=1.7, width=11.3)

# Finding callout
tb = s.shapes.add_textbox(Inches(0.5), Inches(6.2), Inches(12.3), Inches(0.9))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
r = p.add_run()
r.text = "Finding:  "
r.font.name = "Arial"; r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = VERMILLION
r = p.add_run()
r.text = ("SMILES effect = +0.065 MRR, which is 5.5× larger than the raw-vs-filtered protocol effect "
           "and larger than any methodological ablation (D1, D2, D3) we tested.")
r.font.name = "Arial"; r.font.size = Pt(14); r.font.color.rgb = DARK

add_footer(s); add_slide_number(s, 13, TOTAL)
add_notes(s, "This is the hero slide. THE finding. Chemical structure availability is the primary "
              "driver. Method-level ablations cannot beat this constraint. This is what I'll build "
              "the Part B discussion around.")

# ------ SLIDE 14: D5-Part 2 PATHWAY ENRICHMENT ------
s = new_slide()
add_accent_bar(s)
add_title(s, "D5-Part 2 — Pathway enrichment across 12 configs")
add_subtitle(s, "3,689 gene sets tested with BH-FDR correction")

add_image(s, FIG_DIR / "plot_4_pathway_heatmap.png", left=2.0, top=1.7, width=9.3)

tb = s.shapes.add_textbox(Inches(0.5), Inches(6.4), Inches(12.3), Inches(0.7))
tf = tb.text_frame
p = tf.paragraphs[0]
r = p.add_run()
r.text = "Initial finding:  "
r.font.name = "Arial"; r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = BLUE
r = p.add_run()
r.text = "10 PGx drug pathways FDR-significant across ALL 12 configurations (Paroxetine, Etoposide, Taxane...)"
r.font.name = "Arial"; r.font.size = Pt(14); r.font.color.rgb = DARK

add_footer(s); add_slide_number(s, 14, TOTAL)
add_notes(s, "Initially I thought this was a strong positive finding. Then I ran a null enrichment "
              "check — set that up. The next slide is the honest reveal.")

# ------ SLIDE 15: D5 NULL ENRICHMENT (HONEST) ------
s = new_slide()
add_accent_bar(s, color=VERMILLION)
add_title(s, "But — is this specific to the model?")
add_subtitle(s, "Null enrichment check with drug-gene degree baseline")

add_image(s, FIG_DIR / "plot_5_null_enrichment.png", left=2.5, top=1.7, width=8.0)

tb = s.shapes.add_textbox(Inches(0.5), Inches(6.3), Inches(12.3), Inches(0.9))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
r = p.add_run()
r.text = "Honest reveal:  "
r.font.name = "Arial"; r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = VERMILLION
r = p.add_run()
r.text = ("Degree baseline also finds the 10 headline pathways. D5-Part 2 headline is largely structural. "
           "But 43 model-only pathways represent genuine mechanism-specific contribution.")
r.font.name = "Arial"; r.font.size = Pt(13); r.font.color.rgb = DARK

add_footer(s); add_slide_number(s, 15, TOTAL)
add_notes(s, "Be direct. I ran the check anyway because I'd rather find this myself than have "
              "an examiner find it. The 43 model-only pathways ARE the honest positive finding.")

# ------ SLIDE 16: D5-Part 1 LITERATURE ------
s = new_slide()
add_accent_bar(s)
add_title(s, "D5-Part 1 — External literature validation")
add_subtitle(s, "PubMed evidence for top novel predictions, 1990-2026")

add_image(s, FIG_DIR / "plot_6_literature.png", left=1.0, top=1.7, width=6.5)

# Right side: key numbers + examples
right_bullets = [
    "4,636 predictions queried",
    "190 unique test drugs (25% of test set)",
    "17.5% support rate (811 pairs)",
    "3,505 total articles",
    "",
    "Biologically-supported pairs:",
    ("carbidopa → COMT (Parkinson's)", 1),
    ("dimethyl fumarate → FOXP3 (MS)", 1),
    ("doxorubicinol → ABCB1 (chemo resistance)", 1),
    "",
    "Caveat: some pairs are broad chemicals (Ca, testosterone) — inflated by name-match",
]

tb = s.shapes.add_textbox(Inches(7.7), Inches(1.9), Inches(5.4), Inches(5))
tf = tb.text_frame
tf.word_wrap = True

for i, item in enumerate(right_bullets):
    if isinstance(item, tuple):
        text, level = item
    else:
        text, level = item, 0
    
    if i == 0:
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    p.level = level
    
    if text:
        r = p.add_run()
        r.text = "  " + text if level else text
        r.font.name = "Arial"
        r.font.size = Pt(12 if level else 13)
        r.font.color.rgb = DARK if level else BLUE
        if level == 0:
            r.font.bold = True
    p.space_after = Pt(3)

add_footer(s); add_slide_number(s, 16, TOTAL)
add_notes(s, "17.5% is a defensible rate for novel predictions. Note the honest caveat about "
              "broad chemicals — this is important for scientific integrity.")

# ------ SLIDE 17: INTRINSIC INTERPRETABILITY ------
s = new_slide()
add_accent_bar(s)
add_title(s, "D5 Session 1a — Model respects evidence grading")
add_subtitle(s, "Intrinsic interpretability: relation weights by Frobenius norm")

add_image(s, FIG_DIR / "plot_8_relation_importance.png", left=2.5, top=1.7, width=8.0)

tb = s.shapes.add_textbox(Inches(0.5), Inches(6.3), Inches(12.3), Inches(0.9))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
r = p.add_run()
r.text = "Finding:  "
r.font.name = "Arial"; r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = BLUE
r = p.add_run()
r.text = ("Clinical evidence relations get the highest weight (8.46). Model learned what the evidence-graded "
           "supervision intended. Satisfies Requirement 5c intrinsic component.")
r.font.name = "Arial"; r.font.size = Pt(13); r.font.color.rgb = DARK

add_footer(s); add_slide_number(s, 17, TOTAL)
add_notes(s, "Intrinsic interpretability shows the model implements evidence-graded reasoning. "
              "This satisfies Requirement 5c-a from Part A.")

# ------ SLIDE 18: INTEGRATED INTERPRETABILITY ------
s = new_slide()
add_accent_bar(s)
add_title(s, "D5 Session 1b — Integrated per-prediction evidence")
add_subtitle(s, "Post-hoc paths + pathway + literature triangulated")

add_image(s, FIG_DIR / "plot_7_integrated.png", left=2.5, top=1.7, width=8.0)

tb = s.shapes.add_textbox(Inches(0.5), Inches(6.3), Inches(12.3), Inches(0.9))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
r = p.add_run()
r.text = "Finding:  "
r.font.name = "Arial"; r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = BLUE
r = p.add_run()
r.text = ("14% of top predictions have full evidence triangulation. Closes Requirement 5c fully — "
           "intrinsic + post-hoc + pathway + literature integration.")
r.font.name = "Arial"; r.font.size = Pt(13); r.font.color.rgb = DARK

add_footer(s); add_slide_number(s, 18, TOTAL)
add_notes(s, "This closes Requirement 5c. Coupled interpretability with pathway contextualisation, done. "
              "Reference the testosterone → ABCB1 exemplar.")

# ------ SLIDE 19: OBJECTIVES SUMMARY TABLE ------
s = new_slide()
add_accent_bar(s)
add_title(s, "All 5 objectives met")

# Table-style layout
rows = [
    ("Objective", "Status", "Notes"),
    ("1. KG construction", "✓ Complete", "38,955 nodes, 44,218 edges"),
    ("2. R-GCN training", "✓ Complete", "12 configurations, multi-seed"),
    ("3. Phenotype propagation", "⚠ Reformulated", "0 drug-phenotype edges in ClinPGx"),
    ("4. Interpret rankings", "✓ Complete", "Intrinsic + post-hoc + integrated"),
    ("5. Pathway + literature", "✓ Complete", "Enhanced with null check + 17.5% lit"),
]

# Draw table
top_y = 1.9
row_h = 0.6
col_widths = [4.5, 2.5, 5.3]
col_x = [0.5, 5.0, 7.5]

for row_idx, row in enumerate(rows):
    is_header = row_idx == 0
    for col_idx, cell in enumerate(row):
        tb = s.shapes.add_textbox(Inches(col_x[col_idx]),
                                    Inches(top_y + row_idx * row_h),
                                    Inches(col_widths[col_idx]),
                                    Inches(row_h))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = cell
        r.font.name = "Arial"
        r.font.size = Pt(15) if is_header else Pt(14)
        r.font.bold = is_header
        
        # Color coding for status column
        if col_idx == 1 and not is_header:
            if "✓" in cell:
                r.font.color.rgb = GREEN
            elif "⚠" in cell:
                r.font.color.rgb = VERMILLION
        else:
            r.font.color.rgb = DARK if not is_header else BLUE

add_footer(s); add_slide_number(s, 19, TOTAL)
add_notes(s, "Summary of all 5 objectives. Objective 3 needs careful framing in Part B — "
              "we discussed this on slide 11.")


# ============================================================
# SECTION 4: DISCUSSION (Slides 20-23)
# ============================================================

# ------ SLIDE 20: COMBINED NARRATIVE ------
s = new_slide()
add_accent_bar(s)
add_title(s, "Combined narrative — what we learned")

bullets = [
    "1.  Method-level choices don't move the needle  (D1, D2, D3, D4.1)",
    "2.  Chemical structure availability dominates  (D4.3, 5.5× effect)",
    "3.  Pathway enrichment is largely structural  (D5-Part 2 + null check)",
    "4.  43 model-only pathways = genuine model contribution  (mechanism-specific)",
    "5.  17.5% literature support with meaningful pairs  (D5-Part 1)",
    "6.  14% fully-triangulated predictions with integrated evidence  (D5 Session 1)",
]

tb = s.shapes.add_textbox(Inches(0.5), Inches(1.9), Inches(12.3), Inches(5))
tf = tb.text_frame
tf.word_wrap = True

for i, item in enumerate(bullets):
    if i == 0:
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    r = p.add_run()
    r.text = item
    r.font.name = "Arial"; r.font.size = Pt(18); r.font.color.rgb = DARK
    p.space_after = Pt(10)

add_footer(s); add_slide_number(s, 20, TOTAL)
add_notes(s, "Read through these findings as a coherent story. The narrative arc: null on method-level, "
              "positive on feature-level (SMILES), honest on pathway (mostly structural), "
              "modest positive on literature, defensible integrated framework.")

# ------ SLIDE 21: CONTRIBUTION ------
s = new_slide()
add_accent_bar(s)
add_title(s, "The MSc contribution")

# NOT box
not_box = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                Inches(0.5), Inches(1.7),
                                Inches(12.3), Inches(1.0))
not_box.fill.solid()
not_box.fill.fore_color.rgb = LIGHT_GREY
not_box.line.fill.background()

tb = s.shapes.add_textbox(Inches(0.8), Inches(1.85), Inches(12), Inches(0.8))
tf = tb.text_frame
p = tf.paragraphs[0]
r = p.add_run()
r.text = 'Not:  '
r.font.name = "Arial"; r.font.size = Pt(16); r.font.bold = True; r.font.color.rgb = VERMILLION
r = p.add_run()
r.text = '"We built a state-of-the-art model"'
r.font.name = "Arial"; r.font.size = Pt(16); r.font.italic = True; r.font.color.rgb = DARK

# YES section
tb = s.shapes.add_textbox(Inches(0.5), Inches(3.0), Inches(12.3), Inches(4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
r = p.add_run()
r.text = "Yes:"
r.font.name = "Arial"; r.font.size = Pt(20); r.font.bold = True; r.font.color.rgb = GREEN

bullets = [
    "Rigorous multi-seed evaluation identifying what does and doesn't drive performance",
    "Chemical structure availability identified as the primary constraint (D4)",
    "Null enrichment check for scientific defensibility (D5)",
    "Integrated multi-evidence interpretability framework (D5 Session 1)",
    "Honest, reproducible reporting standards",
]
for b in bullets:
    p = tf.add_paragraph()
    r = p.add_run()
    r.text = "•  " + b
    r.font.name = "Arial"; r.font.size = Pt(15); r.font.color.rgb = DARK
    p.space_after = Pt(6)

add_footer(s); add_slide_number(s, 21, TOTAL)
add_notes(s, "This is a characterisation contribution. Not glamorous but scientifically honest. "
              "State this clearly — supervisors respect honest framing.")

# ------ SLIDE 22: LIMITATIONS ------
s = new_slide()
add_accent_bar(s)
add_title(s, "Honest limitations")

# Three-column: Method, Data, Interpretation
col_x = [0.5, 4.7, 8.9]
col_w = 4.0

for i, (header, items) in enumerate([
    ("Method", [
        "Single architecture (R-GCN)",
        "64-dim embeddings only",
        "PubMed 1990-2026 date filter",
        "Single-config literature",
    ]),
    ("Data", [
        "ClinPGx sparsity (~44k edges)",
        "No drug-phenotype edges (Obj 3)",
        "SMILES coverage 537/751 drugs",
    ]),
    ("Interpretation", [
        "Aggregate MRR does not fully capture utility",
        "Pathway enrichment doesn't prove causality",
        "17.5% inflated by broad chemicals",
    ]),
]):
    # Header
    tb = s.shapes.add_textbox(Inches(col_x[i]), Inches(1.7), Inches(col_w), Inches(0.6))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = header
    r.font.name = "Arial"; r.font.size = Pt(20); r.font.bold = True; r.font.color.rgb = VERMILLION
    
    # Items
    tb = s.shapes.add_textbox(Inches(col_x[i]), Inches(2.4), Inches(col_w), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    for j, item in enumerate(items):
        if j == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        r = p.add_run()
        r.text = "•  " + item
        r.font.name = "Arial"; r.font.size = Pt(13); r.font.color.rgb = DARK
        p.space_after = Pt(6)

add_footer(s); add_slide_number(s, 22, TOTAL)
add_notes(s, "Be direct about limitations. Don't over-defend — acknowledge and move on. "
              "Note that most are scope decisions, not failures.")

# ------ SLIDE 23: FUTURE WORK ------
s = new_slide()
add_accent_bar(s)
add_title(s, "Future directions")

bullets = [
    "Short-term (before submission):",
    ("Complete Part B writing (chapters 3-6)", 1),
    ("Address supervisor feedback from today", 1),
    "",
    "Long-term (beyond MSc):",
    ("Alternative architectures (RGAT, CompGCN, HGT)", 1),
    ("Descriptor-rich features (ChemBERTa, ProtT5)", 1),
    ("Structure-free representations for uncharacterised drugs", 1),
    ("SIDER integration for drug-phenotype ground truth", 1),
    ("Multi-config literature validation", 1),
]
add_body_text(s, bullets, y=1.9, size=17, bullet_char="")

add_footer(s); add_slide_number(s, 23, TOTAL)
add_notes(s, "Future work section shows I understand what a stronger paper would look like, "
              "but scope was appropriately bounded for an MSc.")


# ============================================================
# SECTION 5: ASK (Slides 24-25)
# ============================================================

# ------ SLIDE 24: WHAT I NEED ------
s = new_slide()
add_accent_bar(s, color=BLUE)
add_title(s, "Your guidance requested")

bullets = [
    "1.  Approval to begin Part B writing",
    ("Chapters 3 (methodology), 4 (results), 5 (discussion), 6 (conclusion)", 1),
    "",
    "2.  Confirmation these findings are defensible as an MSc contribution",
    ("Null-plus-characterisation framing, integrated interpretability", 1),
    "",
    "3.  Guidance on Objective 3 reformulation framing",
    ("Data reality: 0 drug-phenotype edges; is the phenotype-relevant proxy acceptable?", 1),
    "",
    "4.  Timeline check",
    ("December submission target, 5-6 weeks ahead of Part A schedule", 1),
]
add_body_text(s, bullets, y=1.7, size=16, bullet_char="")

add_footer(s); add_slide_number(s, 24, TOTAL)
add_notes(s, "Be specific about what you need. These four are the actionable items for the meeting.")

# ------ SLIDE 25: TIMELINE ------
s = new_slide()
add_accent_bar(s, color=BLUE)
add_title(s, "Path to December submission")

timeline = [
    ("July 2026", "✓ All experimental deliverables complete"),
    ("This week", "Presentation to supervisors"),
    ("Aug – Oct 2026", "Part B chapter drafts"),
    ("November 2026", "Supervisor review + revisions"),
    ("Early December 2026", "Submission"),
]

top_y = 2.0
for i, (date, event) in enumerate(timeline):
    y = top_y + i * 0.9
    
    # Date column
    tb = s.shapes.add_textbox(Inches(0.5), Inches(y), Inches(3.5), Inches(0.7))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = date
    r.font.name = "Arial"; r.font.size = Pt(16); r.font.bold = True; r.font.color.rgb = BLUE
    
    # Event column
    tb = s.shapes.add_textbox(Inches(4.5), Inches(y), Inches(8.0), Inches(0.7))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = event
    r.font.name = "Arial"; r.font.size = Pt(16); r.font.color.rgb = DARK

add_footer(s); add_slide_number(s, 25, TOTAL)
add_notes(s, "End on the timeline. We're ahead of schedule. That buffer becomes writing time. "
              "This is your closing statement.")


# ============================================================
# BACKUP SLIDES (26-31)
# ============================================================

# ------ SLIDE 26: BACKUP — CONFIGURATIONS ------
s = new_slide()
add_accent_bar(s, color=GREY)
add_title(s, "Backup: 12 configuration details", color=GREY)

bullets = [
    "D1 supervision regime experiments (9 configs):",
    ("regime = default, ambig_as_pos, or nonassoc_excluded", 1),
    ("seed = 42, 123, or 2026", 1),
    ("β = 0.10 (hub penalty)", 1),
    "",
    "D2 hub penalty ablation (3 configs):",
    ("regime = default", 1),
    ("β = 0.00 (no hub penalty)", 1),
    ("seed = 42, 123, or 2026", 1),
    "",
    "All hyperparameters: hidden_dim=64, output_dim=64, num_bases=8, dropout=0.2",
]
add_body_text(s, bullets, y=1.7, size=14, bullet_char="")

add_footer(s); add_slide_number(s, 26, TOTAL)

# ------ SLIDE 27: BACKUP — MULTI-SEED DATA ------
s = new_slide()
add_accent_bar(s, color=GREY)
add_title(s, "Backup: Filtered MRR per config", color=GREY)

# Data table
rows = [
    ("Config", "Seed 42", "Seed 123", "Seed 2026", "Mean ± SD"),
    ("default β=0.10", "0.0710", "0.0895", "0.1105", "0.0903 ± 0.020"),
    ("ambig_as_pos β=0.10", "0.0745", "0.0910", "0.0910", "0.0855 ± 0.011"),
    ("nonassoc_excl β=0.10", "0.0710", "0.0900", "0.0920", "0.0844 ± 0.012"),
    ("default β=0.00", "0.0620", "0.0895", "0.0947", "0.0821 ± 0.016"),
]

top_y = 1.9
row_h = 0.5
col_widths = [3.5, 1.7, 1.7, 1.7, 2.5]
col_x = [0.5, 4.0, 5.7, 7.4, 9.1]

for row_idx, row in enumerate(rows):
    is_header = row_idx == 0
    for col_idx, cell in enumerate(row):
        tb = s.shapes.add_textbox(Inches(col_x[col_idx]),
                                    Inches(top_y + row_idx * row_h),
                                    Inches(col_widths[col_idx]),
                                    Inches(row_h))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = cell
        r.font.name = "Arial"; r.font.size = Pt(13)
        r.font.bold = is_header
        r.font.color.rgb = BLUE if is_header else DARK

add_footer(s); add_slide_number(s, 27, TOTAL)

# ------ SLIDE 28: BACKUP — NULL ENRICHMENT ------
s = new_slide()
add_accent_bar(s, color=GREY)
add_title(s, "Backup: 43 model-only pathways (sample)", color=GREY)

bullets = [
    "Wnt/β-catenin signaling pathway family",
    "REACTOME:: TCF-dependent Wnt signaling",
    "REACTOME:: Nuclear Receptor transcription",
    "REACTOME:: Interferon signaling (multiple sub-pathways)",
    "REACTOME:: ADAR signaling",
    "REACTOME:: G alpha (s) signalling events",
    "REACTOME:: Class B/2 Secretin receptors",
    "REACTOME:: Antimicrobial peptides",
    "KEGG:: SEB-mediated Th cell response",
    "",
    "Interpretation: mechanism-specific pathways that pure degree-based selection misses.",
]
add_body_text(s, bullets, y=1.7, size=14, bullet_char="")

add_footer(s); add_slide_number(s, 28, TOTAL)

# ------ SLIDE 29: BACKUP — TESTOSTERONE EXEMPLAR ------
s = new_slide()
add_accent_bar(s, color=GREY)
add_title(s, "Backup: Fully-triangulated exemplar", color=GREY)
add_subtitle(s, "testosterone → ABCB1  (model score -0.43, rank 1)")

bullets = [
    "Structural (graph path, 3 hops):",
    ("testosterone → CYP3A4 → paroxetine → ABCB1", 1),
    ("Biologically plausible: testosterone is CYP3A4 substrate", 1),
    "",
    "Pathway (D5-Part 2, FDR-significant):",
    ("27 significant PGx pathways contain ABCB1", 1),
    ("Includes: Paroxetine, Etoposide, Tacrolimus/Cyclosporine, Taxane, Verapamil, Statin", 1),
    "",
    "Literature (D5-Part 1, PubMed):",
    ("10 articles co-mentioning testosterone and ABCB1", 1),
    ("Range: 2024-2026 (all within date filter)", 1),
    ("PMIDs: 42280472, 39488872, 38713375, ...", 1),
]
add_body_text(s, bullets, y=1.7, size=14, bullet_char="")

add_footer(s); add_slide_number(s, 29, TOTAL)

# ------ SLIDE 30: BACKUP — LIT SUPPORT EXAMPLES ------
s = new_slide()
add_accent_bar(s, color=GREY)
add_title(s, "Backup: Literature-supported novel predictions", color=GREY)

# Table
rows = [
    ("Drug → Gene", "Articles", "Biological context"),
    ("carbidopa → COMT", "10", "Parkinson's (COMT inhibits levodopa)"),
    ("dimethyl fumarate → FOXP3", "7", "MS (Tecfidera → T-reg cells)"),
    ("doxorubicinol → ABCB1", "3", "Chemo resistance (efflux)"),
    ("doxorubicinol → CBR3", "2", "Doxorubicin metabolism"),
    ("canakinumab → IL1B", "10", "Anti-IL1β mAb (direct target)"),
    ("etoposide → ABCC1/ABCC2", "10 each", "Chemo efflux resistance"),
    ("fludarabine → NQO1", "1", "Leukemia drug detoxification"),
]

top_y = 1.9
row_h = 0.5
col_widths = [4.0, 1.5, 6.5]
col_x = [0.5, 4.5, 6.0]

for row_idx, row in enumerate(rows):
    is_header = row_idx == 0
    for col_idx, cell in enumerate(row):
        tb = s.shapes.add_textbox(Inches(col_x[col_idx]),
                                    Inches(top_y + row_idx * row_h),
                                    Inches(col_widths[col_idx]),
                                    Inches(row_h))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = cell
        r.font.name = "Arial"; r.font.size = Pt(13)
        r.font.bold = is_header
        r.font.color.rgb = BLUE if is_header else DARK

add_footer(s); add_slide_number(s, 30, TOTAL)

# ------ SLIDE 31: BACKUP — RELATED WORK ------
s = new_slide()
add_accent_bar(s, color=GREY)
add_title(s, "Backup: How this fits related work", color=GREY)

bullets = [
    "Turon et al. (2025) — Descriptor-rich features achieve better biomedical KG completion",
    ("Our D4 finding explains why: chemical structure availability is the primary constraint", 1),
    "",
    "Bonner et al. (2022) — Multi-lens evaluation in biomedical KG completion",
    ("Our D5 Session 1 exemplifies: pathway + literature + interpretability together", 1),
    "",
    "Schlichtkrull et al. (2018) — Original R-GCN paper",
    ("Our work stress-tests R-GCN in a specialised biomedical setting", 1),
    ("Provides reference for future work with the same rigorous methodology", 1),
]
add_body_text(s, bullets, y=1.7, size=15, bullet_char="")

add_footer(s); add_slide_number(s, 31, TOTAL)


# ============================================================
# SAVE
# ============================================================
OUT_PATH.parent.mkdir(exist_ok=True)
prs.save(str(OUT_PATH))
print(f"\n✓ Presentation saved: {OUT_PATH}")
print(f"  Slides: {len(prs.slides)}")
print(f"  Size: {OUT_PATH.stat().st_size // 1024} KB")
