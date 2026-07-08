# D3, D4, D5 Design Document
**Committed:** 8 July 2026 (evening)  
**MSc:** MLPKGA007 — Molepo  
**Project:** Interpretable GNNs for Pharmacogenomic Drug-Gene Ranking

---

## Preamble

This document consolidates the design for MSc Deliverables 3, 4, and 5. 
It replaces earlier scattered decisions and represents the finalised scope.

**Approved by student on 8 July 2026 evening.**

---

## D3 — Phenotype-Relevant Gene Ranking

### Scientific Question
Does the model rank *biologically-relevant* genes at the top of its 
cold-drug predictions? Specifically, does it prioritise genes that have 
downstream phenotype connectivity in ClinPGx?

### Task Definition
For each held-out test drug in cold-drug evaluation:
1. Compute drug-gene scores against all 25,041 genes (already done in D1/D2)
2. Filter the ranking to phenotype-relevant genes — those with ≥1 
   gene→phenotype edge in ClinPGx
3. Compute MRR/Hits@K on this filtered ranking

### Ground Truth
Gene-phenotype edges from ClinPGx (3,540 gene→phenotype edges).

**Note:** ClinPGx does not contain direct drug-phenotype ground truth 
(0 drug→phenotype edges in relationships.tsv). Evaluating drug-phenotype 
ranking directly would therefore require pseudo-ground-truth (e.g. 
literature co-occurrence). We instead use the gene-phenotype layer, which 
IS available, and frame the task as "did the model rank a phenotype-
connected gene at the top?" This maintains the biologically-mediated 
reasoning chain (drug → gene → phenotype) that Part A commits to, while 
using only real ClinPGx ground truth.

### Baselines
Report against BOTH:
- **(a) Drug-gene degree baseline:** rank all 25,041 genes by their global 
  in-degree from drugs. This matches D1/D2 baseline directly.
- **(b) Phenotype-connected gene degree baseline:** rank phenotype-
  relevant genes by their gene-phenotype degree. Tests whether the model 
  beats a naive "phenotype-hub" heuristic.

### Model Checkpoints
Reuse all 12 existing runs:
- 9 D1 runs = 3 supervision regimes × 3 seeds (42, 123, 2026)
- 3 D2 runs = β=0 × 3 seeds
- Same test set, same split (`dg_context`)

Report per-configuration mean ± SD across seeds.

### Evaluation Protocols
- **Raw:** rank of true positive gene among all phenotype-relevant genes
- **Filtered:** rank of true positive gene among phenotype-relevant genes, 
  excluding known-positive genes for this drug

Both reported side-by-side.

### Expected Output Table (per configuration)
| Config | Filt MRR (mean±SD) | Filt H@10 | Baseline A | Baseline B | n_drugs |

### Implementation Complexity
~50 lines of Python added to Stage 3 evaluator. No new experiments; reuses 
existing checkpoints and scores.

### Timeline
Thursday 9 July: implementation + test on one checkpoint  
Friday 10 July: full evaluation across 12 configs  
Weekend: rest

---

## D4 — Raw AND Filtered Ranking Analysis

### Scientific Question
How do raw and filtered ranking protocols differ in this specific 
pipeline? What does the gap tell us about the model's behaviour on 
well-connected vs poorly-connected test drugs?

### Task Definition (Analytical, not Experimental)
D4 does NOT require new runs. All data exists in existing test_metrics.json 
files across the 12 D1/D2 configurations. D4 is a reporting and analytical 
study.

Three sub-analyses:

**D4.1 — Configuration-level raw vs filtered comparison**
- For each of 12 configs, report raw MRR, filtered MRR, gap = (filtered − raw)
- Show how the gap varies across regimes and β values
- Discuss what the gap indicates (rank inflation for well-connected drugs)

**D4.2 — Per-drug protocol sensitivity**
- Bin test drugs by their number of known positives (low/medium/high 
  connectivity)
