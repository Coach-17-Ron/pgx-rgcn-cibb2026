# Methodology and Expected Outcomes

*Draft text for Part B — Methods and Expected Outcomes sections.*
*Author: Kgabe Ronald Molepo (MLPKGA007), MSc Computational Health Informatics, UCT.*
*Supervisors: Hocine Bendou, Khuthala Mnika.*

---

## 3. Methodology

### 3.1 Data source and access

The Clinical Pharmacogenomics Knowledgebase (ClinPGx, formerly PharmGKB) was the primary source for all pharmacogenomic relationships used in this study [CITE PharmGKB]. Five tab-separated files were obtained from the ClinPGx download portal: `relationships.tsv`, `genes.tsv`, `chemicals.tsv`, `phenotypes.tsv`, and `variants.tsv`. The accompanying `pathways/` folder, containing 210 manually curated drug-pathway TSV files, was retrieved in the same release. [CONFIRM access date — January or March 2026.]

ClinPGx records each curated relationship between two biomedical entities with two complementary annotations: an **association label** taking one of four values — `associated`, `not_associated`, `ambiguous`, or `uncurated` — and an **evidence category** drawn from five tiers: `guideline` (CPIC/DPWG dosing guidelines), `label` (FDA-approved drug-label annotations), `clinical` (curated clinical-annotation studies), `literature` (primary research articles), and `pathway` (manually drawn drug-action mechanism diagrams). This four-state association plus five-tier evidence hierarchy is preserved throughout the pipeline so that downstream interpretation can distinguish curated positive evidence from curated negative evidence — a distinction that is collapsed in most binary link-prediction formulations.

### 3.2 Knowledge graph construction (Stage 1)

A heterogeneous, undirected, evidence-typed knowledge graph G = (V, E) was constructed from the ClinPGx tables. The node set V comprises four biological entity types: drugs (chemicals), genes, variants (haplotype and single-nucleotide entries), and clinical phenotypes. Each entity in the source TSVs that passed basic cleaning — non-null name, deduplication on `(node_type, node_name)` — was assigned a unique integer `node_index`.

The edge set E was constructed from the `relationships.tsv` file. Each row was retained if both endpoints resolved to nodes in V and both entity types were canonical. Edge typing departed from naive triple typing in one important respect: rather than encoding only the structural pair `(source_type, target_type)`, the relation identifier was composed from four signals:

> `relation_type = source_type + target_type + evidence + association`

This composition preserves evidence semantics in the relational structure itself. A `drug→gene_guideline_associated` edge is therefore a structurally different relation from a `drug→gene_guideline_not_associated` edge, allowing the relational graph convolutional encoder to assign distinct transformation weights to evidence-distinguished relations.

By deliberate ClinPGx convention, direct `drug→phenotype` edges are omitted: the curators encode phenotype outcomes via curated gene-phenotype and variant-phenotype edges, requiring multi-hop traversal through the gene/variant layer to recover drug-to-phenotype inference. This convention is preserved (Section 3.10).

The final graph artifacts — `nodes.parquet`, `edges.parquet`, and `graph_metadata.json` — are persisted per-run alongside the configuration snapshot. [REPLACE WITH ACTUAL NUMBERS FROM ILIFU RUN: total nodes ~38,956 with breakdown by type; total edges ~90,000; unique relation types ~88, based on the prior 26 May 2026 run.]

### 3.3 Cold-drug split (Stage 2)

The train/validation/test partition was performed over **drugs**, not edges. Drug identifiers were shuffled with a fixed seed and split 70 / 15 / 15 into train, validation, and test cohorts. Two split protocols are supported and compared:

**Main protocol — `dg_context`.** Every curated drug-gene edge incident to a validation-set drug was assigned to the validation partition; every drug-gene edge incident to a test-set drug was assigned to the test partition. Non-drug-gene context edges (gene-variant, gene-phenotype, variant-phenotype) involving the same drug-set membership were **retained in the training graph**. This is the standard cold-tail link-prediction protocol in the heterogeneous knowledge-graph literature, and is the configuration under which all primary results are reported.

**Sensitivity protocol — `strict_cold_drug`.** Every edge incident to a validation or test drug was moved to the corresponding split — the training graph contains zero edges touching any held-out drug. Because the model has no molecular drug descriptors, performance under this stricter protocol is bounded by the floor achievable from relational context alone and is reported as a sensitivity analysis rather than as a primary outcome.

