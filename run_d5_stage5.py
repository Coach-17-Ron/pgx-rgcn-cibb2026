"""
D5: Run Stage 5 (contextualisation) on an existing completed run folder.

Two modes:
  --pathway_only: Skip literature (D5-Part 2). Fast, no API queries.
  (default):      Full Stage 5 including literature + pathway (D5-Part 1).

Usage:
  # D5-Part 2 (pathway only):
  python3 run_d5_stage5.py --run_dir results/YYYYMMDD_... --pathway_only

  # D5-Part 1 (full):
  python3 run_d5_stage5.py --run_dir results/YYYYMMDD_...
"""

import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parent))
from pgx_pipeline_combined import (
    run_stage_05_contextualise,
    setup_logger,
)


def parse_args():
    p = argparse.ArgumentParser(description="D5 Stage 5 wrapper.")
    p.add_argument("--run_dir", required=True,
                   help="Path to an existing completed run folder")
    p.add_argument("--pathway_only", action="store_true",
                   help="Skip literature queries (D5-Part 2 mode)")
    p.add_argument("--pubmed_email", default="mlpkga007@myuct.ac.za",
                   help="Email for NCBI Entrez / EuroPMC")
    p.add_argument("--top_n", type=int, default=None,
                   help="Override number of top predictions to contextualise")
    return p.parse_args()


def main():
    cli_args = parse_args()
    run_dir = Path(cli_args.run_dir).absolute()
    
    with open(run_dir / "run_config.json") as f:
        cfg = json.load(f)
    
    paths = {
        "results_dir": run_dir,
        "artifacts_dir": run_dir / "artifacts",
        "logs_dir": run_dir / "logs",
        "figures_dir": run_dir / "figures",
        "data_dir": Path("./data").absolute(),
        "run_id": run_dir.name,
    }
    
    paths["logs_dir"].mkdir(exist_ok=True)
    paths["figures_dir"].mkdir(exist_ok=True)
    
    stage5_log = paths["logs_dir"] / "d5_stage_05.log"
    logger = setup_logger(stage5_log, name="d5_contextualise")
    
    logger.info(f"=== D5 Stage 5 (Contextualisation) ===")
    logger.info(f"Existing run: {run_dir}")
    logger.info(f"pathway_only: {cli_args.pathway_only}")
    logger.info(f"pubmed_email: {cli_args.pubmed_email}")
    
    novel_path = paths["artifacts_dir"] / "novel_predictions.parquet"
    nodes_path = paths["artifacts_dir"] / "nodes.parquet"
    if not novel_path.exists():
        logger.error(f"Missing: {novel_path}")
        sys.exit(1)
    if not nodes_path.exists():
        logger.error(f"Missing: {nodes_path}")
        sys.exit(1)
    logger.info(f"Inputs found.")
    
    stage5_args = SimpleNamespace(
        skip_literature=cli_args.pathway_only,
        pubmed_email=cli_args.pubmed_email,
        top_n=cli_args.top_n,
    )
    
    # Override pubmed_email in cfg if provided
    if "contextualisation" in cfg and "literature" in cfg["contextualisation"]:
        cfg["contextualisation"]["literature"]["pubmed_email"] = cli_args.pubmed_email
    
    logger.info("Starting Stage 5...")
    run_stage_05_contextualise(cfg, paths, logger, stage5_args)
    logger.info("Stage 5 complete.")
    
    logger.info("=== Outputs ===")
    for f in [
        "literature_evidence.parquet",
        "literature_evidence.csv",
        "pathway_enrichment.parquet",
        "predictions_with_literature.parquet",
    ]:
        path = paths["artifacts_dir"] / f
        if path.exists():
            size_kb = path.stat().st_size // 1024
            logger.info(f"  {f}: {size_kb} KB")


if __name__ == "__main__":
    main()
