# ilifu transfer + run setup — v2 pipeline

The commands below assume:
- You're on Windows (paths use backslashes for the local side)
- Your ilifu SSH key is `C:\Users\ronal\.ssh\id_ed25519_ilifu`
- Your downloaded files are in `C:\Users\ronal\Downloads\` (adjust if different)
- Your ilifu username is `kmolepo`

---

## Step 1 — From your Windows terminal, copy files to ilifu

ilifu has a dedicated transfer node (`transfer.ilifu.ac.za`) — the banner says don't use `slurm.ilifu.ac.za` for transfers, but the transfer node uses the same SSH key.

Open a **new** PowerShell or Command Prompt window (keep your existing SSH session alive). Then:

```powershell
cd C:\Users\ronal\Downloads

# Single scp pushing everything we need to ilifu
scp -i C:\Users\ronal\.ssh\id_ed25519_ilifu ^
    pgx_pipeline_combined.py ^
    pgx_pipeline_combined.ipynb ^
    run_rgcn_v2.sh ^
    run_rgcn_v2_beta0.sh ^
    submit_multiseed.sh ^
    requirements_combined.txt ^
    methodology_and_expected_outcomes.md ^
    kmolepo@transfer.ilifu.ac.za:~/
```

You'll get the same Keycloak MFA prompt as the SSH login. Approve it. Files land in your ilifu home directory.

Expected upload size: ~600 KB total, takes a couple of seconds.

---

## Step 2 — On the ilifu login node (your existing SSH session), set up the v2 directory

```bash
# Make the v2 working directory next to MLPKGA007
mkdir -p ~/MLPKGA007_v2/data
cd ~/MLPKGA007_v2

# Symlink the five TSVs from the May 26 directory (no copy — saves 22 MB)
ln -sf ~/MLPKGA007/chemicals.tsv     data/chemicals.tsv
ln -sf ~/MLPKGA007/genes.tsv         data/genes.tsv
ln -sf ~/MLPKGA007/phenotypes.tsv    data/phenotypes.tsv
ln -sf ~/MLPKGA007/relationships.tsv data/relationships.tsv
ln -sf ~/MLPKGA007/variants.tsv      data/variants.tsv

# Symlink the pathways folder (208 PharmGKB TSVs, no copy)
ln -sf ~/MLPKGA007/pathways          data/pathways

# Move the uploaded files into the working directory
mv ~/pgx_pipeline_combined.py ~/MLPKGA007_v2/
mv ~/pgx_pipeline_combined.ipynb ~/MLPKGA007_v2/
mv ~/run_rgcn_v2.sh ~/MLPKGA007_v2/
mv ~/run_rgcn_v2_beta0.sh ~/MLPKGA007_v2/
mv ~/submit_multiseed.sh ~/MLPKGA007_v2/
mv ~/requirements_combined.txt ~/MLPKGA007_v2/

# Methodology doc can stay in home for now
# mv ~/methodology_and_expected_outcomes.md ~/MLPKGA007_v2/  # optional

chmod +x ~/MLPKGA007_v2/*.sh

# Verify the layout
cd ~/MLPKGA007_v2
ls -la
echo "---"
ls -la data/
echo "---"
ls data/pathways/ | head -5
ls data/pathways/ | wc -l   # should report ~208
```

---

## Step 3 — Edit the SLURM script with your real PubMed email

```bash
# Quick check first - what email is in the script?
grep PUBMED_EMAIL ~/MLPKGA007_v2/run_rgcn_v2.sh

# If it's still placeholder, edit:
nano ~/MLPKGA007_v2/run_rgcn_v2.sh
# Find the line:    PUBMED_EMAIL="kgabe.molepo@uct.ac.za"
# Replace with your actual UCT email
# Ctrl-O, Enter, Ctrl-X

# Same for the ablation script:
nano ~/MLPKGA007_v2/run_rgcn_v2_beta0.sh

# And the multi-seed driver:
nano ~/MLPKGA007_v2/submit_multiseed.sh
```

---

## Step 4 — Pre-flight dry run on the login node (optional but recommended)

Just to confirm the script parses and the data is wired correctly. This DOES NOT train — it bails out immediately because we'll pass `--stages 1` and immediately check the artifacts.

```bash
cd ~/MLPKGA007_v2

# Quick smoke test — just stage 1 (build graph). Should take <1 minute on the login node.
# But the banner says no software on login, so use a 30-minute Devel partition slot:
srun --account=b181-humgen-ag --partition=Devel --cpus-per-task=2 --mem=8GB \
     --time=00:30:00 --pty bash

# Inside the srun shell:
singularity exec /idia/software/containers/ASTRO-GPU-PyTorch-2026-01-28.sif bash -c "
    pip install --user --quiet torch-geometric==2.5.0 networkx==3.2.1 pyarrow==15.0.0 2>&1 | tail -3
    python3 pgx_pipeline_combined.py --data_dir ./data --results_dir ./results --stages 1
"
# Expected: writes ~/MLPKGA007_v2/results/<RUN_ID>/artifacts/{nodes,edges}.parquet
# in 30-60 seconds. If anything errors, fix BEFORE running the full pipeline.

# Check what was produced:
ls results/*/artifacts/

