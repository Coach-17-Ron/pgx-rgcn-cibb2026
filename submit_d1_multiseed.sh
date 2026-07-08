#!/bin/bash
#SBATCH --account=b181-humgen-ag
#SBATCH --partition=Main
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=05:00:00
#SBATCH --output=d1_multiseed_%j.log
#SBATCH --job-name=d1_multi

cd ~/MLPKGA007_v2_MSC

echo "=========================================="
echo "  D1 MULTI-SEED SWEEP"
echo "  3 regimes x 3 seeds = 9 runs"
echo "  Started: $(date)"
echo "=========================================="

# Run all 9 combinations sequentially
for seed in 42 123 2026; do
    for regime in default ambig_as_pos nonassoc_excluded; do
        echo ""
        echo "-------------------------------------------"
        echo "Starting: regime=$regime, seed=$seed"
        echo "Time: $(date)"
        echo "-------------------------------------------"
        
        singularity exec \
            /idia/software/containers/ASTRO-GPU-PyTorch-2026-01-28.sif \
            python3 pgx_pipeline_combined.py \
            --data_dir ./data \
            --seed $seed \
            --hub_penalty_beta 0.10 \
            --supervision_regime $regime \
            --split_mode dg_context \
            --stages 1,2,3 \
            --pubmed_email mokumong.lg@gmail.com
        
        echo ""
        echo "Completed: regime=$regime, seed=$seed at $(date)"
    done
done

echo ""
echo "=========================================="
echo "  ALL 9 RUNS COMPLETE"
echo "  Finished: $(date)"
echo "=========================================="
