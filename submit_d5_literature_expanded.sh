#!/bin/bash
#SBATCH --account=b181-humgen-ag
#SBATCH --partition=Main
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=05:00:00
#SBATCH --output=d5_literature_expanded_%j.log
#SBATCH --job-name=d5_lit_ext

cd ~/MLPKGA007_v2_MSC

echo "=========================================="
echo "  D5-PART 1 EXPANDED LITERATURE VALIDATION"
echo "  max_pairs=5000, date_from=1990"
echo "  Started: $(date)"
echo "=========================================="

REF="results/20260708_044757_dg_context_beta0p1_seed42_reg-default"

singularity exec \
    /idia/software/containers/ASTRO-GPU-PyTorch-2026-01-28.sif \
    python3 run_d5_stage5.py \
    --run_dir "$REF" \
    --max_pairs 5000 \
    --date_from 1990 \
    --date_to 2026 \
    --pubmed_email mlpkga007@myuct.ac.za

echo ""
echo "=========================================="
echo "  D5-PART 1 EXPANDED RUN COMPLETE"
echo "  Finished: $(date)"
echo "=========================================="
