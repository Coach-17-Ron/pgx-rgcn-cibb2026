#!/bin/bash
# Round 3 multi-seed sweep: same config as the headline run (β=0.10,
# dg_context, fingerprints attached), three seeds in parallel to measure
# seed variance.

set -euo pipefail

for seed in 42 123 2026; do
    sbatch \
        --job-name=pgx_r3_s${seed} \
        --account=b181-humgen-ag \
        --partition=Main \
        --cpus-per-task=8 \
        --mem=48GB \
        --time=04:00:00 \
        --output="rgcn_r3_seed${seed}_%j.log" \
        --wrap="
            set -e
            cd \"\$HOME/MLPKGA007_v2\"
            singularity exec /idia/software/containers/ASTRO-GPU-PyTorch-2026-01-28.sif bash -c '
                pip install --user --quiet torch-geometric==2.5.0 networkx==3.2.1 pyarrow==15.0.0 rdkit 2>&1 | tail -3
                python3 pgx_pipeline_combined.py \
                    --data_dir ./data \
                    --results_dir ./results \
                    --split_mode dg_context \
                    --seed ${seed} \
                    --hub_penalty_beta 0.10 \
                    --pubmed_email mlpkga007@myuct.ac.za \
                    --stages all
            '
        "
    echo "Submitted seed ${seed}"
    sleep 2
done

squeue -u kmolepo
