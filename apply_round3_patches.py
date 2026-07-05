"""Apply Round 3 molecular-descriptor patches to pgx_pipeline_combined.py.

Idempotent: skips any patch already applied. Backs up to .py.bak_round3
on first run. Run from the directory containing pgx_pipeline_combined.py.

Patches:
  1. Add load_drug_fingerprints helper
  2. Add drug_fingerprints_path to CONFIG.data
  3. PGx_RGCN class: accept drug_fp_dim + n_drugs_for_fp, register buffers,
     add attach_drug_fingerprints() + encode() methods
  4. PGx_RGCN.forward: use self.encode() instead of self.encoder()
  5. evaluate_mrr: use model.encode() instead of model.encoder()
  6. compute_ranks: use model.encode(), also track has_fp per query
  7. Stage 3 ambig + novel forward sites: use model.encode()
  8. Stage 2 setup: load fingerprints, construct model with drug_fp_dim,
     attach, save fingerprint flag in checkpoint
  9. Stage 3 setup: read flag, construct model accordingly, attach fingerprints
 10. Add stratified MRR (with_smiles / without_smiles) to test_metrics.json
"""
import re
import sys
from pathlib import Path

SCRIPT = Path("pgx_pipeline_combined.py")
if not SCRIPT.exists():
    sys.exit(f"{SCRIPT} not found in current directory")

src = SCRIPT.read_text()
backup = SCRIPT.with_suffix(".py.bak_round3")
if not backup.exists():
    backup.write_text(src)
    print(f"Backup -> {backup}")
else:
    print(f"Backup already exists at {backup} (preserving original)")

changes = 0

def patch(name, old, new, must_exist=True):
    """Apply a single replacement. If `new` already present, skip."""
    global src, changes
    if new in src and old not in src:
        print(f"[skip] {name} (already applied)")
        return
    if old not in src:
        if must_exist:
            sys.exit(f"[FAIL] {name}: anchor not found:\n---\n{old[:200]}\n---")
        else:
            print(f"[skip] {name} (anchor not present)")
            return
    src = src.replace(old, new, 1)
    changes += 1
    print(f"[ok]   {name}")

# -----------------------------------------------------------------
# Patch 1: load_drug_fingerprints helper, inserted before STAGE 1
# -----------------------------------------------------------------
HELPER = '''

# ============================================================================
# Round 3: drug-fingerprint loader
# ============================================================================
def load_drug_fingerprints(fp_path, nodes, logger, fp_dim=2048):
    """Load drug Morgan fingerprints from a parquet and align with the drug
    node indices in `nodes`.

    Returns
    -------
    fp_tensor : torch.Tensor of shape (n_drugs, fp_dim) float32, or None
    has_fp    : torch.Tensor of shape (n_drugs,)        bool,    or None
    n_with    : int  count of drugs with a non-zero fingerprint
    """
    from pathlib import Path as _P
    fp_path = _P(fp_path)
    if not fp_path.exists():
        logger.info(f"No drug-fingerprint parquet at {fp_path}; "
                    f"drug features will be random Xavier (legacy).")
        return None, None, 0

    fp_df = pd.read_parquet(fp_path)
    logger.info(f"Loaded {len(fp_df)} fingerprint rows from {fp_path}")

    # Join by lowercased name (canonical key)
    fp_df = fp_df.copy()
    fp_df["_join_key"] = fp_df["drug_name"].astype(str).str.strip().str.lower()
    fp_map = {}
    for _, r in fp_df.iterrows():
        if r["has_smiles"] and r["fingerprint"] is not None:
            fp_map[r["_join_key"]] = np.asarray(r["fingerprint"], dtype=np.float32)

    drug_nodes = nodes[nodes["node_type"] == "drug"].reset_index(drop=True)
    n_drugs = len(drug_nodes)
    fp_arr = np.zeros((n_drugs, fp_dim), dtype=np.float32)
    has_fp = np.zeros(n_drugs, dtype=bool)
    for i, name in enumerate(drug_nodes["node_name"].values):
        key = str(name).strip().lower()
        if key in fp_map:
            fp_arr[i] = fp_map[key]
            has_fp[i] = True

    n_with = int(has_fp.sum())
    logger.info(f"Drug nodes: {n_drugs}; with fingerprint: {n_with} "
                f"({100*n_with/n_drugs:.1f}%); without: {n_drugs - n_with}")
    return (torch.from_numpy(fp_arr),
            torch.from_numpy(has_fp),
            n_with)


'''
patch(
    "1. load_drug_fingerprints helper",
    "# ====================== Split logic (70/15/15) =========================",
    HELPER + "# ====================== Split logic (70/15/15) =========================",
)

