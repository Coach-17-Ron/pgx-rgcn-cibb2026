# MSc Progress Presentation — Speaker Script
**Kgabe Ronald Molepo (MLPKGA007) | Friday 24 July 2026 | 12:00**

## Timing budget
- Slide 1: 60 sec (intro)
- Slides 2-4: 60-90 sec each (framing)
- Slides 5-8: 60-90 sec each (methodology)
- Slides 9-19: 90-150 sec each (results — this is the meat)
- Slides 20-25: 60-90 sec each (discussion, ask)
- **Total: ~40-45 minutes**

Aim for the shorter end. Better to finish 42 minutes and have more discussion than to overrun.

---

## SLIDE 1 — Title (60 sec)

**Opening (memorize):**
"Good afternoon. My name is Kgabe Molepo. Thank you both for meeting with me. I'm here to give a progress update on my MSc dissertation: Interpretable Graph Neural Networks for Learning Drug-Gene Relationships and Inferring Phenotype Outcomes in Pharmacogenomics.

This meeting is intended as a progress review rather than a defence. I've completed all experimental work planned in Part A, and I'd like to walk you through the findings before starting Part B writing. I'll aim for about 45 minutes, leaving time for discussion."

**Then click next.**

---

## SLIDE 2 — Where we are (75 sec)

**Say:**
"To orient us — Part A was submitted in November last year. Since then, I've completed all experimental deliverables. That means D1 through D5, plus enhancements including a null enrichment check and integrated interpretability composition.

I'm at the writing phase now, targeting December 2026 submission. Currently the experimental work finished 5-6 weeks ahead of the Part A schedule, which converts to writing buffer.

Today my aim is to report the findings so I can move confidently into Part B writing, and to check with you on the framing of a few things."

**Transition:** "Let me quickly recap what Part A committed to."

---

## SLIDE 3 — Part A gap (60 sec)

**Say:**
"Part A identified a specific gap in the literature: no prior pipeline had combined all five of these requirements. Evidence-graded supervision, ranking with hub penalty and degree-aware sampling, biologically-mediated propagation, cold-drug evaluation with raw and filtered MRR, and coupled interpretability with pathway contextualisation.

The Part A contribution statement was that combining all five in one reproducible pipeline is the contribution. Today's talk is essentially answering: did we deliver on this?"

**Transition:** "The specific objectives were..."

---

## SLIDE 4 — Aim and objectives (60 sec)

**Say:**
"The overall aim is straightforward: evaluate whether R-GCN can rank drug-gene relationships for previously-unseen drugs on ClinPGx, and characterise what actually drives performance.

The five specific objectives map directly to the five requirements from the gap analysis. I'll walk through each and show whether it was met."

**Transition:** "Let me cover methodology briefly, then spend most of our time on results."

---

## SLIDE 5 — KG construction (75 sec)

**Say:**
"The knowledge graph was built from ClinPGx, formerly PharmGKB — the primary curated pharmacogenomics resource.

The final graph has 38,955 nodes across four types: drugs, genes, variants, and phenotypes. 44,218 edges connect them, spanning 56 different evidence-typed relations. This is important: we preserved the evidence categories that curators originally assigned. Clinical evidence differs from drug-label evidence differs from pathway evidence, and R-GCN can distinguish these.

Objective 1 met."

**Transition:** "For the model itself..."

---

## SLIDE 6 — R-GCN training (75 sec)

**Say:**
"The model is a two-layer R-GCN with basis decomposition — 8 basis matrices. 64-dimensional embeddings, DistMult decoder for scoring. Drug nodes use Morgan fingerprints as input features.

Training uses a pairwise margin ranking loss with the hub penalty from Part A, degree-aware negative sampling, and evidence-graded supervision — only 'associated' edges as positives.

All 12 configurations trained on ilifu. CPU only, because the P100 GPU there is too old for PyTorch 2.10 with the CUDA build we're using.

Objective 2 met."

**Transition:** "Evaluation was a cold-drug setup..."

---

## SLIDE 7 — Evaluation protocol (75 sec)

**Say:**
"751 drugs held out entirely from training. Message passing on training subgraph only, so no leakage. For each held-out drug, we score all genes and measure where the true positive ranks — MRR and Hits@K, both raw and filtered.