A relation vocabulary was built from the training partition only. Validation and test edges referencing a relation type absent from training were excluded from evaluation rather than mapped to an "unknown" relation, preventing the test set from being scored against relation embeddings that have never been updated.

**Leakage audit.** A `split_leakage_audit.json` artifact is written per run, recording the number of validation and test drugs that still appear in the training edge set. Under `strict_cold_drug` this is expected to be zero; under `dg_context` it is intentionally non-zero (context edges retained), and the absolute count quantifies the size of the context bleed-through for transparency. This audit accompanies every run output.

### 3.4 Model architecture

The architecture is a two-layer Relational Graph Convolutional Network (R-GCN) [CITE Schlichtkrull et al. 2018] paired with a DistMult decoder [CITE Yang et al. 2014].

**Encoder.** Each R-GCN layer aggregates messages over all relation types simultaneously:

> h<sub>v</sub><sup>(l+1)</sup> = σ ( Σ<sub>r</sub> Σ<sub>u ∈ N<sub>r</sub>(v)</sub> (1 / c<sub>v,r</sub>) · W<sub>r</sub><sup>(l)</sup> · h<sub>u</sub><sup>(l)</sup> )

where N<sub>r</sub>(v) is the set of neighbours of node v connected via relation r, c<sub>v,r</sub> is a normalisation constant equal to the degree of v under relation r, W<sub>r</sub><sup>(l)</sup> is the layer-l relation-specific weight matrix, and σ is the ReLU activation. The relation-specific matrices W<sub>r</sub> are parameterised by basis decomposition with eight bases [CITE basis decomp paper], reducing the parameter count from O(R · d²) to O(R · B + B · d²) for R relations, d hidden dimensions, and B = 8 bases. Basis decomposition is essential for this graph because the 88 relation types include many low-frequency relations whose own W matrices would otherwise be undertrained.

Both encoder layers map into 64-dimensional embeddings. Dropout (p = 0.25) is applied between layers during training.

**Decoder.** DistMult scores a triple (head, relation, tail) as the trilinear dot product of the head embedding, a relation embedding, and the tail embedding:

> score(h, r, t) = ⟨ z<sub>h</sub>, r<sub>emb</sub>, z<sub>t</sub> ⟩ = Σ<sub>i</sub> z<sub>h,i</sub> · r<sub>emb,i</sub> · z<sub>t,i</sub>

DistMult was chosen over more expressive decoders (RotatE, ComplEx) on parsimony grounds — the graph is relatively small and the additional parameters of complex-valued or rotational decoders provide negligible benefit at this scale while reducing interpretability.

### 3.5 Training objective with hub penalty

A pairwise margin-ranking loss was used for the supervised objective. For each curated positive drug-gene edge (h, r, t), eight negative tail genes t<sup>−</sup> were sampled and the loss is:

> L<sub>rank</sub> = max(0, margin − score(h, r, t) + score(h, r, t<sup>−</sup>))

with `margin = 1.0`. The negative tail sampler draws from genes with probability proportional to degree<sup>0.75</sup> (the standard smoothed-frequency scheme [CITE word2vec]) and explicitly **excludes** all curated positive drug-gene pairs across train, validation, and test sets, preventing a known positive from being sampled as a negative for a different drug.

**Hub penalty.** A small auxiliary loss term penalises the model for defaulting to high-degree genes (predominantly the CYP family in pharmacogenomics):

> L<sub>hub</sub> = E<sub>t<sup>−</sup></sub> [ σ(score(h, r, t<sup>−</sup>)) · w(t<sup>−</sup>) ]

where w(t<sup>−</sup>) is the sampling weight of gene t<sup>−</sup> normalised to [0, 1]. The total training loss is:

> L = L<sub>rank</sub> + β · L<sub>hub</sub>

with β = 0.005. β was selected on the validation MRR over the set {0, 0.001, 0.005, 0.01, 0.05} in preliminary work and held fixed for the main run. A β = 0 ablation run will quantify the contribution of the hub penalty in isolation.

### 3.6 Optimisation

