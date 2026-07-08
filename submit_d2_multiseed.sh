#!/bin/bash
#SBATCH --account=b181-humgen-ag
#SBATCH --partition=Main
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=02:30:00
#SBATCH --output=d2_multiseed_%j.log
#SBATCH --job-name=d2_multi

cd ~/MLPKGA007_v2_MSC

echo "=========================================="
echo "  D2 β=0 HUB-PENALTY ABLATION SWEEP"
echo "  3 seeds x β=0.0 = 3 runs"
echo "  Started: $(date)"
echo "=========================================="

# Run all 3 combinations sequentially
for seed in 42 123 2026; do
    echo ""
    echo "-------------------------------------------"
    echo "Starting: β=0.0, seed=$seed, regime=default"
    echo "Time: $(date)"
    echo "-------------------------------------------"
    
    singularity exec \
        /idia/software/containers/ASTRO-GPU-PyTorch-2026-01-28.sif \
        python3 pgx_pipeline_combined.py \
        --data_dir ./data \
        --seed $seed \
        --ablation_beta_zero \
        --supervision_regime default \
        --split_mode dg_context \
        --stages 1,2,3 \
        --pubmed_email mokumong.lg@gmail.com
    
    echo ""
    echo "Completed: β=0.0, seed=$seed at $(date)"
done

echo ""
echo "=========================================="
echo "  ALL 3 D2 RUNS COMPLETE"
echo "  Finished: $(date)"
echo "=========================================="
