#!/bin/bash
#SBATCH --job-name=pgx_r3_randFP
#SBATCH --account=b181-humgen-ag
#SBATCH --partition=Main
#SBATCH --cpus-per-task=8
#SBATCH --mem=48GB
#SBATCH --time=04:00:00
#SBATCH --output=rgcn_r3_randFP_%j.log

# Random-fingerprint negative control. Tests whether the gain in Round 3 is
# from chemistry, or merely from having a higher-dimensional input feature.
# Identifies its results folder by reading the most-recent dg_context
# beta0p1 seed42 folder created during this job (timestamped).

set -euo pipefail
cd "$HOME/MLPKGA007_v2"

echo "Random-fingerprint ablation started: $(date)"

# Snapshot the existing list of result folders so we can identify the new one
ls -dt results/*dg_context*beta0p1*seed42 2>/dev/null | head -10 > /tmp/r3_before_$$.txt

# Swap the real parquet for the random one. Trap restores on any exit path.
mv data/drug_fingerprints.parquet data/drug_fingerprints.parquet.real
cp data/drug_fingerprints_random.parquet data/drug_fingerprints.parquet

trap '
    echo "Restoring real fingerprints..."
    if [ -f data/drug_fingerprints.parquet.real ]; then
        mv -f data/drug_fingerprints.parquet.real data/drug_fingerprints.parquet
    fi
' EXIT

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

# Identify the new folder and tag it
NEW_FOLDER=$(ls -dt results/*dg_context*beta0p1*seed42 | head -1)
echo "New random-FP folder: $NEW_FOLDER"
echo "Tagging with marker file..."
touch "$NEW_FOLDER/RANDOM_FINGERPRINT_ABLATION.marker"

echo "Random-fingerprint ablation finished: $(date)"
