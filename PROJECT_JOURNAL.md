# MSc Project Journal — Kgabe Ronald Molepo (MLPKGA007)

## Project Title
Interpretable Graph Neural Networks for Learning Drug-Gene Relationships 
and Inferring Phenotype Outcomes in Pharmacogenomics

## Target Submission
Early December 2026 (intention to submit: ~20 October 2026)

## Weekly Time Commitment
30 hours/week confirmed

## Confirmed Status (as of July 5, 2026)
- CIBB 2026 camera-ready submitted
- Ethics: HREC 215/2026 approved 8 May 2026 (full review)
- Supervisors: Hocine Bendou, Khuthala Mnika
- Kick-off email sent — awaiting response for scheduling

## Discoveries from Code Audit (July 5-6, 2026)
Most Part-A commitments already implemented in the CIBB code:
- Degree-aware negative sampling with deg^0.75 smoothing (TransE-style, per Bordes 2013)
- Hub penalty with configurable β and --ablation_beta_zero flag
- Raw AND filtered MRR/Hits@K computed and saved (both in JSON per run)
- Bootstrap 95% CIs on all metrics
- Degree-frequency baseline
- Path-based post-hoc Explainer (shortest paths, shared k-hop neighbours)
- Intrinsic interpretability (Frobenius norms of W_r per relation)
- Reactome + KEGG loading via GMT files
- ORA with Benjamini-Hochberg FDR correction
- Three-way evidence-graded supervision (positive/not-associated/ambiguous)

## Five Part-A Deliverables Status

### D1: Evidence-graded supervision + sensitivity analysis
- Current: three-way handling done for CIBB defaults
- MSc addition: --supervision_regime flag + 4 ablation runs
- Target: Weeks 2-3 (July 14 - July 27)
- Effort: ~1 week (code + experiments)

### D2: Hub-penalty ablation + degree-aware sampling
- Sampling: DONE (line 1110, degree^0.75)
- β sweep: DONE for CIBB
- β=0 ablation: FLAG EXISTS, experiments NOT YET RUN
- MSc action: run --ablation_beta_zero at 3 seeds (42, 123, 2026)
- Target: Weeks 4-5 (July 28 - Aug 10)
- Effort: ~1 week

### D3: Phenotype-level evaluation
- Propagation: DONE (Stage 6)
- Drug→phenotype MRR/Hits@K: NOT YET COMPUTED
- MSc action: new evaluate_phenotype_ranking() function in Stage 6
- Target: Weeks 6-8 (Aug 11 - Aug 31)
- Effort: 2-3 weeks

### D4: Raw AND filtered ranking metrics
- Computation: DONE for all runs (raw and filtered in every test_metrics.json)
- MSc addition: reporting side-by-side in Part B tables
- Target: Weeks 12-15 (Oct, during writing)
- Effort: Half a day

### D5: Reactome/KEGG FDR enrichment
- Loading + ORA + BH: DONE
- MSc action: verify pathway_enrichment.parquet for each config, 
  aggregate results, interpret
- Target: Weeks 9-10 (Sep 8 - Sep 21)
- Effort: ~1 week

## Timeline

### Week 0 (Jun 27 - Jul 7): Setup ✅ COMPLETE
- CIBB submitted, MSc directory set up, audit complete, 
  supervisors aligned, HREC 215/2026 confirmed

### Week 1 (Jul 6 - Jul 12): Kick-off phase
- Kick-off email sent
- Awaiting supervisor response to schedule 60-90 min meeting

### Weeks 2-3 (Jul 14 - Jul 27): D1 Supervision Sensitivity
- Implement --supervision_regime flag
- Run 4 supervision-sensitivity experiments at seed 42
- Analyse

### Weeks 4-5 (Jul 28 - Aug 10): D2 β=0 Ablation
- Run --ablation_beta_zero at 3 seeds
- Compare against default (β=0.10) baseline
- Analyse

### Weeks 6-8 (Aug 11 - Aug 31): D3 Phenotype-level evaluation
- Implement evaluate_phenotype_ranking() in Stage 6
- Compute drug→phenotype MRR/Hits@K on existing checkpoints
- Compare to naive baseline
- Analyse

### CIBB Conference: Sep 2-4 (Rome)

### Weeks 9-10 (Sep 8 - Sep 21): D5 + integration
- Verify pathway_enrichment.parquet for all configs
- Aggregate Reactome + KEGG results across configurations
- Cross-configuration comparison
- Complete Part B methods draft

### Weeks 11-14 (Sep 22 - Oct 20): Part B writing
- Full Part B manuscript draft
- Integrate all deliverables
- File intention-to-submit ~Oct 20

### Weeks 15-16 (Oct 21 - Nov 3): Part A polish + Part C
- Polish Part A literature review
- Draft Part C appendices (ethics letter, technical appendices, extra tables)

### Weeks 17-19 (Nov 4 - Nov 24): Supervisor review round 1
- Send full dissertation to supervisors ~Nov 3
- 2-3 week review turnaround
- Apply feedback

### Weeks 20-21 (Nov 25 - Dec 5): Final polish + submit
- Second review round if needed
- Final integration
- Submission

## Weekly Log

### Week 0 (Jun 27 - Jul 7): Setup phase ✅
- CIBB camera-ready submitted July 7
- MSc directory created, git initialised on msc-extensions branch
- Nested duplicate cleaned up (~900 MB freed)
- Code audit complete; scope confirmed against Part A commitments
- HREC 215/2026 confirmed (approved 8 May 2026, full review)
- Supervisor kick-off email sent