- Report raw vs filtered MRR per bin
- Test hypothesis: filtered inflates rank primarily for well-connected drugs

**D4.3 — SMILES stratification and protocol interaction**
- Report raw AND filtered separately for drugs with/without SMILES
- Show whether protocol choice matters more for one subgroup
- Interpret alongside the persistent SMILES effect from D1/D2

### Data Source
Existing `results/*/artifacts/test_metrics.json` files across all D1/D2 runs.
Additionally, `results/*/artifacts/all_predictions.parquet` for per-drug 
analysis.

### Expected Output
- 1 configuration-level table (D4.1)
- 1 drug-connectivity binned table (D4.2)  
- 1 SMILES-stratified table (D4.3)
- ~200-word interpretation for Part B

### Implementation Complexity
~100 lines of Python analysis script. No new compute.

### Timeline
Option A (recommended): during Part B writing phase, October 2026  
Option B (alternative): Thursday-Friday next week if bandwidth allows  

**Decision:** Do during writing phase (October). No experimental risk of 
losing data by postponing.

---

## D5 — External Validation via Literature and Pathway Enrichment

### Scientific Question
Are the model's top predictions supported by external biological evidence 
that was not used during training?

### Two Complementary Validation Streams

#### D5-Part 1: Literature Validation (Case Study)

**Scope:** Focused case study on the **Primary MSc Reference Configuration**.

**Primary MSc Reference Configuration:**
- Regime: `default` (CIBB baseline)
- β: 0.10
- Seed: 42
- Split: `dg_context`
- Fingerprints: none
- All other parameters: as in D1/D2

**Task:**
1. From the primary reference config's Stage 3 output, extract top-10 
   predictions per test drug (751 drugs × 10 = 7,510 candidate pairs)
2. Filter to novel predictions only — those not in ClinPGx as either 
   associated or ambiguous
3. Query PubMed and EuroPMC for drug-gene co-mention in abstract/title
4. Report:
   - Rediscovery rate (predictions that ARE in ClinPGx as associated)
   - Novel + literature support rate (candidates for curator upgrade)
   - Novel + no literature (weakest predictions; still might be new biology)

**API details:**
- Email: `mlpkga007@myuct.ac.za`
- Rate limit: 3 requests/second (no API key)
- Estimated time: ~30-60 minutes for ~2,000-3,000 unique novel pairs

**Expected output:**
- 1 case-study table showing rediscovery vs novel+literature vs novel+no-lit
- 1 list of top-5 most literature-supported novel predictions (for Part B 
  discussion + curator triage)

#### D5-Part 2: Pathway Enrichment (Exhaustive)

**Scope:** All 12 configurations (9 D1 + 3 D2).

**Task:**
For each config:
1. Aggregate top-100 predictions across all test drugs
2. Extract the associated gene set
3. Run over-representation analysis (ORA) against:
   - **Reactome** pathways (via loaded GMT files)
   - **KEGG** pathways (via loaded GMT files)
4. Apply Benjamini-Hochberg (BH) FDR correction
5. Report q-values per pathway hit

**Expected output:**
- 1 aggregate pathway table showing top-10 enriched pathways per config
- Distribution of q-values across all 12 configs
- Comparison: do different regimes/β find different pathways, or the same 
  biological signal?

**Existing code:** Your pipeline already has `load_gmt_gene_sets`, 
`ora_enrichment`, and BH FDR correction implemented. D5-Part 2 is 
primarily about running and aggregating.

### Timeline
- Monday 13 July: D5-Part 2 pathway enrichment across all 12 configs  
- Tuesday-Wednesday 14-15 July: D5-Part 1 literature validation for 
  primary reference config
- Thursday-Friday 16-17 July: Aggregate, interpret, draft Part B

---

## Master Timeline (Post D3/D4/D5 Commit)

