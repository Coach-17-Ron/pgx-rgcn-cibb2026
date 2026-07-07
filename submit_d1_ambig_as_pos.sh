#!/bin/bash
#SBATCH --account=b181-humgen-ag
#SBATCH --partition=Main
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=00:45:00
#SBATCH --output=d1_ambig_as_pos_%j.log
#SBATCH --job-name=d1_ambig

cd ~/MLPKGA007_v2_MSC

singularity exec \
    /idia/software/containers/ASTRO-GPU-PyTorch-2026-01-28.sif \
    python3 pgx_pipeline_combined.py \
    --data_dir ./data \
    --seed 42 \
    --hub_penalty_beta 0.10 \
    --supervision_regime ambig_as_pos \
    --split_mode dg_context \
    --stages 1,2,3 \
    --pubmed_email mokumong.lg@gmail.com