### Week 1 (Jul 6 - Jul 12): Kick-off phase
- Kick-off email sent [DATE]
- Awaiting supervisor response

## Decisions Log
- Descriptor-rich features (Bioteque, ProtT5) EXCLUDED from MSc scope
  - Reason: Part A commits to five specific deliverables, not features
- Focus on five Part-A deliverables as literature review commits
- Timeline: December 5-8, 2026 submission target with January fallback

## Blocked Items
- Supervisor kick-off meeting scheduling (waiting on response)

## References To Follow Up
- Bordes et al. 2013 (TransE): confirm cite in Part B methods for 
  degree-aware sampling
- Verify all pathway_enrichment.parquet files from CIBB runs

### Week 2 Day 1 (Jul 7): D1 code and first experiments

**Code changes committed:**
- --supervision_regime flag added (default | ambig_as_pos | nonassoc_excluded)
- 4 code changes: parse_args, RUN_ID generation, run_config saving, dg_positives branching
- Syntax verified, git commit 2650896 on d1-supervision-regime branch

**Experiments run (seed=42, β=0.10, no fingerprints, dg_context split):**
| Regime            | Filt MRR | Baseline | Val MRR (best) |
|-------------------|----------|----------|----------------|
| default           | 0.0779   | 0.0795   | 0.0705         |
| ambig_as_pos (r1) | 0.0763   | 0.0795   | 0.0599         |
| ambig_as_pos (r2) | 0.0881   | 0.0795   | 0.0769         |
| nonassoc_excluded | 0.0684   | 0.0795   | 0.0724         |

**Key observations:**
1. Duplicate ambig_as_pos runs differ by ±0.012 MRR (~15% relative).
   Confirms substantial CPU multi-threading non-determinism.
2. Single-seed regime comparisons cannot be trusted.
3. Simultaneous parallel jobs may cause PyG JIT cache contention 
   (job 210509 failed with this error).

**Decision:**
- Multi-seed replication essential for D1 (seeds 42, 123, 2026 x 3 regimes = 9 runs)
- Submit sequentially, not in parallel
- Next: Wednesday July 8, multi-seed submission

### Week 2 Day 2 (Jul 8): D1 complete + D2 launched

**D1 wrapped:**
- Multi-seed replication complete (9 runs across seeds 42/123/2026, 3 regimes)
- Analysis: regime choice NOT distinguishable within seed variance
- Filtered MRR: default 0.090±0.020 | ambig_as_pos 0.083±0.013 | nonassoc 0.084±0.010
- Baseline (across seeds): 0.088
- Merged d1-supervision-regime → msc-extensions
- Findings summary: d1_results_summary.md

**Secondary D1 finding:** Curator-facing recommendations differ dramatically 
across regimes despite equivalent MRR. Ambig_as_pos: 90% upgrade. 
Nonassoc_excluded: 74% downgrade. Worth reporting in Part B discussion.

**Tertiary D1 finding:** Drugs with SMILES score 3x higher across all regimes 
(0.09-0.11 vs 0.03-0.04). Persistent pattern; independent of supervision.

**D2 launched:**
- Job submitted to test --ablation_beta_zero at 3 seeds
- Comparison: β=0.10 (existing D1 default runs) vs β=0.0 (new D2 runs)
- Expected completion: ~75 min sequential
- Hypothesis: hub penalty has no effect (degree-aware sampling does the work)

### Week 2 Day 4 (Jul 10 early morning): D3 complete

**D3 wrapped:**
- New evaluation function evaluate_d3_phenotype_relevant.py (~470 lines)
- Debugged and fixed 3 issues: config key names, checkpoint key ('model_state' 
  not 'model_state_dict'), and double-offset bug on global gene IDs
- Ran across all 12 configurations from D1+D2 in ~3 minutes
- Analysis: model matches GP baseline, slightly below DG baseline
- Model filt MRR range: 0.093-0.101 across 12 configs
- Pattern: consistent baseline-level performance, regime/β insensitive
- Findings summary: d3_results_summary.md
- Draft methods: writing/d3_methods_draft.md

**Combined D1+D2+D3 finding:**
Model performance is approximately baseline-level across all evaluation 
slices tested (all-genes, phenotype-relevant subset), and insensitive to 
supervision regime and hub-penalty variations. Improvement must come from 
methodological changes beyond these dimensions.

**Next:**
- D5 pathway enrichment + literature validation starting Monday 13 July
- Weekend rest

### Week 2 Day 5 (Jul 10 late evening): D4 complete

**D4 wrapped:**
- Analytical study using existing test_metrics.json across all 12 configs
- No new compute needed (~1 second analysis)
- D4.1 (filtered vs raw gap): +0.012 MRR consistent across configs
- D4.3 (SMILES stratification): SMILES availability = +0.065 MRR gap
- D4.2 (per-drug binning): deferred, needs rescoring, not critical for MSc
- Analysis script: analyse_d4_raw_filtered.py
- Findings summary: d4_results_summary.md
- Draft methods: writing/d4_methods_draft.md

**KEY FINDING FOR MSC:**
Chemical structure availability drives performance ~5.5× more than any 
methodological choice tested. Cold-drug ranking improvements should focus 
on expanding SMILES coverage or developing structure-free representations 
for uncharacterised drugs, not on refining label handling, loss architecture, 
or evaluation protocol.

**Cross-deliverable pattern established:**
Model performance is baseline-level everywhere (D1, D2, D3) except when 
stratified by chemical structure availability (D4). This is the primary 
substantive claim for Part B.

**Next:**
- D5 pathway enrichment (~3 hours compute) + literature validation
- Starting Sunday or Monday