| Week | Dates | Activity |
|------|-------|----------|
| Week 2 (in progress) | Jul 6-10 | D1 done, D2 done, D3 implementation + evaluation |
| Weekend | Jul 11-12 | REST |
| Week 3 | Jul 13-17 | D5 pathway + literature validation |
| Week 4 | Jul 20-24 | Aggregate D3+D5 findings, draft Part B methods+results |
| Weeks 5-6 | Jul 27 - Aug 7 | Full Part B first draft |
| Weeks 7-8 | Aug 10-21 | Part B revision, D4 analysis integrated |
| Week 9 | Aug 24-28 | Final experiments if needed |
| — | Sep 2-4 | CIBB Rome conference |
| Weeks 10-13 | Sep 8 - Oct 6 | Part A polish, Part B revisions, D4 finalised |
| Weeks 14-17 | Oct 7 - Nov 3 | Full draft to supervisors (~Nov 3) |
| Weeks 18-20 | Nov 4-24 | Supervisor review round 1, revisions |
| Weeks 21-22 | Nov 25 - Dec 5 | Final polish, submission |

**Target submission date:** early December 2026.

---

## Rationale for Design Decisions

### Why D3 uses gene-phenotype instead of direct drug-phenotype
ClinPGx has 0 direct drug-phenotype edges. The gene-phenotype layer (3,540 
edges) is the strongest available ground truth for evaluating whether the 
model's cold-drug ranking prioritises biologically-relevant targets.

### Why D5 has two parts
Literature and pathway validation ask different questions:
- Literature validation asks: "Are individual predictions supported?"
- Pathway enrichment asks: "Are the model's predictions biologically 
  coherent as a set?"

Both are needed for a rigorous validation, but they have very different 
compute profiles:
- Literature: expensive per query (rate-limited API). Justifies focused 
  case study.
- Pathway: cheap (local computation on cached GMT files). Enables 
  exhaustive comparison.

### Why the Primary MSc Reference Configuration is default+β=0.10+seed=42
- Matches CIBB paper for continuity
- Is the "canonical" reference against which all D1/D2/D3 ablations were 
  measured
- Provides a single, defensible reference point for external validation

### Why D4 is postponed to writing phase
- All data exists in test_metrics.json (no experimental risk)
- Analysis is straightforward once the writing narrative is clear
- Postponing avoids premature framing before D3 and D5 findings are in

---

## Files Referenced in This Design

**Existing pipeline outputs (per config):**
- `results/*/artifacts/test_metrics.json` — ranking metrics (D1, D2, D4 use)
- `results/*/artifacts/all_predictions.parquet` — top predictions (D5 uses)
- `results/*/artifacts/edges.parquet` — graph structure (D3 uses)
- `results/*/artifacts/model_checkpoint.pt` — trained model (if re-scoring needed)

**New scripts to be created:**
- `evaluate_d3_phenotype_relevant.py` — D3 metric computation (~50 lines)
- `submit_d3_multiseed.sh` — SLURM submission for D3 across configs
- `analyse_d3_phenotype.sh` — aggregation and comparison
- `run_d5_literature_validation.py` — PubMed + EuroPMC queries
- `run_d5_pathway_enrichment.py` — Reactome + KEGG ORA aggregation
- `d3_results_summary.md`, `d4_analysis_summary.md`, `d5_results_summary.md`

**Draft writing files:**
- `writing/d3_methods_draft.md`
- `writing/d4_methods_draft.md`
- `writing/d5_methods_draft.md`

---

## Approvals

- **D3 reformulation** (gene ranking with phenotype-relevance filter, not 
  direct drug-phenotype): APPROVED
- **D4 as analytical study** using existing data: APPROVED
- **D5 two-part structure** (literature + pathway): APPROVED
- **Primary MSc Reference Configuration** = default regime, β=0.10, seed 42: 
  APPROVED
- **Literature validation limited to primary reference config**: APPROVED
- **Pathway enrichment across all 12 configs**: APPROVED
- **PubMed email:** mlpkga007@myuct.ac.za

Signed: MLPKGA007  
Date: 8 July 2026 (evening SAST)

