#!/bin/bash
#SBATCH --job-name=pgx_v3_fp
#SBATCH --account=b181-humgen-ag
#SBATCH --partition=Main
#SBATCH --cpus-per-task=8
#SBATCH --mem=48GB
#SBATCH --time=04:00:00
#SBATCH --output=rgcn_v3_fp_%j.log

set -euo pipefail
cd "$HOME/MLPKGA007_v2"
echo "Round 3 (fingerprints, β=0.10) started: $(date)"
singularity exec /idia/software/containers/ASTRO-GPU-PyTorch-2026-01-28.sif bash -c "
    pip install --user --quiet torch-geometric==2.5.0 networkx==3.2.1 pyarrow==15.0.0 rdkit 2>&1 | tail -3
    python3 pgx_pipeline_combined.py \
        --data_dir ./data \
        --results_dir ./results \
        --split_mode dg_context \
        --seed 42 \
        --hub_penalty_beta 0.10 \
        --pubmed_email mlpkga007@myuct.ac.za \
        --stages all
"
echo "Round 3 finished: $(date)"
