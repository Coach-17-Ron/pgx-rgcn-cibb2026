#!/bin/bash
# D3 multi-seed aggregation across regimes and β values

echo "=========================================="
echo "  D3 PHENOTYPE-RELEVANT RANKING ANALYSIS"
echo "  Multi-seed across 12 configurations"
echo "=========================================="

python3 << 'PYEOF'
import json
from pathlib import Path
from statistics import mean, stdev

RESULTS = Path("results")
SEEDS = [42, 123, 2026]

# The 12 canonical configs
CONFIGS = {
    "default_beta0p1": [f"*_beta0p1_seed{s}_reg-default" for s in SEEDS],
    "ambig_as_pos_beta0p1": [f"*_beta0p1_seed{s}_reg-ambig_as_pos" for s in SEEDS],
    "nonassoc_excluded_beta0p1": [f"*_beta0p1_seed{s}_reg-nonassoc_excluded" for s in SEEDS],
    "default_beta0p0": [f"*_beta0p0_seed{s}_reg-default" for s in SEEDS],
}

def find_and_load(pattern):
    """Find matching run folder and load its d3_phenotype_metrics.json"""
    matches = sorted(RESULTS.glob(pattern), reverse=True)
    if not matches:
        return None
    path = matches[0] / "artifacts" / "d3_phenotype_metrics.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)

results = {}
for cfg_name, patterns in CONFIGS.items():
    data = {"model_filt_mrr": [], "model_raw_mrr": [],
            "baseline_dg_filt_mrr": [], "baseline_gp_filt_mrr": []}
    for p in patterns:
        m = find_and_load(p)
        if m is not None:
            data["model_filt_mrr"].append(m["model"]["filtered"]["mrr"])
            data["model_raw_mrr"].append(m["model"]["raw"]["mrr"])
            data["baseline_dg_filt_mrr"].append(m["baseline_drug_gene_degree"]["filtered"]["mrr"])
            data["baseline_gp_filt_mrr"].append(m["baseline_gene_phenotype_degree"]["filtered"]["mrr"])
    results[cfg_name] = data

print()
print("=" * 100)
print(f"{'Config':<28} {'Model Filt MRR':<18} {'DG Degree Baseline':<20} {'GP Degree Baseline':<20}")
print("-" * 100)

for cfg_name, data in results.items():
    if len(data["model_filt_mrr"]) >= 2:
        m_mrr = mean(data["model_filt_mrr"])
        m_std = stdev(data["model_filt_mrr"])
        b_dg = mean(data["baseline_dg_filt_mrr"])
        b_gp = mean(data["baseline_gp_filt_mrr"])
        print(f"{cfg_name:<28} {m_mrr:.4f} ± {m_std:.4f}   {b_dg:.4f} (mean)       {b_gp:.4f} (mean)")
    elif len(data["model_filt_mrr"]) == 1:
        m_mrr = data["model_filt_mrr"][0]
        b_dg = data["baseline_dg_filt_mrr"][0]
        b_gp = data["baseline_gp_filt_mrr"][0]
        print(f"{cfg_name:<28} {m_mrr:.4f} (n=1)          {b_dg:.4f}              {b_gp:.4f}")
    else:
        print(f"{cfg_name:<28} NO DATA")

print("=" * 100)
print()

# Interpretation
print("=== Interpretation ===")
default_data = results.get("default_beta0p1", {}).get("model_filt_mrr", [])
if len(default_data) >= 2:
    m = mean(default_data)
    s = stdev(default_data)
    b_dg = mean(results["default_beta0p1"]["baseline_dg_filt_mrr"])
    b_gp = mean(results["default_beta0p1"]["baseline_gp_filt_mrr"])
    print(f"Default β=0.10 (reference):")
    print(f"  Model filt MRR (n=3):  {m:.4f} ± {s:.4f}")
    print(f"  DG degree baseline:     {b_dg:.4f}")
    print(f"  GP degree baseline:     {b_gp:.4f}")
    print(f"  Model vs DG baseline:   {m-b_dg:+.4f}")
    print(f"  Model vs GP baseline:   {m-b_gp:+.4f}")
    print()
    if m > b_dg and m > b_gp:
        print("Judgement: Model beats both baselines → D3 finding is POSITIVE")
    elif m > b_gp:
        print("Judgement: Model matches DG baseline, beats GP baseline")
    elif m > b_dg:
        print("Judgement: Model beats DG baseline, matches/loses to GP")
    else:
        print("Judgement: Model does NOT beat naive baselines on phenotype-relevant subset.")
        print("           Consistent with D1/D2: model performs at baseline everywhere tested.")
PYEOF

echo ""
echo "Analysis complete."