The key discipline is multi-seed replication. Everything I show tonight has three seeds. 12 configurations total: three regimes at three seeds, plus three seeds at β=0 for the hub penalty ablation. Single-seed findings are unreliable at this data scale."

**Transition:** "Now the results, objective by objective."

---

## SLIDE 8 — Objectives 1-2 status (30 sec)

**Say:**
"Objective 1 is met by construction. Objective 2 is met by training all 12 configurations with multi-seed variance measured. Moving on to what we learned from those experiments."

**Transition:** "D1 tested whether supervision regime matters."

---

## SLIDE 9 — D1 regime comparison (120 sec)

**Say:**
"D1 tested three supervision regimes. Default treats only 'associated' edges as positives; ambig_as_pos also treats ambiguous as positives; and nonassoc_excluded excludes 'not associated' entirely.

Three seeds each — 9 configurations. What you see is that all three regimes converge to filtered MRR around 0.08-0.09. The differences between regimes are smaller than the variance between seeds within a single regime.

This is a null result but an important one. Early single-seed runs suggested ambig_as_pos was slightly better. Multi-seed replication revealed that difference was noise. This validates our Part A default choice and demonstrates why single-seed comparisons in the literature are unreliable."

**Transition:** "D2 tested a similar question about the hub penalty."

---

## SLIDE 10 — D2 hub penalty (90 sec)

**Say:**
"D2 tested whether the hub penalty term does useful work. We compared β=0.10 against β=0, three seeds each.

The difference is 0.008 MRR — well within seed variance. The hub penalty is essentially inactive.

The interpretation is that degree-aware negative sampling already handles the hub-bias problem. The penalty term is redundant given that mechanism. Not wrong to include it, but not doing measurable work."

**Transition:** "D3 was where I had to reformulate an objective."

---

## SLIDE 11 — D3 reformulation (150 sec) [BE DIRECT]

**Say:**
"D3 is a slide I want to spend real time on because it required a reformulation.

Part A committed to evaluating biologically-mediated drug-to-phenotype prediction through the reasoning chain of drug → gene → variant → phenotype. When I started implementation, I discovered that ClinPGx does not curate direct drug-phenotype associations. Zero drug-phenotype edges in the relationships table.

This is significant. It means direct drug-phenotype ranking cannot be evaluated because there's no ground truth in ClinPGx. Biological mediation is architecturally enforced by data structure rather than by design choice.

I reformulated D3 to test a proxy: does the model prioritise phenotype-relevant genes — those with at least one gene-phenotype edge — above a naive frequency baseline?

Result: the model achieves filtered MRR of about 0.10 on this subset. That matches the gene-phenotype degree baseline. Same pattern as D1 and D2.

**The discussion point I want to check with you:** is this reformulation acceptable for the dissertation? Should I frame it as I've done here, or would you prefer different language?"

**Transition:** "D4 was the analysis that gave us the substantive positive finding."

---

## SLIDE 12 — D4.1 raw vs filtered (45 sec)

**Say:**
"Quickly — D4.1 compared raw and filtered MRR protocols. Filtered is consistently 0.012 MRR higher across configurations. Small effect from removing known positives from the ranking pool. This is a setup for the interesting finding on the next slide."

**Transition:** "D4.3 is where we got the strongest positive finding."

---

## SLIDE 13 — D4.3 SMILES EFFECT (150 sec) [HERO SLIDE]

**Say (with confidence):**
"D4.3 stratifies performance by whether the test drug has a SMILES chemical structure available. Our pipeline uses Morgan fingerprints as drug features, so without SMILES, a drug is essentially represented as a random embedding vector.

The result across all 12 configurations: drugs with SMILES achieve filtered MRR around 0.10. Drugs without SMILES achieve about 0.04. The gap is 0.065 MRR.

That's 5.5 times larger than the raw-versus-filtered effect from D4.1. And it's larger than any effect from D1, D2, or D3 — supervision regime, hub penalty, or phenotype-relevance filtering.

