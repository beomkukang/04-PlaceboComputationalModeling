"""Step 07: Component Meta-Regression (analysis_plan.md Section 6.6)

Mixed-effects models testing whether afferent input, deqi, and
cognitive-perceptual components predict neural gradients and
clinical responsiveness.

Outcomes:
- Clinical responsiveness
- Neural gradient scores
- Network summary scores
- Deqi/interoceptive scores

Models:
    Responsiveness ~ Afferent + Deqi + Cognitive + Neural_Gradient_1 +
                     Disease_Domain + (1 | study_id)

    Neural_Gradient_1 ~ Afferent + Cognitive + Deqi +
                        Analysis_Family + Population_Type + (1 | study_id)

    Deqi ~ Afferent * Cognitive + Population_Type + (1 | study_id)

Inputs:
    data_analysis/outputs/gradients/neural_gradient_scores.csv (step 06)
    data_analysis/outputs/behavioral/domain_responsiveness.csv (step 03)
    data_processing/v1/perturbation_space/arm_components.csv
    data_processing/v1/meta_regression/study_predictors.csv

Outputs:
    data_analysis/outputs/models/component_meta_regression_results.csv
    data_analysis/outputs/models/model_diagnostics.md
"""

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


def build_analysis_dataset() -> pd.DataFrame:
    """Merge gradient scores, responsiveness, and perturbation variables."""

    # --- Load perturbation PCA coordinates ---
    perturbation_path = config.OUT_PERTURBATION / "perturbation_pca_coordinates.csv"
    if not perturbation_path.exists():
        print(f"  WARNING: Perturbation coordinates not found: {perturbation_path}")
        return pd.DataFrame()

    pert = pd.read_csv(perturbation_path)
    print(f"  Loaded perturbation coordinates: {pert.shape[0]} rows")

    # Aggregate perturbation indices to study level (mean per pmid)
    pert_cols = ["Afferent_Input_Index", "Cognitive_Anchoring"]
    available_pert_cols = [c for c in pert_cols if c in pert.columns]
    if not available_pert_cols:
        print("  WARNING: No perturbation index columns found.")
        return pd.DataFrame()

    pert_study = pert.groupby("pmid")[available_pert_cols].mean().reset_index()

    # --- Load domain responsiveness ---
    resp_path = config.OUT_BEHAVIORAL / "domain_responsiveness.csv"
    if not resp_path.exists():
        print(f"  WARNING: Domain responsiveness not found: {resp_path}")
        return pd.DataFrame()

    resp = pd.read_csv(resp_path)
    print(f"  Loaded domain responsiveness: {resp.shape[0]} rows")

    # --- Merge perturbation with responsiveness on pmid ---
    df = resp.merge(pert_study, on="pmid", how="inner")
    print(f"  Merged dataset (perturbation x responsiveness): {df.shape[0]} rows")

    # --- Optionally load deqi data ---
    deqi_path = config.DEQI_SUMMARY
    if deqi_path.exists():
        deqi = pd.read_csv(deqi_path)
        # Parse numeric values from the value column (e.g., "3.6±2.1" -> 3.6)
        deqi["deqi_numeric"] = deqi["value"].apply(_parse_numeric_value)
        # Compute mean deqi per study
        deqi_study = (
            deqi.dropna(subset=["deqi_numeric"])
            .groupby("pmid")["deqi_numeric"]
            .mean()
            .reset_index()
            .rename(columns={"deqi_numeric": "mean_deqi"})
        )
        df = df.merge(deqi_study, on="pmid", how="left")
        print(f"  Merged deqi data: {deqi_study.shape[0]} studies with deqi")
    else:
        print(f"  INFO: Deqi summary not found: {deqi_path}")
        df["mean_deqi"] = np.nan

    # --- Optionally load neural gradient scores ---
    gradient_path = config.OUT_GRADIENTS / "neural_gradient_scores.csv"
    if gradient_path.exists():
        gradients = pd.read_csv(gradient_path)
        # Merge at study level
        grad_cols = [c for c in gradients.columns if c.startswith("Gradient_")]
        if grad_cols:
            grad_study = gradients.groupby("pmid")[grad_cols].mean().reset_index()
            df = df.merge(grad_study, on="pmid", how="left")
            print(f"  Merged gradient scores: {grad_study.shape[0]} studies")
    else:
        print(f"  INFO: Neural gradient scores not found (expected): {gradient_path}")

    return df


