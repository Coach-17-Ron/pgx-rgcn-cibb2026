"""
D5-Part 2 Null Enrichment Check.

Test whether the pathway enrichment observed in D5-Part 2 is:
(A) genuinely from the model's predictions being biologically coherent, or
(B) circular — just re-deriving pathway membership from high-degree genes.

Method: run the same pathway ORA on genes ranked purely by drug-gene degree
(no model involved). Compare significant pathways against model's set.
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from pgx_pipeline_combined import (
    load_gene_sets,
    ora_enrichment,
    setup_logger,
)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--run_dir", required=True,
                   help="Path to reference config run folder")
    p.add_argument("--protein_coding_size", type=int, default=20000,
                   help="Protein-coding gene universe size")
    return p.parse_args()


def main():
    args = parse_args()
    run_dir = Path(args.run_dir).absolute()
    
    log_path = run_dir / "logs" / "null_enrichment.log"
    log_path.parent.mkdir(exist_ok=True)
    logger = setup_logger(log_path, name="null_enrichment")
    
    logger.info("=== Null Enrichment Check (Degree Baseline) ===")
    logger.info(f"Run: {run_dir}")
    
    # Load MODEL's novel predictions (for comparison)
    novel = pd.read_parquet(run_dir / "artifacts" / "novel_predictions.parquet")
    logger.info(f"Loaded {len(novel)} model novel predictions")
    
    # Load nodes to get gene names
    nodes = pd.read_parquet(run_dir / "artifacts" / "nodes.parquet")
    gene_nodes = nodes[nodes["node_type"] == "gene"]
    # Node index -> gene name (upper case for pathway matching)
    gene_idx_to_name = dict(zip(
        gene_nodes["node_index"].astype(int),
        gene_nodes["node_name"].str.upper()
    ))
    logger.info(f"Total genes in graph: {len(gene_idx_to_name)}")
    
    # MODEL'S HIT LIST — unique genes from novel predictions
    model_genes = set(novel["gene_node_index"].astype(int).tolist())
    model_gene_names = {gene_idx_to_name[g] for g in model_genes 
                         if g in gene_idx_to_name}
    logger.info(f"Model unique genes in novel predictions: {len(model_gene_names)}")
    
    # DEGREE BASELINE HIT LIST — top-N genes by drug-gene degree
    edges = pd.read_parquet(run_dir / "artifacts" / "edges.parquet")
    dg_edges = edges[
        (edges["source_type"] == "drug") & 
        (edges["target_type"] == "gene")
    ]
    gene_degree = dg_edges["target_idx"].value_counts()
    
    # Take same number of top-degree genes as model hit list
    n_model = len(model_gene_names)
    top_degree_genes_idx = gene_degree.head(n_model).index.tolist()
    baseline_gene_names = {gene_idx_to_name[int(g)] for g in top_degree_genes_idx
                            if int(g) in gene_idx_to_name}
    logger.info(f"Degree baseline unique genes (top-{n_model} by degree): "
                f"{len(baseline_gene_names)}")
    
    # Overlap between the two sets
    overlap = model_gene_names & baseline_gene_names
    logger.info(f"Overlap between model hits and degree baseline: {len(overlap)} "
                f"({len(overlap)/len(model_gene_names)*100:.1f}% of model set)")
    
    # Load pathway gene sets
    pathways_dir = Path("data/pathways")
    gene_sets = load_gene_sets(pathways_dir, logger)
    logger.info(f"Loaded {len(gene_sets)} pathway gene sets")
    
    # Run ORA on MODEL hit list
    logger.info("Running ORA on model novel predictions...")
    model_ora = ora_enrichment(
        hit_list=model_gene_names,
        gene_sets=gene_sets,
        universe_size=args.protein_coding_size,
        fdr_threshold=0.05,
    )
    model_ora_df = pd.DataFrame(model_ora)
    model_sig = model_ora_df[model_ora_df["significant"] == True]
    logger.info(f"MODEL significant pathways: {len(model_sig)}")
    
    # Run ORA on DEGREE BASELINE hit list
    logger.info("Running ORA on degree baseline (top-N by drug-gene degree)...")
    baseline_ora = ora_enrichment(
        hit_list=baseline_gene_names,
        gene_sets=gene_sets,
        universe_size=args.protein_coding_size,
        fdr_threshold=0.05,
    )
    baseline_ora_df = pd.DataFrame(baseline_ora)
    baseline_sig = baseline_ora_df[baseline_ora_df["significant"] == True]
    logger.info(f"BASELINE significant pathways: {len(baseline_sig)}")
    
    # Save both
    out_model = run_dir / "artifacts" / "null_enrichment_model.parquet"
    out_baseline = run_dir / "artifacts" / "null_enrichment_baseline.parquet"
    model_ora_df.to_parquet(out_model, index=False)
    baseline_ora_df.to_parquet(out_baseline, index=False)
    logger.info(f"Saved model ORA: {out_model}")
    logger.info(f"Saved baseline ORA: {out_baseline}")
    
    # Compare significant pathway sets
    model_sig_pathways = set(model_sig["pathway"].tolist())
    baseline_sig_pathways = set(baseline_sig["pathway"].tolist())
    
    common = model_sig_pathways & baseline_sig_pathways
    model_only = model_sig_pathways - baseline_sig_pathways
    baseline_only = baseline_sig_pathways - model_sig_pathways
    
    logger.info("")
    logger.info("=== COMPARISON ===")
    logger.info(f"Model significant pathways: {len(model_sig_pathways)}")
    logger.info(f"Baseline significant pathways: {len(baseline_sig_pathways)}")
    logger.info(f"Common: {len(common)}")
    logger.info(f"Model only (biology beyond degree): {len(model_only)}")
    logger.info(f"Baseline only (degree without model): {len(baseline_only)}")
    logger.info("")
    
    # By source
    if len(model_sig) > 0 and len(baseline_sig) > 0:
        logger.info("Model significant pathways by source:")
        for src, count in model_sig["source"].value_counts().items():
            logger.info(f"  {src}: {count}")
        logger.info("Baseline significant pathways by source:")
        for src, count in baseline_sig["source"].value_counts().items():
            logger.info(f"  {src}: {count}")
    
    # Sample of model-only pathways (biology beyond degree)
    if len(model_only) > 0:
        logger.info("")
        logger.info(f"Sample of MODEL-ONLY pathways (up to 10):")
        model_only_sample = list(model_only)[:10]
        for p in model_only_sample:
            row = model_sig[model_sig["pathway"] == p].iloc[0]
            logger.info(f"  {p[:70]}  q={row['q_value']:.4f}")
    
    if len(baseline_only) > 0:
        logger.info("")
        logger.info(f"Sample of BASELINE-ONLY pathways (up to 10):")
        baseline_only_sample = list(baseline_only)[:10]
        for p in baseline_only_sample:
            row = baseline_sig[baseline_sig["pathway"] == p].iloc[0]
            logger.info(f"  {p[:70]}  q={row['q_value']:.4f}")


if __name__ == "__main__":
    main()
