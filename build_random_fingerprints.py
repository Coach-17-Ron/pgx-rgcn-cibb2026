"""Generate RANDOM-shuffled fingerprints for the negative control.

For each drug that has a real fingerprint, this script REPLACES it with a
uniformly random bit vector with the same mean bit-count as the real
fingerprint corpus (~46 bits set out of 2048). Drugs without SMILES
remain has_smiles=False (same as real fingerprints).

The control tests: does the gain we observed in Round 3 come from chemical
information, or merely from having a higher-dimensional input feature?
If the random control still beats the no-FP baseline by a similar margin,
the gain is from input dimensionality / capacity. If it does not, the gain
is genuinely from chemistry.

Usage:
    python3 build_random_fingerprints.py \\
        --input ./data/drug_fingerprints.parquet \\
        --output ./data/drug_fingerprints_random.parquet \\
        --seed 42
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="./data/drug_fingerprints.parquet")
    p.add_argument("--output", default="./data/drug_fingerprints_random.parquet")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--n_bits", type=int, default=2048)
    args = p.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        sys.exit(f"Input {in_path} not found")
    df = pd.read_parquet(in_path)
    print(f"Loaded {len(df)} rows from {in_path}")
    print(f"  with_smiles: {df['has_smiles'].sum()}")

    # Compute mean bits-set across the real fingerprints (so the control
    # has the same overall density, just permuted bits).
    real = df[df["has_smiles"]]
    mean_bits = int(np.mean(
        [int(sum(fp)) for fp in real["fingerprint"] if fp is not None]
    ))
    print(f"  mean bits set (real): {mean_bits}")

    rng = np.random.default_rng(args.seed)
    new_rows = []
    for _, r in df.iterrows():
        if r["has_smiles"]:
            # Random bit vector with the same density as real fingerprints.
            # Each drug gets an independent random fingerprint, so two drugs
            # with similar chemistry won't have correlated random fingerprints.
            bits = np.zeros(args.n_bits, dtype=np.int8)
            on_bits = rng.choice(args.n_bits, size=mean_bits, replace=False)
            bits[on_bits] = 1
            new_rows.append({
                "drug_pgkb_id": r["drug_pgkb_id"],
                "drug_name": r["drug_name"],
                "has_smiles": True,
                "smiles": r["smiles"],
                "fingerprint": bits.tolist(),
            })
        else:
            new_rows.append({
                "drug_pgkb_id": r["drug_pgkb_id"],
                "drug_name": r["drug_name"],
                "has_smiles": False,
                "smiles": "",
                "fingerprint": None,
            })

    out_df = pd.DataFrame(new_rows)
    out_path = Path(args.output)
    out_df.to_parquet(out_path, index=False)
    print(f"Saved {out_path}")
    print(f"  {len(out_df)} rows, "
          f"{out_df['has_smiles'].sum()} with random fingerprints, "
          f"mean bits per drug: {mean_bits}")


if __name__ == "__main__":
    main()
