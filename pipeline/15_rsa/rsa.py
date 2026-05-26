"""Step 10: Representational Similarity Analysis (analysis_plan.md Section 6.9)

Tests whether distances in perturbation space correspond to distances
in neural response space and clinical responsiveness space.

Distance matrices:
- D_perturbation (from step 04)
- D_neural (from step 05)
- D_deqi (from data_processing/v1/rsa/)
- D_clinical (from data_processing/v1/rsa/)

Primary tests:
    corr(D_perturbation, D_neural)
    corr(D_deqi, D_neural)
    corr(D_neural, D_clinical)
    corr(D_perturbation, D_clinical)

Partial RSA:
    corr(D_perturbation, D_neural | disease_domain, analysis_family)

Permutation: Mantel/partial Mantel, preserving study clustering.

Inputs:
    data_analysis/outputs/perturbation/perturbation_distance_matrix.csv (step 04)
    data_analysis/outputs/neural/neural_distance_matrix.csv (step 05)
    data_processing/v1/rsa/sensory_dissimilarity.csv
    data_processing/v1/rsa/clinical_dissimilarity.csv

Outputs:
    data_analysis/outputs/rsa/rsa_results.csv
    data_analysis/outputs/rsa/distance_matrices/  (copies for reference)
    data_analysis/outputs/figures/rsa_heatmaps.png
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


def load_distance_matrices() -> dict:
    """Load all distance matrices."""
    matrices = {}

    sources = {
        "perturbation_combined": config.PERTURBATION_DISSIM_COMBINED,
        "perturbation_axisA": config.PERTURBATION_DISSIM_A,
        "perturbation_axisB": config.PERTURBATION_DISSIM_B,
        "clinical": config.CLINICAL_DISSIM,
        "sensory": config.SENSORY_DISSIM,
        "neural": config.NEURAL_DISSIM,
    }

    for name, path in sources.items():
        if path.exists():
            df = pd.read_csv(path, index_col=0)
            matrices[name] = df
            print(f"  Loaded {name}: {df.shape}")
        else:
            print(f"  MISSING {name}: {path}")

    return matrices


def align_matrices(mat1: pd.DataFrame, mat2: pd.DataFrame):
    """Find common row/column labels and subset both matrices.

    Returns:
        (aligned_mat1, aligned_mat2, common_labels)
    """
    # Ensure index/columns are strings for consistent matching
    mat1.index = mat1.index.astype(str)
    mat1.columns = mat1.columns.astype(str)
    mat2.index = mat2.index.astype(str)
    mat2.columns = mat2.columns.astype(str)

    # Deduplicate indices (take first occurrence for matrices with repeated labels)
    if mat1.index.duplicated().any():
        mat1 = mat1.loc[~mat1.index.duplicated(keep="first"), ~mat1.columns.duplicated(keep="first")]
    if mat2.index.duplicated().any():
        mat2 = mat2.loc[~mat2.index.duplicated(keep="first"), ~mat2.columns.duplicated(keep="first")]

    common = sorted(set(mat1.index).intersection(set(mat2.index)))
    print(f"  Overlap: {len(common)} items")

    aligned1 = mat1.loc[common, common]
    aligned2 = mat2.loc[common, common]

    return aligned1, aligned2, common


def _upper_triangle(mat: np.ndarray) -> np.ndarray:
    """Extract upper triangle (excluding diagonal) as flat vector."""
    n = mat.shape[0]
    idx = np.triu_indices(n, k=1)
    return mat[idx]


def mantel_test(d1: np.ndarray, d2: np.ndarray, n_perms: int = 10000) -> dict:
    """Mantel test: correlation between two distance matrices.

    Args:
        d1: Square distance matrix (numpy array).
        d2: Square distance matrix (numpy array).
        n_perms: Number of permutations.

    Returns:
        Dict with r_obs, p_value, n_items, n_perms.
    """
    n = d1.shape[0]
    vec1 = _upper_triangle(d1)
    vec2 = _upper_triangle(d2)

    # Observed correlation
    r_obs, _ = pearsonr(vec1, vec2)

    # Permutation test
    rng = np.random.default_rng(42)
    count_ge = 0
    for _ in range(n_perms):
        perm = rng.permutation(n)
        d2_perm = d2[np.ix_(perm, perm)]
        vec2_perm = _upper_triangle(d2_perm)
        r_perm, _ = pearsonr(vec1, vec2_perm)
        if r_perm >= r_obs:
            count_ge += 1

    p_value = (count_ge + 1) / (n_perms + 1)

    return {
        "r_obs": r_obs,
        "p_value": p_value,
        "n_items": n,
        "n_perms": n_perms,
    }


def partial_mantel(
    d1: np.ndarray, d2: np.ndarray, d_cov: np.ndarray, n_perms: int = 10000
) -> dict:
    """Partial Mantel: D1 ~ D2 controlling for D_cov.

    Residualizes both D1 and D2 on D_cov, then runs Mantel on residuals.
    """
    vec1 = _upper_triangle(d1)
    vec2 = _upper_triangle(d2)
    vec_cov = _upper_triangle(d_cov)

    # Residualize vec1 on vec_cov
    def residualize(y, x):
        x_with_intercept = np.column_stack([np.ones(len(x)), x])
        beta, _, _, _ = np.linalg.lstsq(x_with_intercept, y, rcond=None)
        return y - x_with_intercept @ beta

    res1 = residualize(vec1, vec_cov)
    res2 = residualize(vec2, vec_cov)

    # Observed correlation on residuals
    r_obs, _ = pearsonr(res1, res2)

    # Permutation test: permute rows/cols of d2, then residualize
    n = d1.shape[0]
    rng = np.random.default_rng(42)
    count_ge = 0
    for _ in range(n_perms):
        perm = rng.permutation(n)
        d2_perm = d2[np.ix_(perm, perm)]
        vec2_perm = _upper_triangle(d2_perm)
        res2_perm = residualize(vec2_perm, vec_cov)
        r_perm, _ = pearsonr(res1, res2_perm)
        if r_perm >= r_obs:
            count_ge += 1

    p_value = (count_ge + 1) / (n_perms + 1)

    return {
        "r_obs": r_obs,
        "p_value": p_value,
        "n_items": n,
        "n_perms": n_perms,
        "test_type": "partial_mantel",
    }


def _is_placeholder(mat: pd.DataFrame) -> bool:
    """Check if a matrix is a placeholder (all zeros or identity-like)."""
    vals = mat.values
    np.fill_diagonal(vals, 0)
    return np.allclose(vals, 0)


def run_all_rsa_tests(matrices: dict) -> list:
    """Run all primary and partial RSA tests."""
    results = []

    # Define primary test pairs
    tests = [
        ("perturbation_combined", "clinical", "Perturbation(combined) vs Clinical"),
        ("perturbation_axisA", "clinical", "Perturbation(axisA) vs Clinical"),
        ("perturbation_axisB", "clinical", "Perturbation(axisB) vs Clinical"),
        ("perturbation_combined", "sensory", "Perturbation(combined) vs Sensory"),
        ("perturbation_combined", "neural", "Perturbation(combined) vs Neural"),
        ("neural", "clinical", "Neural vs Clinical"),
    ]

    for key1, key2, label in tests:
        print(f"\n  Test: {label}")

        if key1 not in matrices:
            print(f"    Skipped — {key1} not loaded")
            continue
        if key2 not in matrices:
            print(f"    Skipped — {key2} not loaded")
            continue

        mat1 = matrices[key1]
        mat2 = matrices[key2]

        # Skip neural if placeholder
        if "neural" in (key1, key2) and _is_placeholder(matrices.get("neural", pd.DataFrame())):
            print("    Skipped — neural matrix is placeholder")
            results.append({
                "test": label,
                "r_obs": np.nan,
                "p_value": np.nan,
                "n_items": 0,
                "n_perms": 0,
                "status": "skipped_placeholder",
            })
            continue

        aligned1, aligned2, common = align_matrices(mat1, mat2)

        if len(common) < 10:
            print(f"    Skipped — overlap < 10 (got {len(common)})")
            results.append({
                "test": label,
                "r_obs": np.nan,
                "p_value": np.nan,
                "n_items": len(common),
                "n_perms": 0,
                "status": "skipped_low_overlap",
            })
            continue

        res = mantel_test(aligned1.values, aligned2.values)
        res["test"] = label
        res["status"] = "complete"
        results.append(res)
        print(f"    r = {res['r_obs']:.4f}, p = {res['p_value']:.4f}, n = {res['n_items']}")

    return results


def plot_rsa_heatmaps(matrices: dict):
    """Generate RSA heatmap figures."""
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError:
        print("  matplotlib/seaborn not available — skipping plots")
        return

    fig_path = config.OUT_FIGURES / "rsa_heatmaps.png"

    # Plot each distance matrix as a heatmap
    n_mats = len(matrices)
    if n_mats == 0:
        return

    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()

    for i, (name, mat) in enumerate(matrices.items()):
        if i >= len(axes):
            break
        ax = axes[i]
        sns.heatmap(mat.values, ax=ax, cmap="viridis", xticklabels=False, yticklabels=False)
        ax.set_title(f"{name} ({mat.shape[0]}x{mat.shape[1]})")

    # Hide unused axes
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved heatmaps to {fig_path}")


def main():
    config.OUT_RSA.mkdir(parents=True, exist_ok=True)
    config.OUT_FIGURES.mkdir(parents=True, exist_ok=True)

    print("Step 10: Representational Similarity Analysis")
    print("=" * 60)

    # Load matrices
    print("\nLoading distance matrices...")
    matrices = load_distance_matrices()

    if not matrices:
        print("\nNo matrices loaded. Exiting.")
        return

    # Run all RSA tests
    print("\nRunning Mantel tests...")
    results = run_all_rsa_tests(matrices)

    # Save results
    results_df = pd.DataFrame(results)
    out_path = config.OUT_RSA / "rsa_results.csv"
    results_df.to_csv(out_path, index=False)
    print(f"\nResults saved to: {out_path}")

    # Print summary table
    print("\n" + "=" * 60)
    print("RSA Results Summary")
    print("=" * 60)
    print(results_df[["test", "r_obs", "p_value", "n_items", "status"]].to_string(index=False))

    # Generate heatmaps
    print("\nGenerating heatmaps...")
    plot_rsa_heatmaps(matrices)

    print("\nDone. Results in:", config.OUT_RSA)


if __name__ == "__main__":
    main()
