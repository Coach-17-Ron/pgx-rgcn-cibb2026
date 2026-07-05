#!/bin/bash
# =====================================================================
# SLURM batch script - v2 pipeline (combined script, all fixes applied)
#
# Adapted from May 26 run_rgcn.sh. Key differences:
#   * Targets the new `Main` partition (was GPUV100 — removed by cluster)
#   * CPU-only by default (no GPUV100 anymore; GPU partition needs separate
#     access check). CPU is fine for this graph size.
#   * Uses the v2 combined script with split_mode + filtered MRR + ablation
#     CLI args.
#   * Pinned RUN_ID so all artifacts land in a predictable directory.
#
# Submit:   sbatch run_rgcn_v2.sh
# Monitor:  squeue -u kmolepo  and  tail -f rgcn_v2_<jobid>.log
# Outputs:  ~/MLPKGA007_v2/results/<auto-tagged-RUN_ID>/
# =====================================================================
#SBATCH --job-name=pgx_v2_main
#SBATCH --account=b181-humgen-ag
#SBATCH --partition=Main
#SBATCH --cpus-per-task=8
#SBATCH --mem=48GB
#SBATCH --time=08:00:00
#SBATCH --output=rgcn_v2_%j.log

set -euo pipefail

# ---- Configuration ----
CONTAINER=/idia/software/containers/ASTRO-GPU-PyTorch-2026-01-28.sif
WORKDIR=$HOME/MLPKGA007_v2
SCRIPT=pgx_pipeline_combined.py
PUBMED_EMAIL="mlpkga007@myuct.ac.za"   # >>> EDIT to your real address <<<

# ---- Sanity checks before we burn HPC time ----
echo "Job started: $(date)"
echo "Node: $(hostname)"
echo "Working dir: $WORKDIR"

if [ ! -d "$WORKDIR" ]; then
    echo "ERROR: $WORKDIR does not exist." >&2
    exit 1
fi
cd "$WORKDIR"

if [ ! -f "$SCRIPT" ]; then
    echo "ERROR: $SCRIPT not found in $WORKDIR." >&2
    exit 1
fi

if [ ! -d "data" ]; then
    echo "ERROR: data/ folder not found. Set up symlinks first." >&2
    exit 1
fi

# Confirm the five TSVs are reachable (could be symlinks)
for f in chemicals.tsv genes.tsv phenotypes.tsv relationships.tsv variants.tsv; do
    if [ ! -e "data/$f" ]; then
        echo "ERROR: data/$f missing or broken symlink." >&2
        exit 1
    fi
done

# Check pathways folder has something
N_PA=$(find data/pathways -maxdepth 1 -name "PA*.tsv" 2>/dev/null | wc -l)
N_GMT=$(find data/pathways -maxdepth 1 \( -name "*.gmt" -o -name "*.GMT" \) 2>/dev/null | wc -l)
echo "Pathway sources detected: $N_PA PharmGKB TSV files, $N_GMT GMT files"
if [ "$N_PA" -eq 0 ] && [ "$N_GMT" -eq 0 ]; then
    echo "WARNING: no pathway files found in data/pathways/ — stage 5 ORA will skip." >&2
fi

# ---- Run the pipeline ----
# Auto-tagged RUN_ID format: <ts>_<split_mode>_<beta_tag>_<seed_tag>
# So multiple jobs with different ablation flags land in different folders.
echo "Launching pipeline..."
singularity exec --nv "$CONTAINER" bash -c "
    set -e
    # Install missing deps locally (pinned versions match requirements_combined.txt)
    pip install --user --quiet \
        torch-geometric==2.5.0 \
        networkx==3.2.1 \
        pyarrow==15.0.0 \
        2>&1 | tail -5
    python3 $SCRIPT \
        --data_dir ./data \
        --results_dir ./results \
        --split_mode dg_context \
        --seed 42 \
        --pubmed_email $PUBMED_EMAIL \
        --stages all
"

echo "Job finished: $(date)"