def _parse_numeric_value(val) -> float:
    """Extract leading numeric value from strings like '3.6±2.1' or '3.6 (2.1)'."""
    if pd.isna(val):
        return np.nan
    val_str = str(val).strip()
    # Try direct float conversion first
    try:
        return float(val_str)
    except ValueError:
        pass
    # Match leading number (possibly negative, with decimal)
    match = re.match(r"^(-?\d+\.?\d*)", val_str)
    if match:
        return float(match.group(1))
    return np.nan


def fit_responsiveness_model(df: pd.DataFrame) -> dict:
    """Responsiveness ~ component predictors + (1|study_id)."""
    import statsmodels.api as sm
    from statsmodels.regression.mixed_linear_model import MixedLM

    model_name = "responsiveness_mixed"
    required_cols = ["R_within", "Afferent_Input_Index", "Cognitive_Anchoring",
                     "outcome_domain", "pmid"]
    if not _check_columns(df, required_cols):
        print("  WARNING: Insufficient columns for responsiveness model.")
        return {}

    # Drop rows with missing outcome
    sub = df.dropna(subset=["R_within", "Afferent_Input_Index", "Cognitive_Anchoring"]).copy()
    if len(sub) < 10:
        print(f"  WARNING: Only {len(sub)} observations for responsiveness model, skipping.")
        return {}

    # Create dummy variables for outcome_domain
    sub = pd.get_dummies(sub, columns=["outcome_domain"], drop_first=True, dtype=float)
    domain_dummies = [c for c in sub.columns if c.startswith("outcome_domain_")]

    # Build design matrix
    predictor_cols = ["Afferent_Input_Index", "Cognitive_Anchoring"] + domain_dummies
    exog = sub[predictor_cols].copy()
    exog.insert(0, "Intercept", 1.0)
    endog = sub["R_within"]
    groups = sub["pmid"]

    n_obs = len(sub)
    n_groups = groups.nunique()
    converged = False

    # Try MixedLM first
    try:
        model = MixedLM(endog, exog, groups=groups)
        result = model.fit(reml=True, maxiter=200)
        converged = result.converged
        coefficients = result.fe_params.to_dict()
        p_values = result.pvalues.to_dict()
        aic = result.aic
        bic = result.bic
        model_name = "responsiveness_mixed_lm"
        print(f"  MixedLM fit: converged={converged}, AIC={aic:.2f}")
    except Exception as e:
        print(f"  MixedLM failed ({e}), falling back to OLS with clustered SEs.")
        model = sm.OLS(endog, exog)
        result = model.fit(cov_type="cluster", cov_kwds={"groups": groups})
        converged = True
        coefficients = result.params.to_dict()
        p_values = result.pvalues.to_dict()
        aic = result.aic
        bic = result.bic
        model_name = "responsiveness_ols_clustered"

    return {
        "model_name": model_name,
        "coefficients": coefficients,
        "p_values": p_values,
        "n_obs": n_obs,
        "n_groups": n_groups,
        "aic": aic,
        "bic": bic,
        "converged": converged,
    }


def fit_neural_gradient_model(df: pd.DataFrame) -> dict:
    """Neural_Gradient ~ component predictors + (1|study_id)."""
    import statsmodels.api as sm
    from statsmodels.regression.mixed_linear_model import MixedLM

    # Check if gradient scores are available
    if "Gradient_1" not in df.columns:
        print("  INFO: Gradient_1 column not available, skipping neural gradient model.")
        return {}

    required_cols = ["Gradient_1", "Afferent_Input_Index", "Cognitive_Anchoring", "pmid"]
    if not _check_columns(df, required_cols):
        print("  WARNING: Insufficient columns for neural gradient model.")
        return {}

    sub = df.dropna(subset=["Gradient_1", "Afferent_Input_Index", "Cognitive_Anchoring"]).copy()
    if len(sub) < 10:
        print(f"  WARNING: Only {len(sub)} observations for gradient model, skipping.")
        return {}

    predictor_cols = ["Afferent_Input_Index", "Cognitive_Anchoring"]
    exog = sub[predictor_cols].copy()
    exog.insert(0, "Intercept", 1.0)
    endog = sub["Gradient_1"]
    groups = sub["pmid"]

    n_obs = len(sub)
    n_groups = groups.nunique()
    converged = False
    model_name = "neural_gradient_mixed_lm"

    try:
        model = MixedLM(endog, exog, groups=groups)
        result = model.fit(reml=True, maxiter=200)
        converged = result.converged
        coefficients = result.fe_params.to_dict()
        p_values = result.pvalues.to_dict()
        aic = result.aic
        bic = result.bic
        print(f"  Gradient MixedLM fit: converged={converged}, AIC={aic:.2f}")
    except Exception as e:
        print(f"  Gradient MixedLM failed ({e}), falling back to OLS.")
        model = sm.OLS(endog, exog)
        result = model.fit(cov_type="cluster", cov_kwds={"groups": groups})
        converged = True
        coefficients = result.params.to_dict()
        p_values = result.pvalues.to_dict()
        aic = result.aic
        bic = result.bic
        model_name = "neural_gradient_ols_clustered"

    return {
        "model_name": model_name,
        "coefficients": coefficients,
        "p_values": p_values,
        "n_obs": n_obs,
        "n_groups": n_groups,
        "aic": aic,
        "bic": bic,
        "converged": converged,
    }


