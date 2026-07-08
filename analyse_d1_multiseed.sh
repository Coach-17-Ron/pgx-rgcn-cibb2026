#!/bin/bash
# Multi-seed D1 analysis: mean +/- std across seeds per regime

echo "=========================================="
echo "  D1 MULTI-SEED ANALYSIS"
echo "  seed=[42, 123, 2026], β=0.10"
echo "=========================================="

python3 << 'PYEOF'
import json
import os
from pathlib import Path
from statistics import mean, stdev

RESULTS = Path("results")
REGIMES = ["default", "ambig_as_pos", "nonassoc_excluded"]
SEEDS = [42, 123, 2026]
BETA_TAG = "beta0p1"

def find_run(regime, seed):
    """Find the most recent run matching regime and seed."""
    pattern = f"*_dg_context_{BETA_TAG}_seed{seed}_reg-{regime}"
    matches = sorted(RESULTS.glob(pattern), reverse=True)
    return matches[0] if matches else None

def load_metrics(run_dir):
    """Load test_metrics.json from a run directory."""
    path = run_dir / "artifacts" / "test_metrics.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)

# Collect all metrics per regime
data = {regime: {"filt_mrr": [], "raw_mrr": [], "filt_h10": [], "baseline": [], 
                 "with_smi": [], "without_smi": []} 
        for regime in REGIMES}

for regime in REGIMES:
    print(f"\n--- {regime} ---")
    for seed in SEEDS:
        run = find_run(regime, seed)
        if run is None:
            print(f"  seed={seed}: NO RUN FOUND")
            continue
        m = load_metrics(run)
        if m is None:
            print(f"  seed={seed}: NO METRICS")
            continue
        filt_mrr = m["filtered"]["mrr"]
        raw_mrr = m["raw"]["mrr"]
        filt_h10 = m["filtered"]["hits_at_10"]
        baseline = m["degree_baseline"]["mrr"]
        with_smi = m["filtered_with_smiles"]["mrr"]
        without_smi = m["filtered_without_smiles"]["mrr"]
        
        data[regime]["filt_mrr"].append(filt_mrr)
        data[regime]["raw_mrr"].append(raw_mrr)
        data[regime]["filt_h10"].append(filt_h10)
        data[regime]["baseline"].append(baseline)
        data[regime]["with_smi"].append(with_smi)
        data[regime]["without_smi"].append(without_smi)
        
        print(f"  seed={seed}: filt_MRR={filt_mrr:.4f} baseline={baseline:.4f}")

# Summary table
print("\n")
print("=" * 90)
print(f"{'Regime':<25} {'Filt MRR (mean±sd)':<22} {'Baseline':<12} {'Filt H@10 mean':<15}")
print("-" * 90)

for regime in REGIMES:
    d = data[regime]
    if len(d["filt_mrr"]) >= 2:
        mrr_m = mean(d["filt_mrr"])
        mrr_s = stdev(d["filt_mrr"])
        base_m = mean(d["baseline"])
        h10_m = mean(d["filt_h10"])
        print(f"{regime:<25} {mrr_m:.4f} ± {mrr_s:.4f}     {base_m:.4f}      {h10_m:.4f}")
    elif len(d["filt_mrr"]) == 1:
        mrr_m = d["filt_mrr"][0]
        base_m = d["baseline"][0]
        h10_m = d["filt_h10"][0]
        print(f"{regime:<25} {mrr_m:.4f} (n=1)         {base_m:.4f}      {h10_m:.4f}")
    else:
        print(f"{regime:<25} NO DATA")

print("=" * 90)

# Judgement call
print()
print("=== Interpretation ===")
default_data = data["default"]["filt_mrr"]
if len(default_data) >= 2:
    default_std = stdev(default_data)
    default_mean = mean(default_data)
    print(f"Intra-regime SD (default): {default_std:.4f}")
    print(f"Baseline (mean across seeds): {mean(data['default']['baseline']):.4f}")
    
    for regime in ["ambig_as_pos", "nonassoc_excluded"]:
        if len(data[regime]["filt_mrr"]) >= 2:
            r_mean = mean(data[regime]["filt_mrr"])
            r_std = stdev(data[regime]["filt_mrr"])
            diff = r_mean - default_mean
            pooled_sd = (default_std + r_std) / 2
            print(f"\n{regime} vs default:")
            print(f"  Difference: {diff:+.4f}")
            print(f"  Pooled SD:  {pooled_sd:.4f}")
            if abs(diff) > 2 * pooled_sd:
                print(f"  Judgement:  DIFFERENCE > 2x SD -> likely real effect")
            elif abs(diff) > pooled_sd:
                print(f"  Judgement:  Difference approaches SD -> weak signal, may need more seeds")
            else:
                print(f"  Judgement:  Difference within SD -> likely noise")
PYEOF

echo ""
echo "Analysis complete."