Optimisation was performed with Adam (learning rate 3 × 10<sup>−3</sup>, weight decay 1 × 10<sup>−4</sup>) for up to 100 epochs at batch size 512. Gradients were clipped at a global ℓ<sub>2</sub> norm of 2.0 to mitigate the rare exploding-gradient spikes occasionally seen with the hub penalty.

Early stopping was triggered by validation Mean Reciprocal Rank rather than training loss. Validation MRR was computed every five epochs on the held-out validation drugs; the best-MRR model weights were checkpointed and restored at termination. Patience was set to 10 (consecutive non-improving validation steps), with a minimum-delta threshold of 1 × 10<sup>−4</sup>.

### 3.7 Cold-drug evaluation (Stage 3)

The primary evaluation metrics are Mean Reciprocal Rank and Hits@K on cold-drug test positive drug-gene edges, reported under both **raw** and **filtered** protocols.

For each positive triple (h, r, t) in the test partition, the trained model encoder is run once over the training graph, the drug head embedding is scored against every gene embedding (n ≈ 25 000), and the rank of the curated tail t among all genes is recorded. Hits@K for K ∈ {1, 3, 5, 10} are reported alongside MRR.

**Raw ranks** use the unmodified score distribution. **Filtered ranks** apply the standard filtering protocol introduced by Bordes et al. [CITE Bordes et al. 2013]: when computing the rank of a target tail t for a given head h, all other known positive tails t' ≠ t for the same head are masked to −∞ in the score vector before ranking. Without filtering, a model that correctly ranks multiple known positives at the top is penalised at each evaluation because the other positives inflate the ranks of one another. Both raw and filtered MRR are reported; the filtered values are taken as the headline results in keeping with current convention in the knowledge-graph completion literature.

95% confidence intervals on both metrics are obtained by 1 000-sample bootstrap resampling of the rank list, with a fixed bootstrap seed for reproducibility.

A **degree-frequency baseline** provides a floor: genes are ranked purely by their training-set degree, most-connected first. This baseline captures the "always predict the most-connected gene" strategy and is the appropriate comparator for a hub-penalty method.

**Hub-bias analysis.** The dominance of the CYP family in top-1 predictions is computed as the fraction of test drugs whose top-1 predicted gene belongs to the CYP gene family. Comparison against the degree baseline quantifies the reduction in hub bias.

**Candidate vs rediscovered predictions.** For each test drug the top-25 highest-scoring genes are recorded and labelled by curation status as one of `rediscovered_positive`, `rediscovered_negative`, `rediscovered_ambiguous`, or `candidate_novel`. Only the `candidate_novel` set — pairs with no curated drug-gene edge of any kind in the source data — is propagated to downstream literature, pathway, and phenotype contextualisation. The rediscovered subset is retained for transparency but is reported as a separate artifact (`rediscovered_predictions.parquet`) and does not contribute to the novel-hypothesis tables.

### 3.8 Ambiguous-pair prioritisation for re-curation

A separate analysis targets the `ambiguous` association label, which in ClinPGx denotes pairs with conflicting or insufficient evidence to commit to either `associated` or `not_associated`. For every ambiguous drug-gene edge across all three splits, the model's rank of the curated gene was computed and converted into a percentile (rank divided by total candidate genes). Each pair was assigned a suggested curator action from five graded outcomes:

| Rank percentile | Suggested action |
| --- | --- |
| ≤ 5% | upgrade_to_associated |
| ≤ 20% | lean_associated |
| 20–80% | remains_ambiguous |
| ≥ 80% | lean_not_associated |
| ≥ 95% | downgrade_to_not_associated |

The output artifact `ambiguous_priorities.csv` records, per pair: drug and gene names, split membership, model rank and percentile, priority score (1 / rank), the suggested action, and the top five alternative genes the model would have ranked above the curated tail (excluding any gene already curated as a positive for that drug). The artifact is sorted by descending priority score so the highest-confidence upgrade candidates appear first. This artifact is intended as input to a downstream manual re-curation workflow rather than as a publication output in its own right.

### 3.9 Three-level interpretation (Stage 4)

Three complementary interpretation views are produced, each addressing a different audit need.

**Intrinsic — global.** The Frobenius norm of each relation-specific weight matrix W<sub>r</sub> is computed per encoder layer. For the basis-decomposed encoder W<sub>r</sub> is reconstructed as Σ<sub>b</sub> comp<sub>r,b</sub> · basis<sub>b</sub> before taking the norm. The mean Frobenius norm across the two encoder layers ranks relation types by their cumulative encoder weight magnitude, providing a global summary of which evidence-distinguished relation types the trained model leans on most.

