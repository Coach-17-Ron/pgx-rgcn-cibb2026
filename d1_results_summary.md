# D1 Supervision Sensitivity Analysis — Multi-seed Results

## Method
Three-way supervision regime tested at 3 seeds (42, 123, 2026):
- **default**: is_dg_positive edges only (CIBB baseline)
- **ambig_as_pos**: is_dg_positive OR is_dg_ambiguous edges as positives
- **nonassoc_excluded**: is_dg_negative edges dropped from training graph

All runs: β=0.10, no fingerprints, dg_context split, 100 epochs, CPU.

## Per-seed Filtered MRR

| Regime | seed=42 | seed=123 | seed=2026 |
|---|---|---|---|
| default | 0.0775 | 0.1132 | 0.0801 |
| ambig_as_pos | 0.0819 | 0.0955 | 0.0704 |
| nonassoc_excluded | 0.0823 | 0.0950 | 0.0750 |
| **baseline** | 0.0795 | 0.0983 | 0.0878 |

## Multi-seed Summary

| Regime | Filtered MRR (mean±SD) | Filtered H@10 |
|---|---|---|
| default | 0.0903 ± 0.0199 | 0.1490 |
| ambig_as_pos | 0.0826 ± 0.0126 | 0.1497 |
| nonassoc_excluded | 0.0841 ± 0.0101 | 0.1442 |
| baseline (mean) | 0.0885 | - |

## Statistical Interpretation
- Intra-regime SD: 0.010-0.020 across seeds
- Inter-regime differences: ≤0.008
- **Regime differences fall within noise; regimes are statistically indistinguishable.**

## Finding
Supervision-regime handling of ambiguous and not-associated ClinPGx drug-gene 
edges does not materially affect aggregate cold-drug ranking under multi-seed 
evaluation. The intra-regime seed variance is comparable to or larger than any 
inter-regime effect. This demonstrates that R-GCN cold-drug ranking on ClinPGx 
is robust to specific label-handling choices, and that improvements in the 
model must come from other methodological changes (feature enrichment, 
alternative sampling, or richer graph structure) rather than label-handling 
refinements alone.

## SMILES stratification (persistent across regimes)
For drugs with SMILES available: MRR consistently 0.09-0.11 (all runs).
For drugs without SMILES: MRR consistently 0.03-0.04 (all runs).
This 3x gap persists regardless of supervision regime — suggesting chemical 
structure availability is a bigger driver of model performance than label 
handling.

## Curator-facing output shift
Ambiguous edge curator-action distribution differs across regimes:
- default (seed 42): 628 upgrade / 181 downgrade
- ambig_as_pos (seed 42): 742 upgrade / 76 downgrade
- nonassoc_excluded (seed 42): 206 upgrade / 601 downgrade (very different!)

While aggregate MRR is stable, the model's inferred curator recommendations 
are meaningfully affected by regime choice. This is a secondary finding 
worth reporting.

## References
- Runs archived: results/20260708_*_dg_context_beta0p1_seed*_reg-*
- Multi-seed submission: submit_d1_multiseed.sh
- Multi-seed analysis: analyse_d1_multiseed.sh
- Job ID: 211206 (completed 08:05 SAST, 8 July 2026)
