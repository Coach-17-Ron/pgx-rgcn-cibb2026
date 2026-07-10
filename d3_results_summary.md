# D3 Phenotype-Relevant Gene Ranking — Multi-seed Results

## Method
For each held-out test drug in cold-drug evaluation, we rank all 1,131 
genes that have at least one gene→phenotype edge in ClinPGx (phenotype-
relevant subset). We compute filtered/raw MRR/Hits@K on this subset and 
compare against two baselines:
- **DG degree baseline:** rank phenotype-relevant genes by drug-gene degree
- **GP degree baseline:** rank phenotype-relevant genes by gene-phenotype degree

Evaluation uses each edge's actual relation index (per-edge scoring, 
mirroring CIBB Stage 3). No retraining; existing checkpoints scored.

## Configurations Tested (12 total)

Three supervision regimes at β=0.10 (from D1), plus one β=0 ablation 
(from D2), each at three seeds (42, 123, 2026).

## Multi-seed Filtered MRR Results

| Configuration | Model Filt MRR (mean ± SD) | DG Baseline | GP Baseline |
|---|---|---|---|
| default β=0.10 | 0.1013 ± 0.0203 | 0.1190 | 0.1003 |
| ambig_as_pos β=0.10 | 0.0988 ± 0.0074 | 0.1190 | 0.1003 |
| nonassoc_excluded β=0.10 | 0.0986 ± 0.0117 | 0.1190 | 0.1003 |
| default β=0.00 | 0.0931 ± 0.0165 | 0.1190 | 0.1003 |

## Per-seed Filtered MRR

### Default β=0.10
- seed=42: 0.0895
- seed=123: 0.1247
- seed=2026: 0.0896

### ambig_as_pos β=0.10
- seed=42: 0.0960
- seed=123: 0.1072
- seed=2026: 0.0933

### nonassoc_excluded β=0.10
- seed=42: 0.0996
- seed=123: 0.1097
- seed=2026: 0.0864

### Default β=0.00
- seed=42: 0.0952
- seed=123: 0.1083
- seed=2026: 0.0756

## Statistical Interpretation

**Model vs Drug-Gene degree baseline:** Model is 0.018 filtered MRR below 
baseline on average (across 12 configs). Difference is comparable to 
intra-config seed variance (~0.010-0.020 SD).

**Model vs Gene-Phenotype degree baseline:** Model matches baseline 
(+0.001 filtered MRR difference at reference config).

**Across-configuration variance:** Range of model means is 0.008 
(0.093-0.101). All configurations fall within one standard deviation 
of each other. Regime and β choices do not affect performance on this 
evaluation slice.

## Finding

The R-GCN model does not preferentially prioritise phenotype-connected 
genes for cold-drug ranking beyond what naive baselines achieve. On the 
phenotype-relevant subset:
- Model matches the gene-phenotype degree baseline
- Model slightly underperforms the drug-gene degree baseline

This is consistent with the D1/D2 pattern: model performance is 
approximately baseline-level across all evaluation slices tested. 
Supervision regime and hub-penalty variations do not enable superiority 
over naive frequency-based baselines.

## Reference to D1 and D2

D3 confirms and extends the D1/D2 pattern to a new evaluation slice 
(phenotype-relevant subset). The consistency across evaluation types 
(all-genes → phenotype-relevant genes) suggests that improvements in 
cold-drug PGx-KG completion must come from methodological changes 
beyond label handling, hub penalties, or evaluation subsetting.

## Data provenance

- 12 model checkpoints from D1 (9 runs) and D2 (3 runs)
- No retraining; existing checkpoints scored with new evaluation
- Total D3 compute: ~3 minutes for all 12 configs (job 216975)
- Analysis script: analyse_d3_multiseed.sh
- Result files: results/*/artifacts/d3_phenotype_metrics.json