This is the substantive positive finding. Chemical structure availability at test time is the primary constraint on cold-drug ranking performance in this pipeline. It's not a model choice, it's a feature-availability constraint.

For Part B this becomes the central actionable insight. Improvements should focus on chemical structure coverage or structure-free representations for drugs without SMILES — not on refining label handling or loss architectures."

**Transition:** "Then D5 tested biological grounding of the predictions."

---

## SLIDE 14 — D5-Part 2 pathway enrichment (90 sec)

**Say:**
"D5-Part 2 tested whether the top predictions from each configuration are enriched in known biological pathways. 3,689 gene sets from Reactome, KEGG, and PharmGKB, tested with Benjamini-Hochberg FDR correction at 0.05.

The initial finding: 10 PharmGKB drug pathways are FDR-significant in ALL 12 configurations. This includes Paroxetine, Etoposide, Taxane, Verapamil, Tacrolimus and Cyclosporine — all clinically important PGx drugs.

At first I interpreted this as strong biological validation. Then I asked whether the finding is specifically from the model, or a structural artefact."

**Transition:** "That question led to a null enrichment check."

---

## SLIDE 15 — Null enrichment (150 sec) [HONEST]

**Say (directly):**
"This is the slide where I want to be transparent about a finding that weakens the D5-Part 2 headline.

I compared the model's predicted gene set against a drug-gene degree baseline — no learning at all, just 'take the top 322 genes by drug-gene connectivity'. Ran the same pathway ORA.

The result: the degree baseline finds 620 significant pathways. The model finds 264. And all 10 headline pathways I just showed — Paroxetine, Etoposide, and the others — are also FDR-significant under the degree baseline.

The D5-Part 2 headline is largely a structural effect of gene degree, not a specific model contribution. High-degree genes happen to be drug-metabolising CYP enzymes and transporters that populate curated PGx pathways.

However — 43 pathways are significant only for the model. Not for the degree baseline. These are more mechanism-specific: Wnt/β-catenin signaling, interferon signaling, nuclear receptor transcription, G-alpha subunit signalling. These 43 pathways represent the genuine model contribution.

I ran this check anyway because I'd rather find it myself than have an examiner find it later. For Part B, I'll report this honestly. The 43 model-only pathways are the defensible positive finding, not the 10 headline pathways."

**Transition:** "External literature was the other validation lens."

---

## SLIDE 16 — D5-Part 1 literature (120 sec)

**Say:**
"D5-Part 1 queried PubMed for external literature evidence. For the reference configuration, I ran 4,636 predictions covering 190 unique test drugs — that's 25% of the test set. 1990 to 2026 date filter, 10 articles per pair maximum.

17.5% of predictions have at least one supporting PubMed article. 3,505 articles total. Importantly, 45% of these articles pre-date 2020, which shows why the wider date range mattered — classical PGx literature would have been excluded by a narrow recent-only filter.

Biologically meaningful supported pairs include carbidopa to COMT for Parkinson's, dimethyl fumarate to FOXP3 for multiple sclerosis, and doxorubicinol to ABCB1 for chemotherapy resistance.

Honest caveat: the 17.5% rate is inflated by some pairs involving broad chemicals like calcium and testosterone, where PubMed co-mention reflects general biology rather than specific pharmacogenomics. If we filtered to canonical pharmaceuticals, the rate would be lower but more specific."

**Transition:** "For interpretability — first the intrinsic side."

---

## SLIDE 17 — Intrinsic interpretability (75 sec)

**Say:**
"Intrinsic interpretability computed Frobenius norms of the R-GCN encoder weight matrices, per relation type. This tells us which of the 56 evidence-typed relations the model relied on most.

The top-weighted relation is drug-to-gene clinical association at 8.46. Then gene-to-drug clinical at 5.15. Then drug-to-gene label at 4.07. Then pathway at 3.63.

The model learned to weight clinical evidence higher than label evidence, which is higher than pathway evidence. It respects the evidence-graded supervision as designed. This satisfies the intrinsic component of Requirement 5c from Part A."

**Transition:** "Then post-hoc and integrated."

---

## SLIDE 18 — Integrated interpretability (120 sec)

**Say:**
"D5 Session 1 combined structural graph paths, pathway enrichment, and literature evidence into per-prediction integrated reports.

