#!/bin/bash
# D5-Part 2 aggregation: pathway enrichment across 12 configs

echo "=========================================="
echo "  D5 PATHWAY ENRICHMENT MULTI-CONFIG ANALYSIS"
echo "  Reactome + KEGG + PharmGKB, BH FDR<0.05"
echo "=========================================="

singularity exec /idia/software/containers/ASTRO-GPU-PyTorch-2026-01-28.sif \
python3 << 'PYEOF'
import pandas as pd
from pathlib import Path
from statistics import mean

RESULTS = Path("results")
SEEDS = [42, 123, 2026]

CONFIGS = {
    "default_beta0p1": [f"*_beta0p1_seed{s}_reg-default" for s in SEEDS],
    "ambig_as_pos_beta0p1": [f"*_beta0p1_seed{s}_reg-ambig_as_pos" for s in SEEDS],
    "nonassoc_excluded_beta0p1": [f"*_beta0p1_seed{s}_reg-nonassoc_excluded" for s in SEEDS],
    "default_beta0p0": [f"*_beta0p0_seed{s}_reg-default" for s in SEEDS],
}

def find_pathway_file(pattern):
    matches = sorted(RESULTS.glob(pattern), reverse=True)
    if not matches:
        return None
    path = matches[0] / "artifacts" / "pathway_enrichment.parquet"
    return path if path.exists() else None


print(f"{'Config':<28} {'n_sig_mean':<12} {'REACTOME':<12} {'KEGG':<8} {'PGKB':<8}")
print("-" * 80)

all_sig_pathways = {}

for cfg_name, patterns in CONFIGS.items():
    n_sig_list = []
    src_counts = {"REACTOME": 0, "KEGG": 0, "PGKB": 0}
    for p in patterns:
        path = find_pathway_file(p)
        if path is None:
            continue
        df = pd.read_parquet(path)
        sig = df[df["significant"] == True]
        n_sig_list.append(len(sig))
        for src in ["REACTOME", "KEGG", "PGKB"]:
            src_counts[src] += len(sig[sig["source"] == src])
        for _, row in sig.iterrows():
            key = row["pathway"]
            all_sig_pathways[key] = all_sig_pathways.get(key, 0) + 1
    
    if n_sig_list:
        avg_sig = mean(n_sig_list)
        print(f"{cfg_name:<28} {avg_sig:<12.1f} {src_counts['REACTOME']:<12} {src_counts['KEGG']:<8} {src_counts['PGKB']:<8}")
    else:
        print(f"{cfg_name:<28} NO DATA")

print()

if all_sig_pathways:
    print(f"Unique significant pathways across configs: {len(all_sig_pathways)}")
    majority = [p for p, c in all_sig_pathways.items() if c >= 6]
    print(f"Pathways significant in >=6/12 configs: {len(majority)}")
    if majority:
        print("Top majority-hit pathways:")
        for pathway, count in sorted(all_sig_pathways.items(), key=lambda x: -x[1])[:10]:
            if count >= 6:
                print(f"  [{count}/12] {pathway[:80]}")
else:
    print("=== No FDR-significant pathways in ANY configuration ===")
    print("Legitimate null finding under BH-FDR correction.")

# Nominal (uncorrected) top pathways for reference config
print()
print("=== Reference config nominal top 10 by p-value ===")
ref_path = find_pathway_file("*_beta0p1_seed42_reg-default")
if ref_path:
    df = pd.read_parquet(ref_path)
    top = df.sort_values("p_value").head(10)
    for _, row in top.iterrows():
        sig_mark = "**" if row["significant"] else "  "
        pname = row['pathway'].split("::")[-1][:60]
        print(f"  {sig_mark} {row['source']:8s}  p={row['p_value']:.2e}  q={row['q_value']:.3f}  {pname}")
PYEOF

echo ""
echo "Analysis complete."
