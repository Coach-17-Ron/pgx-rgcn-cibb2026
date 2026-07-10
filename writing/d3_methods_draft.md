### D3 — Phenotype-Relevant Gene Ranking

#### Methodology

To assess whether the model prioritises biologically-relevant genes at the 
top of its cold-drug predictions, we evaluated ranking performance on the 
subset of genes with at least one direct gene→phenotype edge in ClinPGx 
(n = 1,131 genes, of 25,041 total). This subset represents genes for 
which downstream phenotype relevance is documented in the curated 
knowledge base.

For each held-out test drug, we scored all phenotype-relevant genes using 
the trained R-GCN model with the actual relation index of the ground-
truth test edge (per-edge scoring, following the CIBB Stage 3 protocol). 
We report both raw and filtered MRR/Hits@K on this subset.

We compared against two naive baselines that rank the same subset:
- **Drug-gene degree baseline:** genes ranked by their global in-degree 
  from drugs
- **Gene-phenotype degree baseline:** genes ranked by their outgoing 
  degree to phenotypes

The comparison against the gene-phenotype degree baseline is the more 
demanding test: if the model provides no additional signal over how well-
connected a gene is to phenotypes, this baseline should match model 
performance.

Multi-seed evaluation was conducted across all 12 configurations from D1 
(3 regimes × 3 seeds) and D2 (β=0 × 3 seeds). No retraining was needed; 
existing checkpoints were scored with the new evaluation function.

#### Results

Filtered MRR values (mean ± SD across 3 seeds per configuration):

| Configuration | Model | DG Baseline | GP Baseline |
|---|---|---|---|
| default β=0.10 | 0.101 ± 0.020 | 0.119 | 0.100 |
| ambig_as_pos β=0.10 | 0.099 ± 0.007 | 0.119 | 0.100 |
| nonassoc_excluded β=0.10 | 0.099 ± 0.012 | 0.119 | 0.100 |
| default β=0.00 | 0.093 ± 0.017 | 0.119 | 0.100 |

Across all 12 configurations, the model performed 0.02 filtered MRR below 
the drug-gene degree baseline and matched the gene-phenotype degree 
baseline. Regime and hub-penalty variations did not measurably shift 
model performance on this evaluation slice (range: 0.093-0.101, well 
within intra-config seed variance of 0.010-0.020).

#### Interpretation

The finding extends the D1/D2 pattern to a phenotype-focused evaluation 
slice: the R-GCN model performs at approximately baseline level and 
provides no additional signal for phenotype-connected genes beyond what 
naive frequency-based baselines achieve. This suggests that ranking 
performance improvements for cold-drug pharmacogenomic prediction on 
ClinPGx will require more substantial methodological changes — such as 
feature enrichment, alternative encoders, or richer graph structure — 
rather than refinements to label handling, hub penalties, or evaluation 
subsetting alone.

Since the phenotype-relevance filter reduces the ranking pool from 25,041 
to 1,131 genes, aggregate MRR values are naturally higher on this subset. 
The subset-level model MRR (~0.10) is comparable to what the model 
achieves on all-genes (D1: ~0.10) once the ranking is restricted to this 
biologically-informed subset; this suggests the model does not benefit 
from an easier evaluation setting, further indicating that the 
performance ceiling lies in the model architecture and training data 
rather than in the evaluation protocol.

