#!/bin/bash
# =====================================================================
# SLURM batch script - β=0 ABLATION (no hub penalty)
# Submit after run_rgcn_v2.sh has completed and you've sanity-checked
# the main results.
# =====================================================================
#SBATCH --job-name=pgx_v2_beta0
#SBATCH --account=b181-humgen-ag
#SBATCH --partition=Main
#SBATCH --cpus-per-task=8
#SBATCH --mem=48GB
#SBATCH --time=08:00:00
#SBATCH --output=rgcn_v2_beta0_%j.log

set -euo pipefail
CONTAINER=/idia/software/containers/ASTRO-GPU-PyTorch-2026-01-28.sif
WORKDIR=$HOME/MLPKGA007_v2
PUBMED_EMAIL="mlpkga007@myuct.ac.za"   # EDIT to your real address

cd "$WORKDIR"
echo "β=0 ablation started: $(date)"

singularity exec --nv "$CONTAINER" bash -c "
    set -e
    pip install --user --quiet \
        torch-geometric==2.5.0 networkx==3.2.1 pyarrow==15.0.0 2>&1 | tail -5
    python3 pgx_pipeline_combined.py \
        --data_dir ./data --results_dir ./results \
        --split_mode dg_context --seed 42 \
        --hub_penalty_beta 0.0 \
        --pubmed_email $PUBMED_EMAIL --stages all
"
echo "β=0 ablation finished: $(date)"