A technical detail worth recording: PyTorch Geometric's homogeneous conversion assigns relation-index identifiers in iteration order over the heterogeneous `data.edge_types` tuple, which does not in general match the alphabetical decoder relation index used by DistMult. To prevent biological mislabelling of the relation-importance figure, the pipeline persists the PyG-specific edge-type mapping (`pyg_edge_type_mapping.json`) at the end of Stage 2 and uses it — rather than the decoder mapping — when annotating Frobenius-norm results in Stage 4.

**Post-hoc — per-prediction.** Each top-50 prediction in `candidate_predictions.parquet` is explained by extracting structured evidence from the curated graph. For the (drug, gene) pair, the explainer computes: all shortest paths between drug and gene up to a configurable maximum count, the relation-type composition along each path, the shared k-hop neighbours of the drug and gene partitioned by node type (genes, variants, phenotypes), and the bridge-node ranking by combined drug-distance plus gene-distance plus inverse node degree. These structured explanations are written to `explanations.parquet`. Because every edge in every reported path is a real curated edge with a recorded evidence tier, the explanations are auditable: a domain expert can inspect the path and ask, of each intermediate node, whether the connecting biology is credible.

This path-based explanation paradigm was chosen over gradient-based interpretation (GNNExplainer, integrated gradients) because the resulting artifacts contain biomedical entities and curated relation types rather than gradients of an opaque scoring function. For a clinician auditing a pharmacogenomic prediction, "Warfarin → CYP2C9 (drug-gene-guideline edge) → VKORC1 (gene-gene-clinical edge)" is interpretable in a way that an attribution heatmap is not.

**Integrated — joined.** The third level fuses all available evidence into one row per top-50 prediction (Section 3.10).

### 3.10 Real-evidence contextualisation (Stage 5)

#### 3.10.1 PubMed literature evidence

Literature evidence is obtained from the National Center for Biotechnology Information (NCBI) E-utilities API via the canonical three-call chain: ESearch retrieves PubMed identifiers matching a drug-gene co-occurrence query, ESummary retrieves bibliographic metadata (title, journal, year, authors, DOI), and EFetch retrieves the verbatim abstract XML. Queries are restricted to the publication date range 2020–2026 using the PDAT field. The `tool` and `email` parameters required by NCBI's terms of service are populated from configuration. Inter-request delay is 0.34 seconds (under the unauthenticated three-requests-per-second limit). Up to ten articles are retrieved per drug-gene pair, for up to 50 top predictions per run, yielding a literature evidence dataframe of one row per (drug, gene, article) triple with PMID, full citation metadata, and the unmodified abstract text.

A critical methodological commitment is that no large-language-model generation appears anywhere in the literature pipeline. Citations are retrieved verbatim from PubMed; abstract sentences in the integrated output are exact substrings of the EFetch response, not paraphrases. Every PMID in the output is verifiable via its PubMed URL. This non-hallucination guarantee is a deliberate design choice in the context of a clinically-adjacent application.

#### 3.10.2 Multi-source pathway over-representation

Pathway enrichment is computed against three independent gene-set sources in parallel:

- **PharmGKB pharmacology pathways** (n ≈ 210, mean ≈ 15 genes per pathway). These are manually curated mechanism diagrams for individual drugs and drug classes — the source most directly aligned with the prediction task.
- **Reactome reaction networks** (n ≈ 2 600, mean ≈ 60 genes per pathway). These provide granular reaction-level biology orthogonal to the drug-specific perspective.
- **KEGG canonical pathways** (n ≈ 330, mean ≈ 80 genes per pathway), from the MSigDB curated collection. These provide broad cellular-process biology.

The hit list for enrichment testing is the union of the top-50 predicted genes across all test drugs (a maximum of 50 unique gene symbols per run). The background universe is fixed at 19 969 protein-coding genes (GENCODE v44 [CITE GENCODE]). For each gene set in each source, a one-sided hypergeometric tail probability is computed:

> p = P(X ≥ k | N, K, n) = Σ<sub>i=k</sub><sup>min(n,K)</sup> (K choose i) (N − K choose n − i) / (N choose n)

