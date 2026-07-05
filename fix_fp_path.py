"""Fix the broken fingerprint-path resolution in stage 2 and stage 3.

The CONFIG value 'drug_fingerprints_path' is './data/drug_fingerprints.parquet'
relative to the project root. The original patch tried to join it under
data_dir, producing 'data/data/drug_fingerprints.parquet'. Replace with a
simple direct Path() and skip the data_dir join.
"""
from pathlib import Path
import sys

SCRIPT = Path("pgx_pipeline_combined.py")
if not SCRIPT.exists():
    sys.exit(f"{SCRIPT} not found")

src = SCRIPT.read_text()
backup = SCRIPT.with_suffix(".py.bak_fp_pathfix")
if not backup.exists():
    backup.write_text(src)
    print(f"Backup -> {backup}")

# Patch 1: stage 2 fingerprint path resolution
OLD2 = '''    # Round 3: load drug fingerprints if available
    fp_path = paths["data_dir"] / cfg["data"].get(
        "drug_fingerprints_path", "drug_fingerprints.parquet"
    ) if isinstance(paths["data_dir"], Path) else \\
        Path(cfg["data"].get("drug_fingerprints_path", "./data/drug_fingerprints.parquet"))
    if not Path(fp_path).is_absolute():
        # Resolve relative to data_dir
        fp_path = Path(paths["data_dir"]) / Path(fp_path).name \\
            if Path(fp_path).name == "drug_fingerprints.parquet" else Path(fp_path)
    drug_fp, drug_has_fp, n_with_fp = load_drug_fingerprints('''

NEW2 = '''    # Round 3: load drug fingerprints if available
    # CONFIG value is already relative to the run directory (e.g.
    # "./data/drug_fingerprints.parquet"); use as-is, no extra joining.
    fp_path = Path(cfg["data"].get(
        "drug_fingerprints_path", "./data/drug_fingerprints.parquet"
    ))
    drug_fp, drug_has_fp, n_with_fp = load_drug_fingerprints('''

assert OLD2 in src, "Stage 2 path block not found"
src = src.replace(OLD2, NEW2, 1)
print("[ok] Stage 2 fingerprint path resolution fixed")

# Patch 2: stage 3 fingerprint path resolution
OLD3 = '''        fp_path = Path(paths["data_dir"]) / "drug_fingerprints.parquet"
        if fp_path.exists():'''

NEW3 = '''        fp_path = Path(cfg["data"].get(
            "drug_fingerprints_path", "./data/drug_fingerprints.parquet"
        ))
        if fp_path.exists():'''

assert OLD3 in src, "Stage 3 path block not found"
src = src.replace(OLD3, NEW3, 1)
print("[ok] Stage 3 fingerprint path resolution fixed")

SCRIPT.write_text(src)

# Syntax check
import ast
try:
    ast.parse(src)
    print(f"Syntax OK, {len(src.splitlines())} lines")
except SyntaxError as e:
    print(f"SYNTAX ERROR line {e.lineno}: {e.msg}")
    sys.exit(1)
