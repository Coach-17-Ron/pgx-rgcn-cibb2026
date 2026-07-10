#!/bin/bash
#SBATCH --account=b181-humgen-ag
#SBATCH --partition=Main
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=d3_all_configs_%j.log
#SBATCH --job-name=d3_all

cd ~/MLPKGA007_v2_MSC

echo "=========================================="
echo "  D3 EVALUATION ACROSS 12 CONFIGS"
echo "  Started: $(date)"
echo "=========================================="

# The 12 canonical configs (most recent per unique key)
# β=0.10 default: 3 seeds
# β=0.10 ambig_as_pos: 3 seeds
# β=0.10 nonassoc_excluded: 3 seeds
# β=0.0 default: 3 seeds

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
    echo "[$N/12] Evaluating: $(basename $RUN_DIR)"
    echo "Time: $(date)"
    echo "-------------------------------------------"
    
    singularity exec \
        /idia/software/containers/ASTRO-GPU-PyTorch-2026-01-28.sif \
        python3 evaluate_d3_phenotype_relevant.py \
        --run_dir "$RUN_DIR"
    
    echo "Completed: $(basename $RUN_DIR) at $(date)"
done

echo ""
echo "=========================================="
echo "  ALL 12 D3 EVALUATIONS COMPLETE"
echo "  Finished: $(date)"
echo "=========================================="
