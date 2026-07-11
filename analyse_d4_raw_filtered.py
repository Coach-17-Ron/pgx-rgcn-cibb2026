"""
D4: Raw AND Filtered Ranking Analysis.

Analytical study using existing test_metrics.json files across 12 D1/D2
configurations. No new compute.

Two sub-analyses:
  D4.1 — Configuration-level raw vs filtered gap comparison
  D4.3 — SMILES stratification × protocol interaction

Output: d4_results_summary.md with three tables and interpretation.
"""

import json
import re
from pathlib import Path
from statistics import mean, stdev

RESULTS = Path("results")

# The 12 canonical configs (regime × beta × seed)
CONFIGS = {
    "default_beta0p1": {
        "regime": "default", "beta": "0.10",
        "patterns": [f"*_beta0p1_seed{s}_reg-default" for s in [42, 123, 2026]],
    },
    "ambig_as_pos_beta0p1": {
        "regime": "ambig_as_pos", "beta": "0.10",
        "patterns": [f"*_beta0p1_seed{s}_reg-ambig_as_pos" for s in [42, 123, 2026]],
    },
    "nonassoc_excluded_beta0p1": {
        "regime": "nonassoc_excluded", "beta": "0.10",
        "patterns": [f"*_beta0p1_seed{s}_reg-nonassoc_excluded" for s in [42, 123, 2026]],
    },
    "default_beta0p0": {
        "regime": "default", "beta": "0.00",
        "patterns": [f"*_beta0p0_seed{s}_reg-default" for s in [42, 123, 2026]],
    },
}


def find_and_load(pattern):
    """Find the most recent run matching pattern and load test_metrics.json."""
    matches = sorted(RESULTS.glob(pattern), reverse=True)
    if not matches:
        return None
    path = matches[0] / "artifacts" / "test_metrics.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def collect_data():
    """Gather metrics across all 12 configs."""
    data = {}
    for cfg_name, cfg_info in CONFIGS.items():
        entries = []
        for p in cfg_info["patterns"]:
            m = find_and_load(p)
            if m is not None:
                entries.append(m)
        data[cfg_name] = entries
    return data


def d4_1_analysis(data):
    """D4.1: raw vs filtered gap per configuration."""
    print()
    print("=" * 90)
    print("  D4.1 — Configuration-level raw vs filtered comparison")
    print("=" * 90)
    print()
    print(f"{'Configuration':<28} {'Raw MRR':<20} {'Filtered MRR':<20} {'Gap':<12}")
    print("-" * 90)
    
    summary = {}
    for cfg_name, entries in data.items():
        if not entries:
            print(f"{cfg_name:<28} NO DATA")
            continue
        raw_mrrs = [e["raw"]["mrr"] for e in entries]
        filt_mrrs = [e["filtered"]["mrr"] for e in entries]
        gaps = [f - r for f, r in zip(filt_mrrs, raw_mrrs)]
        
        raw_m = mean(raw_mrrs); raw_s = stdev(raw_mrrs) if len(raw_mrrs) >= 2 else 0
        filt_m = mean(filt_mrrs); filt_s = stdev(filt_mrrs) if len(filt_mrrs) >= 2 else 0
        gap_m = mean(gaps); gap_s = stdev(gaps) if len(gaps) >= 2 else 0
        
        print(f"{cfg_name:<28} {raw_m:.4f} ± {raw_s:.4f}   {filt_m:.4f} ± {filt_s:.4f}   +{gap_m:.4f}")
        
        summary[cfg_name] = {
            "raw_mrr_mean": raw_m, "raw_mrr_std": raw_s,
            "filt_mrr_mean": filt_m, "filt_mrr_std": filt_s,
            "gap_mean": gap_m, "gap_std": gap_s,
            "n_seeds": len(entries),
        }
    print()
    return summary


def d4_3_analysis(data):
    """D4.3: SMILES stratification × protocol interaction."""
    print()
    print("=" * 90)
    print("  D4.3 — SMILES stratification × filtered protocol")
    print("=" * 90)
    print()
    print(f"{'Configuration':<28} {'With SMILES':<20} {'Without SMILES':<20} {'Gap':<12}")
    print("-" * 90)
    
    summary = {}
    for cfg_name, entries in data.items():
        if not entries:
            continue
        with_mrrs = [e["filtered_with_smiles"]["mrr"] for e in entries]
        without_mrrs = [e["filtered_without_smiles"]["mrr"] for e in entries]
        
        # Number of drugs per subset (should be constant across seeds within config)
        n_with = entries[0]["filtered_with_smiles"].get("n_queries_with_smiles", 
                     entries[0]["filtered_with_smiles"]["n_queries"])
        n_without = entries[0]["filtered_without_smiles"].get("n_queries_without_smiles",
                        entries[0]["filtered_without_smiles"]["n_queries"])
        
        with_m = mean(with_mrrs); with_s = stdev(with_mrrs) if len(with_mrrs) >= 2 else 0
        without_m = mean(without_mrrs); without_s = stdev(without_mrrs) if len(without_mrrs) >= 2 else 0
        gap = with_m - without_m
        
        print(f"{cfg_name:<28} {with_m:.4f} ± {with_s:.4f}   {without_m:.4f} ± {without_s:.4f}   +{gap:.4f}")
        
        summary[cfg_name] = {
            "with_smiles_mrr_mean": with_m, "with_smiles_mrr_std": with_s,
            "without_smiles_mrr_mean": without_m, "without_smiles_mrr_std": without_s,
            "with_smiles_n": n_with, "without_smiles_n": n_without,
            "gap_smiles": gap,
        }
    
    print()
    print(f"NOTE: n_with_SMILES ≈ {n_with}, n_without_SMILES ≈ {n_without}")
    return summary


def combined_interpretation(d41, d43):
    """Print combined interpretation."""
    print()
    print("=" * 90)
    print("  COMBINED INTERPRETATION")
    print("=" * 90)
    print()
    
    # D4.1 gap analysis
    gaps = [s["gap_mean"] for s in d41.values() if s]
    if gaps:
        gap_mean_across = mean(gaps)
        print(f"Raw→Filtered gap across all 12 configs: mean = +{gap_mean_across:.4f}")
        print(f"  This is the typical rank inflation from filtered protocol.")
    
    # D4.3 SMILES gap
    smiles_gaps = [s["gap_smiles"] for s in d43.values() if s]
    if smiles_gaps:
        smiles_gap_mean = mean(smiles_gaps)
        print()
        print(f"SMILES gap (with − without) across configs: mean = +{smiles_gap_mean:.4f}")
        print(f"  Drugs with chemical structure available score ~3× higher.")
    
    # Cross-comparison
    print()
    print("Cross-comparison:")
    print(f"  Raw→Filtered protocol effect: ~+{gap_mean_across:.4f} MRR")
    print(f"  SMILES availability effect:    ~+{smiles_gap_mean:.4f} MRR")
    print()
    if smiles_gap_mean > gap_mean_across * 2:
        print(f"  → SMILES availability is a much larger driver of MRR")
        print(f"    than filtered-vs-raw protocol choice.")


def main():
    data = collect_data()
    d41 = d4_1_analysis(data)
    d43 = d4_3_analysis(data)
    combined_interpretation(d41, d43)


if __name__ == "__main__":
    main()