# -----------------------------------------------------------------
# Patch 2: CONFIG drug_fingerprints_path
# -----------------------------------------------------------------
patch(
    "2. CONFIG.data.drug_fingerprints_path",
    '''    "data": {
        "files": {''',
    '''    "data": {
        "drug_fingerprints_path": "./data/drug_fingerprints.parquet",
        "files": {''',
)

# -----------------------------------------------------------------
# Patch 3: PGx_RGCN __init__ accepts drug_fp_dim + n_drugs_for_fp
# -----------------------------------------------------------------
patch(
    "3. PGx_RGCN.__init__ signature + buffers",
    '''class PGx_RGCN(nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels,
                 num_edge_types, num_decoder_relations,
                 num_bases=8, dropout=0.25):
        super().__init__()''',
    '''class PGx_RGCN(nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels,
                 num_edge_types, num_decoder_relations,
                 num_bases=8, dropout=0.25,
                 drug_fp_dim=None, n_drugs_for_fp=0):
        """Optional Round 3 args:
        - drug_fp_dim: dimension of drug input fingerprints (e.g. 2048).
          If None, drug nodes use random Xavier features (legacy behaviour).
        - n_drugs_for_fp: number of drug nodes in the graph (needed to
          pre-register buffers of correct shape).
        """
        super().__init__()
        self.drug_fp_dim = drug_fp_dim
        if drug_fp_dim is not None and n_drugs_for_fp > 0:
            self.drug_fp_proj = nn.Linear(drug_fp_dim, in_channels)
            self.drug_missing_emb = nn.Parameter(torch.empty(in_channels))
            nn.init.xavier_uniform_(self.drug_missing_emb.unsqueeze(0))
            # Buffers (persistent=True so checkpoint is self-contained)
            self.register_buffer(
                "drug_fp_buffer",
                torch.zeros(n_drugs_for_fp, drug_fp_dim),
                persistent=True,
            )
            self.register_buffer(
                "drug_has_fp_buffer",
                torch.zeros(n_drugs_for_fp, dtype=torch.bool),
                persistent=True,
            )
            self.drug_offset = None  # set via attach_drug_fingerprints()''',
)

# -----------------------------------------------------------------
# Patch 4: Add attach_drug_fingerprints + encode methods, and use them
# in PGx_RGCN.forward
# -----------------------------------------------------------------
patch(
    "4. PGx_RGCN methods + forward uses self.encode",
    '''    def forward(self, x, edge_index, edge_type, head_idx, rel_idx, tail_idx):
        z = self.encoder(x, edge_index, edge_type)
        return self.decoder(z[head_idx], rel_idx, z[tail_idx])''',
    '''    def attach_drug_fingerprints(self, drug_fp, has_fp, drug_offset):
        """Populate the pre-registered fingerprint buffers. Called once
        per run after model construction, by stage 2 (train) and stage 3
        (eval). Idempotent; safe to call repeatedly."""
        if self.drug_fp_dim is None:
            raise RuntimeError(
                "Cannot attach drug fingerprints to a model constructed "
                "with drug_fp_dim=None. Re-construct with drug_fp_dim set."
            )
        assert drug_fp.shape == self.drug_fp_buffer.shape, (
            f"drug_fp shape {drug_fp.shape} != buffer shape "
            f"{self.drug_fp_buffer.shape}")
        self.drug_fp_buffer.data.copy_(drug_fp.float())
        self.drug_has_fp_buffer.data.copy_(has_fp.bool())
        self.drug_offset = int(drug_offset)

    def encode(self, x, edge_index, edge_type):
        """Wrapper around encoder that injects drug fingerprints if available.

        For drugs with a Morgan fingerprint, the random Xavier row in x is
        replaced by drug_fp_proj(fingerprint). For drugs without one, the
        row is replaced by a single shared learnable vector
        (drug_missing_emb). Gradients flow through both. If the model was
        constructed without drug_fp_dim, this falls back to a plain
        encoder forward (legacy / backward-compat)."""
        if self.drug_fp_dim is None or self.drug_offset is None:
            return self.encoder(x, edge_index, edge_type)
        n_drugs = self.drug_fp_buffer.size(0)
        proj = self.drug_fp_proj(self.drug_fp_buffer)  # (n_drugs, in_channels)
        missing = self.drug_missing_emb.unsqueeze(0).expand(n_drugs, -1)
        drug_rows = torch.where(
            self.drug_has_fp_buffer.unsqueeze(-1), proj, missing,
        )
        x_mut = x.clone()
        x_mut[self.drug_offset:self.drug_offset + n_drugs] = drug_rows
        return self.encoder(x_mut, edge_index, edge_type)

    def forward(self, x, edge_index, edge_type, head_idx, rel_idx, tail_idx):
        z = self.encode(x, edge_index, edge_type)
        return self.decoder(z[head_idx], rel_idx, z[tail_idx])''',
)