def fit_deqi_model(df: pd.DataFrame) -> dict:
    """Deqi ~ Afferent * Cognitive + (1|study_id)."""
    import statsmodels.api as sm
    from statsmodels.regression.mixed_linear_model import MixedLM

    # Build deqi dataset from raw deqi_summary
    deqi_path = config.DEQI_SUMMARY
    if not deqi_path.exists():
        print("  WARNING: Deqi summary not found, skipping deqi model.")
        return {}

    deqi = pd.read_csv(deqi_path)
    deqi["deqi_value"] = deqi["value"].apply(_parse_numeric_value)
    deqi = deqi.dropna(subset=["deqi_value"])

    if deqi.empty:
        print("  WARNING: No numeric deqi values found, skipping deqi model.")
        return {}

    # Aggregate to arm level (mean across items/subscales)
    deqi_arm = deqi.groupby(["pmid", "arm_id"])["deqi_value"].mean().reset_index()

    # Load perturbation coordinates for arm-level merge
    pert_path = config.OUT_PERTURBATION / "perturbation_pca_coordinates.csv"
    if not pert_path.exists():
        print("  WARNING: Perturbation coordinates not found for deqi model.")
        return {}

    pert = pd.read_csv(pert_path)
    pert_cols_needed = ["arm_id", "pmid", "Afferent_Input_Index", "Cognitive_Anchoring"]
    available = [c for c in pert_cols_needed if c in pert.columns]
    if len(available) < len(pert_cols_needed):
        # Fall back to pmid-level merge
        pert_study = pert.groupby("pmid")[["Afferent_Input_Index", "Cognitive_Anchoring"]].mean().reset_index()
        deqi_merged = deqi_arm.merge(pert_study, on="pmid", how="inner")
    else:
        deqi_merged = deqi_arm.merge(
            pert[pert_cols_needed], on=["pmid", "arm_id"], how="inner"
        )

    if len(deqi_merged) < 10:
        print(f"  WARNING: Only {len(deqi_merged)} observations for deqi model, skipping.")
        return {}

    # Build design matrix with interaction term
    sub = deqi_merged.dropna(
        subset=["deqi_value", "Afferent_Input_Index", "Cognitive_Anchoring"]
    ).copy()
    sub["Afferent_x_Cognitive"] = sub["Afferent_Input_Index"] * sub["Cognitive_Anchoring"]

    predictor_cols = ["Afferent_Input_Index", "Cognitive_Anchoring", "Afferent_x_Cognitive"]
    exog = sub[predictor_cols].copy()
    exog.insert(0, "Intercept", 1.0)
    endog = sub["deqi_value"]
    groups = sub["pmid"]

    n_obs = len(sub)
    n_groups = groups.nunique()
    converged = False
    model_name = "deqi_mixed_lm"

    try:
        model = MixedLM(endog, exog, groups=groups)
        result = model.fit(reml=True, maxiter=200)
        converged = result.converged
        coefficients = result.fe_params.to_dict()
        p_values = result.pvalues.to_dict()
        aic = result.aic
        bic = result.bic
        print(f"  Deqi MixedLM fit: converged={converged}, AIC={aic:.2f}")
    except Exception as e:
        print(f"  Deqi MixedLM failed ({e}), falling back to OLS.")
        model = sm.OLS(endog, exog)
        result = model.fit(cov_type="cluster", cov_kwds={"groups": groups})
        converged = True
        coefficients = result.params.to_dict()
        p_values = result.pvalues.to_dict()
        aic = result.aic
        bic = result.bic
        model_name = "deqi_ols_clustered"

    return {
        "model_name": model_name,
        "coefficients": coefficients,
        "p_values": p_values,
        "n_obs": n_obs,
        "n_groups": n_groups,
        "aic": aic,
        "bic": bic,
        "converged": converged,
    }


