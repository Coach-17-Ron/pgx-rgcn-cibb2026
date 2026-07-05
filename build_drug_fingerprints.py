"""Generate Morgan fingerprints for all drugs in ClinPGx chemicals.tsv.

Reads ~/MLPKGA007_v2/data/chemicals.tsv (or wherever specified via --chemicals),
parses SMILES for each entry, computes 2048-bit Morgan fingerprints at
radius 2 using RDKit's MorganGenerator, and writes a parquet:

    drug_fingerprints.parquet
      columns:
        drug_pgkb_id   str   PharmGKB accession (PA12345)
        drug_name      str   Display name (for human inspection)
        has_smiles     bool  True if a non-empty SMILES was present
        smiles         str   The SMILES string (empty if no SMILES)
        fingerprint    list  2048 ints (0/1) if has_smiles else None

Usage:
    python3 build_drug_fingerprints.py
    python3 build_drug_fingerprints.py --chemicals /path/to/chemicals.tsv \
                                       --out /path/to/drug_fingerprints.parquet
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Use the new RDKit Morgan API (no deprecation warning)
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
from rdkit import RDLogger

# Silence RDKit's "SMILES parse error" stderr spam for known-bad entries
RDLogger.DisableLog("rdApp.error")
RDLogger.DisableLog("rdApp.warning")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--chemicals", default="./data/chemicals.tsv",
                   help="ClinPGx chemicals.tsv (tab-separated)")
    p.add_argument("--out", default="./data/drug_fingerprints.parquet",
                   help="Where to write the fingerprint parquet")
    p.add_argument("--n_bits", type=int, default=2048,
                   help="Fingerprint length in bits")
    p.add_argument("--radius", type=int, default=2,
                   help="Morgan radius (2 is standard for drug-target prediction)")
    args = p.parse_args()

    chem_path = Path(args.chemicals)
    out_path = Path(args.out)
    if not chem_path.exists():
        sys.exit(f"chemicals.tsv not found at {chem_path}")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Reading {chem_path}...")
    chem = pd.read_csv(chem_path, sep="\t", dtype=str, keep_default_na=False)
    print(f"  {len(chem)} chemicals")

    # Locate the SMILES column (we saw earlier it's named 'SMILES')
    smiles_col = None
    for c in chem.columns:
        if c.strip().upper() == "SMILES":
            smiles_col = c
            break
    if smiles_col is None:
        sys.exit(f"No SMILES column found in {chem_path}. Columns: {list(chem.columns)}")

    # Also find the PharmGKB ID and Name columns
    pgkb_col = next(c for c in chem.columns
                    if "PharmGKB" in c or c.strip().lower().startswith("pharmgkb"))
    name_col = next(c for c in chem.columns if c.strip().lower() == "name")
    print(f"  Columns: pgkb_id={pgkb_col!r}, name={name_col!r}, smiles={smiles_col!r}")

    # Morgan generator (new API; equivalent to AllChem.GetMorganFingerprintAsBitVect)
    mfpgen = rdFingerprintGenerator.GetMorganGenerator(
        radius=args.radius, fpSize=args.n_bits,
    )

    rows = []
    n_parsed = 0
    n_failed_parse = 0
    n_no_smiles = 0
    for _, r in chem.iterrows():
        sm = str(r[smiles_col]).strip()
        pgkb_id = str(r[pgkb_col]).strip()
        name = str(r[name_col]).strip()
        if len(sm) <= 5:  # match earlier awk threshold; "" or whitespace
            rows.append({
                "drug_pgkb_id": pgkb_id, "drug_name": name,
                "has_smiles": False, "smiles": "", "fingerprint": None,
            })
            n_no_smiles += 1
            continue
        mol = Chem.MolFromSmiles(sm)
        if mol is None:
            rows.append({
                "drug_pgkb_id": pgkb_id, "drug_name": name,
                "has_smiles": False, "smiles": sm, "fingerprint": None,
            })
            n_failed_parse += 1
            continue
        fp = mfpgen.GetFingerprint(mol)
        # Convert ExplicitBitVect to list of ints; pyarrow handles lists fine
        bits = list(fp.GetOnBits())
        # Dense representation as a list of 2048 ints (0/1)
        dense = np.zeros(args.n_bits, dtype=np.int8)
        for b in bits:
            dense[b] = 1
        rows.append({
            "drug_pgkb_id": pgkb_id, "drug_name": name,
            "has_smiles": True, "smiles": sm,
            "fingerprint": dense.tolist(),
        })
        n_parsed += 1

    df = pd.DataFrame(rows)
    df.to_parquet(out_path, index=False)
    print()
    print(f"Saved {out_path}")
    print(f"  Total chemicals:           {len(df)}")
    print(f"  Successfully fingerprinted: {n_parsed}")
    print(f"  SMILES parse failure:       {n_failed_parse}")
    print(f"  No SMILES:                  {n_no_smiles}")
    print(f"  Mean bits set (SMILES rows): "
          f"{df[df['has_smiles']]['fingerprint'].apply(lambda l: sum(l) if l else 0).mean():.1f}")


if __name__ == "__main__":
    main()
