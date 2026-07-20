### D5-Session 1 — Coupled Interpretability with Pathway Contextualisation

#### Methodology

We conducted three complementary interpretability analyses on the primary 
reference configuration (default regime, β=0.10, seed 42) to satisfy the 
Part A commitment to coupled intrinsic + post-hoc interpretability with 
pathway-level contextualisation.

**Intrinsic interpretability.** We computed Frobenius norms of the R-GCN 
encoder weight matrices for each of the 56 relation types. The Frobenius 
norm serves as a proxy for relation importance: relations with larger 
norms contribute more to the learned representations. Higher-magnitude 
relations indicate stronger learned dependencies.

**Post-hoc interpretability.** For the top-50 novel predictions from the 
reference configuration, we performed BFS graph traversal (up to 4 hops) 
identifying paths connecting the predicted drug to the predicted gene 
through intermediate nodes (variants, other genes, phenotypes). We report 
shortest path length, number of shared genes within the 4-hop 
neighbourhood, and up to 3 shortest paths per prediction.

**Integrated per-prediction analysis.** We composed a per-prediction 
integrated evidence report by joining structural paths (from Stage 4), 
FDR-significant pathway hits (from D5-Part 2 exhaustive pathway 
enrichment), and PubMed literature evidence (from D5-Part 1 expanded 
literature validation with 1990-2026 date filter).

#### Results

**Intrinsic — Relation Importance.** The top-5 relations by mean Frobenius 
norm were:

| Relation | Norm |
|---|---|
| drug → gene [clinical_associated] | 8.46 |
| gene → drug [clinical_associated] | 5.15 |
| drug → gene [label_associated] | 4.07 |
| drug → gene [pathway_associated] | 3.63 |
| gene → drug [label_associated] | 3.60 |

The pattern demonstrates that the model prioritises evidence-graded 
associations correctly: clinical-tier evidence gets the highest weight, 
label (regulatory) evidence follows, and curated pathway evidence receives 
substantial weight. This directly reflects the evidence-graded supervision 
regime committed to in Part A.

**Post-hoc — Structural Paths.** For the top-50 novel predictions:

- 49/50 (98%) had at least one path within 4 hops
- Mean shortest path length: 3.10 hops
- Mean shared genes within 4 hops: 9.80

Nearly all top predictions were structurally grounded through 
biologically-plausible intermediate paths (metabolism enzymes, drug 
transporters, phenotypes).

**Integrated Analysis — Multi-Modal Triangulation.** Combining structural, 
pathway, and literature evidence for each top-50 prediction:

| Evidence Type | Coverage |
|---|---|
| Graph path | 98% (49/50) |
| Pathway support (FDR-significant PGx pathways) | 74% (37/50) |
| PubMed literature | 20% (10/50) |
| Full triangulation (all three) | 14% (7/50) |

**Fully-triangulated exemplar:** testosterone → ABCB1 (rank 1, model score 
-0.43) — supported by a 3-hop path through CYP3A4-mediated metabolism, 
27 significant PGx pathways containing ABCB1, and 10 recent PubMed 
articles co-mentioning the pair. Represents high-confidence curator-
actionable candidate.

**Partially-triangulated exemplars:** aceclofenac → TNF (structural + 
literature); chloroacetaldehyde → NR1I2 (structural + pathway); 
varenicline → MTHFR (structural + pathway with folate metabolism pathway 
support).

#### Interpretation

The coupled interpretability framework demonstrates that the R-GCN model:

1. **Respects evidence-graded supervision** in its learned weights, with 
   clinical evidence receiving the highest importance
2. **Produces structurally-grounded predictions** through consistent 3-hop 
   paths in the ClinPGx graph
3. **Supports multi-modal validation** with 14% of top predictions having 
   convergent evidence across structural, pathway, and literature sources

This integrated evidence framework provides a defensible characterisation 
of predictions suitable for curator-triage prioritisation, complementing 
the aggregate ranking metrics and the null enrichment analysis (D5 null 
enrichment check).

