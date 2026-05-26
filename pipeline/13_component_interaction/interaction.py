"""Step 08: Component Interaction Modeling (analysis_plan.md Section 6.7)

Core theoretical test: are neural and clinical responses better explained
by additive effects, interaction effects, deqi-bridging, substitution/
compensation, or overlap/shared neural implementation?

Model families:
    A. Additive:     R_within ~ Afferent + Cognitive + C(outcome_domain) + (1|pmid)
    B. Interaction:  R_within ~ Afferent * Cognitive + C(outcome_domain) + (1|pmid)
    C. Deqi-bridge:  Deqi ~ Afferent + Cognitive; R_within ~ Deqi + Afferent + Cognitive
    D. Substitution: Probe simple slopes of Cognitive at low/med/high Afferent
    E. Overlap:      Do Afferent and Cognitive predict overlapping network scores?

Model comparison via:
    AIC/BIC, adjusted R2, likelihood-ratio tests

Inputs:
    data_analysis/outputs/gradients/neural_gradient_scores.csv (step 06)
    data_analysis/outputs/behavioral/domain_responsiveness.csv (step 03)
    data_analysis/outputs/neural/network_summary_scores.csv (step 05)
    data_analysis/outputs/perturbation/perturbation_pca_coordinates.csv (step 04)
    data_processing/v1/sensory/deqi_summary_by_arm.csv

Outputs:
    data_analysis/outputs/models/component_interaction_model_comparison.csv
    data_analysis/outputs/models/component_interaction_coefficients.csv
    data_analysis/outputs/models/deqi_bridging_path_results.csv
    data_analysis/outputs/models/shared_network_overlap_results.csv
    data_analysis/outputs/figures/additive_vs_interaction_model_fit.png
    data_analysis/outputs/figures/afferent_cognitive_interaction_slopes.png
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


# ---------------------------------------------------------------------------
# Helper: Build merged dataset
# ---------------------------------------------------------------------------

def _build_dataset() -> pd.DataFrame:
    """Merge domain_responsiveness with perturbation PCA and deqi data.

    Returns a study-level DataFrame suitable for mixed models.
    """
    # Load responsiveness (primary outcome, ~113 rows)
    resp_path = config.OUT_BEHAVIORAL / "domain_responsiveness.csv"
    resp = pd.read_csv(resp_path)

    # Load perturbation PCA coordinates
    pca_path = config.OUT_PERTURBATION / "perturbation_pca_coordinates.csv"
    pca = pd.read_csv(pca_path)

    # Compute study-level mean of Afferent and Cognitive per pmid
    agg_cols = []
    for col in ["Afferent_Input_Index", "Cognitive_Anchoring"]:
        if col in pca.columns:
            agg_cols.append(col)
    # Also include PC columns if present
    pc_cols = [c for c in pca.columns if c.startswith("PC")]
    agg_cols.extend(pc_cols)

    if "pmid" in pca.columns and len(agg_cols) > 0:
        pca_study = pca.groupby("pmid")[agg_cols].mean().reset_index()
    else:
        pca_study = pca[["pmid"] + agg_cols].drop_duplicates() if "pmid" in pca.columns else pd.DataFrame()

    # Merge responsiveness with perturbation scores
    df = resp.merge(pca_study, on="pmid", how="inner")

    # Load and merge deqi where available
    deqi_path = config.DEQI_SUMMARY
    if deqi_path.exists():
        deqi = pd.read_csv(deqi_path)
        # Compute mean deqi per pmid (aggregate across arms/subscales)
        deqi_cols = [c for c in deqi.columns if c not in ["pmid", "arm_id", "arm_type", "arm_label"]]
        numeric_deqi = deqi.select_dtypes(include=[np.number]).columns.tolist()
        if "pmid" in deqi.columns and len(numeric_deqi) > 0:
            # Use a single summary score: mean of numeric deqi columns per pmid
            deqi["deqi_mean"] = deqi[numeric_deqi].mean(axis=1)
            deqi_study = deqi.groupby("pmid")["deqi_mean"].mean().reset_index()
            df = df.merge(deqi_study, on="pmid", how="left")
        else:
            df["deqi_mean"] = np.nan
    else:
        df["deqi_mean"] = np.nan

    # Ensure required columns exist
    for col in ["Afferent_Input_Index", "Cognitive_Anchoring"]:
        if col not in df.columns:
            df[col] = np.nan

    return df


# ---------------------------------------------------------------------------
# Model A: Additive
# ---------------------------------------------------------------------------

def fit_additive_model(df: pd.DataFrame) -> dict:
    """Model A: independent component contributions.

    R_within ~ Afferent_Input_Index + Cognitive_Anchoring + C(outcome_domain)
    with random intercept (1|pmid).
    """
    result = {
        "model_name": "additive",
        "coefficients": {},
        "p_values": {},
        "aic": np.nan,
        "bic": np.nan,
        "r2": np.nan,
        "n_obs": 0,
    }

    # Drop rows missing key variables
    cols_needed = ["R_within", "Afferent_Input_Index", "Cognitive_Anchoring", "outcome_domain", "pmid"]
    sub = df.dropna(subset=[c for c in cols_needed if c in df.columns])
    if len(sub) < 10:
        print("  [Additive] Insufficient data (n={})".format(len(sub)))
        return result

    result["n_obs"] = len(sub)
    formula = "R_within ~ Afferent_Input_Index + Cognitive_Anchoring + C(outcome_domain)"

    try:
        # Try MixedLM with random intercept for pmid
        model = smf.mixedlm(formula, data=sub, groups=sub["pmid"])
        fit = model.fit(reml=False, method="lbfgs", maxiter=200)
        result["coefficients"] = dict(zip(fit.params.index, fit.params.values))
        result["p_values"] = dict(zip(fit.pvalues.index, fit.pvalues.values))
        result["aic"] = fit.aic
        result["bic"] = fit.bic
        # Pseudo R2: 1 - (resid variance / total variance)
        y = sub["R_within"]
        resid_var = fit.resid.var() if hasattr(fit, "resid") else np.nan
        total_var = y.var()
        result["r2"] = 1 - resid_var / total_var if total_var > 0 else np.nan
        result["_fit"] = fit
    except Exception as e:
        print(f"  [Additive] MixedLM failed ({e}), falling back to OLS")
        try:
            ols_model = smf.ols(formula, data=sub).fit()
            result["coefficients"] = dict(zip(ols_model.params.index, ols_model.params.values))
            result["p_values"] = dict(zip(ols_model.pvalues.index, ols_model.pvalues.values))
            result["aic"] = ols_model.aic
            result["bic"] = ols_model.bic
            result["r2"] = ols_model.rsquared_adj
            result["_fit"] = ols_model
        except Exception as e2:
            print(f"  [Additive] OLS also failed: {e2}")

    return result


# ---------------------------------------------------------------------------
# Model B: Interaction
# ---------------------------------------------------------------------------

def fit_interaction_model(df: pd.DataFrame) -> dict:
    """Model B: Afferent * Cognitive interaction.

    R_within ~ Afferent_Input_Index * Cognitive_Anchoring + C(outcome_domain)
    with random intercept (1|pmid).
    """
    result = {
        "model_name": "interaction",
        "coefficients": {},
        "p_values": {},
        "aic": np.nan,
        "bic": np.nan,
        "r2": np.nan,
        "n_obs": 0,
    }

    cols_needed = ["R_within", "Afferent_Input_Index", "Cognitive_Anchoring", "outcome_domain", "pmid"]
    sub = df.dropna(subset=[c for c in cols_needed if c in df.columns])
    if len(sub) < 10:
        print("  [Interaction] Insufficient data (n={})".format(len(sub)))
        return result

    result["n_obs"] = len(sub)
    formula = "R_within ~ Afferent_Input_Index * Cognitive_Anchoring + C(outcome_domain)"

    try:
        model = smf.mixedlm(formula, data=sub, groups=sub["pmid"])
        fit = model.fit(reml=False, method="lbfgs", maxiter=200)
        result["coefficients"] = dict(zip(fit.params.index, fit.params.values))
        result["p_values"] = dict(zip(fit.pvalues.index, fit.pvalues.values))
        result["aic"] = fit.aic
        result["bic"] = fit.bic
        y = sub["R_within"]
        resid_var = fit.resid.var() if hasattr(fit, "resid") else np.nan
        total_var = y.var()
        result["r2"] = 1 - resid_var / total_var if total_var > 0 else np.nan
        result["_fit"] = fit
    except Exception as e:
        print(f"  [Interaction] MixedLM failed ({e}), falling back to OLS")
        try:
            ols_model = smf.ols(formula, data=sub).fit()
            result["coefficients"] = dict(zip(ols_model.params.index, ols_model.params.values))
            result["p_values"] = dict(zip(ols_model.pvalues.index, ols_model.pvalues.values))
            result["aic"] = ols_model.aic
            result["bic"] = ols_model.bic
            result["r2"] = ols_model.rsquared_adj
            result["_fit"] = ols_model
        except Exception as e2:
            print(f"  [Interaction] OLS also failed: {e2}")

    return result


# ---------------------------------------------------------------------------
# Model C: Deqi bridging
# ---------------------------------------------------------------------------

def fit_deqi_bridging_model(df: pd.DataFrame) -> dict:
    """Model C: deqi as integration point between afferent and cognitive.

    Step 1: deqi_mean ~ Afferent_Input_Index + Cognitive_Anchoring (OLS, limited data)
    Step 2: R_within ~ deqi_mean + Afferent_Input_Index + Cognitive_Anchoring + C(outcome_domain) (MixedLM)
    """
    result = {
        "model_name": "deqi_bridging",
        "step1": {"coefficients": {}, "p_values": {}, "r2": np.nan, "n_obs": 0},
        "step2": {"coefficients": {}, "p_values": {}, "aic": np.nan, "bic": np.nan, "r2": np.nan, "n_obs": 0},
    }

    # Step 1: deqi_mean ~ Afferent + Cognitive (OLS on subset with deqi data)
    cols_step1 = ["deqi_mean", "Afferent_Input_Index", "Cognitive_Anchoring"]
    sub1 = df.dropna(subset=cols_step1)
    if len(sub1) >= 5:
        result["step1"]["n_obs"] = len(sub1)
        try:
            formula1 = "deqi_mean ~ Afferent_Input_Index + Cognitive_Anchoring"
            ols1 = smf.ols(formula1, data=sub1).fit()
            result["step1"]["coefficients"] = dict(zip(ols1.params.index, ols1.params.values))
            result["step1"]["p_values"] = dict(zip(ols1.pvalues.index, ols1.pvalues.values))
            result["step1"]["r2"] = ols1.rsquared_adj
        except Exception as e:
            print(f"  [Deqi-bridge Step1] Failed: {e}")
    else:
        print(f"  [Deqi-bridge Step1] Insufficient deqi data (n={len(sub1)})")

    # Step 2: R_within ~ deqi_mean + Afferent + Cognitive + C(outcome_domain) (MixedLM)
    cols_step2 = ["R_within", "deqi_mean", "Afferent_Input_Index", "Cognitive_Anchoring", "outcome_domain", "pmid"]
    sub2 = df.dropna(subset=[c for c in cols_step2 if c in df.columns])
    if len(sub2) >= 10:
        result["step2"]["n_obs"] = len(sub2)
        formula2 = "R_within ~ deqi_mean + Afferent_Input_Index + Cognitive_Anchoring + C(outcome_domain)"
        try:
            model2 = smf.mixedlm(formula2, data=sub2, groups=sub2["pmid"])
            fit2 = model2.fit(reml=False, method="lbfgs", maxiter=200)
            result["step2"]["coefficients"] = dict(zip(fit2.params.index, fit2.params.values))
            result["step2"]["p_values"] = dict(zip(fit2.pvalues.index, fit2.pvalues.values))
            result["step2"]["aic"] = fit2.aic
            result["step2"]["bic"] = fit2.bic
            y = sub2["R_within"]
            resid_var = fit2.resid.var() if hasattr(fit2, "resid") else np.nan
            total_var = y.var()
            result["step2"]["r2"] = 1 - resid_var / total_var if total_var > 0 else np.nan
        except Exception as e:
            print(f"  [Deqi-bridge Step2] MixedLM failed ({e}), falling back to OLS")
            try:
                ols2 = smf.ols(formula2, data=sub2).fit()
                result["step2"]["coefficients"] = dict(zip(ols2.params.index, ols2.params.values))
                result["step2"]["p_values"] = dict(zip(ols2.pvalues.index, ols2.pvalues.values))
                result["step2"]["aic"] = ols2.aic
                result["step2"]["bic"] = ols2.bic
                result["step2"]["r2"] = ols2.rsquared_adj
            except Exception as e2:
                print(f"  [Deqi-bridge Step2] OLS also failed: {e2}")
    else:
        print(f"  [Deqi-bridge Step2] Insufficient data (n={len(sub2)})")

    return result


# ---------------------------------------------------------------------------
# Model D: Simple slopes
# ---------------------------------------------------------------------------

def probe_simple_slopes(df: pd.DataFrame) -> pd.DataFrame:
    """Model D: effect of Cognitive at low/medium/high Afferent.

    From the interaction model, compute effect of Cognitive_Anchoring at
    Afferent_Input_Index = mean - 1SD, mean, mean + 1SD.
    """
    cols_needed = ["R_within", "Afferent_Input_Index", "Cognitive_Anchoring", "outcome_domain", "pmid"]
    sub = df.dropna(subset=[c for c in cols_needed if c in df.columns])

    if len(sub) < 10:
        print("  [Simple slopes] Insufficient data")
        return pd.DataFrame(columns=["afferent_level", "cognitive_slope", "std_err", "p_value"])

    # Center variables for interpretability
    aff_mean = sub["Afferent_Input_Index"].mean()
    aff_sd = sub["Afferent_Input_Index"].std()

    if aff_sd == 0:
        print("  [Simple slopes] No variance in Afferent_Input_Index")
        return pd.DataFrame(columns=["afferent_level", "cognitive_slope", "std_err", "p_value"])

    # Fit interaction model using OLS (simpler for extracting slopes)
    formula = "R_within ~ Afferent_Input_Index * Cognitive_Anchoring + C(outcome_domain)"
    try:
        model = smf.ols(formula, data=sub).fit()
    except Exception as e:
        print(f"  [Simple slopes] Model fit failed: {e}")
        return pd.DataFrame(columns=["afferent_level", "cognitive_slope", "std_err", "p_value"])

    # Extract coefficients
    params = model.params
    cov = model.cov_params()

    # Identify interaction term name
    interaction_term = None
    for name in params.index:
        if "Afferent_Input_Index" in name and "Cognitive_Anchoring" in name and ":" in name:
            interaction_term = name
            break

    if interaction_term is None:
        print("  [Simple slopes] Could not find interaction term")
        return pd.DataFrame(columns=["afferent_level", "cognitive_slope", "std_err", "p_value"])

    cog_term = "Cognitive_Anchoring"
    b_cog = params.get(cog_term, 0)
    b_inter = params.get(interaction_term, 0)

    # Simple slope of Cognitive at each level of Afferent
    levels = {
        "low (mean-1SD)": aff_mean - aff_sd,
        "medium (mean)": aff_mean,
        "high (mean+1SD)": aff_mean + aff_sd,
    }

    rows = []
    for label, aff_val in levels.items():
        # slope = b_cog + b_inter * aff_val
        slope = b_cog + b_inter * aff_val

        # SE of slope: var(b_cog) + aff_val^2 * var(b_inter) + 2*aff_val*cov(b_cog, b_inter)
        if cog_term in cov.index and interaction_term in cov.index:
            var_slope = (
                cov.loc[cog_term, cog_term]
                + aff_val**2 * cov.loc[interaction_term, interaction_term]
                + 2 * aff_val * cov.loc[cog_term, interaction_term]
            )
            se = np.sqrt(max(var_slope, 0))
        else:
            se = np.nan

        # t-test
        if se > 0:
            t_val = slope / se
            df_resid = model.df_resid
            p_val = 2 * stats.t.sf(abs(t_val), df_resid)
        else:
            p_val = np.nan

        rows.append({
            "afferent_level": label,
            "afferent_value": aff_val,
            "cognitive_slope": slope,
            "std_err": se,
            "p_value": p_val,
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Model E: Network overlap
# ---------------------------------------------------------------------------

def test_network_overlap(df: pd.DataFrame) -> pd.DataFrame:
    """Model E: do Afferent and Cognitive predict overlapping networks?

    For each network in network_summary_scores, fit:
        Network_k ~ Afferent_Input_Index (OLS)
        Network_k ~ Cognitive_Anchoring (OLS)
    Flag networks where both predictors are significant or both have large effects.
    """
    # Load network summary scores (analysis-level, n=7-10)
    net_path = config.OUT_NEURAL / "network_summary_scores.csv"
    if not net_path.exists():
        print("  [Network overlap] network_summary_scores.csv not found")
        return pd.DataFrame(columns=["network", "afferent_coef", "afferent_p",
                                      "cognitive_coef", "cognitive_p", "overlap"])

    net_df = pd.read_csv(net_path)

    # Load perturbation scores at analysis level
    pca_path = config.OUT_PERTURBATION / "perturbation_pca_coordinates.csv"
    if not pca_path.exists():
        print("  [Network overlap] perturbation_pca_coordinates.csv not found")
        return pd.DataFrame(columns=["network", "afferent_coef", "afferent_p",
                                      "cognitive_coef", "cognitive_p", "overlap"])

    pca = pd.read_csv(pca_path)

    # Aggregate perturbation to analysis level if needed
    # network_summary_scores has 'analysis' column
    if "analysis" in net_df.columns and "analysis" not in pca.columns:
        # Cannot directly merge; try pmid-based aggregation
        # Use the df passed in (study-level) and aggregate to analysis if possible
        print("  [Network overlap] Cannot align perturbation with network data at analysis level")
        # Attempt: compute mean Afferent/Cognitive per analysis from study data
        # This is a heuristic given the data structure mismatch
        if "pmid" in pca.columns:
            pca_means = pca.groupby("pmid")[["Afferent_Input_Index", "Cognitive_Anchoring"]].mean().reset_index()
        else:
            return pd.DataFrame(columns=["network", "afferent_coef", "afferent_p",
                                          "cognitive_coef", "cognitive_p", "overlap"])
    elif "analysis" in net_df.columns and "analysis" in pca.columns:
        pca_means = pca.groupby("analysis")[["Afferent_Input_Index", "Cognitive_Anchoring"]].mean().reset_index()
    else:
        pca_means = pca[["Afferent_Input_Index", "Cognitive_Anchoring"]].copy()

    # Merge on analysis if both have it
    merge_key = "analysis" if "analysis" in net_df.columns and "analysis" in pca_means.columns else None
    if merge_key:
        merged = net_df.merge(pca_means, on=merge_key, how="inner")
    else:
        # If same number of rows, assume aligned
        if len(net_df) == len(pca_means):
            merged = pd.concat([net_df.reset_index(drop=True), pca_means.reset_index(drop=True)], axis=1)
        else:
            print("  [Network overlap] Cannot merge network and perturbation data")
            return pd.DataFrame(columns=["network", "afferent_coef", "afferent_p",
                                          "cognitive_coef", "cognitive_p", "overlap"])

    # Identify network columns (exclude metadata and perturbation cols)
    exclude = {"analysis", "pmid", "Afferent_Input_Index", "Cognitive_Anchoring",
               "arm_id", "arm_type", "PC1", "PC2", "PC3", "PC4", "PC5"}
    network_cols = [c for c in merged.columns if c not in exclude and merged[c].dtype in [np.float64, np.int64, float, int]]

    if len(network_cols) == 0:
        print("  [Network overlap] No numeric network columns found")
        return pd.DataFrame(columns=["network", "afferent_coef", "afferent_p",
                                      "cognitive_coef", "cognitive_p", "overlap"])

    # Threshold for "large effect" given low power (|beta| > 0.3 standardized)
    COEF_THRESHOLD = 0.3

    rows = []
    for net_col in network_cols:
        sub = merged[["Afferent_Input_Index", "Cognitive_Anchoring", net_col]].dropna()
        if len(sub) < 4:
            continue

        # Standardize for comparability
        for col in ["Afferent_Input_Index", "Cognitive_Anchoring", net_col]:
            col_std = sub[col].std()
            if col_std > 0:
                sub[col] = (sub[col] - sub[col].mean()) / col_std

        # Fit: Network ~ Afferent
        try:
            X_aff = sm.add_constant(sub["Afferent_Input_Index"])
            res_aff = sm.OLS(sub[net_col], X_aff).fit()
            aff_coef = res_aff.params.get("Afferent_Input_Index", np.nan)
            aff_p = res_aff.pvalues.get("Afferent_Input_Index", np.nan)
        except Exception:
            aff_coef, aff_p = np.nan, np.nan

        # Fit: Network ~ Cognitive
        try:
            X_cog = sm.add_constant(sub["Cognitive_Anchoring"])
            res_cog = sm.OLS(sub[net_col], X_cog).fit()
            cog_coef = res_cog.params.get("Cognitive_Anchoring", np.nan)
            cog_p = res_cog.pvalues.get("Cognitive_Anchoring", np.nan)
        except Exception:
            cog_coef, cog_p = np.nan, np.nan

        # Flag overlap: both significant or both large effect
        both_sig = (aff_p < 0.05 and cog_p < 0.05) if (not np.isnan(aff_p) and not np.isnan(cog_p)) else False
        both_large = (abs(aff_coef) > COEF_THRESHOLD and abs(cog_coef) > COEF_THRESHOLD) if (not np.isnan(aff_coef) and not np.isnan(cog_coef)) else False
        overlap = both_sig or both_large

        rows.append({
            "network": net_col,
            "afferent_coef": aff_coef,
            "afferent_p": aff_p,
            "cognitive_coef": cog_coef,
            "cognitive_p": cog_p,
            "overlap": overlap,
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Model comparison
# ---------------------------------------------------------------------------

def compare_models(results: dict) -> pd.DataFrame:
    """Compare additive vs interaction models: AIC, BIC, likelihood ratio test.

    Parameters
    ----------
    results : dict
        Keys 'additive' and 'interaction' mapping to model result dicts.

    Returns
    -------
    DataFrame with columns: model, aic, bic, r2, lr_test_p
    """
    rows = []
    for name in ["additive", "interaction"]:
        r = results.get(name, {})
        rows.append({
            "model": name,
            "aic": r.get("aic", np.nan),
            "bic": r.get("bic", np.nan),
            "r2": r.get("r2", np.nan),
            "n_obs": r.get("n_obs", 0),
            "lr_test_p": np.nan,
        })

    # Likelihood ratio test: interaction vs additive (interaction is less restricted)
    add_res = results.get("additive", {})
    int_res = results.get("interaction", {})
    add_fit = add_res.get("_fit")
    int_fit = int_res.get("_fit")

    if add_fit is not None and int_fit is not None:
        try:
            # LR = -2 * (ll_restricted - ll_full)
            ll_add = add_fit.llf
            ll_int = int_fit.llf
            lr_stat = -2 * (ll_add - ll_int)
            # df difference = 1 (interaction term)
            df_diff = 1
            lr_p = stats.chi2.sf(lr_stat, df_diff) if lr_stat > 0 else 1.0
            # Update the interaction row
            for row in rows:
                if row["model"] == "interaction":
                    row["lr_test_p"] = lr_p
        except Exception as e:
            print(f"  [Model comparison] LR test failed: {e}")

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

def _plot_simple_slopes(slopes_df: pd.DataFrame, out_path: Path):
    """Plot simple slopes: effect of Cognitive at different Afferent levels."""
    if slopes_df.empty:
        return

    fig, ax = plt.subplots(figsize=(7, 5))
    x = range(len(slopes_df))
    ax.bar(x, slopes_df["cognitive_slope"], yerr=slopes_df["std_err"],
           capsize=5, color=["#4C72B0", "#55A868", "#C44E52"], alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(slopes_df["afferent_level"], fontsize=9)
    ax.set_ylabel("Cognitive Anchoring slope on R_within")
    ax.set_xlabel("Afferent Input Index level")
    ax.set_title("Simple Slopes: Effect of Cognitive at Varying Afferent Levels")
    ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)

    # Add significance markers
    for i, row in slopes_df.iterrows():
        if row["p_value"] < 0.001:
            marker = "***"
        elif row["p_value"] < 0.01:
            marker = "**"
        elif row["p_value"] < 0.05:
            marker = "*"
        else:
            marker = "ns"
        y_pos = row["cognitive_slope"] + row["std_err"] + 0.01
        ax.text(i, y_pos, marker, ha="center", fontsize=10)

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_path}")


def _plot_model_comparison(comp_df: pd.DataFrame, out_path: Path):
    """Bar chart comparing AIC/BIC across models."""
    if comp_df.empty:
        return

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    models = comp_df["model"].tolist()
    x = range(len(models))

    # AIC
    axes[0].bar(x, comp_df["aic"], color=["#4C72B0", "#C44E52"], alpha=0.8)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(models)
    axes[0].set_ylabel("AIC")
    axes[0].set_title("Model Comparison: AIC (lower = better)")

    # BIC
    axes[1].bar(x, comp_df["bic"], color=["#4C72B0", "#C44E52"], alpha=0.8)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(models)
    axes[1].set_ylabel("BIC")
    axes[1].set_title("Model Comparison: BIC (lower = better)")

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    config.OUT_MODELS.mkdir(parents=True, exist_ok=True)
    config.OUT_FIGURES.mkdir(parents=True, exist_ok=True)

    print("Step 08: Component Interaction Modeling")
    print("=" * 60)

    # Build merged dataset
    print("\n[1] Building merged dataset...")
    try:
        df = _build_dataset()
        print(f"    Merged dataset: {len(df)} rows, {len(df.columns)} columns")
    except Exception as e:
        print(f"    ERROR building dataset: {e}")
        print("    Cannot proceed without data.")
        return

    if df.empty or len(df) < 10:
        print("    Insufficient merged data. Exiting.")
        return

    # Fit all model families
    print("\n[2] Fitting additive model...")
    additive_res = fit_additive_model(df)
    print(f"    n_obs={additive_res['n_obs']}, R2={additive_res['r2']:.3f}" if not np.isnan(additive_res["r2"]) else "    Model did not converge")

    print("\n[3] Fitting interaction model...")
    interaction_res = fit_interaction_model(df)
    print(f"    n_obs={interaction_res['n_obs']}, R2={interaction_res['r2']:.3f}" if not np.isnan(interaction_res["r2"]) else "    Model did not converge")

    print("\n[4] Fitting deqi bridging model...")
    deqi_res = fit_deqi_bridging_model(df)
    print(f"    Step1 n={deqi_res['step1']['n_obs']}, Step2 n={deqi_res['step2']['n_obs']}")

    print("\n[5] Probing simple slopes...")
    slopes_df = probe_simple_slopes(df)
    if not slopes_df.empty:
        print(slopes_df.to_string(index=False))

    print("\n[6] Testing network overlap...")
    overlap_df = test_network_overlap(df)
    if not overlap_df.empty:
        n_overlap = overlap_df["overlap"].sum()
        print(f"    {n_overlap}/{len(overlap_df)} networks show overlap")

    # Compare models
    print("\n[7] Comparing models...")
    model_results = {"additive": additive_res, "interaction": interaction_res}
    comp_df = compare_models(model_results)
    if not comp_df.empty:
        print(comp_df.to_string(index=False))

    # Save results
    print("\n[8] Saving results...")

    # Model comparison
    comp_df.to_csv(config.OUT_MODELS / "component_interaction_model_comparison.csv", index=False)

    # Coefficients from additive and interaction models
    coef_rows = []
    for name, res in model_results.items():
        for var, coef in res.get("coefficients", {}).items():
            p_val = res.get("p_values", {}).get(var, np.nan)
            coef_rows.append({"model": name, "variable": var, "coefficient": coef, "p_value": p_val})
    if coef_rows:
        pd.DataFrame(coef_rows).to_csv(
            config.OUT_MODELS / "component_interaction_coefficients.csv", index=False
        )

    # Deqi bridging results
    deqi_rows = []
    for step_name, step_data in [("step1", deqi_res["step1"]), ("step2", deqi_res["step2"])]:
        for var, coef in step_data.get("coefficients", {}).items():
            p_val = step_data.get("p_values", {}).get(var, np.nan)
            deqi_rows.append({"step": step_name, "variable": var, "coefficient": coef, "p_value": p_val})
    if deqi_rows:
        pd.DataFrame(deqi_rows).to_csv(
            config.OUT_MODELS / "deqi_bridging_path_results.csv", index=False
        )

    # Network overlap
    if not overlap_df.empty:
        overlap_df.to_csv(config.OUT_MODELS / "shared_network_overlap_results.csv", index=False)

    # Generate figures
    print("\n[9] Generating figures...")
    _plot_simple_slopes(slopes_df, config.OUT_FIGURES / "afferent_cognitive_interaction_slopes.png")
    _plot_model_comparison(comp_df, config.OUT_FIGURES / "additive_vs_interaction_model_fit.png")

    print("\nDone. Results in:", config.OUT_MODELS)


if __name__ == "__main__":
    main()
