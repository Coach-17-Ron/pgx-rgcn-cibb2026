"""
Compose integrated per-prediction explanations from existing artefacts.

For each of the top-N novel predictions, combine:
1. Model score + rank (from novel_predictions.parquet)
2. Structural graph paths + shared genes (from explanations.parquet)
3. Pathway enrichment hits for the predicted gene (from pathway_enrichment.parquet)
4. PubMed literature evidence for the drug-gene pair (from literature_evidence.parquet)

Output: integrated_explanations.parquet + integrated_explanations.csv
"""

import argparse
import pandas as pd
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--run_dir", required=True)
    return p.parse_args()


def main():
    args = parse_args()
    run_dir = Path(args.run_dir).absolute()
    artifacts = run_dir / "artifacts"
    
    print(f"=== Composing Integrated Explanations ===")
    print(f"Run: {run_dir}")
    
    # Load all four sources
    novel = pd.read_parquet(artifacts / "novel_predictions.parquet")
    expl = pd.read_parquet(artifacts / "explanations.parquet")
    pathway = pd.read_parquet(artifacts / "pathway_enrichment.parquet")
    lit = pd.read_parquet(artifacts / "literature_evidence.parquet")
    
    print(f"  novel_predictions: {len(novel)} rows")
    print(f"  explanations: {len(expl)} rows (top-50)")
    print(f"  pathway_enrichment: {len(pathway)} rows")
    print(f"  literature_evidence: {len(lit)} rows")
    print()
    
    # Get significant pathways only (BH-FDR)
    sig_pathways = pathway[pathway["significant"] == True].copy()
    print(f"Significant pathways: {len(sig_pathways)}")
    
    # For each pathway, we don't have gene lists in the parquet (that's in gmt files)
    # But we CAN check which pathways each gene appears in via the pathway data
    # Actually — the sig_pathways table has ONE row per pathway that IS significant.
    # We need to know: for gene X, which sig pathways does it belong to?
    # This requires loading gene_sets and matching. Let's do that.
    
    # Load pathway gene sets (same code as Stage 5)
    import sys
    sys.path.insert(0, ".")
    from pgx_pipeline_combined import load_gene_sets, setup_logger
    import logging
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("integrator")
    
    pathways_dir = Path("data/pathways")
    gene_sets = load_gene_sets(pathways_dir, logger)
    print(f"Loaded {len(gene_sets)} gene sets from pathway files")
    
    # Build gene -> [significant pathways] mapping
    sig_pathway_names = set(sig_pathways["pathway"].tolist())
    gene_to_sig_pathways = {}
    for pname, genes in gene_sets.items():
        if pname in sig_pathway_names:
            for g in genes:
                if g not in gene_to_sig_pathways:
                    gene_to_sig_pathways[g] = []
                gene_to_sig_pathways[g].append(pname)
    print(f"Gene→sig-pathway map: {len(gene_to_sig_pathways)} genes with sig pathway membership")
    print()
    
    # Build drug-gene pair -> literature articles map
    pair_to_articles = {}
    for _, row in lit.iterrows():
        if row.get("pmid") and str(row["pmid"]) != "":
            key = (row["drug_name"], row["gene_name"])
            if key not in pair_to_articles:
                pair_to_articles[key] = []
            pair_to_articles[key].append({
                "pmid": row["pmid"],
                "year": row.get("year"),
                "title": (row.get("title") or "")[:100],
            })
    print(f"Drug-gene pairs with literature: {len(pair_to_articles)}")
    print()
    
    # Now compose integrated rows for each top-N explanation
    integrated_rows = []
    for _, row in expl.iterrows():
        drug_name = row.get("drug_name", "")
        gene_name = row.get("gene_name", "")
        gene_upper = gene_name.upper() if gene_name else ""
        
        # Structural: path info from expl
        struct = {
            "shortest_path_length": row.get("shortest_path_length"),
            "shortest_paths": row.get("shortest_paths"),
            "n_shared_genes": row.get("n_shared_genes"),
        }
        
        # Pathway: which sig pathways does this gene belong to?
        sig_paths = gene_to_sig_pathways.get(gene_upper, [])
        pathway_info = {
            "n_sig_pathways": len(sig_paths),
            "top_sig_pathways": " | ".join(sig_paths[:5]) if sig_paths else "",
        }
        
        # Literature: articles for this pair
        articles = pair_to_articles.get((drug_name, gene_name), [])
        lit_info = {
            "n_articles": len(articles),
            "top_pmids": ", ".join(str(a["pmid"]) for a in articles[:3]) if articles else "",
            "top_article_years": ", ".join(str(int(a["year"])) if a.get("year") else "?" 
                                            for a in articles[:3]) if articles else "",
        }
        
        # Combine
        integrated_rows.append({
            "rank": row.get("rank"),
            "drug_node_index": row.get("drug_node_index"),
            "gene_node_index": row.get("gene_node_index"),
            "drug_name": drug_name,
            "gene_name": gene_name,
            "model_score": row.get("model_score"),
            **struct,
            **pathway_info,
            **lit_info,
        })
    
    integrated = pd.DataFrame(integrated_rows).sort_values("rank")
    
    # Save
    out_parquet = artifacts / "integrated_explanations.parquet"
    out_csv = artifacts / "integrated_explanations.csv"
    integrated.to_parquet(out_parquet, index=False)
    integrated.to_csv(out_csv, index=False)
    
    print(f"Saved: {out_parquet}")
    print(f"Saved: {out_csv}")
    print()
    print("=== Sample: Top-5 integrated explanations ===")
    for _, row in integrated.head(5).iterrows():
        print(f"\nRank {int(row['rank'])}: {row['drug_name']} -> {row['gene_name']}")
        print(f"  Model score: {row['model_score']:.4f}")
        print(f"  Path length: {row['shortest_path_length']} hops, shared genes: {int(row['n_shared_genes']) if pd.notna(row['n_shared_genes']) else 'N/A'}")
        if row['shortest_paths']:
            first_path = row['shortest_paths'].split(' || ')[0]
            print(f"  Path: {first_path}")
        print(f"  Sig pathways for gene: {int(row['n_sig_pathways'])}")
        if row['top_sig_pathways']:
            first_pw = row['top_sig_pathways'].split(' | ')[0]
            print(f"    First: {first_pw[:80]}")
        print(f"  Literature articles: {int(row['n_articles'])}")
        if row['top_pmids']:
            print(f"    PMIDs: {row['top_pmids']} ({row['top_article_years']})")
    
    print()
    print("=== Summary ===")
    n_with_path = (integrated["shortest_path_length"].notna()).sum()
    n_with_pw = (integrated["n_sig_pathways"] > 0).sum()
    n_with_lit = (integrated["n_articles"] > 0).sum()
    n_all_three = ((integrated["shortest_path_length"].notna()) & 
                   (integrated["n_sig_pathways"] > 0) & 
                   (integrated["n_articles"] > 0)).sum()
    print(f"Predictions with graph path:      {n_with_path}/{len(integrated)}")
    print(f"Predictions with pathway support: {n_with_pw}/{len(integrated)}")
    print(f"Predictions with literature:      {n_with_lit}/{len(integrated)}")
    print(f"Predictions with ALL THREE:       {n_all_three}/{len(integrated)}")


if __name__ == "__main__":
    main()