# -----------------------------------------------------------------
# Patch 5: evaluate_mrr — use model.encode
# -----------------------------------------------------------------
patch(
    "5. evaluate_mrr uses model.encode",
    '''    # Encoder pass (once)
    z = model.encoder(x, edge_index, edge_type)''',
    '''    # Encoder pass (once)  -- Round 3: model.encode applies fingerprints
    # if attached, else falls back to plain encoder (legacy behaviour)
    z = model.encode(x, edge_index, edge_type)''',
)

# -----------------------------------------------------------------
# Patch 6: compute_ranks — use model.encode, track has_fp per query
# -----------------------------------------------------------------
patch(
    "6a. compute_ranks uses model.encode",
    '''    with torch.no_grad():
        z = model.encoder(x, edge_index, edge_type)
        all_gene_global = gene_offset + torch.arange(n_genes, device=device,
                                                     dtype=torch.long)
        tail_emb_all = z[all_gene_global]

        ranks = []
        predicted_top_gene = []''',
    '''    with torch.no_grad():
        z = model.encode(x, edge_index, edge_type)
        all_gene_global = gene_offset + torch.arange(n_genes, device=device,
                                                     dtype=torch.long)
        tail_emb_all = z[all_gene_global]

        # Round 3: track which queries have a fingerprinted head for
        # stratified MRR reporting
        drug_has_fp_local = None
        if hasattr(model, "drug_has_fp_buffer") \\
                and model.drug_has_fp_buffer.numel() > 0:
            drug_has_fp_local = model.drug_has_fp_buffer.detach().cpu()

        ranks = []
        predicted_top_gene = []
        query_has_fp = []  # parallel to ranks, True if head drug has SMILES''',
)

patch(
    "6b. compute_ranks records has_fp per query and returns it",
    '''            rank = (scores > scores[tail_local_i]).sum().item() + 1
            ranks.append(rank)
            predicted_top_gene.append(int(scores.argmax().item()))

    return np.array(ranks), predicted_top_gene''',
    '''            rank = (scores > scores[tail_local_i]).sum().item() + 1
            ranks.append(rank)
            predicted_top_gene.append(int(scores.argmax().item()))
            if drug_has_fp_local is not None:
                query_has_fp.append(bool(drug_has_fp_local[head_local_i].item()))
            else:
                query_has_fp.append(False)

    return np.array(ranks), predicted_top_gene, np.array(query_has_fp, dtype=bool)''',
)

