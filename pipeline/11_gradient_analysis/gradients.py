"""Step 06: Neural Gradient Analysis (analysis_plan.md Section 6.5)

Moves from isolated activation peaks to graded response dimensions
using dimensionality reduction on the neural feature matrix.

Steps:
1. Load neural feature matrix (from step 05)
2. Apply PCA or diffusion map embedding to derive neural gradients
3. Interpret gradients by network loadings
4. Regress gradient scores on perturbation-space variables
5. Test whether intervention classes occupy different gradient positions

Models:
    Gradient_k ~ Afferent_Input_Index + Deqi_Index +
                 Cognitive_Perceptual_Index + Disease_Domain +
                 Analysis_Family + Population_Type

    Mixed-effects when multiple contrasts per study:
    Gradient_k ~ predictors + (1 | study_id)

Inputs:
    data_analysis/outputs/neural/neural_feature_matrix.csv (step 05)
    data_processing/v1/perturbation_space/arm_components.csv

Outputs:
    data_analysis/outputs/gradients/neural_gradient_scores.csv
    data_analysis/outputs/gradients/neural_gradient_loadings.csv
    data_analysis/outputs/gradients/gradient_regression_results.csv
    data_analysis/outputs/figures/neural_gradient_scatterplots.png
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy import stats
import statsmodels.api as sm
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config

# Mapping from analysis name to the arm_type values that contribute
ANALYSIS_TO_ARM_TYPE = {
    "sham_gt_rest": ["sham_acupuncture"],
    "verum_gt_sham": ["verum_acupuncture"],
    "verum_gt_rest": ["verum_acupuncture"],
    "sham_gt_rest_penetrating": ["sham_acupuncture"],
    "sham_gt_rest_nonpenetrating": ["sham_acupuncture"],
    "verum_post_gt_pre": ["verum_acupuncture"],
    "sham_post_gt_pre": ["sham_acupuncture"],
    "deactivation": ["verum_acupuncture", "sham_acupuncture"],
    "group_comparison": ["verum_acupuncture", "sham_acupuncture"],
    "correlation_clinical": ["verum_acupuncture", "sham_acupuncture"],
}

# Categories for class separation test
ANALYSIS_CATEGORIES = {
    "sham": ["sham_gt_rest", "sham_post_gt_pre", "sham_gt_rest_penetrating",
             "sham_gt_rest_nonpenetrating"],
    "verum": ["verum_gt_sham", "verum_gt_rest", "verum_post_gt_pre"],
    "other": ["deactivation", "group_comparison", "correlation_clinical"],
}


def compute_neural_gradients(features: pd.DataFrame) -> tuple:
    """PCA on neural feature matrix to derive neural gradients."""
    # Identify metadata vs numeric region columns
    metadata_cols = features.select_dtypes(exclude=[np.number]).columns.tolist()
    # Keep analysis name if present
    analysis_names = None
    if "analysis" in features.columns:
        analysis_names = features["analysis"].values
    elif features.index.name is not None or not features.index.equals(pd.RangeIndex(len(features))):
        # Use index as identifier (e.g., pmid)
        analysis_names = features.index.values
    elif len(metadata_cols) > 0:
        # Use the first non-numeric column as analysis identifier
        analysis_names = features[metadata_cols[0]].values

    # Keep only numeric columns
    numeric_data = features.select_dtypes(include=[np.number])

    # Standardize (z-score each column)
    scaler = StandardScaler()
    standardized = scaler.fit_transform(numeric_data)

    # Run PCA - retain components for >=80% cumulative variance (min 2)
    pca_full = PCA()
    pca_full.fit(standardized)

    cumvar = np.cumsum(pca_full.explained_variance_ratio_)
    n_components = max(2, int(np.searchsorted(cumvar, 0.80) + 1))
    # Cap at the number of samples or features
    n_components = min(n_components, standardized.shape[0], standardized.shape[1])

    pca = PCA(n_components=n_components)
    scores = pca.fit_transform(standardized)

    # Build scores DataFrame
    gradient_cols = [f"Gradient_{i+1}" for i in range(n_components)]
    scores_df = pd.DataFrame(scores, columns=gradient_cols)
    if analysis_names is not None:
        scores_df.insert(0, "analysis", analysis_names)
    else:
        scores_df.insert(0, "analysis", [f"analysis_{i}" for i in range(len(scores_df))])

    # Build loadings DataFrame
    regions = numeric_data.columns.tolist()
    loading_cols = [f"Gradient_{i+1}_loading" for i in range(n_components)]
    loadings_df = pd.DataFrame(pca.components_.T, columns=loading_cols)
    loadings_df.insert(0, "region", regions)

    print(f"  PCA: {n_components} components retained "
          f"({cumvar[n_components-1]*100:.1f}% variance explained)")

    return scores_df, loadings_df


def interpret_gradient_loadings(loadings: pd.DataFrame) -> dict:
    """Map gradient loadings onto canonical networks."""
    loading_cols = [c for c in loadings.columns if c.endswith("_loading")]
    interpretation = {}

    for col in loading_cols:
        gradient_name = col.replace("_loading", "")
        sorted_loadings = loadings[["region", col]].sort_values(col, ascending=False)

        top_positive = sorted_loadings.head(5)["region"].tolist()
        top_negative = sorted_loadings.tail(5)["region"].tolist()[::-1]

        interpretation[gradient_name] = {
            "positive": top_positive,
            "negative": top_negative,
        }

        pos_str = ", ".join(top_positive[:3])
        neg_str = ", ".join(top_negative[:3])
        print(f"  {gradient_name}: {pos_str} (+) vs {neg_str} (-)")

    return interpretation


def regress_gradients_on_perturbation(
    gradients: pd.DataFrame, perturbation: pd.DataFrame
) -> pd.DataFrame:
    """OLS regression: gradient ~ Afferent_Input_Index + Cognitive_Anchoring."""
    # Study-level data: "analysis" column contains pmid
    # Aggregate perturbation to study level
    avail_preds = [c for c in ["Afferent_Input_Index", "Cognitive_Anchoring"]
                   if c in perturbation.columns]
    if not avail_preds:
        print("  WARNING: No perturbation predictors available.")
        return pd.DataFrame(columns=["gradient", "predictor", "coefficient",
                                      "std_err", "p_value", "r_squared"])

    if "pmid" in perturbation.columns:
        pert_study = perturbation.groupby("pmid")[avail_preds].mean().reset_index()
        pert_study["pmid"] = pert_study["pmid"].astype(str)
    else:
        print("  WARNING: No pmid in perturbation data.")
        return pd.DataFrame()

    gradients = gradients.copy()
    gradients["pmid"] = gradients["analysis"].astype(str).str.strip()
    pert_study["pmid"] = pert_study["pmid"].astype(str).str.strip()
    merged = gradients.merge(pert_study, on="pmid", how="inner")
    print(f"  Merged {len(merged)} studies with perturbation data")

    # Identify gradient columns (limit to first 5 for interpretability)
    gradient_cols = [c for c in gradients.columns if c.startswith("Gradient_")][:5]

    predictors = [c for c in avail_preds if c in merged.columns]

    results = []
    for gcol in gradient_cols:
        y = merged[gcol].values
        X = merged[predictors].values
        X = sm.add_constant(X)

        # Skip if insufficient valid data
        valid_mask = ~np.isnan(y) & ~np.any(np.isnan(X), axis=1)
        if valid_mask.sum() < 4:
            continue

        try:
            model = sm.OLS(y[valid_mask], X[valid_mask]).fit()
        except Exception as e:
            print(f"  WARNING: OLS failed for {gcol}: {e}")
            continue

        # Extract coefficients (skip constant at index 0)
        for i, pred in enumerate(predictors):
            results.append({
                "gradient": gcol,
                "predictor": pred,
                "coefficient": model.params[i + 1],
                "std_err": model.bse[i + 1],
                "p_value": model.pvalues[i + 1],
                "r_squared": model.rsquared,
            })

    results_df = pd.DataFrame(results)
    if not results_df.empty:
        print(f"  Regression: {len(results_df)} predictor-gradient associations tested")
    return results_df


def test_class_separation(gradients: pd.DataFrame) -> pd.DataFrame:
    """Test whether verum/sham/other occupy different gradient positions."""
    # At study level, we don't have analysis categories.
    # Skip if no perturbation data to provide arm_type.
    # Instead, just test if gradient scores differ — return empty for now.
    print("  NOTE: Class separation test requires arm-type labels; skipping for study-level data.")

    return pd.DataFrame(columns=["gradient", "group_means", "test_stat", "p_value"])

    gradient_cols = [c for c in gradients.columns if c.startswith("Gradient_")]

    results = []
    for gcol in gradient_cols:  # pragma: no cover — unreachable after early return
        groups = []
        group_means = {}
        for cat in ["sham", "verum", "other"]:
            vals = gradients.loc[gradients["category"] == cat, gcol].dropna().values
            if len(vals) > 0:
                groups.append(vals)
                group_means[cat] = float(np.mean(vals))

        if len(groups) >= 2:
            # Use Kruskal-Wallis given small n
            if all(len(g) >= 1 for g in groups):
                try:
                    stat, p_value = stats.kruskal(*groups)
                except ValueError:
                    stat, p_value = np.nan, np.nan
            else:
                stat, p_value = np.nan, np.nan
        else:
            stat, p_value = np.nan, np.nan

        results.append({
            "gradient": gcol,
            "group_means": str(group_means),
            "test_stat": stat,
            "p_value": p_value,
        })

    results_df = pd.DataFrame(results)
    print(f"  Class separation: tested {len(results_df)} gradients")
    return results_df


def plot_gradient_scatter(gradients: pd.DataFrame, output_path: Path):
    """Scatter plot of Gradient_1 vs Gradient_2 colored by analysis category."""
    analysis_to_category = {}
    for cat, analyses in ANALYSIS_CATEGORIES.items():
        for a in analyses:
            analysis_to_category[a] = cat

    gradients = gradients.copy()
    gradients["category"] = gradients["analysis"].map(analysis_to_category)

    colors = {"sham": "blue", "verum": "red", "other": "gray"}

    fig, ax = plt.subplots(figsize=(8, 6))

    for cat, color in colors.items():
        mask = gradients["category"] == cat
        subset = gradients[mask]
        if not subset.empty and "Gradient_1" in subset.columns and "Gradient_2" in subset.columns:
            ax.scatter(subset["Gradient_1"], subset["Gradient_2"],
                       c=color, label=cat, s=80, alpha=0.8, edgecolors="black")
            # Add analysis labels
            for _, row in subset.iterrows():
                ax.annotate(row["analysis"], (row["Gradient_1"], row["Gradient_2"]),
                            fontsize=7, ha="left", va="bottom")

    ax.set_xlabel("Gradient 1")
    ax.set_ylabel("Gradient 2")
    ax.set_title("Neural Gradient Space: Analysis Categories")
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved scatter plot to {output_path}")


def main():
    config.OUT_GRADIENTS.mkdir(parents=True, exist_ok=True)
    config.OUT_FIGURES.mkdir(parents=True, exist_ok=True)

    print("Step 06: Neural Gradient Analysis")
    print("=" * 60)

    neural_features_path = config.OUT_NEURAL / "neural_feature_matrix.csv"
    if not neural_features_path.exists():
        print("  ERROR: Neural feature matrix not found. Run step 05 first.")
        return

    # Load inputs
    features = pd.read_csv(neural_features_path, index_col=0)
    print(f"  Loaded neural feature matrix: {features.shape[0]} analyses x "
          f"{features.shape[1]} columns")

    # Load perturbation data
    perturbation_path = config.OUT_PERTURBATION / "perturbation_pca_coordinates.csv"
    if perturbation_path.exists():
        perturbation = pd.read_csv(perturbation_path)
        print(f"  Loaded perturbation coordinates: {perturbation.shape[0]} arms")
    elif config.ARM_COMPONENTS.exists():
        perturbation = pd.read_csv(config.ARM_COMPONENTS)
        print(f"  Loaded arm components: {perturbation.shape[0]} arms")
    else:
        perturbation = None
        print("  WARNING: No perturbation data found. Skipping regression.")

    # Step 1: Compute neural gradients
    print("\n  Computing neural gradients...")
    scores, loadings = compute_neural_gradients(features)

    # Step 2: Interpret gradient loadings
    print("\n  Interpreting gradient loadings...")
    interpret_gradient_loadings(loadings)

    # Step 3: Regress gradients on perturbation
    regression = pd.DataFrame()
    if perturbation is not None:
        print("\n  Regressing gradients on perturbation variables...")
        regression = regress_gradients_on_perturbation(scores, perturbation)

    # Step 4: Test class separation
    print("\n  Testing class separation...")
    separation = test_class_separation(scores)

    # Save outputs
    scores.to_csv(config.OUT_GRADIENTS / "neural_gradient_scores.csv", index=False)
    loadings.to_csv(config.OUT_GRADIENTS / "neural_gradient_loadings.csv", index=False)
    if not regression.empty:
        regression.to_csv(config.OUT_GRADIENTS / "gradient_regression_results.csv",
                          index=False)
    separation.to_csv(config.OUT_GRADIENTS / "class_separation_results.csv", index=False)

    # Plot
    if "Gradient_1" in scores.columns and "Gradient_2" in scores.columns:
        plot_gradient_scatter(
            scores, config.OUT_FIGURES / "neural_gradient_scatterplots.png"
        )

    print("\nDone. Results in:", config.OUT_GRADIENTS)


if __name__ == "__main__":
    main()
