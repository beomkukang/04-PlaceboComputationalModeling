"""Step 04: Perturbation-Space Construction (analysis_plan.md Section 6.3)

Builds on the arm component matrix from data_processing/v1/ to
construct the full perturbation space with dimensionality reduction
and pairwise distance computation.

Steps:
1. Load encoded afferent, cognitive-perceptual, deqi variables
2. Generate composite scores and retain original components
3. Perform PCA for visualization
4. Calculate pairwise Gower distances between interventions

Inputs:
    data_processing/v1/meta_regression/study_predictors.csv
    data_processing/v1/perturbation_space/arm_components.csv

Outputs:
    data_analysis/outputs/perturbation/perturbation_pca_coordinates.csv
    data_analysis/outputs/perturbation/perturbation_distance_matrix.csv
    data_analysis/outputs/figures/perturbation_space_scatter.png
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config

# ---------------------------------------------------------------------------
# Column definitions
# ---------------------------------------------------------------------------

# Afferent Input Index components (Section 4.1)
AFFERENT_COLS = [
    "penetration_level",
    "skin_contact",
    "electrical_stim",
    "manipulation_intensity",
    "needle_retention_min",
    "n_sessions",
]

# Cognitive-Perceptual Anchoring components (Section 4.2, design-proxy)
COGNITIVE_COLS = [
    "blinding_quality",
    "practitioner_interaction",
    "treatment_rationale_given",
]

# All numeric perturbation variables used for PCA
PCA_COLS = AFFERENT_COLS + COGNITIVE_COLS


# ---------------------------------------------------------------------------
# Composite scores
# ---------------------------------------------------------------------------

def _zscore_columns(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Z-score the requested columns, ignoring NaN."""
    out = df.copy()
    for c in cols:
        if c in out.columns:
            vals = out[c].astype(float)
            mu = vals.mean()
            sd = vals.std()
            if sd > 0:
                out[f"{c}_z"] = (vals - mu) / sd
            else:
                out[f"{c}_z"] = 0.0
    return out