implemented as `scipy.stats.hypergeom.sf(k − 1, N, K, n)`, where N is the universe size, K is the gene set size (clipped to N), n is the hit list size, and k is the observed intersection.

**Benjamini–Hochberg false discovery rate** correction is applied **independently per source**. Mixing the three sources under a single global BH correction would mis-estimate the false-discovery rate because the three sources have very different prior probabilities of enrichment, very different average set sizes, and consequently very different statistical power; an effective BH on the combined list would either over-penalise the larger source or fail to detect true signal in the smaller one. The per-source correction is the appropriate procedure when the goal is to support distinct claims grounded in distinct sources of evidence.

The significance threshold is q < 0.05 within each source. Gene sets are reported in `pathway_enrichment.parquet` with an additional `source` column (`PGKB`, `REACTOME`, `KEGG`, or `OTHER`) so downstream summaries and figures can be stratified by source.

#### 3.10.3 Integrated explanation table

For each of the top 50 predictions by integrated score, a single row in `integrated_explanations.csv` joins: the model rank and raw DistMult score; the hub-adjusted (1 / rank, normalised) score; the literature signal (log1p of the article count); the pathway signal (binary indicator of membership in any significant pathway); the integrated composite score; the shortest curated graph path with relation types; the curated bridge-node summary from Stage 4; the verbatim citation block for every retrieved PubMed article; and the first sentence of each abstract (sliced verbatim, no generation). The integrated score is a fixed-weight composite:

> score<sub>integrated</sub> = 0.40 · hub_adjusted + 0.30 · literature + 0.30 · pathway

Each component is rescaled to [0, 1] before weighting. The weights reflect a deliberate methodological position: prediction rank (the model output) is given a plurality of weight; literature and pathway evidence each receive equal additional weight; no single signal can dominate. The composite is intended as a tool for ranked exploration, not as a single fitness measure.

### 3.11 Phenotype propagation (Stage 6)

To operationalise the abstract objective of inferring phenotype outcomes from drug-gene predictions, the pipeline propagates each top-K prediction through the curated gene-phenotype sub-graph along two route classes:

- **1-hop route:** drug → predicted gene → curated phenotype (direct gene-phenotype edge).
- **2-hop route:** drug → predicted gene → curated variant → curated phenotype (variant-mediated, capturing haplotype-driven phenotypes).

Only the drug-gene step is learnt; everything downstream is graph traversal through curated edges. This design avoids the failure mode of end-to-end learnt drug-phenotype prediction — which would require either training labels that do not exist in ClinPGx (which omits drug-phenotype edges by curation policy) or generating them, with the attendant hallucination risk.

Every triple in the output `phenotype_inferences.csv` is tagged with the evidence tier of the gene-phenotype edge, the association polarity (`associated` / `not_associated` / `ambiguous`), the propagation distance (1 or 2 hops), the originating drug-gene integrated score, and a Boolean `is_negative_evidence` flag set true when the gene-phenotype association is curated as `not_associated`. Negative curated evidence is never silently discarded: a `not_associated` gene-phenotype edge is surfaced in the output as negative evidence so that a clinician auditing the propagated phenotype list sees both supportive and counter-indicating annotations.

The deliberate choice of `is_negative_evidence` rather than `is_contraindication` is worth flagging: a ClinPGx `not_associated` annotation indicates that curated evidence does not support an association in either direction — this is a weaker and more accurate claim than "contraindication," which has specific clinical meaning. The output preserves the curator's epistemic commitment without strengthening it.

### 3.12 Reproducibility, code availability, and computational resources

All pipeline stages run from a single configuration dictionary that is snapshotted into each per-run artifact directory as `run_config.json`. The complete pipeline is implemented in Python 3 and is openly available [CITATION: GitHub URL to be added on submission]. Key dependencies are pinned to specific versions in `requirements.txt`: `torch 2.1.2`, `torch-geometric 2.5.0`, `networkx 3.2.1`.

The random seed is fixed across `random`, `numpy`, and `torch` (and deterministic cuDNN settings enabled where available). Each per-seed run is auto-tagged with a `RUN_ID` of the form `<timestamp>_<split_mode>_<beta_tag>_<seed_tag>` so that ablation runs and multi-seed sweeps land in independent output folders.

Three model variants were trained and compared:

