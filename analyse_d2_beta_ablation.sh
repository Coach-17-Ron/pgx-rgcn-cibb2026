#!/bin/bash
# D2 analysis: compare β=0.10 (from D1 default runs) vs β=0.0 (new D2 runs)

echo "=========================================="
echo "  D2 β=0 HUB-PENALTY ABLATION ANALYSIS"
echo "  Comparing β=0.10 vs β=0.0"
echo "  Both at regime=default, seeds=[42, 123, 2026]"
echo "=========================================="

python3 << 'PYEOF'
import json
from pathlib import Path
from statistics import mean, stdev

RESULTS = Path("results")
SEEDS = [42, 123, 2026]

def find_run(seed, beta_tag):
    """Find the most recent run matching seed and beta tag."""
    pattern = f"*_dg_context_{beta_tag}_seed{seed}_reg-default"
    matches = sorted(RESULTS.glob(pattern), reverse=True)
    return matches[0] if matches else None

def load_metrics(run_dir):
    path = run_dir / "artifacts" / "test_metrics.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)

# Collect data for both conditions
data = {"beta_0p1": {"filt_mrr": [], "raw_mrr": [], "filt_h10": [], 
                     "cyp_frac": [], "baseline": []},
        "beta_0p0": {"filt_mrr": [], "raw_mrr": [], "filt_h10": [], 
                     "cyp_frac": [], "baseline": []}}

conditions = [("beta_0p1", "beta0p1"), ("beta_0p0", "beta0p0")]

for cond_name, beta_tag in conditions:
    print(f"\n--- {cond_name} ---")
    for seed in SEEDS:
        run = find_run(seed, beta_tag)
        if run is None:
            print(f"  seed={seed}: NO RUN FOUND for {beta_tag}")
            continue
        m = load_metrics(run)
        if m is None:
            print(f"  seed={seed}: NO METRICS")
            continue
        filt_mrr = m["filtered"]["mrr"]
        raw_mrr = m["raw"]["mrr"]
        filt_h10 = m["filtered"]["hits_at_10"]
        baseline = m["degree_baseline"]["mrr"]
        # CYP fraction might not be in metrics; check safely
        cyp = m.get("cyp_fraction_top_predictions", None)
        
        data[cond_name]["filt_mrr"].append(filt_mrr)
        data[cond_name]["raw_mrr"].append(raw_mrr)
        data[cond_name]["filt_h10"].append(filt_h10)
        data[cond_name]["baseline"].append(baseline)
        if cyp is not None:
            data[cond_name]["cyp_frac"].append(cyp)
        
        print(f"  seed={seed}: filt_MRR={filt_mrr:.4f} raw_MRR={raw_mrr:.4f} baseline={baseline:.4f}")

# Summary
print("\n")
print("=" * 80)
print(f"{'Condition':<18} {'Filt MRR (mean±sd)':<24} {'Raw MRR (mean±sd)':<24}")
print("-" * 80)

for cond in ["beta_0p1", "beta_0p0"]:
    d = data[cond]
    if len(d["filt_mrr"]) >= 2:
        fm = mean(d["filt_mrr"]); fs = stdev(d["filt_mrr"])
        rm = mean(d["raw_mrr"]); rs = stdev(d["raw_mrr"])
        print(f"{cond:<18} {fm:.4f} ± {fs:.4f}      {rm:.4f} ± {rs:.4f}")
    elif len(d["filt_mrr"]) == 1:
        print(f"{cond:<18} {d['filt_mrr'][0]:.4f} (n=1)")
    else:
        print(f"{cond:<18} NO DATA")

print("=" * 80)

# Judgement
if len(data["beta_0p1"]["filt_mrr"]) >= 2 and len(data["beta_0p0"]["filt_mrr"]) >= 2:
    m1 = mean(data["beta_0p1"]["filt_mrr"])
    m0 = mean(data["beta_0p0"]["filt_mrr"])
    s1 = stdev(data["beta_0p1"]["filt_mrr"])
    s0 = stdev(data["beta_0p0"]["filt_mrr"])
    diff = m0 - m1
    pooled_sd = (s1 + s0) / 2
    
    print()
    print("=== Interpretation ===")
    print(f"β=0.10 mean filt MRR: {m1:.4f} (SD {s1:.4f})")
    print(f"β=0.0  mean filt MRR: {m0:.4f} (SD {s0:.4f})")
    print(f"Difference (β=0 minus β=0.1): {diff:+.4f}")
    print(f"Pooled SD:                    {pooled_sd:.4f}")
    
    if abs(diff) > 2 * pooled_sd:
        print("Judgement: DIFFERENCE > 2x SD -> hub penalty has real effect")
    elif abs(diff) > pooled_sd:
        print("Judgement: Weak signal -> hub penalty may have small effect")
    else:
        print("Judgement: Difference within SD -> hub penalty has NO measurable effect")
        print("           (degree-aware sampling alone appears sufficient)")

PYEOF

echo ""
echo "Analysis complete."
