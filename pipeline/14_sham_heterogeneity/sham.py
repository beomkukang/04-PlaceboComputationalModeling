"""Step 09: Sham Heterogeneity Analysis (analysis_plan.md Section 6.8)

Central analysis: explain why sham-acupuncture fMRI responses vary
using component-level covariates rather than sham labels.

Working hypothesis: sham responses differ because sham procedures
vary in physical stimulation AND in how participants perceive,
interpret, and anchor the intervention.

Analyses:
1. Build sham-only analytic dataset
2. Descriptive: do sham types occupy distinct perturbation positions?
3. Sequential models testing component explanations:
   Model 0: Afferent ~ 1 (null)
   Model 1: Afferent ~ sham_penetration_level
   Model 2: Afferent ~ sham_penetration_level + sham_skin_contact + sham_at_acupoints
4. Anchoring-specific tests (cognitive anchoring ~ visual cue + blinding)
5. Visualization of sham arms in perturbation space

Inputs:
    data_processing/v1/perturbation_space/sham_decomposition.csv
    data_processing/v1/meta_regression/study_predictors.csv
    data_processing/v1/sensory/deqi_summary_by_arm.csv
    data_analysis/outputs/perturbation/perturbation_pca_coordinates.csv

Outputs:
    data_analysis/outputs/sham/sham_component_table.csv
    data_analysis/outputs/sham/sham_descriptive_models.csv
    data_analysis/outputs/sham/sham_anchoring_tests.csv
    data_analysis/outputs/figures/sham_perturbation_space.png
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


def build_sham_dataset() -> pd.DataFrame:
    """Build sham-only analytic dataset with all covariates."""

    # Load sham decomposition
    sham_path = config.SHAM_DECOMPOSITION
    if not sham_path.exists():
        print(f"  WARNING: {sham_path} not found. Cannot build sham dataset.")
        return pd.DataFrame()

    sham_df = pd.read_csv(sham_path)
    print(f"  Loaded sham_decomposition: {len(sham_df)} rows")

    # Ensure pmid is string for merging
    sham_df["pmid"] = sham_df["pmid"].astype(str)

    # Merge with study_predictors for numeric codes
    predictors_path = config.STUDY_PREDICTORS
    if predictors_path.exists():
        predictors = pd.read_csv(predictors_path)
        predictors["pmid"] = predictors["pmid"].astype(str)
        # Keep relevant predictor columns
        pred_cols = [
            c for c in predictors.columns
            if c in [
                "arm_id", "pmid", "penetration_level",
                "sham_penetration_level", "sham_skin_contact",
                "sham_at_acupoints", "sham_visual_cue",
                "blinding_quality", "electrical_stim", "skin_contact",
            ]
        ]
        predictors_subset = predictors[pred_cols].drop_duplicates()
        sham_df = sham_df.merge(
            predictors_subset, on=["pmid", "arm_id"], how="left"
        )
        print(f"  After merge with study_predictors: {len(sham_df)} rows")
    else:
        print(f"  WARNING: {predictors_path} not found. Skipping predictor merge.")

    # Merge with perturbation PCA coordinates for composite indices
    pca_path = config.OUT_PERTURBATION / "perturbation_pca_coordinates.csv"
    if pca_path.exists():
        pca_df = pd.read_csv(pca_path)
        pca_df["pmid"] = pca_df["pmid"].astype(str)
        pca_cols = [
            c for c in pca_df.columns
            if c in [
                "arm_id", "pmid", "arm_type",
                "Afferent_Input_Index", "Cognitive_Anchoring",
                "PC1", "PC2", "PC3", "PC4", "PC5",
            ]
        ]
        pca_subset = pca_df[pca_cols].drop_duplicates()
        sham_df = sham_df.merge(
            pca_subset, on=["pmid", "arm_id"], how="left"
        )
        print(f"  After merge with PCA coordinates: {len(sham_df)} rows")
    else:
        print(f"  WARNING: {pca_path} not found. Skipping PCA merge.")

    # Optionally merge deqi summary for sham arms
    deqi_path = config.DEQI_SUMMARY
    if deqi_path.exists():
        deqi_df = pd.read_csv(deqi_path)
        deqi_df["pmid"] = deqi_df["pmid"].astype(str)
        # Filter to sham arms if arm_type is available
        if "arm_type" in deqi_df.columns:
            deqi_sham = deqi_df[
                deqi_df["arm_type"].str.contains("sham", case=False, na=False)
            ].copy()
        else:
            deqi_sham = deqi_df.copy()
        if not deqi_sham.empty:
            # Parse numeric values from strings like "3.6±2.1"
            deqi_sham["_value_num"] = pd.to_numeric(
                deqi_sham["value"].astype(str).str.extract(r"([\d.]+)", expand=False),
                errors="coerce",
            )
            # Pivot or aggregate deqi values per arm
            deqi_agg = (
                deqi_sham.groupby(["pmid", "arm_id"])["_value_num"]
                .mean()
                .reset_index()
                .rename(columns={"_value_num": "deqi_mean"})
            )
            sham_df = sham_df.merge(
                deqi_agg, on=["pmid", "arm_id"], how="left"
            )
            print(f"  After merge with deqi: {len(sham_df)} rows")
    else:
        print(f"  WARNING: {deqi_path} not found. Skipping deqi merge.")

    # Optionally merge neural gradient scores if available
    gradient_path = config.OUT_GRADIENTS / "neural_gradient_scores.csv"
    if gradient_path.exists():
        grad_df = pd.read_csv(gradient_path)
        grad_df["pmid"] = grad_df["pmid"].astype(str) if "pmid" in grad_df.columns else grad_df["pmid"]
        grad_cols = [c for c in grad_df.columns if c in ["arm_id", "pmid", "gradient_score"]]
        if len(grad_cols) >= 2:
            sham_df = sham_df.merge(
                grad_df[grad_cols].drop_duplicates(),
                on=["pmid", "arm_id"], how="left"
            )
            print(f"  After merge with gradients: {len(sham_df)} rows")
    else:
        print(f"  NOTE: {gradient_path} not found (may not be generated yet).")

    print(f"  Final sham dataset: {len(sham_df)} rows, {len(sham_df.columns)} columns")
    return sham_df


def compute_descriptive_stats(sham_df: pd.DataFrame) -> pd.DataFrame:
    """Compute descriptive statistics grouped by sham subtype."""

    if sham_df.empty:
        print("  WARNING: Empty sham dataset. Skipping descriptive stats.")
        return pd.DataFrame()

    # Determine grouping variable
    if "sham_subtype" in sham_df.columns:
        group_col = "sham_subtype"
    elif "sham_penetration_level" in sham_df.columns:
        group_col = "sham_penetration_level"
    elif "sham_penetration" in sham_df.columns:
        group_col = "sham_penetration"
    else:
        print("  WARNING: No sham grouping variable found. Using full sample.")
        group_col = None

    # Metrics to summarize
    metrics = ["Afferent_Input_Index", "Cognitive_Anchoring", "PC1", "PC2"]
    available_metrics = [m for m in metrics if m in sham_df.columns]

    if not available_metrics:
        print("  WARNING: No perturbation metrics available for descriptive stats.")
        return pd.DataFrame()

    if group_col is not None:
        grouped = sham_df.groupby(group_col)
        results = []
        for name, grp in grouped:
            row = {group_col: name, "n_studies": grp["pmid"].nunique(), "n_arms": len(grp)}
            for m in available_metrics:
                vals = grp[m].dropna()
                row[f"{m}_mean"] = vals.mean() if len(vals) > 0 else np.nan
                row[f"{m}_sd"] = vals.std() if len(vals) > 1 else np.nan
            results.append(row)
        desc_df = pd.DataFrame(results)
    else:
        row = {"group": "all", "n_studies": sham_df["pmid"].nunique(), "n_arms": len(sham_df)}
        for m in available_metrics:
            vals = sham_df[m].dropna()
            row[f"{m}_mean"] = vals.mean() if len(vals) > 0 else np.nan
            row[f"{m}_sd"] = vals.std() if len(vals) > 1 else np.nan
        desc_df = pd.DataFrame([row])

    # Save
    out_path = config.OUT_SHAM / "sham_component_table.csv"
    desc_df.to_csv(out_path, index=False)
    print(f"  Saved descriptive stats to {out_path}")
    return desc_df


def fit_sequential_models(sham_df: pd.DataFrame) -> pd.DataFrame:
    """Fit sequential OLS models predicting Afferent_Input_Index from sham characteristics."""

    if sham_df.empty:
        print("  WARNING: Empty sham dataset. Skipping model fitting.")
        return pd.DataFrame()

    # Check for required outcome
    if "Afferent_Input_Index" not in sham_df.columns:
        print("  WARNING: Afferent_Input_Index not available. Skipping models.")
        return pd.DataFrame()

    # Drop rows with missing outcome
    model_df = sham_df.dropna(subset=["Afferent_Input_Index"]).copy()
    n = len(model_df)

    if n < 20:
        print(f"  WARNING: Only {n} observations with Afferent_Input_Index. "
              f"Need >=20 for model fitting. Skipping.")
        return pd.DataFrame()

    try:
        import statsmodels.api as sm
        import statsmodels.formula.api as smf
    except ImportError:
        print("  WARNING: statsmodels not available. Skipping model fitting.")
        return pd.DataFrame()

    results = []

    # Model 0: Null (intercept only)
    try:
        m0 = smf.ols("Afferent_Input_Index ~ 1", data=model_df).fit()
        results.append({
            "model": "Model 0 (null)",
            "formula": "Afferent ~ 1",
            "n": int(m0.nobs),
            "df_model": int(m0.df_model),
            "r_squared": m0.rsquared,
            "adj_r_squared": m0.rsquared_adj,
            "aic": m0.aic,
            "bic": m0.bic,
        })
    except Exception as e:
        print(f"  WARNING: Model 0 failed: {e}")

    # Model 1: + sham_penetration_level
    if "sham_penetration_level" in model_df.columns:
        df1 = model_df.dropna(subset=["sham_penetration_level"])
        if len(df1) >= 20:
            try:
                m1 = smf.ols(
                    "Afferent_Input_Index ~ sham_penetration_level", data=df1
                ).fit()
                results.append({
                    "model": "Model 1 (penetration)",
                    "formula": "Afferent ~ sham_penetration_level",
                    "n": int(m1.nobs),
                    "df_model": int(m1.df_model),
                    "r_squared": m1.rsquared,
                    "adj_r_squared": m1.rsquared_adj,
                    "aic": m1.aic,
                    "bic": m1.bic,
                })
            except Exception as e:
                print(f"  WARNING: Model 1 failed: {e}")
    else:
        print("  WARNING: sham_penetration_level not available for Model 1.")

    # Model 2: + sham_skin_contact + sham_at_acupoints
    model2_vars = ["sham_penetration_level", "sham_skin_contact", "sham_at_acupoints"]
    available_vars = [v for v in model2_vars if v in model_df.columns]
    if len(available_vars) >= 2:
        df2 = model_df.dropna(subset=available_vars)
        if len(df2) >= 20:
            formula2 = "Afferent_Input_Index ~ " + " + ".join(available_vars)
            try:
                m2 = smf.ols(formula2, data=df2).fit()
                results.append({
                    "model": "Model 2 (multi-component)",
                    "formula": formula2.replace("Afferent_Input_Index", "Afferent"),
                    "n": int(m2.nobs),
                    "df_model": int(m2.df_model),
                    "r_squared": m2.rsquared,
                    "adj_r_squared": m2.rsquared_adj,
                    "aic": m2.aic,
                    "bic": m2.bic,
                })
            except Exception as e:
                print(f"  WARNING: Model 2 failed: {e}")
    else:
        print(f"  WARNING: Only {len(available_vars)} of 3 predictors available for Model 2.")

    if not results:
        print("  WARNING: No models were successfully fit.")
        return pd.DataFrame()

    comparison_df = pd.DataFrame(results)

    # Save
    out_path = config.OUT_SHAM / "sham_descriptive_models.csv"
    comparison_df.to_csv(out_path, index=False)
    print(f"  Saved model comparison to {out_path}")
    return comparison_df


def test_anchoring_effects(sham_df: pd.DataFrame) -> pd.DataFrame:
    """Test cognitive anchoring effects: Cognitive_Anchoring ~ sham_visual_cue + blinding_quality."""

    if sham_df.empty:
        print("  WARNING: Empty sham dataset. Skipping anchoring tests.")
        return pd.DataFrame()

    if "Cognitive_Anchoring" not in sham_df.columns:
        print("  WARNING: Cognitive_Anchoring not available. Skipping anchoring tests.")
        return pd.DataFrame()

    # Determine available predictors
    anchor_preds = ["sham_visual_cue", "blinding_quality"]
    available_preds = [p for p in anchor_preds if p in sham_df.columns]

    if not available_preds:
        print("  WARNING: No anchoring predictors available. Skipping.")
        return pd.DataFrame()

    # Drop missing
    keep_cols = ["Cognitive_Anchoring", "pmid"] + available_preds
    anchor_df = sham_df[keep_cols].dropna()
    n = len(anchor_df)

    if n < 15:
        print(f"  WARNING: Only {n} observations for anchoring analysis. "
              f"Need >=15. Skipping.")
        return pd.DataFrame()

    try:
        import statsmodels.formula.api as smf
    except ImportError:
        print("  WARNING: statsmodels not available. Skipping anchoring tests.")
        return pd.DataFrame()

    results = []

    # Try mixed effects if enough clusters, otherwise OLS
    n_clusters = anchor_df["pmid"].nunique()

    if n_clusters >= 5 and n >= 20:
        # Attempt mixed-effects: Cognitive_Anchoring ~ predictors + (1|pmid)
        formula = "Cognitive_Anchoring ~ " + " + ".join(available_preds)
        try:
            import statsmodels.api as sm
            md = smf.mixedlm(formula, anchor_df, groups=anchor_df["pmid"])
            mdf = md.fit(reml=True, method="lbfgs")
            for pred in available_preds:
                if pred in mdf.params.index:
                    results.append({
                        "predictor": pred,
                        "coefficient": mdf.params[pred],
                        "std_error": mdf.bse[pred] if pred in mdf.bse.index else np.nan,
                        "z_value": mdf.tvalues[pred] if pred in mdf.tvalues.index else np.nan,
                        "p_value": mdf.pvalues[pred] if pred in mdf.pvalues.index else np.nan,
                        "model_type": "mixed_effects",
                        "n": n,
                        "n_clusters": n_clusters,
                    })
            print(f"  Fit mixed-effects anchoring model (n={n}, clusters={n_clusters})")
        except Exception as e:
            print(f"  WARNING: Mixed-effects failed ({e}). Falling back to OLS.")
            n_clusters = 0  # trigger OLS fallback

    if n_clusters < 5 or not results:
        # OLS fallback
        formula = "Cognitive_Anchoring ~ " + " + ".join(available_preds)
        try:
            m = smf.ols(formula, data=anchor_df).fit()
            for pred in available_preds:
                if pred in m.params.index:
                    results.append({
                        "predictor": pred,
                        "coefficient": m.params[pred],
                        "std_error": m.bse[pred],
                        "z_value": m.tvalues[pred],
                        "p_value": m.pvalues[pred],
                        "model_type": "ols",
                        "n": n,
                        "n_clusters": anchor_df["pmid"].nunique(),
                    })
            print(f"  Fit OLS anchoring model (n={n})")
        except Exception as e:
            print(f"  WARNING: OLS anchoring model failed: {e}")

    if not results:
        return pd.DataFrame()

    results_df = pd.DataFrame(results)

    # Save
    out_path = config.OUT_SHAM / "sham_anchoring_tests.csv"
    results_df.to_csv(out_path, index=False)
    print(f"  Saved anchoring tests to {out_path}")
    return results_df


def plot_sham_perturbation_space(sham_df: pd.DataFrame) -> None:
    """Scatter plot of PC1 vs PC2 for sham arms, colored by sham_penetration_level."""

    if sham_df.empty:
        print("  WARNING: Empty sham dataset. Skipping plot.")
        return

    if "PC1" not in sham_df.columns or "PC2" not in sham_df.columns:
        print("  WARNING: PC1/PC2 not available. Skipping perturbation space plot.")
        return

    plot_df = sham_df.dropna(subset=["PC1", "PC2"]).copy()
    if len(plot_df) < 3:
        print("  WARNING: Fewer than 3 data points for plot. Skipping.")
        return

    fig, ax = plt.subplots(figsize=(8, 6))

    # Color by sham_penetration_level if available
    if "sham_penetration_level" in plot_df.columns:
        plot_df["sham_penetration_level"] = plot_df["sham_penetration_level"].fillna(-1)
        categories = plot_df["sham_penetration_level"].unique()
        colors = {0: "#4C72B0", 1: "#DD8452", -1: "#CCCCCC"}
        labels = {0: "Non-penetrating", 1: "Penetrating", -1: "Unknown"}

        for cat in sorted(categories):
            mask = plot_df["sham_penetration_level"] == cat
            ax.scatter(
                plot_df.loc[mask, "PC1"],
                plot_df.loc[mask, "PC2"],
                c=colors.get(cat, "#999999"),
                label=labels.get(cat, f"Level {cat}"),
                alpha=0.7,
                edgecolors="white",
                linewidth=0.5,
                s=60,
            )
        ax.legend(title="Sham Penetration", loc="best")
    else:
        ax.scatter(
            plot_df["PC1"], plot_df["PC2"],
            c="#4C72B0", alpha=0.7, edgecolors="white", linewidth=0.5, s=60,
        )

    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title("Sham Arms in Perturbation Space")
    ax.axhline(0, color="gray", linewidth=0.5, linestyle="--")
    ax.axvline(0, color="gray", linewidth=0.5, linestyle="--")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    out_path = config.OUT_FIGURES / "sham_perturbation_space.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved plot to {out_path}")


def main():
    config.OUT_SHAM.mkdir(parents=True, exist_ok=True)
    config.OUT_FIGURES.mkdir(parents=True, exist_ok=True)

    print("Step 09: Sham Heterogeneity Analysis")
    print("=" * 60)

    # 1. Build dataset
    print("\n[1] Building sham dataset...")
    sham_df = build_sham_dataset()

    if sham_df.empty:
        print("\n  No sham data available. Exiting.")
        print("Done. Results in:", config.OUT_SHAM)
        return

    # 2. Descriptive statistics
    print("\n[2] Computing descriptive statistics...")
    desc_df = compute_descriptive_stats(sham_df)
    if not desc_df.empty:
        print(desc_df.to_string(index=False))

    # 3. Sequential models
    print("\n[3] Fitting sequential models...")
    model_df = fit_sequential_models(sham_df)
    if not model_df.empty:
        print(model_df[["model", "n", "r_squared", "aic", "bic"]].to_string(index=False))

    # 4. Anchoring effects
    print("\n[4] Testing anchoring effects...")
    anchor_df = test_anchoring_effects(sham_df)
    if not anchor_df.empty:
        print(anchor_df.to_string(index=False))

    # 5. Perturbation space plot
    print("\n[5] Plotting sham perturbation space...")
    plot_sham_perturbation_space(sham_df)

    print("\n" + "=" * 60)
    print("Done. Results in:", config.OUT_SHAM)


if __name__ == "__main__":
    main()
