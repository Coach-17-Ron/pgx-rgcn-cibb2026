#!/bin/bash
# Extract and compare D1 regime results across all three runs

echo "=== D1 SUPERVISION REGIME COMPARISON (seed=42, β=0.10) ==="
echo ""
printf "%-25s | %-8s | %-8s | %-8s | %-8s | %-8s\n" \
    "Regime" "MRR_raw" "MRR_filt" "H10_raw" "H10_filt" "Baseline"
printf "%-25s | %-8s | %-8s | %-8s | %-8s | %-8s\n" \
    "-------------------------" "--------" "--------" "--------" "--------" "--------"

for regime in default ambig_as_pos nonassoc_excluded; do
    DIR=$(ls -td results/*_reg-${regime} 2>/dev/null | head -1)
    if [ -z "$DIR" ]; then
        printf "%-25s | %-8s\n" "$regime" "NO_RUN"
        continue
    fi
    
    METRICS="$DIR/artifacts/test_metrics.json"
    if [ -f "$METRICS" ]; then
        mrr_raw=$(python3 -c "import json; d=json.load(open('$METRICS')); print(f\"{d['raw']['mrr']:.4f}\")" 2>/dev/null || echo "ERR")
        mrr_filt=$(python3 -c "import json; d=json.load(open('$METRICS')); print(f\"{d['filtered']['mrr']:.4f}\")" 2>/dev/null || echo "ERR")
        h10_raw=$(python3 -c "import json; d=json.load(open('$METRICS')); print(f\"{d['raw']['hits_at_10']:.4f}\")" 2>/dev/null || echo "ERR")
        h10_filt=$(python3 -c "import json; d=json.load(open('$METRICS')); print(f\"{d['filtered']['hits_at_10']:.4f}\")" 2>/dev/null || echo "ERR")
        base=$(python3 -c "import json; d=json.load(open('$METRICS')); print(f\"{d['degree_baseline']['mrr']:.4f}\")" 2>/dev/null || echo "ERR")
        
        printf "%-25s | %-8s | %-8s | %-8s | %-8s | %-8s\n" \
            "$regime" "$mrr_raw" "$mrr_filt" "$h10_raw" "$h10_filt" "$base"
    fi
done