For the top 50 novel predictions: 98% have a graph path within 4 hops — that's 49 out of 50. 74% have pathway support. 20% have PubMed literature. And 14% — seven predictions — have all three evidence types simultaneously. Fully triangulated.

The exemplar is testosterone predicting ABCB1. Graph path via CYP3A4 metabolism. 27 significant PGx pathways containing ABCB1. Ten PubMed articles from 2024 to 2026. This is high-confidence curator-actionable evidence.

This closes Requirement 5c fully — intrinsic plus post-hoc plus pathway plus literature, integrated at the per-prediction level."

**Transition:** "Summary of all objectives."

---

## SLIDE 19 — Objectives summary (60 sec)

**Say:**
"So all five objectives met. Objective 3 required reformulation because ClinPGx has no direct drug-phenotype edges. The others are direct.

I want to flag Objective 3 explicitly for discussion. My proposed framing for Part B is that the reformulation is a finding about the knowledge base, not a shortcoming of the work. But I want your input on how to frame this."

**Transition:** "Let me pull the story together."

---

## SLIDE 20 — Combined narrative (120 sec)

**Say:**
"The story from these six findings:

Method-level choices — supervision regime, hub penalty, evaluation subset, raw versus filtered protocol — don't move the needle. That's D1, D2, D3, and D4.1.

Chemical structure availability dominates. That's D4.3, the 5.5-times effect.

Pathway enrichment is largely structural, not model-specific. That's D5-Part 2 plus the null check. But the model does uniquely find 43 mechanism-specific pathways.

17.5% literature support with biologically meaningful pairs. That's D5-Part 1.

And 14% fully-triangulated predictions with integrated evidence. That's D5 Session 1.

The narrative is: aggregate MRR is baseline-level, but the model captures specific biology at the pathway level and produces curator-actionable predictions when combined with pathway and literature validation."

**Transition:** "The contribution then is..."

---

## SLIDE 21 — The contribution (90 sec)

**Say:**
"I want to be direct about what this MSc claims and does not claim.

It does not claim state-of-the-art performance. It doesn't beat naive baselines on aggregate MRR.

What it does claim: rigorous multi-seed evaluation identifying what does and doesn't drive performance. Chemical structure availability identified as the primary constraint. A null enrichment check for scientific defensibility. Integrated multi-evidence interpretability framework. And honest, reproducible reporting standards.

This is a characterisation contribution rather than a state-of-the-art claim. Not glamorous, but scientifically honest and defensible."

**Transition:** "The limitations honestly."

---

## SLIDE 22 — Limitations (90 sec)

**Say:**
"Method limitations: we tested one architecture. RGAT, CompGCN, HGT would all be reasonable alternatives. Small hidden dimension. Broader coverage of literature dates would help.

Data limitations: ClinPGx is sparse relative to full biology. Absence of drug-phenotype edges forced the Objective 3 reformulation. SMILES coverage of 537 out of 751 test drugs is a real ceiling.

Interpretation caveats: aggregate MRR doesn't fully capture prediction utility. Pathway enrichment doesn't prove mechanistic causality. The 17.5% literature support rate is inflated by broad chemicals.

Most of these are scope decisions rather than failures. I want to acknowledge them clearly rather than defend against them."

**Transition:** "Future work."

---

## SLIDE 23 — Future work (60 sec)

**Say:**
"Short-term: complete Part B writing and address feedback from today.

Longer-term beyond the MSc: alternative architectures for direct comparison. Descriptor-rich features like ChemBERTa or ProtT5. Structure-free representations for drugs without SMILES. SIDER for direct drug-phenotype ground truth. Multi-config literature validation.

These are natural extensions but not required for a complete MSc."

**Transition:** "This brings me to what I need from you."

---

## SLIDE 24 — What I need (120 sec)

**Say (clear and direct):**
"There are four specific things I'd like from this meeting.

First: approval to begin Part B writing. Chapters 3 through 6 — methodology, results, discussion, conclusion.

Second: confirmation that these findings are defensible as an MSc contribution. Specifically the null-plus-characterisation framing, and the integrated interpretability approach.

