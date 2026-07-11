### D4 — Raw AND Filtered Ranking Analysis

#### Methodology

D4 is an analytical study using existing evaluation metrics from all 12 
D1/D2 configurations. No new experiments were conducted. Two sub-analyses 
address different aspects of the ranking evaluation protocol:

- **D4.1** — Comparison of raw vs filtered MRR/Hits@K per configuration, 
  quantifying the rank inflation introduced by the filtered protocol
  (which excludes each drug's other known positives from the ranking pool)
- **D4.3** — Stratified analysis of the filtered protocol for drugs with 
  vs without chemical structure (SMILES) available

D4.2 (per-drug protocol sensitivity binning) was deferred; the existing 
runs do not save per-drug rank arrays. Adding this analysis would require 
lightweight re-scoring analogous to the D3 evaluation.

#### Results

**D4.1 — Filtered protocol effect (Table X):**

Across all 12 configurations, the filtered protocol systematically 
inflated MRR by ~0.012 relative to raw evaluation. Filtered MRR was 
0.084 ± 0.014 (mean ± SD across configs); raw MRR was 0.073 ± 0.013. 
The gap was consistent across regimes (0.010-0.015).

**D4.3 — SMILES stratification (Table Y):**

Filtered MRR for drugs with SMILES was 0.105 ± 0.019 (across configs); 
for drugs without SMILES, 0.040 ± 0.008. The gap between SMILES-available 
and SMILES-unavailable drugs (~0.065 MRR) was 5.5× larger than the raw-
vs-filtered protocol effect (~0.012 MRR).

#### Interpretation

D4 identifies chemical structure availability as the single strongest 
driver of cold-drug ranking performance on ClinPGx. Across all 12 tested 
configurations and multi-seed evaluation:

- Drugs with SMILES available consistently score ~0.10 filtered MRR
- Drugs without SMILES available consistently score ~0.04 filtered MRR

This gap is:
- 5.5× larger than the raw/filtered protocol effect (D4.1)
- Far larger than any effect of supervision regime (D1)
- Far larger than any effect of hub penalty (D2)
- Persistent when evaluation is restricted to phenotype-relevant genes (D3)

Cold-drug PGx prediction improvements will therefore come from expanding 
chemical structure coverage or developing structure-free representations 
for uncharacterised drugs, rather than from refining label handling, loss 
architectures, or evaluation subsetting.

This is consistent with the finding of Turon et al. 2025, which used 
descriptor-rich features (Bioteque, ProtT5) to achieve substantially 
higher performance on related biomedical tasks. Our results demonstrate 
that at the ClinPGx cold-drug ranking baseline, chemical structure 
availability is a necessary condition for competitive performance.

