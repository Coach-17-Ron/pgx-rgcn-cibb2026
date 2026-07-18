# D5 Null Enrichment Check — Model vs Drug-Gene Degree Baseline

## Question

D5-Part 2 identified 10 PharmGKB drug pathways FDR-significant in ALL 12 
configurations tested. This finding was interpreted as evidence that the 
model captures pharmacogenomic biology at the pathway level.

However, a skeptic could argue this is circular: the model may simply be 
finding high-degree genes (CYP enzymes, drug transporters) that appear 
in curated PGx pathways by construction.

To test this, we conducted a null enrichment check comparing the model's 
predicted gene set against a drug-gene degree baseline of the same size.

## Method

For the primary reference config (default β=0.10 seed 42):

1. Extract the model's top predicted genes from `novel_predictions.parquet` 
   (322 unique genes)
2. Construct a matched-size baseline: the top-322 genes by drug-gene 
   degree from `edges.parquet` (no model involved)
3. Run identical pathway ORA on both gene sets (3,689 gene sets from 
   Reactome + KEGG + PGKB)
4. Apply BH-FDR correction (α=0.05)
5. Compare significant pathway sets

## Results

**Set overlap:** 49.1% (158/322) — the model and degree baseline share 
about half their gene selections.

**Significant pathways:**

| Set | # Pathways |
|---|---|
| Model | 264 |
| Baseline (degree only) | 620 |
| Common to both | 221 |
| Model only | 43 |
| Baseline only | 399 |

**Critical finding:** The degree baseline identifies MORE significant 
pathways than the model (620 vs 264).

## D5-Part 2 headline pathways — all 10 present in both sets

| PharmGKB Pathway | Model | Baseline |
|---|---|---|
| Paroxetine Pathway | SIG | SIG |
| Etoposide Pathway | SIG | SIG |
| Taxane Pathway | SIG | SIG |
| Mitotane Pathway | SIG | SIG |
| Carbamazepine Pathway | SIG | SIG |
| Tacrolimus/Cyclosporine Pathway | SIG | SIG |
| Erlotinib Pathway | SIG | SIG |
| Verapamil Pathway | SIG | SIG |
| Gefitinib Pathway | SIG | SIG |
| Nilotinib Pathway | SIG | SIG |

**All 10 D5-Part 2 headline pathways are also FDR-significant under the 
degree baseline.**

## Interpretation

**The D5-Part 2 "10 PGx pathways significant across all configs" finding 
is largely a structural effect of drug-gene degree, not a specific model 
contribution.** These PGx pathways contain high-degree drug-metabolising 
genes (CYP enzymes, drug transporters) that any large gene selection 
including high-degree genes would enrich.

## What remains genuinely model-specific

**43 pathways are significant for the model but not for the degree 
baseline.** These are more mechanism-specific pathways that pure degree 
selection misses.

**Top model-only pathways (by q-value):**

- REACTOME: Wnt/β-catenin signaling (multiple related pathways)
- REACTOME: TCF7L2 mutants don't bind CTBP
- REACTOME: Interferon signaling (multiple pathways)
- REACTOME: ADAR signaling (multiple pathways)  
- REACTOME: Nuclear Receptor transcription
- REACTOME: G alpha (s) signalling events
- REACTOME: Class B/2 Secretin receptors
- REACTOME: Antimicrobial peptides
- REACTOME: Type II interferon signaling
- KEGG: SEB-mediated Th cell response

**399 pathways are significant for the baseline but not the model** — 
these are predominantly broad, non-specific categories: cell cycle, 
membrane trafficking, GPCR signaling, metabolism, gene expression, 
nervous system development. The degree baseline captures these because 
its gene set contains broadly-connected genes annotated in many broad 
pathway categories.

## Revised interpretation

The model does not exceed a drug-gene degree baseline on pathway 
enrichment. However, the model uniquely captures 43 more mechanism-
specific pathways — nuclear receptor transcription, Wnt/β-catenin, 
interferon signaling, G-α subunit signalling — that are absent from 
the degree baseline's significant set.

**This is a nuanced positive-plus-null finding:**

- Broad pathway enrichment (D5-Part 2 headline) is structural, not 
  model-specific
- Specific pharmacological mechanism pathways ARE model-specific
- The model prioritises narrower, mechanism-focused biology while the 
  degree baseline captures broader pathway categories

## Consistency with other findings

This is consistent with the pattern from D1-D3:
- Model does not beat frequency baselines on aggregate metrics
- Some methodological ablations don't change this
- Model captures specific things that baselines miss (in D4, per-drug 
  SMILES effect; here, mechanism-specific pathways)

## Files produced

- `null_enrichment_model.parquet` — model ORA results
- `null_enrichment_baseline.parquet` — degree baseline ORA results  
- Analysis script: `null_enrichment_check.py`

## Data Provenance

- Run directory: `results/20260708_044757_dg_context_beta0p1_seed42_reg-default`
- Log file: `null_enrichment_check.log`
- Executed: 18 July 2026 SAST

