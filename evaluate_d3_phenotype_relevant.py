"""
D3: Phenotype-relevant gene ranking evaluation.

For a given run folder, compute filtered/raw MRR/Hits@K on the
phenotype-relevant gene subset (genes with at least one gene->phenotype
edge in ClinPGx). Reports against two baselines.

Usage:
    python3 evaluate_d3_phenotype_relevant.py --run_dir results/YYYYMMDD_...
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

# Import the model class from the main pipeline (must be in same directory)
sys.path.insert(0, str(Path(__file__).parent))
from pgx_pipeline_combined import (
    PGx_RGCN,
    load_config,
    setup_logger,
    load_drug_fingerprints,
)


def parse_args():
    p = argparse.ArgumentParser(
        description="D3 phenotype-relevant gene ranking evaluation.",
    )
    p.add_argument("--run_dir", required=True,
                   help="Path to a completed run folder "
                        "(must contain artifacts/model_checkpoint.pt)")
    p.add_argument("--top_k", type=int, nargs="+", default=[1, 3, 5, 10],
                   help="K values for Hits@K")
    return p.parse_args()


def load_run_data(run_dir):
    """Load all artifacts from a completed run."""
    artifacts = Path(run_dir) / "artifacts"
    
    logger.info(f"Loading artifacts from {artifacts}")
    
    # Split assignments (test positives are here)
    split_assignments = pd.read_parquet(artifacts / "split_assignments.parquet")
    logger.info(f"  split_assignments: {len(split_assignments)} rows")
    
    # Edges and nodes
    edges = pd.read_parquet(artifacts / "edges.parquet")
    nodes = pd.read_parquet(artifacts / "nodes.parquet")
    logger.info(f"  edges: {len(edges)}, nodes: {len(nodes)}")
    
    # Model checkpoint
    ckpt_path = artifacts / "model_checkpoint.pt"
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    logger.info(f"  checkpoint loaded")
    
    # Homogeneous tensors (for direct scoring)
    homog = torch.load(artifacts / "homogeneous_tensors.pt",
                       map_location="cpu", weights_only=False)
    logger.info(f"  homogeneous tensors loaded")
    
    # PyG edge type mapping (for scoring)
    with open(artifacts / "pyg_edge_type_mapping.json") as f:
        pyg_map = json.load(f)
    
    return {
        "split_assignments": split_assignments,
        "edges": edges,
        "nodes": nodes,
        "ckpt": ckpt,
        "homog": homog,
        "pyg_map": pyg_map,
        "run_dir": Path(run_dir),
    }


def get_phenotype_relevant_genes(edges, nodes):
    """
    Return set of gene node_indexes with >=1 gene->phenotype edge.
    """
    gp_edges = edges[
        (edges["source_type"] == "gene") &
        (edges["target_type"] == "phenotype")
    ]
    pg_edges = edges[
        (edges["source_type"] == "phenotype") &
        (edges["target_type"] == "gene")
    ]
    
    gene_ids_from_gp = set(gp_edges["source_idx"].astype(int).tolist())
    gene_ids_from_pg = set(pg_edges["target_idx"].astype(int).tolist())
    
    phenotype_relevant = gene_ids_from_gp | gene_ids_from_pg
    logger.info(f"Phenotype-relevant genes: {len(phenotype_relevant)}")
    return phenotype_relevant


def get_test_positives(split_assignments, phenotype_relevant_gene_set):
    """
    Get test-set positive drug-gene pairs where the gene is phenotype-relevant.
    """
    # Filter to test split and positive drug-gene edges
    test_pos = split_assignments[
        (split_assignments["split"] == "test") &
        (split_assignments["is_dg_positive"] == True) &
        (split_assignments["source_type"] == "drug") &
        (split_assignments["target_type"] == "gene")
    ].copy()
    
    logger.info(f"Total test drug-gene positives: {len(test_pos)}")
    
    # Further filter to those where the gene is phenotype-relevant
    test_pos["gene_pheno_relevant"] = test_pos["target_idx"].isin(
        phenotype_relevant_gene_set
    )
    filtered = test_pos[test_pos["gene_pheno_relevant"]].reset_index(drop=True)
    logger.info(f"Test positives with phenotype-relevant target genes: {len(filtered)}")
    
    return filtered


def build_known_positives_map(split_assignments, phenotype_relevant_gene_set):
    """
    For filtered evaluation: for each drug (global ID), get set of 
    phenotype-relevant genes (global IDs) that are already positive.
    """
    all_pos = split_assignments[
        (split_assignments["is_dg_positive"] == True) &
        (split_assignments["source_type"] == "drug") &
        (split_assignments["target_type"] == "gene")
    ]
    
    known_map = {}
    for _, row in all_pos.iterrows():
        drug_global = int(row["source_idx"])   # already global
        gene_global = int(row["target_idx"])   # already global
        if gene_global in phenotype_relevant_gene_set:
            if drug_global not in known_map:
                known_map[drug_global] = set()
            known_map[drug_global].add(gene_global)
    return known_map


def build_model_from_checkpoint(ckpt, homog, pyg_map, cfg, drug_offset):
    """
    Reconstruct the PGx_RGCN model from checkpoint.
    Uses hyperparameters saved with the checkpoint plus the config.
    """
    # Read hyperparameters from checkpoint (authoritative)
    num_edge_types = int(ckpt["num_edge_types"])
    num_decoder_relations = int(ckpt["num_decoder_relations"])
    use_fp = bool(ckpt.get("use_fingerprints", False))
    drug_fp_dim = int(ckpt.get("drug_fp_dim", 0)) if use_fp else None
    n_drugs_for_fp = int(ckpt.get("n_drugs_for_fp", 0)) if use_fp else 0
    
    # Read hyperparameters from config
    embedding_dim = int(cfg["model"]["embedding_dim"])
    hidden_dim = int(cfg["model"]["hidden_dim"])
    output_dim = int(cfg["model"]["output_dim"])
    num_bases = int(cfg["model"]["num_bases"])
    dropout = float(cfg["model"]["dropout"])
    
    model = PGx_RGCN(
        in_channels=embedding_dim,
        hidden_channels=hidden_dim,
        out_channels=output_dim,
        num_edge_types=num_edge_types,
        num_decoder_relations=num_decoder_relations,
        num_bases=num_bases,
        dropout=dropout,
        drug_fp_dim=drug_fp_dim,
        n_drugs_for_fp=n_drugs_for_fp,
    )
    
    # Load state (checkpoint key is "model_state", not "model_state_dict")
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    
    # If model uses fingerprints, the buffers are already loaded from state.
    # We just need to set drug_offset so the encode() method works correctly.
    if use_fp:
        model.drug_offset = int(drug_offset)
    
    return model, num_edge_types


def encode_once(model, homog):
    """Run the encoder once to get z (node embeddings), following CIBB approach."""
    with torch.no_grad():
        z = model.encode(homog["x"], homog["edge_index"], homog["edge_type"])
    return z


def score_drug_against_genes(model, z, drug_global_idx, gene_global_indexes,
                              rel_idx):
    """
    Score one drug against a set of genes using a specific relation.
    Uses DistMult scoring directly (like CIBB evaluate_mrr).
    Returns numpy array of scores.
    """
    device = z.device
    n_targets = len(gene_global_indexes)
    
    head_global = torch.tensor([drug_global_idx], dtype=torch.long, device=device)
    tail_global = torch.tensor(gene_global_indexes, dtype=torch.long, device=device)
    rel_idx_t = torch.tensor([rel_idx], dtype=torch.long, device=device)
    
    with torch.no_grad():
        head_emb = z[head_global].expand(n_targets, -1)
        tail_emb = z[tail_global]
        rel_emb = model.decoder.rel_emb(rel_idx_t).expand(n_targets, -1)
        scores = (head_emb * rel_emb * tail_emb).sum(dim=-1)
    return scores.cpu().numpy()


def compute_mrr_hits(ranks, ks=(1, 3, 5, 10)):
    """Given array of ranks (1-indexed), compute MRR and Hits@K."""
    ranks = np.asarray(ranks, dtype=float)
    ranks = ranks[ranks > 0]  # sanity
    mrr = float(np.mean(1.0 / ranks)) if len(ranks) > 0 else 0.0
    hits = {}
    for k in ks:
        hits[f"hits_at_{k}"] = float(np.mean(ranks <= k))
    return {"mrr": mrr, "n_queries": len(ranks), **hits}


def compute_drug_gene_degree_baseline(edges, gene_indexes_pool):
    """
    Baseline: rank phenotype-relevant genes by their drug-gene degree.
    """
    dg_edges = edges[
        (edges["source_type"] == "drug") &
        (edges["target_type"] == "gene")
    ]
    gene_degrees = dg_edges["target_idx"].value_counts()
    
    # Return dict: gene_idx -> degree
    return {int(g): int(gene_degrees.get(g, 0)) for g in gene_indexes_pool}


def compute_gene_phenotype_degree_baseline(edges, gene_indexes_pool):
    """
    Baseline: rank phenotype-relevant genes by their gene-phenotype degree.
    """
    gp_edges = edges[
        (edges["source_type"] == "gene") &
        (edges["target_type"] == "phenotype")
    ]
    gene_degrees = gp_edges["source_idx"].value_counts()
    
    return {int(g): int(gene_degrees.get(g, 0)) for g in gene_indexes_pool}


def evaluate_baseline(test_pos, baseline_scores, known_map, drug_offset,
                       gene_indexes_pool_list, ks=(1, 3, 5, 10)):
    """
    Compute MRR/Hits using a fixed baseline score per gene.
    IDs are ALREADY GLOBAL (from split_assignments / edges); no offsetting needed.
    """
    raw_ranks = []
    filt_ranks = []
    
    # Convert to numpy for speed
    pool_array = np.array(gene_indexes_pool_list)
    scores_array = np.array([baseline_scores[int(g)] for g in pool_array],
                             dtype=float)
    # Sort once by score descending
    order = np.argsort(-scores_array, kind="stable")
    sorted_genes = pool_array[order]
    
    # For each test positive, find rank
    for _, row in test_pos.iterrows():
        drug_global = int(row["source_idx"])   # already global
        target_gene = int(row["target_idx"])   # already global
        
        # Raw rank
        raw_rank_arr = np.where(sorted_genes == target_gene)[0]
        if len(raw_rank_arr) > 0:
            raw_ranks.append(int(raw_rank_arr[0]) + 1)
        
        # Filtered rank (remove other known positives for this drug)
        excluded = known_map.get(drug_global, set()) - {target_gene}
        if excluded:
            mask = ~np.isin(sorted_genes, list(excluded))
            filt_sorted = sorted_genes[mask]
            filt_rank_arr = np.where(filt_sorted == target_gene)[0]
            if len(filt_rank_arr) > 0:
                filt_ranks.append(int(filt_rank_arr[0]) + 1)
        else:
            # No known positives to filter; use raw rank
            if len(raw_rank_arr) > 0:
                filt_ranks.append(int(raw_rank_arr[0]) + 1)
    
    return {
        "raw": compute_mrr_hits(raw_ranks, ks),
        "filtered": compute_mrr_hits(filt_ranks, ks),
    }


def main():
    global logger
    args = parse_args()
    run_dir = Path(args.run_dir)
    
    # Setup logger
    log_path = run_dir / "d3_evaluation.log"
    logger = setup_logger(log_path, name="d3_evaluator")
    
    logger.info(f"=== D3 Phenotype-Relevant Gene Ranking Evaluation ===")
    logger.info(f"Run directory: {run_dir}")
    
    # Load all artifacts
    data = load_run_data(run_dir)
    
    # Load original run config for model construction
    with open(run_dir / "run_config.json") as f:
        cfg = json.load(f)
    
    # Identify phenotype-relevant genes
    pheno_relevant = get_phenotype_relevant_genes(data["edges"], data["nodes"])
    pheno_relevant_list = sorted(pheno_relevant)
    
    # Get test positives (drug-gene positives where gene is phenotype-relevant)
    test_pos = get_test_positives(data["split_assignments"], pheno_relevant)
    
    if len(test_pos) == 0:
        logger.error("No test positives with phenotype-relevant genes. Cannot evaluate.")
        return
    
    # Build known positives map for filtered evaluation
    known_map = build_known_positives_map(
        data["split_assignments"], pheno_relevant
    )
    
    # Node offsets (from graph structure)
    nodes = data["nodes"]
    node_offsets = {}
    off = 0
    for nt in ["drug", "gene", "variant", "phenotype"]:
        node_offsets[nt] = off
        off += (nodes["node_type"] == nt).sum()
    drug_offset = node_offsets["drug"]
    gene_offset = node_offsets["gene"]
    n_drugs = (nodes["node_type"] == "drug").sum()
    n_genes = (nodes["node_type"] == "gene").sum()
    logger.info(f"drug_offset={drug_offset}, gene_offset={gene_offset}")
    logger.info(f"n_drugs={n_drugs}, n_genes={n_genes}")
    
    # Build model
    model, num_edge_types = build_model_from_checkpoint(
        data["ckpt"], data["homog"], data["pyg_map"], cfg, drug_offset
    )
    logger.info(f"Model built with {num_edge_types} edge types")
    
    # Encode once (fast — one forward pass of the RGCN encoder)
    logger.info("Running encoder forward pass...")
    z = encode_once(model, data["homog"])
    logger.info(f"Encoded {z.size(0)} node embeddings")
    
    # IMPORTANT: source_idx / target_idx in split_assignments and edges.parquet
    # are ALREADY GLOBAL indices (gene IDs are 5210-30250, etc). Do NOT add
    # gene_offset when using them.
    logger.info(f"Scoring {len(test_pos)} test positives...")
    
    pheno_relevant_array = np.array(pheno_relevant_list)
    
    raw_ranks = []
    filt_ranks = []
    
    for i, row in test_pos.reset_index(drop=True).iterrows():
        drug_global = int(row["source_idx"])   # already global (0-5209 for drugs)
        target_gene = int(row["target_idx"])   # already global (5210-30250 for genes)
        rel_idx = int(row["rel_idx"])          # THIS EDGE'S OWN relation
        
        # Score this drug against all phenotype-relevant genes using this rel
        # (pheno_relevant_list contains global gene IDs from edges.parquet)
        scores = score_drug_against_genes(
            model, z, drug_global, pheno_relevant_list, rel_idx,
        )
        
        # Rank genes by score descending
        order = np.argsort(-scores, kind="stable")
        sorted_gene_indexes = pheno_relevant_array[order]
        
        # Raw rank
        raw_rank_arr = np.where(sorted_gene_indexes == target_gene)[0]
        if len(raw_rank_arr) == 0:
            continue
        raw_rank = int(raw_rank_arr[0]) + 1
        raw_ranks.append(raw_rank)
        
        # Filtered rank (exclude drug's other known positives, keep this target)
        excluded = known_map.get(drug_global, set()) - {target_gene}
        if excluded:
            mask = ~np.isin(sorted_gene_indexes, list(excluded))
            filt_sorted = sorted_gene_indexes[mask]
            filt_rank_arr = np.where(filt_sorted == target_gene)[0]
            if len(filt_rank_arr) > 0:
                filt_ranks.append(int(filt_rank_arr[0]) + 1)
        else:
            filt_ranks.append(raw_rank)
        
        if (i + 1) % 100 == 0:
            logger.info(f"  Scored {i+1}/{len(test_pos)} test positives")
    
    logger.info(f"Total test-positive rankings computed: raw={len(raw_ranks)}, filtered={len(filt_ranks)}")
    
    # Compute metrics
    model_metrics = {
        "raw": compute_mrr_hits(raw_ranks, args.top_k),
        "filtered": compute_mrr_hits(filt_ranks, args.top_k),
    }
    
    # Compute baselines
    logger.info("Computing baselines...")
    dg_degree_baseline = compute_drug_gene_degree_baseline(
        data["edges"], pheno_relevant_list
    )
    gp_degree_baseline = compute_gene_phenotype_degree_baseline(
        data["edges"], pheno_relevant_list
    )
    
    baseline_dg = evaluate_baseline(
        test_pos, dg_degree_baseline, known_map, drug_offset,
        pheno_relevant_list, args.top_k,
    )
    baseline_gp = evaluate_baseline(
        test_pos, gp_degree_baseline, known_map, drug_offset,
        pheno_relevant_list, args.top_k,
    )
    
    # Assemble results
    results = {
        "run_dir": str(run_dir),
        "n_phenotype_relevant_genes": len(pheno_relevant_list),
        "n_test_positives_evaluated": len(raw_ranks),
        "n_unique_test_drugs": int(test_pos["source_idx"].nunique()),
        "model": model_metrics,
        "baseline_drug_gene_degree": baseline_dg,
        "baseline_gene_phenotype_degree": baseline_gp,
    }
    
    # Save results
    out_path = run_dir / "artifacts" / "d3_phenotype_metrics.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"\n=== D3 RESULTS ===")
    logger.info(f"Phenotype-relevant gene pool size: {len(pheno_relevant_list)}")
    logger.info(f"Test positives evaluated: {len(raw_ranks)}")
    logger.info(f"MODEL raw     MRR: {model_metrics['raw']['mrr']:.4f}")
    logger.info(f"MODEL filtered MRR: {model_metrics['filtered']['mrr']:.4f}")
    logger.info(f"MODEL raw H@10: {model_metrics['raw']['hits_at_10']:.4f}")
    logger.info(f"MODEL filt H@10: {model_metrics['filtered']['hits_at_10']:.4f}")
    logger.info(f"BASELINE (drug-gene degree) raw MRR:      {baseline_dg['raw']['mrr']:.4f}")
    logger.info(f"BASELINE (drug-gene degree) filtered MRR: {baseline_dg['filtered']['mrr']:.4f}")
    logger.info(f"BASELINE (gene-phenotype degree) raw MRR:      {baseline_gp['raw']['mrr']:.4f}")
    logger.info(f"BASELINE (gene-phenotype degree) filtered MRR: {baseline_gp['filtered']['mrr']:.4f}")
    logger.info(f"\nResults saved to: {out_path}")


if __name__ == "__main__":
    main()
