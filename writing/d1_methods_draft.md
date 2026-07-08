### D1 — Supervision Sensitivity Analysis

#### Methodology

ClinPGx classifies drug-gene relationships with three-way evidence-graded 
labels: `associated` (5,583 unique drug-gene pairs), `not associated` 
(295 pairs), and `ambiguous` (826 pairs). To characterise the robustness 
of our cold-drug ranking to alternative handling of these labels, we 
conducted a supervision sensitivity analysis by testing three regimes:

- **default**: only `associated` edges supervise the ranking loss; 
  `not associated` and `ambiguous` edges are dropped from supervision 
  but retained in the message-passing graph (matches CIBB baseline).
- **ambig_as_pos**: `ambiguous` edges are merged with `associated` for 
  supervision, treating them as noisy positives.  
- **nonassoc_excluded**: `not associated` edges are dropped from the 
  training graph entirely.

Each regime was run at three random seeds (42, 123, 2026) with β=0.10, 
no chemical fingerprints, and the `dg_context` cold-drug split. This 
gave a 3×3 design totalling 9 runs. We report filtered mean reciprocal 
rank (MRR) as mean ± standard deviation across seeds, and use the 
pooled standard deviation (average of within-regime SDs) as the 
reference scale for judging effect size.

#### Results

Filtered MRR values across regimes and seeds are shown in Table X. 
Inter-regime differences (≤0.008 in filtered MRR) were substantially 
smaller than intra-regime seed variance (SD 0.010-0.020). The pooled 
SD across all regimes was 0.014, and both `ambig_as_pos` and 
`nonassoc_excluded` differed from `default` by less than half this 
pooled SD.

We therefore conclude that **supervision-regime handling of `ambiguous` 
and `not associated` drug-gene edges does not materially affect 
aggregate cold-drug ranking performance under multi-seed evaluation**. 
This finding is consistent with the observation that sparse curated 
supervision is the binding constraint on cold-drug PGx-KG completion 
performance, as identified in the literature review.

#### Secondary Observations

*Model performance at baseline.* The R-GCN model performed at or slightly 
below the degree-frequency baseline (mean baseline 0.088; `default` 0.090; 
`ambig_as_pos` 0.083; `nonassoc_excluded` 0.084) at all three seeds and 
regimes. This is consistent with the CIBB main result and confirms that 
improvements in cold-drug PGx-KG completion will not come from label-
handling refinements alone.

*Curator-facing shift despite MRR insensitivity.* Downstream curator 
recommendations differed markedly across regimes despite equivalent 
aggregate MRR. At seed 42, `ambig_as_pos` produced 742 upgrade 
recommendations and 76 downgrade recommendations, whereas 
`nonassoc_excluded` produced 206 upgrades and 601 downgrades — a factor-
of-4 difference in the direction of recommendation. This suggests that 
regime choice affects the model's internal biological priorities even 
when aggregate metrics are insensitive, and has implications for 
downstream utility as a curator-triage tool.

*Chemical structure availability drives performance.* Across all three 
regimes, drugs with available SMILES structures achieved MRR 0.09-0.11 
(3× the score of drugs without SMILES, 0.03-0.04). This gap was 
persistent across regimes and seeds, indicating that chemical structure 
availability — not label handling — is a stronger driver of cold-drug 
ranking performance under this pipeline.