def _check_columns(df: pd.DataFrame, required: list[str]) -> bool:
    """Check that all required columns exist in the dataframe."""
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"    Missing columns: {missing}")
        return False
    return True


def write_diagnostics(results: list[dict]):
    """Write model diagnostics markdown report."""
    out_path = config.OUT_MODELS / "model_diagnostics.md"

    lines = [
        "# Component Meta-Regression: Model Diagnostics",
        "",
        "## Summary",
        "",
    ]

    for res in results:
        if not res:
            continue
        model_name = res.get("model_name", "unknown")
        lines.append(f"### {model_name}")
        lines.append("")
        lines.append(f"- **N observations**: {res.get('n_obs', 'N/A')}")
        lines.append(f"- **N groups (studies)**: {res.get('n_groups', 'N/A')}")
        lines.append(f"- **AIC**: {res.get('aic', 'N/A')}")
        lines.append(f"- **BIC**: {res.get('bic', 'N/A')}")
        lines.append(f"- **Converged**: {res.get('converged', 'N/A')}")
        lines.append("")

        # Coefficients table
        coefficients = res.get("coefficients", {})
        p_values = res.get("p_values", {})
        if coefficients:
            lines.append("| Predictor | Coefficient | p-value | Significance |")
            lines.append("|-----------|-------------|---------|--------------|")
            for pred, coef in coefficients.items():
                p = p_values.get(pred, np.nan)
                sig = ""
                if not np.isnan(p):
                    if p < 0.001:
                        sig = "***"
                    elif p < 0.01:
                        sig = "**"
                    elif p < 0.05:
                        sig = "*"
                    p_str = f"{p:.4f}"
                else:
                    p_str = "N/A"
                lines.append(f"| {pred} | {coef:.4f} | {p_str} | {sig} |")
            lines.append("")

    # Notes
    lines.append("## Notes")
    lines.append("")
    lines.append("- Models use random intercepts per study (pmid) via MixedLM.")
    lines.append("- If MixedLM fails to converge, OLS with clustered standard errors is used.")
    lines.append("- Significance codes: *** p<0.001, ** p<0.01, * p<0.05")
    lines.append("")

    out_path.write_text("\n".join(lines))
    print(f"  Diagnostics written to: {out_path}")


def main():
    config.OUT_MODELS.mkdir(parents=True, exist_ok=True)

    print("Step 07: Component Meta-Regression")
    print("=" * 60)

    # Build merged dataset
    print("\n[1/5] Building analysis dataset...")
    df = build_analysis_dataset()

    if df.empty:
        print("\n  WARNING: Analysis dataset is empty. Cannot fit models.")
        print("  Ensure upstream steps have been run (steps 03, 04, 06).")
        print("Done. Results in:", config.OUT_MODELS)
        return

    print(f"\n  Analysis dataset: {df.shape[0]} rows, {df.shape[1]} columns")

    # Fit models
    results = []

    print("\n[2/5] Fitting responsiveness model...")
    resp_result = fit_responsiveness_model(df)
    if resp_result:
        results.append(resp_result)

    print("\n[3/5] Fitting neural gradient model...")
    gradient_result = fit_neural_gradient_model(df)
    if gradient_result:
        results.append(gradient_result)

    print("\n[4/5] Fitting deqi model...")
    deqi_result = fit_deqi_model(df)
    if deqi_result:
        results.append(deqi_result)

    # Save results
    print("\n[5/5] Saving results...")
    if results:
        # Flatten coefficients and p_values for CSV output
        rows = []
        for res in results:
            row = {
                "model_name": res["model_name"],
                "n_obs": res["n_obs"],
                "n_groups": res["n_groups"],
                "aic": res["aic"],
                "bic": res["bic"],
                "converged": res["converged"],
            }
            # Add coefficients as coef_<name> columns
            for k, v in res.get("coefficients", {}).items():
                row[f"coef_{k}"] = v
            # Add p-values as pval_<name> columns
            for k, v in res.get("p_values", {}).items():
                row[f"pval_{k}"] = v
            rows.append(row)

        results_df = pd.DataFrame(rows)
        out_csv = config.OUT_MODELS / "component_meta_regression_results.csv"
        results_df.to_csv(out_csv, index=False)
        print(f"  Results saved to: {out_csv}")

        # Write diagnostics
        write_diagnostics(results)
    else:
        print("  No models were successfully fit. No output generated.")

    print("\nDone. Results in:", config.OUT_MODELS)


if __name__ == "__main__":
    main()