# Patch all call sites of compute_ranks to unpack the new 3rd return value.
# There are 3 call sites in stage 3 (raw, filtered, validation).
patch(
    "6c. compute_ranks call (raw)",
    '''    test_ranks_raw, test_top_genes = compute_ranks(
        model, x, edge_index, edge_type, test_pos,
        node_offsets, n_genes, device,
        known_positives_by_drug=None, filtered=False,
    )''',
    '''    test_ranks_raw, test_top_genes, _query_has_fp_raw = compute_ranks(
        model, x, edge_index, edge_type, test_pos,
        node_offsets, n_genes, device,
        known_positives_by_drug=None, filtered=False,
    )''',
)
patch(
    "6d. compute_ranks call (filtered)",
    '''    test_ranks_filt, _ = compute_ranks(
        model, x, edge_index, edge_type, test_pos,
        node_offsets, n_genes, device,
        known_positives_by_drug=known_positives_by_drug, filtered=True,
    )''',
    '''    test_ranks_filt, _, query_has_fp = compute_ranks(
        model, x, edge_index, edge_type, test_pos,
        node_offsets, n_genes, device,
        known_positives_by_drug=known_positives_by_drug, filtered=True,
    )''',
)
patch(
    "6e. compute_ranks call (validation)",
    '''    val_ranks_filt, _ = compute_ranks(
        model, x, edge_index, edge_type, val_pos,
        node_offsets, n_genes, device,
        known_positives_by_drug=known_positives_by_drug, filtered=True,
    )''',
    '''    val_ranks_filt, _, _ = compute_ranks(
        model, x, edge_index, edge_type, val_pos,
        node_offsets, n_genes, device,
        known_positives_by_drug=known_positives_by_drug, filtered=True,
    )''',
)

# -----------------------------------------------------------------
# Patch 7: 2 other forward sites in stage 3 (ambig + novel)
# -----------------------------------------------------------------
# These two `with torch.no_grad():` blocks each open with
# `z = model.encoder(x, edge_index, edge_type)`.  Both are inside the
# stage 3 function.  Patch the first; then patch the second.
# We need unique context so we don't double-patch.
patch(
    "7a. ambiguous-pair forward uses model.encode",
    '''        # Encoder forward pass once (reused for every ambiguous pair)
        model.eval()
        with torch.no_grad():
            z = model.encoder(x, edge_index, edge_type)
            all_gene_global = node_offsets["gene"] + torch.arange(
                n_genes, device=device, dtype=torch.long,
            )
            tail_emb_all = z[all_gene_global]''',
    '''        # Encoder forward pass once (reused for every ambiguous pair)
        model.eval()
        with torch.no_grad():
            z = model.encode(x, edge_index, edge_type)
            all_gene_global = node_offsets["gene"] + torch.arange(
                n_genes, device=device, dtype=torch.long,
            )
            tail_emb_all = z[all_gene_global]''',
)

patch(
    "7b. novel-hypothesis forward uses model.encode",
    '''        gene_offset = node_offsets["gene"]
        drug_offset = node_offsets["drug"]

        with torch.no_grad():
            z = model.encoder(x, edge_index, edge_type)
            all_gene_global = gene_offset + torch.arange(n_genes, device=device,
                                                          dtype=torch.long)
            tail_emb = z[all_gene_global]''',
    '''        gene_offset = node_offsets["gene"]
        drug_offset = node_offsets["drug"]

        with torch.no_grad():
            z = model.encode(x, edge_index, edge_type)
            all_gene_global = gene_offset + torch.arange(n_genes, device=device,
                                                          dtype=torch.long)
            tail_emb = z[all_gene_global]''',
)

