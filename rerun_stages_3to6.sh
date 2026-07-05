#!/bin/bash
#SBATCH --job-name=pgx_v2_resume
#SBATCH --account=b181-humgen-ag
#SBATCH --partition=Main
#SBATCH --cpus-per-task=8
#SBATCH --mem=48GB
#SBATCH --time=04:00:00
#SBATCH --output=rgcn_v2_resume_%j.log

set -euo pipefail
cd "$HOME/MLPKGA007_v2"
echo "Resume job started: $(date)"

singularity exec /idia/software/containers/ASTRO-GPU-PyTorch-2026-01-28.sif bash -c "
    pip install --user --quiet torch-geometric==2.5.0 networkx==3.2.1 pyarrow==15.0.0 2>&1 | tail -3
    python3 pgx_pipeline_combined.py \
        --data_dir ./data \
        --results_dir ./results \
        --run_id 20260613_102151_dg_context_beta0p1_seed42 \
        --pubmed_email mlpkga007@myuct.ac.za \
        --stages 4,5,6
"
echo "Resume job finished: $(date)"
