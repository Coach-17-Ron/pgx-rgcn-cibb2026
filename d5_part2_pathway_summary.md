# D5-Part 2 Pathway Enrichment — Multi-Config Results

## Method
For each of 12 configurations (D1: 9 runs across 3 regimes × 3 seeds; D2: 
3 β=0 runs at 3 seeds), Stage 5's pathway ORA was run on the top novel 
predictions (typically 4,000-5,000 predictions per config, ~160-320 
unique genes per hit list). Over-representation testing used the 
protein-coding gene universe with Benjamini-Hochberg FDR correction 
(α=0.05).

Three pathway sources were combined:
- **Reactome:** 2,868 gene sets
- **KEGG (MSigDB c2.cp.kegg_medicus):** 658 gene sets  
- **PharmGKB drug-specific pathways:** 163 gene sets

Total: 3,689 gene sets tested per config.

Note: KEGG collection is "KEGG_MEDICUS" from MSigDB (2024.1.Hs release) 
in place of classical KEGG (licensing changes at MSigDB).

## Number of FDR-significant pathways per config

| Configuration | Mean sig pathways | REACTOME hits | KEGG hits | PGKB hits |
|---|---|---|---|---|
| default β=0.10 | 53.7 | 15 | 0 | 146 |
| ambig_as_pos β=0.10 | 63.7 | 29 | 3 | 159 |
| nonassoc_excluded β=0.10 | 42.3 | 8 | 2 | 117 |
| default β=0.00 | 64.3 | 25 | 3 | 165 |

Regime and β choice do not qualitatively shift which pathways emerge; the 
same drug-specific PharmGKB pathways dominate across configs.

## Robustness — pathways significant in ≥6/12 configs

**43 pathways** were FDR-significant (q < 0.05) in the majority (≥6/12) 
of configurations tested.

**10 pathways** were significant in ALL 12 configurations:

| PharmGKB Pathway | Drug Class |
|---|---|
| PA166121347 Paroxetine Pathway (PK) | SSRI antidepressant |
| PA2025 Etoposide Pathway (PK/PD) | Anti-cancer topoisomerase inhibitor |
| PA154426155 Taxane Pathway (PK) | Anti-cancer |
| PA166279441 Mitotane Pathway (PK/PD) | Adrenocortical carcinoma |
| PA165817070 Carbamazepine Pathway (PK) | Antiepileptic |
| PA165986114 Tacrolimus/Cyclosporine (PK) | Immunosuppressants |
| PA154426903 Erlotinib Pathway (PK) | Anti-cancer TKI |
| PA166165076 Verapamil Pathway (PK) | Calcium channel blocker |
| PA152325160 Gefitinib Pathway (PK) | Anti-cancer TKI |
| PA166178331 Nilotinib Pathway (PK/PD) | Anti-cancer TKI |

## Reference config nominal top 10 by p-value

**Also significant at FDR<0.05:**
- Paroxetine Pathway (p=2.15e-08)
- Etoposide Pathway (p=2.15e-08)
- **REACTOME::Biological oxidations** (p=2.56e-08) — master drug metabolism pathway
- Taxane Pathway (p=7.35e-08)
- Mitotane Pathway (p=1.01e-07)
- Carbamazepine Pathway (p=4.15e-07)
- **PA145011108 Statin Pathway** (p=6.94e-07)
- **REACTOME::Phase I - Functionalization of compounds** (p=2.09e-06)
- Tacrolimus/Cyclosporine Pathway (p=2.30e-06)
- Erlotinib Pathway (p=4.60e-06)

## Interpretation

**Substantive positive finding for the MSc.** While D1/D2/D3/D4 show the 
model performs at baseline level for aggregate ranking metrics, D5-Part 2 
demonstrates that the model's top novel predictions are consistently 
enriched in pharmacogenomically-relevant pathways under BH-FDR correction 
across all 12 configurations tested.

The 10 PharmGKB pathways significant in ALL configs span:
- Anti-cancer therapeutics (Etoposide, Taxane, Erlotinib, Gefitinib, Nilotinib)
- CYP-metabolised drugs (Paroxetine, Carbamazepine, Verapamil)
- Drug transporters (Tacrolimus/Cyclosporine — ABCB1/CYP3A4 substrates)

**Key insight:** The model captures pharmacogenomic biology at the pathway 
level even when aggregate MRR is at baseline. This is consistent with 
graph structure alone (independent of chemical structure) providing 
biological signal, while chemical structure (D4 finding) is needed for 
competitive per-edge ranking.

## Implications

1. **The model is suitable for hypothesis generation** — its top predictions 
   are biologically coherent even without beating naive baselines on MRR.

2. **Pathway-level evaluation reveals signal that MRR obscures** — the 
   model captures drug-metabolism biology that per-edge ranking metrics 
   cannot detect.

3. **Model outputs are curator-actionable** — predictions consistently 
   land in pathways relevant to real PGx drugs (statins, immunosuppressants, 
   TKIs, antiepileptics).

## Combined narrative with prior deliverables

- **D1/D2/D3:** Model MRR is baseline-level; supervision, hub penalty, 
  and phenotype-relevance filtering don't change this.
- **D4:** Chemical structure availability drives ranking performance 
  (SMILES effect >> methodological effects).
- **D5-Part 2:** Model predictions ARE biologically coherent at the 
  pathway level; ranking baseline-level performance does not preclude 
  scientific utility for hypothesis generation.

## Data Provenance

- 12 SLURM job runs (job ID 243230, 3:27 elapsed)
- All 12 pathway_enrichment.parquet files present
- Analysis script: analyse_d5_pathway_multiseed.sh