# -----------------------------------------------------------------
# Patch 8: stage 2 train — load fingerprints + construct model + attach
# We patch the model construction site in stage 2.
# -----------------------------------------------------------------
patch(
    "8a. stage 2 loads fingerprints + constructs model with drug_fp_dim",
    '''    model = PGx_RGCN(
        in_channels=x.size(-1),
        hidden_channels=cfg["model"]["hidden_dim"],
        out_channels=cfg["model"]["output_dim"],
        num_edge_types=num_edge_types,
        num_decoder_relations=len(rel_to_idx),
        num_bases=cfg["model"]["num_bases"],
        dropout=cfg["model"]["dropout"],
    ).to(device)''',
    '''    # Round 3: load drug fingerprints if available
    fp_path = paths["data_dir"] / cfg["data"].get(
        "drug_fingerprints_path", "drug_fingerprints.parquet"
    ) if isinstance(paths["data_dir"], Path) else \\
        Path(cfg["data"].get("drug_fingerprints_path", "./data/drug_fingerprints.parquet"))
    if not Path(fp_path).is_absolute():
        # Resolve relative to data_dir
        fp_path = Path(paths["data_dir"]) / Path(fp_path).name \\
            if Path(fp_path).name == "drug_fingerprints.parquet" else Path(fp_path)
    drug_fp, drug_has_fp, n_with_fp = load_drug_fingerprints(
        fp_path, nodes, logger, fp_dim=2048,
    )
    n_drugs_for_fp = drug_fp.size(0) if drug_fp is not None else 0
    drug_fp_dim = 2048 if drug_fp is not None else None
    use_fingerprints = drug_fp is not None

    model = PGx_RGCN(
        in_channels=x.size(-1),
        hidden_channels=cfg["model"]["hidden_dim"],
        out_channels=cfg["model"]["output_dim"],
        num_edge_types=num_edge_types,
        num_decoder_relations=len(rel_to_idx),
        num_bases=cfg["model"]["num_bases"],
        dropout=cfg["model"]["dropout"],
        drug_fp_dim=drug_fp_dim,
        n_drugs_for_fp=n_drugs_for_fp,
    ).to(device)
    if use_fingerprints:
        model.attach_drug_fingerprints(
            drug_fp.to(device),
            drug_has_fp.to(device),
            drug_offset=offsets["drug"],
        )
        logger.info(f"Drug fingerprints ATTACHED to model: "
                    f"{n_with_fp}/{n_drugs_for_fp} drugs have SMILES.")
    else:
        logger.info("Drug fingerprints NOT used (parquet absent). "
                    "Falling back to random Xavier drug features.")''',
)

# Save the fingerprint-usage flag in the checkpoint so stage 3 knows.
patch(
    "8b. checkpoint records use_fingerprints flag",
    '''    torch.save({
        "model_state": model.state_dict(),
        "config": cfg,
        "num_edge_types": num_edge_types,
        "num_decoder_relations": len(rel_to_idx),
        "best_val_mrr": float(best_val_mrr),
        "ablation_beta_zero": args.ablation_beta_zero,
    }, paths["artifacts_dir"] / "model_checkpoint.pt")''',
    '''    torch.save({
        "model_state": model.state_dict(),
        "config": cfg,
        "num_edge_types": num_edge_types,
        "num_decoder_relations": len(rel_to_idx),
        "best_val_mrr": float(best_val_mrr),
        "ablation_beta_zero": args.ablation_beta_zero,
        # Round 3 metadata
        "use_fingerprints": bool(use_fingerprints),
        "drug_fp_dim": int(drug_fp_dim) if drug_fp_dim is not None else None,
        "n_drugs_for_fp": int(n_drugs_for_fp),
    }, paths["artifacts_dir"] / "model_checkpoint.pt")''',
)

