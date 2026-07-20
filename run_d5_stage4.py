"""
D5: Run Stage 4 (interpretability) on an existing completed run folder.

Runs both:
  (a) Intrinsic: relation-importance analysis (Frobenius norms of encoder weights)
  (b) Post-hoc: per-prediction structural explanations (BFS graph paths)

Usage:
  python3 run_d5_stage4.py --run_dir results/YYYYMMDD_...
  python3 run_d5_stage4.py --run_dir results/YYYYMMDD_... --top_n 100
"""

import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import torch

sys.path.insert(0, str(Path(__file__).parent))
from pgx_pipeline_combined import (
    run_stage_04_interpret,
    setup_logger,
)


def parse_args():
    p = argparse.ArgumentParser(description="D5 Stage 4 wrapper.")
    p.add_argument("--run_dir", required=True,
                   help="Path to existing completed run folder")
    p.add_argument("--top_n", type=int, default=None,
                   help="Override number of top predictions to explain")
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
    
    stage4_log = paths["logs_dir"] / "d5_stage_04.log"
    logger = setup_logger(stage4_log, name="d5_interpret")
    
    logger.info(f"=== D5 Stage 4 (Interpretability) ===")
    logger.info(f"Existing run: {run_dir}")
    if cli_args.top_n is not None:
        logger.info(f"top_n override: {cli_args.top_n}")
    else:
        logger.info(f"top_n from config: {cfg['interpretation']['top_n_predictions']}")
    
    required = [
        "nodes.parquet", "edges.parquet",
        "homogeneous_tensors.pt", "model_checkpoint.pt",
        "pyg_edge_type_mapping.json", "novel_predictions.parquet",
    ]
    for f in required:
        p = paths["artifacts_dir"] / f
        if not p.exists():
            logger.error(f"Missing: {p}")
            sys.exit(1)
    logger.info(f"All required inputs found.")
    
    stage4_args = SimpleNamespace(top_n=cli_args.top_n)
    device = torch.device("cpu")
    logger.info(f"Device: {device}")
    
    logger.info("Starting Stage 4...")
    run_stage_04_interpret(cfg, paths, logger, stage4_args, device)
    logger.info("Stage 4 complete.")
    
    logger.info("=== Outputs ===")
    for f in ["relation_importance.parquet", "explanations.parquet"]:
        path = paths["artifacts_dir"] / f
        if path.exists():
            size_kb = path.stat().st_size // 1024
            logger.info(f"  {f}: {size_kb} KB")
    
    fig_path = paths["figures_dir"] / "figure_relation_importance.png"
    if fig_path.exists():
        size_kb = fig_path.stat().st_size // 1024
        logger.info(f"  figure_relation_importance.png: {size_kb} KB")


if __name__ == "__main__":
    main()
