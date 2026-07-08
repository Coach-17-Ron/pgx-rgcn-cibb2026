### D2 — Hub-Penalty Ablation Analysis

#### Methodology

Our loss combines a margin-based ranking loss with a hub-penalty term:

L = margin_ranking_loss(pos, neg, y=+1, margin=1) + β * mean(σ(neg_score) * hub_weight)

where hub_weight is the normalised degree distribution across genes. The 
CIBB paper used β = 0.10 as the default. In the CIBB β sweep (0.005, 0.05, 
0.10, 0.20), MRR was observed to be insensitive to β within the tested 
range, but β = 0 was not explicitly evaluated.

To determine whether the hub-penalty term contributes any measurable 
value beyond the degree-aware negative sampling (which already discourages 
high-degree targets via the deg^0.75 weighting from Bordes et al. 2013), 
we ran the pipeline with the --ablation_beta_zero flag at three seeds 
(42, 123, 2026). All other hyperparameters were held identical to the 
default D1 runs (default regime, no fingerprints, dg_context split, 
100 epochs).

We compared filtered MRR mean ± standard deviation across seeds, using 
the pooled standard deviation as the effect-size reference.

#### Results

At β = 0.10: filtered MRR = 0.090 ± 0.020 (n=3 seeds).
At β = 0.00: filtered MRR = 0.082 ± 0.016 (n=3 seeds).

The difference (-0.008) is less than half of the pooled SD (0.018), 
indicating that **the hub-penalty term has no measurable effect on 
cold-drug ranking beyond that provided by the degree-aware sampling 
distribution**.

This confirms and extends the CIBB β sweep finding: not only is the 
model insensitive to the specific value of β within the tested range, 
it is also insensitive to whether the hub-penalty term is present at 
all. The observed effect is smaller than the intra-condition seed 
variance.

#### Implication

The degree-aware negative sampling alone is sufficient to prevent 
overfitting to high-degree ADME pharmacogenes. The additional hub-
penalty term in the loss can be dropped without loss of performance, 
simplifying the loss architecture. This has implications for future 
work extending the pipeline: focus should be on improving graph 
structure, feature representation, and evaluation protocol rather than 
on refining the hub-penalty formulation.

