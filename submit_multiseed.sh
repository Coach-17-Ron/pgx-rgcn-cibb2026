#!/bin/bash
# =====================================================================
# Submit three seeded runs of the main protocol (β=0.005, dg_context).
# Each run gets a separate SLURM job and a unique RUN_ID folder.
#
# Usage: bash submit_multiseed.sh
# Watch: squeue -u kmolepo
# =====================================================================

set -euo pipefail
cd "$HOME/MLPKGA007_v2"

for seed in 42 123 2026; do
    sbatch \
        --job-name=pgx_v2_seed${seed} \
        --account=b181-humgen-ag \
        --partition=Main \
        --cpus-per-task=8 \
        --mem=48GB \
        --time=08:00:00 \
        --output=rgcn_v2_seed${seed}_%j.log \
        --wrap="
            set -e
            cd $HOME/MLPKGA007_v2
            singularity exec --nv \
                /idia/software/containers/ASTRO-GPU-PyTorch-2026-01-28.sif \
                bash -c '
                    pip install --user --quiet torch-geometric==2.5.0 \
                        networkx==3.2.1 pyarrow==15.0.0 2>&1 | tail -5
                    python3 pgx_pipeline_combined.py \
                        --data_dir ./data --results_dir ./results \
                        --split_mode dg_context \
                        --seed ${seed} \
                        --pubmed_email mlpkga007@myuct.ac.za \
                        --stages all
                '
        "
    echo "Submitted seed=${seed}"
    sleep 2  # rate-limit job submissions
done

echo "All three seeded jobs submitted."
echo "Monitor with: squeue -u kmolepo"