- **Degree-frequency baseline** — no neural model; gene predictions ranked by training-set degree.
- **R-GCN with β = 0** — hub-penalty ablation; identical architecture but without the hub-penalty term.
- **R-GCN with β = 0.005** — main model.

All three variants were run under both the `dg_context` (main) and `strict_cold_drug` (sensitivity) split protocols. Each R-GCN variant was additionally run with three random seeds (42, 123, 2026), yielding seed-level variance estimates on every reported metric.

The main runs were executed on the ilifu HPC facility [CITE ilifu] on the `Main` (CPU) partition, with [INSERT: wall time per run, peak memory] per variant.

---

## 4. Expected outcomes

The following outcomes are anticipated based on theoretical considerations and on the 26 May 2026 preliminary run. They are stated as **honestly framed expectations**, distinguishing where prior evidence supports a confident projection from where the outcome is genuinely uncertain.

### 4.1 Ranking performance — confidently projected

The **filtered** Mean Reciprocal Rank on cold-drug test edges under `dg_context` is expected to fall in the range 0.05 to 0.10, with filtered Hits@10 between 0.10 and 0.18. The prior 26 May 2026 run reported MRR ≈ 0.062 and Hits@10 ≈ 0.118 — note that this prior figure was computed under the raw protocol (against the old code that mislabelled raw as filtered) and may shift modestly upward under the corrected filtered protocol. **Raw** MRR will be reported in parallel and is expected to be lower than the filtered values by 5–15 percentage points (in relative terms) because the filtered protocol removes the inflation introduced by known positives crowding the top of the candidate list.

These absolute values are modest in keeping with the difficulty of cold-drug zero-shot link prediction over a 25 000-gene candidate space, but the bootstrap 95% confidence intervals are expected to exclude the degree-frequency baseline at both MRR and Hits@10 — approximately a three-fold ratio between the R-GCN MRR and the baseline MRR, replicating the prior run.

Under the **`strict_cold_drug` sensitivity protocol** all metrics are expected to be substantially lower, possibly approaching the degree baseline. This is the methodologically honest outcome: a model without molecular drug descriptors cannot meaningfully generalise to drugs with no context whatsoever, and the strict protocol is reported precisely to surface this limit.

### 4.2 Hub-bias mitigation — confidently projected, with planned ablation

A pronounced reduction in CYP-family dominance among top-1 predictions is expected. The prior run reduced the average CYP fraction from approximately 6.00 (degree baseline) to 0.87 in the hub-penalised model — a ratio of approximately seven. A comparable order of magnitude is expected for the current run.

The β = 0 ablation run — identical architecture trained without the hub-penalty term — will isolate the hub-penalty contribution from the rest of the modelling pipeline. The expected outcome is that β = 0 sits between the degree baseline and the β = 0.005 main run on CYP fraction; if the ablation shows no measurable CYP reduction relative to the degree baseline, the hub penalty is the sole driver of the bias-mitigation effect. If β = 0 already shows partial CYP reduction (driven by negative sampling exclusion of curated positives), the hub-penalty contribution is incremental rather than the whole story — which would be a more nuanced and arguably more publishable finding.

Multi-seed runs (three seeds) will quantify the seed-to-seed variance of the CYP-fraction reduction; the per-seed standard deviation is expected to be small (≪ the gap between models) but reporting it is necessary for any claim about the hub-penalty effect to be statistically defensible.

### 4.3 PharmGKB pathway enrichment — uncertain, scientifically informative either way

This is the highest-information outcome to be obtained from the current run. The prior pipeline restricted pathway over-representation testing to MSigDB KEGG and Reactome gene sets and obtained null results (all q ≥ 0.58). The current pipeline adds PharmGKB pharmacology pathways as a third source, with per-source FDR correction. Three outcomes are possible:

1. **PharmGKB enrichment is significant** (at least one PharmGKB pathway with q < 0.05). This is the most informative outcome. Significant enrichment in curated drug-mechanism pathways would constitute direct evidence that the model recovers known pharmacological structure, and would be reported as a primary finding.

2. **PharmGKB enrichment is null but Reactome / KEGG enrichment is significant.** This would suggest the model captures generic drug-metabolism biology (e.g., the xenobiotic and cytochrome P450 pathways) but does not recover drug-specific mechanism granularity.

