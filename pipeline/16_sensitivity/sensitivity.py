"""Step 11: Sensitivity Analyses (analysis_plan.md Section 7)

Robustness checks across multiple dimensions:

7.1 Dependence sensitivity:
    - Leave-one-study-out
    - Leave-one-disease-domain-out

7.2 Imaging-family sensitivity:
    - Refit by method_category (GLM, ALFF, ReHo, FC, CBF, etc.)

7.3 Population sensitivity:
    - Pain-related, Non-pain clinical, Healthy

7.4 Cognitive-anchoring missingness sensitivity:
    - Full dataset
    - Deqi-reported subset
    - Clinical populations only

Primary model under test (from step 07):
    R_within ~ Afferent_Input_Index + Cognitive_Anchoring + C(outcome_domain)
    with MixedLM grouping on pmid

Inputs:
    outputs/behavioral/domain_responsiveness.csv
    outputs/perturbation/perturbation_pca_coordinates.csv
    data_processing/v1/contrast_classifications.csv
    data_processing/v1/perturbation_space/arm_components.csv
    data_processing/v1/sensory/deqi_summary_by_arm.csv

Outputs:
    data_analysis/outputs/tables/sensitivity_leave_one_study.csv
    data_analysis/outputs/tables/sensitivity_leave_one_domain.csv
    data_analysis/outputs/tables/sensitivity_imaging_family.csv
    data_analysis/outputs/tables/sensitivity_population.csv
    data_analysis/outputs/tables/sensitivity_missingness.csv
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


# ---------------------------------------------------------------------------
# Helper: fit primary model
# ---------------------------------------------------------------------------

def _fit_primary_model(df: pd.DataFrame) -> dict | None:
    """Fit the responsiveness MixedLM; fall back to OLS if MixedLM fails.

    Returns dict with coefficients and p-values for Afferent_Input_Index
    and Cognitive_Anchoring, or None if fitting is not possible.
    """
    if df is None or len(df) < 10:
        return None

    # Ensure required columns present
    required = ["R_within", "Afferent_Input_Index", "Cognitive_Anchoring",
                "outcome_domain", "pmid"]
    if not all(c in df.columns for c in required):
        return None

    # Drop rows with missing values in model variables
    model_df = df[required].dropna()
    if len(model_df) < 10:
        return None

    formula = "R_within ~ Afferent_Input_Index + Cognitive_Anchoring + C(outcome_domain)"

    # Try MixedLM first
    try:
        model = smf.mixedlm(formula, data=model_df, groups=model_df["pmid"])
        result = model.fit(reml=True, method="lbfgs", maxiter=200)
        return {
            "afferent_coef": result.params.get("Afferent_Input_Index", np.nan),
            "afferent_p": result.pvalues.get("Afferent_Input_Index", np.nan),
            "cognitive_coef": result.params.get("Cognitive_Anchoring", np.nan),
            "cognitive_p": result.pvalues.get("Cognitive_Anchoring", np.nan),
            "n": len(model_df),
            "method": "MixedLM",
        }
    except Exception:
        pass

    # Fallback to OLS
    try:
        result = smf.ols(formula, data=model_df).fit()
        return {
            "afferent_coef": result.params.get("Afferent_Input_Index", np.nan),
            "afferent_p": result.pvalues.get("Afferent_Input_Index", np.nan),
            "cognitive_coef": result.params.get("Cognitive_Anchoring", np.nan),
            "cognitive_p": result.pvalues.get("Cognitive_Anchoring", np.nan),
            "n": len(model_df),
            "method": "OLS",
        }
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Helper: build analysis dataset
# ---------------------------------------------------------------------------

def _build_analysis_dataset() -> pd.DataFrame:
    """Merge domain_responsiveness + perturbation PCA + arm_components."""

    # Load domain responsiveness
    resp_path = config.OUT_BEHAVIORAL / "domain_responsiveness.csv"
    if not resp_path.exists():
        print(f"  WARNING: Not found: {resp_path}")
        return pd.DataFrame()
    resp = pd.read_csv(resp_path)
    print(f"  Loaded domain responsiveness: {resp.shape[0]} rows")

    # Load perturbation PCA coordinates
    pert_path = config.OUT_PERTURBATION / "perturbation_pca_coordinates.csv"
    if not pert_path.exists():
        print(f"  WARNING: Not found: {pert_path}")
        return pd.DataFrame()
    pert = pd.read_csv(pert_path)
    print(f"  Loaded perturbation PCA coordinates: {pert.shape[0]} rows")

    # Aggregate perturbation to study level
    pert_cols = ["Afferent_Input_Index", "Cognitive_Anchoring"]
    available = [c for c in pert_cols if c in pert.columns]
    if not available:
        print("  WARNING: No perturbation index columns found.")
        return pd.DataFrame()
    pert_study = pert.groupby("pmid")[available].mean().reset_index()

    # Merge responsiveness with perturbation
    df = resp.merge(pert_study, on="pmid", how="inner")
    print(f"  After merge with perturbation: {df.shape[0]} rows")

    # Load arm_components for disease_condition and acupuncture_modality
    arm_path = config.ARM_COMPONENTS
    if arm_path.exists():
        arms = pd.read_csv(arm_path)
        # Get study-level disease_condition (take first per pmid)
        arm_cols = ["pmid"]
        if "disease_condition" in arms.columns:
            arm_cols.append("disease_condition")
        if "acupuncture_modality" in arms.columns:
            arm_cols.append("acupuncture_modality")
        if len(arm_cols) > 1:
            arm_study = arms[arm_cols].drop_duplicates(subset=["pmid"])
            df = df.merge(arm_study, on="pmid", how="left")
            print(f"  After merge with arm_components: {df.shape[0]} rows")
    else:
        print(f"  WARNING: Not found: {arm_path}")

    return df


# ---------------------------------------------------------------------------
# Sensitivity 1: Leave-one-out
# ---------------------------------------------------------------------------

def leave_one_out_sensitivity(df: pd.DataFrame, model_func, group_col: str) -> pd.DataFrame:
    """Generic leave-one-out: refit model dropping each group."""
    results = []
    unique_groups = df[group_col].dropna().unique()

    for group_val in unique_groups:
        subset = df[df[group_col] != group_val].copy()
        fit = model_func(subset)
        if fit is not None:
            results.append({
                "dropped": group_val,
                "afferent_coef": fit["afferent_coef"],
                "afferent_p": fit["afferent_p"],
                "cognitive_coef": fit["cognitive_coef"],
                "cognitive_p": fit["cognitive_p"],
                "n": fit["n"],
            })

    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# Sensitivity 2: Imaging family
# ---------------------------------------------------------------------------

def imaging_family_sensitivity(df: pd.DataFrame, model_func) -> pd.DataFrame:
    """Refit key models separately for each imaging family (method_category)."""
    # Load contrast classifications for method_category
    cc_path = config.CONTRAST_CLASSIFICATIONS
    if not cc_path.exists():
        print(f"  WARNING: Not found: {cc_path}")
        return pd.DataFrame()

    cc = pd.read_csv(cc_path)
    if "method_category" not in cc.columns:
        print("  WARNING: method_category column not in contrast_classifications.")
        return pd.DataFrame()

    # Get study-level method_category (a study may have multiple; take first)
    cc_study = cc[["pmid", "method_category"]].drop_duplicates(subset=["pmid"])
    df_merged = df.merge(cc_study, on="pmid", how="left")

    results = []
    for cat in df_merged["method_category"].dropna().unique():
        subset = df_merged[df_merged["method_category"] == cat].copy()
        if len(subset) < 10:
            continue
        fit = model_func(subset)
        if fit is not None:
            results.append({
                "method_category": cat,
                "afferent_coef": fit["afferent_coef"],
                "afferent_p": fit["afferent_p"],
                "cognitive_coef": fit["cognitive_coef"],
                "cognitive_p": fit["cognitive_p"],
                "n": fit["n"],
                "method": fit["method"],
            })

    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# Sensitivity 3: Population
# ---------------------------------------------------------------------------

def population_sensitivity(df: pd.DataFrame, model_func) -> pd.DataFrame:
    """Refit for pain-related, non-pain clinical, and healthy subsets."""
    if "disease_condition" not in df.columns:
        print("  WARNING: disease_condition not available for population sensitivity.")
        return pd.DataFrame()

    # Classify into pain-related vs non-pain vs healthy
    disease = df["disease_condition"].fillna("").str.lower()

    pain_keywords = ["pain", "migraine", "headache", "fibromyalgia",
                     "arthritis", "neuropath", "lbp", "back"]
    healthy_keywords = ["healthy", "normal", "control"]

    def classify(val):
        for kw in pain_keywords:
            if kw in val:
                return "pain_related"
        for kw in healthy_keywords:
            if kw in val:
                return "healthy"
        return "non_pain_clinical"

    df = df.copy()
    df["pop_category"] = disease.apply(classify)

    results = []
    for cat in ["pain_related", "non_pain_clinical", "healthy"]:
        subset = df[df["pop_category"] == cat].copy()
        if len(subset) < 10:
            continue
        fit = model_func(subset)
        if fit is not None:
            results.append({
                "population": cat,
                "afferent_coef": fit["afferent_coef"],
                "afferent_p": fit["afferent_p"],
                "cognitive_coef": fit["cognitive_coef"],
                "cognitive_p": fit["cognitive_p"],
                "n": fit["n"],
                "method": fit["method"],
            })

    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# Sensitivity 4: Missingness
# ---------------------------------------------------------------------------

def missingness_sensitivity(df: pd.DataFrame, model_func) -> pd.DataFrame:
    """Test model under different data availability assumptions."""
    results = []

    # (a) Full dataset as-is
    fit_full = model_func(df)
    if fit_full is not None:
        results.append({
            "subset": "full_dataset",
            "afferent_coef": fit_full["afferent_coef"],
            "afferent_p": fit_full["afferent_p"],
            "cognitive_coef": fit_full["cognitive_coef"],
            "cognitive_p": fit_full["cognitive_p"],
            "n": fit_full["n"],
            "method": fit_full["method"],
        })

    # (b) Restrict to studies with deqi reported
    deqi_path = config.DEQI_SUMMARY
    if deqi_path.exists():
        deqi = pd.read_csv(deqi_path)
        deqi_pmids = deqi["pmid"].unique() if "pmid" in deqi.columns else []
        if len(deqi_pmids) > 0:
            subset_deqi = df[df["pmid"].isin(deqi_pmids)].copy()
            fit_deqi = model_func(subset_deqi)
            if fit_deqi is not None:
                results.append({
                    "subset": "deqi_reported",
                    "afferent_coef": fit_deqi["afferent_coef"],
                    "afferent_p": fit_deqi["afferent_p"],
                    "cognitive_coef": fit_deqi["cognitive_coef"],
                    "cognitive_p": fit_deqi["cognitive_p"],
                    "n": fit_deqi["n"],
                    "method": fit_deqi["method"],
                })
    else:
        print(f"  WARNING: Deqi summary not found: {deqi_path}")

    # (c) Restrict to clinical populations only (exclude healthy)
    if "disease_condition" in df.columns:
        disease = df["disease_condition"].fillna("").str.lower()
        healthy_keywords = ["healthy", "normal", "control"]
        is_clinical = ~disease.apply(
            lambda x: any(kw in x for kw in healthy_keywords)
        )
        subset_clinical = df[is_clinical].copy()
        fit_clinical = model_func(subset_clinical)
        if fit_clinical is not None:
            results.append({
                "subset": "clinical_only",
                "afferent_coef": fit_clinical["afferent_coef"],
                "afferent_p": fit_clinical["afferent_p"],
                "cognitive_coef": fit_clinical["cognitive_coef"],
                "cognitive_p": fit_clinical["cognitive_p"],
                "n": fit_clinical["n"],
                "method": fit_clinical["method"],
            })

    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    config.OUT_TABLES.mkdir(parents=True, exist_ok=True)

    print("Step 11: Sensitivity Analyses")
    print("=" * 60)

    # Build the merged analysis dataset
    print("\nBuilding analysis dataset...")
    df = _build_analysis_dataset()
    if df.empty:
        print("ERROR: Could not build analysis dataset. Exiting.")
        return

    print(f"\nAnalysis dataset: {df.shape[0]} rows, {df['pmid'].nunique()} studies")

    # Define model function
    model_func = _fit_primary_model

    # --- Leave-one-study-out ---
    print("\n--- Leave-one-study-out sensitivity ---")
    loo_study = leave_one_out_sensitivity(df, model_func, group_col="pmid")
    if not loo_study.empty:
        loo_study.to_csv(config.OUT_TABLES / "sensitivity_leave_one_study.csv", index=False)
        print(f"  Saved: {len(loo_study)} iterations")
    else:
        print("  No results produced.")

    # --- Leave-one-domain-out ---
    print("\n--- Leave-one-domain-out sensitivity ---")
    if "disease_condition" in df.columns:
        loo_domain = leave_one_out_sensitivity(df, model_func, group_col="disease_condition")
    elif "outcome_domain" in df.columns:
        loo_domain = leave_one_out_sensitivity(df, model_func, group_col="outcome_domain")
    else:
        loo_domain = pd.DataFrame()

    if not loo_domain.empty:
        loo_domain.to_csv(config.OUT_TABLES / "sensitivity_leave_one_domain.csv", index=False)
        print(f"  Saved: {len(loo_domain)} iterations")
    else:
        print("  No results produced.")

    # --- Imaging family sensitivity ---
    print("\n--- Imaging family sensitivity ---")
    img_fam = imaging_family_sensitivity(df, model_func)
    if not img_fam.empty:
        img_fam.to_csv(config.OUT_TABLES / "sensitivity_imaging_family.csv", index=False)
        print(f"  Saved: {len(img_fam)} imaging families")
    else:
        print("  No results produced.")

    # --- Population sensitivity ---
    print("\n--- Population sensitivity ---")
    pop = population_sensitivity(df, model_func)
    if not pop.empty:
        pop.to_csv(config.OUT_TABLES / "sensitivity_population.csv", index=False)
        print(f"  Saved: {len(pop)} population subsets")
    else:
        print("  No results produced.")

    # --- Missingness sensitivity ---
    print("\n--- Missingness sensitivity ---")
    miss = missingness_sensitivity(df, model_func)
    if not miss.empty:
        miss.to_csv(config.OUT_TABLES / "sensitivity_missingness.csv", index=False)
        print(f"  Saved: {len(miss)} conditions")
    else:
        print("  No results produced.")

    # --- Summary ---
    print("\n" + "=" * 60)
    print("SUMMARY: Afferent_Input_Index significance across analyses")
    print("-" * 60)

    all_results = []
    for name, result_df in [("LOO-study", loo_study), ("LOO-domain", loo_domain),
                            ("Imaging", img_fam), ("Population", pop),
                            ("Missingness", miss)]:
        if result_df.empty:
            continue
        sig_count = (result_df["afferent_p"] < 0.05).sum()
        total = len(result_df)
        pct = 100 * sig_count / total if total > 0 else 0
        print(f"  {name:15s}: {sig_count}/{total} significant ({pct:.0f}%)")
        all_results.append({"analysis": name, "sig_count": sig_count,
                            "total": total, "pct_significant": pct})

    if all_results:
        overall_sig = sum(r["sig_count"] for r in all_results)
        overall_total = sum(r["total"] for r in all_results)
        overall_pct = 100 * overall_sig / overall_total if overall_total > 0 else 0
        print(f"\n  Overall: Afferent significant in {overall_sig}/{overall_total} "
              f"tests ({overall_pct:.0f}%)")
        if overall_pct >= 80:
            print("  --> Result appears ROBUST across sensitivity analyses.")
        elif overall_pct >= 50:
            print("  --> Result is PARTIALLY robust; some sensitivity to subsets.")
        else:
            print("  --> Result is NOT robust; findings are sensitive to analytic choices.")

    print("\nDone. Results in:", config.OUT_TABLES)


if __name__ == "__main__":
    main()
