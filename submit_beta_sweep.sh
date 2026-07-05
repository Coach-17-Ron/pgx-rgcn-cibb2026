#!/bin/bash
# Submit three concurrent jobs at β = 0.05, 0.1, 0.2 — stronger hub penalties.
# Each gets its own auto-tagged RUN_ID and runs the full pipeline.

set -euo pipefail

for beta in 0.05 0.1 0.2; do
    # Sanitise beta for the job name (0.05 -> 0p05)
    beta_tag="${beta//./p}"
    sbatch \
        --job-name=pgx_v2_b${beta_tag} \
        --account=b181-humgen-ag \
        --partition=Main \
        --cpus-per-task=8 \
        --mem=48GB \
        --time=04:00:00 \
        --output="rgcn_v2_b${beta_tag}_%j.log" \
        --wrap="
            set -e
            cd \"\$HOME/MLPKGA007_v2\"
            singularity exec /idia/software/containers/ASTRO-GPU-PyTorch-2026-01-28.sif \
                bash -c '
                    pip install --user --quiet torch-geometric==2.5.0 \
                        networkx==3.2.1 pyarrow==15.0.0 2>&1 | tail -3
                    python3 pgx_pipeline_combined.py \
                        --data_dir ./data --results_dir ./results \
                        --split_mode dg_context \
                        --seed 42 \
                        --hub_penalty_beta ${beta} \
                        --pubmed_email mlpkga007@myuct.ac.za \
                        --stages all
                '
        "
    echo "Submitted β=${beta}"
    sleep 2
done

squeue -u kmolepo