3. **All three sources null.** This would be a substantive negative finding, suggesting the model's top predictions are dispersed across the gene space without preferential clustering in any curated set. In this case the dissertation would honestly report the null result and discuss possible explanations (sparse predictions over a heterogeneous gene set; broader prediction coverage required; insufficient signal at top-50 hit-list size).

Each of the three outcomes leads to a defensible methodological conclusion. The methodology does not depend on obtaining significant enrichment; the validity of the pipeline is not contingent on the sign of the result.

### 4.4 Literature support — confidently projected

The majority of the top-50 predictions are expected to be supported by at least one PubMed article from 2020–2026 referencing both the drug and the predicted gene. The exact fraction depends on the curation status of the predicted pairs, but a literature-support rate above 50% would constitute prima facie evidence that the model's top predictions are not arbitrary. A literature-support rate below 25% would warrant scrutiny of the prediction set for spurious associations.

Every cited article will be verifiable by PMID — this is a structural property of the pipeline rather than a hoped-for outcome, but is noted here because non-hallucination is a methodological commitment of the work.

### 4.5 Ambiguous-pair re-curation candidates — confidently projected

Of the curated `ambiguous` drug-gene edges (approximately 500 in ClinPGx at the time of access), the pipeline is expected to flag between 30 and 100 for the curator-action label `upgrade_to_associated` (rank in the top 5% of all genes for the drug) and a smaller number for `downgrade_to_not_associated` (rank in the bottom 5%). The exact counts depend on the empirical rank-percentile distribution of ambiguous pairs, which will be obtained from the run. The output `ambiguous_priorities.csv` is intended as a deliverable to ClinPGx curators rather than as an end-product of the dissertation per se. Its production is expected to be a tangible secondary contribution.

### 4.6 Phenotype propagation — confidently projected

Each of the top-50 drug-gene predictions is expected to propagate to between zero and twenty phenotype inferences, with a mean in the range of five to ten. A non-trivial fraction is expected to be flagged as `is_negative_evidence` because the underlying gene-phenotype edge has `association = not_associated` in ClinPGx — preserving negative curated evidence in the output is a deliberate design choice and the fraction of negative-evidence inferences will be reported transparently.

### 4.7 Limitations to be acknowledged in the discussion

The following limitations will be explicitly acknowledged when results are reported:

1. **Three seeds is a small variance estimator.** Five or more seeds would give tighter standard errors; three is the minimum sufficient for a defensible variance claim and is what the HPC budget supported for the current report.
2. **No molecular drug descriptors.** Drug nodes are represented only by random Xavier initial features updated through message passing over relational context. Under `strict_cold_drug` this is fundamentally insufficient to generalise to truly unseen drugs, and the protocol is reported precisely to expose this limit. Incorporating molecular descriptors (e.g., Morgan fingerprints, learned chemical embeddings) is a natural extension and is identified as future work.
3. **Modest absolute ranking performance.** Filtered Hits@10 of approximately 0.12 is meaningful relative to the degree baseline but absolute performance is bounded by the sparsity of curated positives over the 25 000-gene candidate space.
4. **Pathway enrichment power.** The top-50 hit list is small; smaller true effect sizes may not reach significance even after multi-source testing.
5. **Cold-drug evaluation is one of several possible held-out protocols.** Cold-gene or cold-relation splits would yield different difficulty regimes and are out of scope for this report.
6. **Literature query date range and rate limits.** PubMed queries are restricted to 2020–2026 and rate-limited; older or rarer pairs may have less retrievable evidence than truly exists.
7. **Phenotype propagation depth.** The pipeline traverses up to two hops (gene → variant → phenotype). Longer chains are biologically interpretable but not currently emitted.
8. **Validation depends on curated ClinPGx evidence.** The pipeline cannot validate predictions for which no curated evidence exists; novel hypotheses for previously uncurated pairs remain hypotheses, not confirmed associations.

These limitations bound the claims that can be made from the results. They do not undermine the methodology itself, which is designed to be honest about the strength of each evidence type, to compare against an appropriate baseline, to ablate the headline architectural choice, and to surface negative evidence rather than discard it.

---

*[End of section. Word count: approximately 3 800 words excluding code references and citation placeholders. Estimated dissertation pages at Arial 12 pt, double-spaced: ~14 pages.]*