def build_composite_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Generate composite indices for afferent and cognitive dimensions.

    Each index is the simple average of its z-scored component columns,
    computed row-wise with NaN-tolerance (nanmean).
    """
    df = _zscore_columns(df, AFFERENT_COLS + COGNITIVE_COLS)

    # Afferent Input Index
    aff_z = [f"{c}_z" for c in AFFERENT_COLS if f"{c}_z" in df.columns]
    df["Afferent_Input_Index"] = df[aff_z].mean(axis=1)  # nanmean by default

    # Cognitive-Perceptual Anchoring
    cog_z = [f"{c}_z" for c in COGNITIVE_COLS if f"{c}_z" in df.columns]
    df["Cognitive_Anchoring"] = df[cog_z].mean(axis=1)

    return df


# ---------------------------------------------------------------------------
# Dimensionality reduction
# ---------------------------------------------------------------------------

def run_dimensionality_reduction(df: pd.DataFrame) -> pd.DataFrame:
    """PCA on numeric perturbation variables for visualization.

    Returns the input dataframe augmented with PC1, PC2, ... columns and
    a column for explained variance info.
    """
    available = [c for c in PCA_COLS if c in df.columns]
    X = df[available].copy().astype(float)

    # Impute missing with column median for PCA (preserves all rows)
    for c in X.columns:
        median_val = X[c].median()
        X[c] = X[c].fillna(median_val)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Fit PCA retaining enough components for >= 80 % variance (or all)
    n_comp = min(len(available), len(X))
    pca = PCA(n_components=n_comp)
    coords = pca.fit_transform(X_scaled)

    cumvar = np.cumsum(pca.explained_variance_ratio_)
    n_keep = int(np.searchsorted(cumvar, 0.80) + 1)
    n_keep = max(n_keep, 2)  # always keep at least 2 for plotting

    for i in range(n_keep):
        df[f"PC{i+1}"] = coords[:, i]

    # Store variance explained as metadata string on the first row
    var_str = ", ".join(
        f"PC{i+1}={pca.explained_variance_ratio_[i]:.3f}" for i in range(n_keep)
    )
    print(f"  PCA variance explained: {var_str}")
    print(f"  Cumulative variance at {n_keep} PCs: {cumvar[n_keep-1]:.3f}")

    return df, pca


# ---------------------------------------------------------------------------
# Gower distance (manual implementation)
# ---------------------------------------------------------------------------

def _gower_distance_matrix(
    df: pd.DataFrame,
    numeric_cols: list[str],
    categorical_cols: list[str] | None = None,
) -> np.ndarray:
    """Compute Gower distance matrix.

    Numeric: |a - b| / range  (skip if both NaN)
    Categorical: 0 if equal, 1 if different  (skip if either NaN)
    Final distance = mean of per-variable partial distances.
    """
    if categorical_cols is None:
        categorical_cols = []

    n = len(df)
    dist = np.zeros((n, n))

    # Precompute numeric arrays and ranges
    num_arrays = {}
    num_ranges = {}
    for c in numeric_cols:
        vals = df[c].astype(float).values
        r = np.nanmax(vals) - np.nanmin(vals)
        num_arrays[c] = vals
        num_ranges[c] = r if r > 0 else 1.0  # avoid div-by-zero

    cat_arrays = {}
    for c in categorical_cols:
        cat_arrays[c] = df[c].values

    all_cols = numeric_cols + categorical_cols

    for i in range(n):
        for j in range(i + 1, n):
            partial_sum = 0.0
            count = 0
            for c in numeric_cols:
                a, b = num_arrays[c][i], num_arrays[c][j]
                if np.isnan(a) or np.isnan(b):
                    continue
                partial_sum += abs(a - b) / num_ranges[c]
                count += 1
            for c in categorical_cols:
                a, b = cat_arrays[c][i], cat_arrays[c][j]
                if pd.isna(a) or pd.isna(b):
                    continue
                partial_sum += 0.0 if a == b else 1.0
                count += 1
            dist[i, j] = partial_sum / count if count > 0 else np.nan
            dist[j, i] = dist[i, j]

    return dist


def compute_pairwise_distances(df: pd.DataFrame) -> pd.DataFrame:
    """Compute pairwise Gower distance matrix between arms."""
    available_num = [c for c in PCA_COLS if c in df.columns]
    # arm_type is categorical for Gower
    cat_cols = ["arm_type"] if "arm_type" in df.columns else []

    dist_mat = _gower_distance_matrix(df, available_num, cat_cols)

    labels = df["arm_id"].values if "arm_id" in df.columns else df.index.astype(str)
    dist_df = pd.DataFrame(dist_mat, index=labels, columns=labels)
    return dist_df


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_perturbation_space(df: pd.DataFrame, save_path: Path):
    """Scatter plot of PC1 vs PC2 colored by arm_type."""
    if "PC1" not in df.columns or "PC2" not in df.columns:
        print("  [WARN] PC1/PC2 not found; skipping scatter plot.")
        return

    fig, ax = plt.subplots(figsize=(8, 6))

    # Color map for arm types
    type_col = "arm_type" if "arm_type" in df.columns else None
    if type_col is not None:
        categories = df[type_col].fillna("unknown").unique()
        cmap = plt.cm.get_cmap("tab10", len(categories))
        color_map = {cat: cmap(i) for i, cat in enumerate(sorted(categories))}
        for cat in sorted(categories):
            mask = df[type_col].fillna("unknown") == cat
            ax.scatter(
                df.loc[mask, "PC1"],
                df.loc[mask, "PC2"],
                label=cat,
                color=color_map[cat],
                alpha=0.7,
                edgecolors="k",
                linewidths=0.3,
                s=60,
            )
        ax.legend(title="Arm Type", fontsize=8, title_fontsize=9)
    else:
        ax.scatter(df["PC1"], df["PC2"], alpha=0.7, edgecolors="k", linewidths=0.3)

    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title("Perturbation Space (PCA)")
    ax.axhline(0, color="grey", linewidth=0.5, linestyle="--")
    ax.axvline(0, color="grey", linewidth=0.5, linestyle="--")
    fig.tight_layout()
    fig.savefig(save_path, dpi=300)
    plt.close(fig)
    print(f"  Saved scatter plot -> {save_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    config.OUT_PERTURBATION.mkdir(parents=True, exist_ok=True)
    config.OUT_FIGURES.mkdir(parents=True, exist_ok=True)

    print("Step 04: Perturbation Space Construction")
    print("=" * 60)

    # --- Load inputs ---
    print("Loading study_predictors.csv ...")
    preds = pd.read_csv(config.STUDY_PREDICTORS)
    print(f"  {len(preds)} rows, {len(preds.columns)} columns")

    print("Loading arm_components.csv ...")
    arms = pd.read_csv(config.ARM_COMPONENTS)
    print(f"  {len(arms)} rows, {len(arms.columns)} columns")

    # Merge arm_type from arm_components into predictors
    arm_type_map = arms[["arm_id", "arm_type"]].drop_duplicates()
    df = preds.merge(arm_type_map, on="arm_id", how="left")
    print(f"  Merged dataset: {len(df)} rows")

    # --- Composite scores ---
    print("Computing composite scores ...")
    df = build_composite_scores(df)
    aff_valid = df["Afferent_Input_Index"].notna().sum()
    cog_valid = df["Cognitive_Anchoring"].notna().sum()
    print(f"  Afferent_Input_Index: {aff_valid}/{len(df)} non-null")
    print(f"  Cognitive_Anchoring:  {cog_valid}/{len(df)} non-null")

    # --- Dimensionality reduction ---
    print("Running PCA ...")
    df, pca_model = run_dimensionality_reduction(df)

    # --- Pairwise distances ---
    print("Computing Gower distance matrix ...")
    dist_df = compute_pairwise_distances(df)
    print(f"  Distance matrix shape: {dist_df.shape}")

    # --- Plot ---
    scatter_path = config.OUT_FIGURES / "perturbation_space_scatter.png"
    plot_perturbation_space(df, scatter_path)

    # --- Save outputs ---
    # PCA coordinates + composite indices
    out_cols = ["arm_id", "pmid", "arm_type",
                "Afferent_Input_Index", "Cognitive_Anchoring"]
    pc_cols = [c for c in df.columns if c.startswith("PC")]
    out_cols += pc_cols
    # Also include the raw perturbation variables for reference
    out_cols += [c for c in PCA_COLS if c in df.columns]
    # Keep only columns that exist
    out_cols = [c for c in out_cols if c in df.columns]
    coords_out = df[out_cols].copy()
    coords_path = config.OUT_PERTURBATION / "perturbation_pca_coordinates.csv"
    coords_out.to_csv(coords_path, index=False)
    print(f"  Saved PCA coordinates -> {coords_path}")

    dist_path = config.OUT_PERTURBATION / "perturbation_distance_matrix.csv"
    dist_df.to_csv(dist_path)
    print(f"  Saved distance matrix  -> {dist_path}")

    print("=" * 60)
    print("Done. Results in:", config.OUT_PERTURBATION)


if __name__ == "__main__":
    main()
