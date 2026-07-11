# D4 Raw AND Filtered Ranking Analysis — Multi-seed Results

## Method
Analytical study using existing `test_metrics.json` files from all 12 D1/D2 
configurations. No new experiments.

Two sub-analyses:
- **D4.1** — Raw vs filtered protocol comparison per configuration
- **D4.3** — SMILES stratification × filtered protocol interaction

D4.2 (per-drug binning) was deferred: existing runs do not save per-drug 
rank arrays. Adding it would require ~15 min of rescoring using D3's 
approach.

## D4.1 — Raw vs Filtered Protocol Comparison

| Configuration | Raw MRR | Filtered MRR | Gap |
|---|---|---|---|
| default β=0.10 | 0.0752 ± 0.0163 | 0.0903 ± 0.0199 | +0.0151 |
| ambig_as_pos β=0.10 | 0.0722 ± 0.0063 | 0.0826 ± 0.0126 | +0.0104 |
| nonassoc_excluded β=0.10 | 0.0735 ± 0.0112 | 0.0841 ± 0.0101 | +0.0105 |
| default β=0.00 | 0.0711 ± 0.0123 | 0.0821 ± 0.0162 | +0.0110 |

**Mean gap across 12 configs: +0.012 MRR.**

The filtered protocol systematically inflates MRR by ~0.012 relative to 
raw evaluation. The inflation is small compared to intra-config seed 
variance (SD ~0.010-0.020) and consistent across regimes.

## D4.3 — SMILES Stratification × Filtered Protocol

| Configuration | With SMILES | Without SMILES | Gap |
|---|---|---|---|
| default β=0.10 | 0.1109 ± 0.0280 | 0.0438 ± 0.0100 | +0.0671 |
| ambig_as_pos β=0.10 | 0.1012 ± 0.0149 | 0.0396 ± 0.0138 | +0.0616 |
| nonassoc_excluded β=0.10 | 0.1031 ± 0.0145 | 0.0404 ± 0.0075 | +0.0627 |
| default β=0.00 | 0.1035 ± 0.0270 | 0.0346 ± 0.0011 | +0.0689 |

**Mean gap across 12 configs: +0.065 MRR (SMILES-available drugs vs not).**

Test set has ~537 drugs with SMILES available (71%) and ~214 drugs 
without (29%). The 5.5× larger effect than the raw/filtered protocol 
choice shows that chemical structure availability is the dominant driver 
of cold-drug ranking performance in this pipeline.

## Cross-Comparison

- **Raw → Filtered protocol effect:** ~+0.012 MRR
- **SMILES availability effect:** ~+0.065 MRR

Ratio: 5.5×. Chemical structure availability drives performance far more 
than any methodological choice tested.

## Combined Finding

**The strongest driver of cold-drug ranking on ClinPGx is chemical 
structure availability, not label handling (D1) or loss architecture 
(D2) or evaluation protocol (D4).** 

Across all 12 configurations spanning three supervision regimes and 
two hub-penalty values, the model consistently:
- Achieves ~0.10 MRR for drugs with SMILES available
- Achieves ~0.04 MRR for drugs without SMILES
- Shows a smaller ~0.012 lift from filtered vs raw evaluation
- Shows essentially no sensitivity to supervision regime or hub penalty

## Implications for Future Work

Cold-drug PGx prediction improvements should prioritise:
1. Expanding chemical structure coverage in curated resources
2. Developing structure-free representations for uncharacterised drugs
3. Reporting stratified metrics (SMILES vs non-SMILES subsets) as standard 
   practice

Improvements should NOT prioritise:
- Refining label handling for ambiguous/not-associated pairs (D1)
- Tuning hub penalty coefficients (D2)  
- Alternative evaluation subsetting to phenotype-relevant genes (D3)
- Choosing between raw and filtered protocol (D4)

## Sample Sizes

- Test drugs with SMILES: ~537 per config
- Test drugs without SMILES: ~214 per config
- Total per config: 751 test drugs (matches D1/D2 test set)

## Data Provenance

- All data extracted from `results/*/artifacts/test_metrics.json`
- No new experimental runs
- Analysis script: `analyse_d4_raw_filtered.py`
- Total D4 compute: ~1 second