# -----------------------------------------------------------------
# Patch 9: stage 3 setup — read flag, construct model + attach if needed
# -----------------------------------------------------------------
patch(
    "9a. stage 3 reads use_fingerprints from checkpoint",
    '''    model = PGx_RGCN(
        in_channels=x.size(-1),
        hidden_channels=cfg["model"]["hidden_dim"],
        out_channels=cfg["model"]["output_dim"],
        num_edge_types=ckpt["num_edge_types"],
        num_decoder_relations=ckpt["num_decoder_relations"],
        num_bases=cfg["model"]["num_bases"],
        dropout=cfg["model"]["dropout"],
    ).to(device)
    model.load_state_dict(ckpt["model_state"])''',
    '''    # Round 3: check if checkpoint was trained with fingerprints
    use_fp_ck = bool(ckpt.get("use_fingerprints", False))
    drug_fp_dim_ck = ckpt.get("drug_fp_dim")
    n_drugs_for_fp_ck = int(ckpt.get("n_drugs_for_fp", 0))

    model = PGx_RGCN(
        in_channels=x.size(-1),
        hidden_channels=cfg["model"]["hidden_dim"],
        out_channels=cfg["model"]["output_dim"],
        num_edge_types=ckpt["num_edge_types"],
        num_decoder_relations=ckpt["num_decoder_relations"],
        num_bases=cfg["model"]["num_bases"],
        dropout=cfg["model"]["dropout"],
        drug_fp_dim=drug_fp_dim_ck if use_fp_ck else None,
        n_drugs_for_fp=n_drugs_for_fp_ck if use_fp_ck else 0,
    ).to(device)
    model.load_state_dict(ckpt["model_state"])

    # Attach the runtime fingerprint tensors (the buffers in state_dict are
    # already populated, but we re-attach to set drug_offset for safety).
    if use_fp_ck:
        fp_path = Path(paths["data_dir"]) / "drug_fingerprints.parquet"
        if fp_path.exists():
            drug_fp, drug_has_fp, _ = load_drug_fingerprints(
                fp_path, nodes, logger, fp_dim=drug_fp_dim_ck,
            )
            if drug_fp is not None:
                model.attach_drug_fingerprints(
                    drug_fp.to(device),
                    drug_has_fp.to(device),
                    drug_offset=node_offsets["drug"],
                )
                logger.info("Drug fingerprints re-attached for stage 3.")
        else:
            # Buffers in state_dict already carry the fingerprints; we only
            # need to set drug_offset
            model.drug_offset = int(node_offsets["drug"])
            logger.info("Using fingerprints from checkpoint buffers "
                        "(no parquet present).")''',
)

# -----------------------------------------------------------------
# Patch 10: stratified MRR in test_metrics.json
# -----------------------------------------------------------------
patch(
    "10. stratified MRR (with/without SMILES) in metrics output",
    '''    metrics = {
        "raw": {**metrics_raw, **cis_raw},
        "filtered": {**metrics_filt, **cis_filt},
    }''',
    '''    metrics = {
        "raw": {**metrics_raw, **cis_raw},
        "filtered": {**metrics_filt, **cis_filt},
    }

    # Round 3: stratified MRR by whether the test-drug head has a SMILES
    # fingerprint. query_has_fp comes from compute_ranks (parallel to
    # test_ranks_filt). Reported only when fingerprints are in use.
    if "query_has_fp" in dir() and query_has_fp is not None and query_has_fp.any():
        mask_with = query_has_fp
        mask_without = ~query_has_fp
        if mask_with.sum() > 0:
            ranks_w = test_ranks_filt[mask_with]
            m_w = metrics_from_ranks(ranks_w, hits_k_list)
            metrics["filtered_with_smiles"] = {
                **m_w,
                "n_queries_with_smiles": int(mask_with.sum()),
            }
        if mask_without.sum() > 0:
            ranks_wo = test_ranks_filt[mask_without]
            m_wo = metrics_from_ranks(ranks_wo, hits_k_list)
            metrics["filtered_without_smiles"] = {
                **m_wo,
                "n_queries_without_smiles": int(mask_without.sum()),
            }
        logger.info("Stratified filtered MRR:")
        if "filtered_with_smiles" in metrics:
            logger.info(f"  with SMILES    ({metrics['filtered_with_smiles']['n_queries_with_smiles']:4d} drugs): "
                        f"MRR={metrics['filtered_with_smiles']['mrr']:.4f}")
        if "filtered_without_smiles" in metrics:
            logger.info(f"  without SMILES ({metrics['filtered_without_smiles']['n_queries_without_smiles']:4d} drugs): "
                        f"MRR={metrics['filtered_without_smiles']['mrr']:.4f}")''',
)

# -----------------------------------------------------------------
# Write the patched file
# -----------------------------------------------------------------
SCRIPT.write_text(src)
print()
print(f"Total patches applied: {changes}")
print(f"Final line count:      {len(src.splitlines())}")

# Syntax check
import ast
try:
    ast.parse(src)
    print("Syntax check:          OK")
except SyntaxError as e:
    print(f"Syntax check FAILED:   line {e.lineno}: {e.msg}")
    sys.exit(1)