Third: guidance on the Objective 3 reformulation framing. Is it acceptable to reformulate as I've described, or would you prefer different language for Part B?

Fourth: a timeline check. December submission is on target, and I'm 5-6 weeks ahead of the Part A plan.

That's what I need. I'd welcome discussion on any of these."

**Transition:** "Final slide."

---

## SLIDE 25 — Timeline (60 sec)

**Say:**
"To close — all experimental deliverables complete in July. Presentation to you today. August through October for Part B chapter drafts. November for your review and any revisions. Early December for submission.

We're ahead of schedule. That buffer becomes writing quality time.

Thank you. I welcome your questions."

**[STOP TALKING. Wait for questions.]**

---

## Q&A — Anticipated questions + answers

### Q: "Why did you not compare against other architectures like RGAT?"

**Answer:** "Scope decision. Part A committed to characterising one architecture rigorously with multi-seed evaluation across 12 configurations. Adding RGAT would mean either doubling the scope or reducing rigor on R-GCN. I prioritised rigor. I've noted it in future work."

### Q: "Isn't 7% or even 17% literature support quite low?"

**Answer:** "For novel predictions — pairs that are not yet in ClinPGx as associated — we would not expect high rates of literature co-mention. The relevant comparison is against a random baseline, which would be near zero. 17.5% with biologically meaningful hits like carbidopa-COMT for Parkinson's is a defensible external validation signal."

### Q: "The null enrichment finding — doesn't this weaken your whole D5 story?"

**Answer:** "It weakens the D5-Part 2 headline about 10 pathways, yes. What it doesn't weaken is the 43 model-only pathways, which represent genuine mechanism-specific model contribution, and the literature validation, and the integrated interpretability. The D5 story becomes more nuanced but not undermined. And I'd rather report it honestly than have it discovered by an examiner."

### Q: "Objective 3 — this reformulation is a big departure from Part A. How do we justify it?"

**Answer:** "I want your guidance specifically on this. My proposed framing is that the reformulation is itself a finding about the knowledge base — that ClinPGx does not curate direct drug-phenotype associations. That's a substantive discovery. The proxy evaluation using phenotype-relevant genes tests the same underlying question with different mechanics. I welcome your view on how to word this in Part B."

### Q: "What's the actual utility for pharmacogenomics if MRR is baseline-level?"

**Answer:** "This is the discussion I want to open in Part B. Aggregate MRR is one measurement dimension. Curators care about whether a prediction is worth investigating — that's the integrated evidence framework I showed. A prediction with structural support, pathway coherence, and literature evidence is worth curator time regardless of where it ranks against all 25,000 genes."

### Q: "SMILES effect is 5.5×. Wouldn't a paper on this alone be publishable?"

**Answer:** "It's a substantive finding. Whether it's publishable independently depends on how it fits into the broader narrative. I'd welcome your thoughts on whether it could be extracted as a standalone paper after the MSc submission."

### Q: "How do we defend the D3 reformulation to an external examiner?"

**Answer:** "By being direct. The Part A commitment described a specific architectural claim about biological mediation. In practice, ClinPGx enforces that mediation architecturally by not curating direct drug-phenotype edges. So the architectural commitment was met by construction. What we evaluate is a proxy — whether the model prioritises phenotype-relevant genes above naive baselines. I think this framing is defensible if it's clear in Part B."

### Q: "What if we asked for a stronger positive finding?"

**Answer:** "Honestly — I don't think I have one beyond what I've shown. The pattern of D1-D3 shows method-level choices don't beat baselines. D4 shows SMILES effect. D5 has 43 model-only pathways and 17.5% literature support. That's what the data says. Adding more experiments this late is scope creep. I'd prefer to write up what we have honestly."

---

## Delivery tips

- **Speak from the outline**, not the slides. Look at your audience, not the screen.
- **Pause between sections.** Don't rush transitions.
- **When discussing D3 or the null check**, slow down. Direct honesty needs pacing to land.
- **On the SMILES slide (13)**, this is your positive finding. Show confidence.
- **Don't apologise for null findings.** State them as facts.
- **Ask for feedback specifically** on the four items in slide 24. Don't be vague.

