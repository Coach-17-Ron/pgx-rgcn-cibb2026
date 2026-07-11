#!/bin/bash
#SBATCH --account=b181-humgen-ag
#SBATCH --partition=Main
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=d5_pathway_all_configs_%j.log
#SBATCH --job-name=d5_pathway

cd ~/MLPKGA007_v2_MSC

echo "=========================================="
echo "  D5 PATHWAY ENRICHMENT ACROSS 12 CONFIGS"
echo "  Started: $(date)"
echo "=========================================="

CONFIGS=(
    "results/20260708_044757_dg_context_beta0p1_seed42_reg-default"
    "results/20260708_055316_dg_context_beta0p1_seed123_reg-default"
    "results/20260708_065820_dg_context_beta0p1_seed2026_reg-default"
    "results/20260708_050859_dg_context_beta0p1_seed42_reg-ambig_as_pos"
    "results/20260708_061636_dg_context_beta0p1_seed123_reg-ambig_as_pos"
    "results/20260708_072107_dg_context_beta0p1_seed2026_reg-ambig_as_pos"
    "results/20260708_053220_dg_context_beta0p1_seed42_reg-nonassoc_excluded"
    "results/20260708_064106_dg_context_beta0p1_seed123_reg-nonassoc_excluded"
    "results/20260708_074340_dg_context_beta0p1_seed2026_reg-nonassoc_excluded"
    "results/20260708_194943_dg_context_beta0p0_seed42_reg-default"
    "results/20260708_200910_dg_context_beta0p0_seed123_reg-default"
    "results/20260708_203125_dg_context_beta0p0_seed2026_reg-default"
)

for i in "${!CONFIGS[@]}"; do
    RUN_DIR="${CONFIGS[$i]}"
    N=$((i+1))
    echo ""
    echo "-------------------------------------------"
    echo "[$N/12] D5 pathway ORA: $(basename $RUN_DIR)"
    echo "Time: $(date)"
    echo "-------------------------------------------"
    
    singularity exec \
        /idia/software/containers/ASTRO-GPU-PyTorch-2026-01-28.sif \
        python3 run_d5_stage5.py \
        --run_dir "$RUN_DIR" \
        --pathway_only
    
    echo "Completed: $(basename $RUN_DIR) at $(date)"
done

echo ""
echo "=========================================="
echo "  ALL 12 D5 PATHWAY EVALUATIONS COMPLETE"
echo "  Finished: $(date)"
echo "=========================================="
