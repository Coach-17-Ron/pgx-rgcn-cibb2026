"""Fix stage 4 (and any other downstream stages) checkpoint loading to be
fingerprint-aware. Mirrors the stage 3 pattern: read use_fingerprints flag
from the checkpoint, construct the model with drug_fp_dim accordingly.
"""
from pathlib import Path
import sys

SCRIPT = Path("pgx_pipeline_combined.py")
if not SCRIPT.exists():
    sys.exit(f"{SCRIPT} not found")

src = SCRIPT.read_text()
backup = SCRIPT.with_suffix(".py.bak_stage4fix")
if not backup.exists():
    backup.write_text(src)
    print(f"Backup -> {backup}")

# Patch: stage 4 model construction is the SECOND occurrence of this exact
# block (the first occurrence is stage 3, already patched).  The block uses
# the same exact text so we replace the FIRST remaining un-patched copy
# (after stage 3 is already patched, this is necessarily the stage 4 one).
OLD = '''    # --- Rebuild model for intrinsic analysis ---
    x = homog["x"].to(device)
    model = PGx_RGCN(
        in_channels=x.size(-1),
        hidden_channels=cfg["model"]["hidden_dim"],
        out_channels=cfg["model"]["output_dim"],
        num_edge_types=ckpt["num_edge_types"],
        num_decoder_relations=ckpt["num_decoder_relations"],
        num_bases=cfg["model"]["num_bases"],
        dropout=cfg["model"]["dropout"],
    ).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()'''

NEW = '''    # --- Rebuild model for intrinsic analysis ---
    x = homog["x"].to(device)
    # Round 3: checkpoint may carry drug-fingerprint layers
    use_fp_ck = bool(ckpt.get("use_fingerprints", False))
    drug_fp_dim_ck = ckpt.get("drug_fp_dim")
    n_drugs_for_fp_ck = int(ckpt.get("n_drugs_for_fp", 0))
    model = PGx_RGCN(
        in_channels=x.size(-1),
        hidden_channels=cfg["model"]["hidden_dim"],
        out_channels=cfg["model"]["output_dim"],
        num_edge_types=ckpt["num_edge_types"],
        num_decoder_relations=ckpt["num_decoder_relations"],
        num_bases=cfg["model"]["num_bases"],
        dropout=cfg["model"]["dropout"],
        drug_fp_dim=drug_fp_dim_ck if use_fp_ck else None,
        n_drugs_for_fp=n_drugs_for_fp_ck if use_fp_ck else 0,
    ).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    # Stage 4 only inspects encoder weights, not the encode() forward,
    # so re-attaching fingerprints is not needed here.'''

assert OLD in src, "Stage 4 model construction block not found"
src = src.replace(OLD, NEW, 1)
print("[ok] Stage 4 model construction now reads use_fingerprints flag")

SCRIPT.write_text(src)

import ast
ast.parse(src)
print(f"Syntax OK, {len(src.splitlines())} lines")