# Exit the srun shell:
exit
```

---

## Step 5 — Submit the main run

```bash
cd ~/MLPKGA007_v2
sbatch run_rgcn_v2.sh
# Outputs the job ID. Note it.

# Monitor:
squeue -u kmolepo
# Once running, follow the log:
tail -f rgcn_v2_<JOBID>.log
```

Expected wall time: 2-4 hours on the `Main` partition (CPU, 8 cores, 48 GB).

---

## Step 6 — Once main run completes, submit ablation and multi-seed

```bash
cd ~/MLPKGA007_v2

# β=0 ablation (single job)
sbatch run_rgcn_v2_beta0.sh

# Multi-seed sweep (3 separate jobs)
bash submit_multiseed.sh

# Watch all four jobs queue:
squeue -u kmolepo
```

Each job lands in its own auto-tagged `results/<TIMESTAMP>_dg_context_<beta>_<seed>/` folder.

---

## Step 7 — When everything is done, pull results back to your laptop

From a fresh Windows PowerShell:

```powershell
cd C:\Users\ronal\Downloads

# Pull the whole results tree
scp -r -i C:\Users\ronal\.ssh\id_ed25519_ilifu ^
    kmolepo@transfer.ilifu.ac.za:~/MLPKGA007_v2/results/ ^
    .\MLPKGA007_v2_results
```

Or selectively, just the key artifacts:

```powershell
scp -r -i C:\Users\ronal\.ssh\id_ed25519_ilifu ^
    "kmolepo@transfer.ilifu.ac.za:~/MLPKGA007_v2/results/*/artifacts/*.csv" ^
    "kmolepo@transfer.ilifu.ac.za:~/MLPKGA007_v2/results/*/figures/*.png" ^
    "kmolepo@transfer.ilifu.ac.za:~/MLPKGA007_v2/results/*/test_metrics.json" ^
    .\MLPKGA007_v2_results
```

---

## Troubleshooting

**"pip install" errors inside singularity** — sometimes the container caches an old version. Add `--upgrade --force-reinstall` to the pip line if you hit version conflicts.

**Job stays in PD (pending) for a long time** — check the cluster load with `sinfo -p Main -o "%P %a %A"`. If the partition is full, switch to `HighMem` or wait.

**"Keycloak MFA accepted" then disconnects** — the MFA token is per-session, not per-command. Each `scp` and `ssh` opens a fresh session. If you're doing many transfers, use one persistent `ssh` session for all of them and issue commands within it.

**Singularity can't find the container** — `ls /idia/software/containers/ASTRO-GPU-PyTorch-2026-01-28.sif` to confirm it still exists; cluster software is occasionally rotated.

**"no kernel image" on GPU partition** — same issue as May 26. The CPU fallback in the script should handle it; if you forced GPU and it crashed, edit the SLURM script back to CPU partition.

**Stage 5 PubMed queries 429-rate-limited** — confirm `PUBMED_EMAIL` is your real address. NCBI is more lenient with attributed requests. If still rate-limited, halve `request_sleep_seconds` in the CONFIG, or pass `--skip_literature` for first attempts.

---

## Quick reference — what each run produces

After Step 5 main run, expect `results/<RUN_ID>/` to contain:

```
artifacts/
    nodes.parquet
    edges.parquet
    graph_metadata.json
    split_assignments.parquet
    split_leakage_audit.json        # NEW — proves dg_context behaviour
    pyg_edge_type_mapping.json      # NEW — correct relation labels for stage 4
    rel_to_idx.json
    model_checkpoint.pt
    test_metrics.json               # contains BOTH raw and filtered now
    hub_bias_analysis.json
    novel_predictions.parquet       # candidate-novel only (no rediscovery)
    candidate_predictions.parquet   # NEW — same as novel_predictions
    rediscovered_predictions.parquet # NEW — known pairs that were re-found
    all_predictions.parquet         # NEW — both, labelled by category
    ambiguous_priorities.parquet
    ambiguous_priorities.csv        # curator-facing
    relation_importance.parquet
    explanations.parquet
    literature_evidence.parquet
    literature_evidence.csv
    pathway_enrichment.parquet      # NEW — has `source` column (PGKB/REACTOME/KEGG)
    integrated_explanations.parquet
    integrated_explanations.csv
    phenotype_inferences.parquet
    phenotype_inferences.csv        # uses is_negative_evidence (renamed)
figures/
    figure_hub_bias.png
    figure_relation_importance.png  # correctly labelled now
    figure_pathway_enrichment.png   # per-source subplots
    figure_phenotype_propagation.png
logs/
    pipeline.log
    01_build_graph.log ... 06_propagate.log
run_config.json                     # NEW — complete config snapshot
```
