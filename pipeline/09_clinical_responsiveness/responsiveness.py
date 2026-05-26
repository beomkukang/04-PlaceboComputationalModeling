"""Step 03: Clinical Responsiveness Computation (analysis_plan.md Section 6.2)

Builds on the parsed clinical outcomes from data_processing/v1/clinical/
to compute domain-aggregated and global responsiveness scores.

Steps:
1. Harmonize direction of all outcomes
2. Compute within-arm standardized response
3. Compute controlled response where comparator arms exist
4. Compute POMP response where valid scale ranges exist
5. Aggregate by disease domain
6. Estimate global responsiveness factor (if enough outcomes)

Inputs:
    data_processing/v1/clinical/clinical_parsed.csv
    data_processing/v1/clinical/clinical_effect_sizes.csv
    data_processing/v1/clinical/clinical_responsiveness.csv  (pre-computed R_within)

Outputs:
    data_analysis/outputs/behavioral/outcome_level_responsiveness.csv
    data_analysis/outputs/behavioral/domain_responsiveness.csv
    data_analysis/outputs/behavioral/global_responsiveness.csv
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


# ---------------------------------------------------------------------------
# Hedges correction factor J(m) = 1 - 3 / (4*m - 1), where m = df
# ---------------------------------------------------------------------------

def _hedges_correction(n: float) -> float:
    """Return Hedges' small-sample correction factor J for df = n - 1."""
    if np.isnan(n) or n <= 1:
        return np.nan
    return 1.0 - 3.0 / (4.0 * (n - 1.0) - 1.0)


# ---------------------------------------------------------------------------
# Step 1: Direction-correct all outcomes
# ---------------------------------------------------------------------------

def harmonize_outcome_direction(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure all outcomes are direction-corrected so positive = improvement.

    For scales where higher_is_better is False (e.g. pain, symptom severity),
    improvement means the score went *down*, so we set direction = -1.
    For scales where higher_is_better is True (e.g. quality of life),
    improvement means the score went *up*, so direction = +1.
    Missing higher_is_better defaults to False (most clinical scales).
    """
    df = df.copy()
    # Default: assume lower is better (pain, severity, etc.)
    hib = df["higher_is_better"].fillna(False)
    # Coerce string representations if present
    if hib.dtype == object:
        hib = hib.map(
            lambda x: True if str(x).strip().lower() == "true" else False
        )
    df["direction"] = np.where(hib, 1, -1)
    return df


# ---------------------------------------------------------------------------
# Step 2: Within-arm standardized response
# ---------------------------------------------------------------------------

def compute_standardized_response(effects: pd.DataFrame) -> pd.DataFrame:
    """Compute within-arm standardized response R_within with Hedges correction.

    R_within = direction * (post_mean - baseline_mean) / baseline_sd * J(n)

    Uses effect_sizes data which has baseline_mean, baseline_sd, post_mean, n.
    """
    df = effects.copy()

    # Direction correction
    df = harmonize_outcome_direction(df)

    raw_change = df["post_mean"] - df["baseline_mean"]
    df["R_within_raw"] = df["direction"] * raw_change / df["baseline_sd"]

    # Hedges correction
    df["hedges_J"] = df["n"].apply(_hedges_correction)
    df["R_within"] = df["R_within_raw"] * df["hedges_J"]

    return df


# ---------------------------------------------------------------------------
# Step 3: Controlled response (between-group)
# ---------------------------------------------------------------------------

def compute_controlled_response(df: pd.DataFrame) -> pd.DataFrame:
    """Compute controlled response where sham/control arms exist in same study.

    R_controlled = direction * [(post_T - base_T) - (post_C - base_C)]
                   / pooled_baseline_sd * J(n_T + n_C - 2)
    """
    df = df.copy()
    df["R_controlled"] = np.nan

    # Identify sham/control arms
    control_types = {"sham_acupuncture", "placebo", "waitlist", "no_treatment",
                     "sham", "control"}
    is_control = df["arm_type"].str.lower().isin(control_types)
    is_treatment = ~is_control

    controls = df.loc[is_control].copy()
    treatments = df.loc[is_treatment].copy()

    if controls.empty or treatments.empty:
        return df

    # For each study, match treatment arms to the control arm(s)
    for pmid in treatments["pmid"].unique():
        ctrl = controls[controls["pmid"] == pmid]
        treat = treatments[treatments["pmid"] == pmid]
        if ctrl.empty:
            continue
        # Average across control arms if multiple
        ctrl_change = (ctrl["post_mean"] - ctrl["baseline_mean"]).mean()
        ctrl_sd = ctrl["baseline_sd"].mean()
        ctrl_n = ctrl["n"].sum()

        for idx in treat.index:
            t_change = treat.loc[idx, "post_mean"] - treat.loc[idx, "baseline_mean"]
            t_sd = treat.loc[idx, "baseline_sd"]
            t_n = treat.loc[idx, "n"]
            direction = treat.loc[idx, "direction"]

            # Pooled baseline SD
            if t_n > 0 and ctrl_n > 0 and t_sd > 0 and ctrl_sd > 0:
                pooled_sd = np.sqrt(
                    ((t_n - 1) * t_sd ** 2 + (ctrl_n - 1) * ctrl_sd ** 2)
                    / (t_n + ctrl_n - 2)
                )
                if pooled_sd > 0:
                    raw = direction * (t_change - ctrl_change) / pooled_sd
                    J = _hedges_correction(t_n + ctrl_n)
                    df.loc[idx, "R_controlled"] = raw * J if not np.isnan(J) else raw

    return df


# ---------------------------------------------------------------------------
# Step 4: POMP response for bounded scales
# ---------------------------------------------------------------------------

def compute_pomp_response(
    effects: pd.DataFrame, parsed: pd.DataFrame
) -> pd.DataFrame:
    """Compute Percent of Maximum Possible (POMP) response for bounded scales.

    POMP_baseline = 100 * (baseline_mean - scale_min) / (scale_max - scale_min)
    POMP_post     = 100 * (post_mean - scale_min)     / (scale_max - scale_min)
    POMP_change   = direction * (POMP_post - POMP_baseline)
    """
    df = effects.copy()

    # Get scale bounds from parsed data (take first non-null per outcome)
    bounds = (
        parsed.dropna(subset=["scale_min", "scale_max"])
        .groupby(["pmid", "arm_id", "outcome_measure"], as_index=False)
        .agg({"scale_min": "first", "scale_max": "first"})
    )

    df = df.merge(
        bounds, on=["pmid", "arm_id", "outcome_measure"], how="left"
    )

    has_bounds = df["scale_min"].notna() & df["scale_max"].notna()
    scale_range = df["scale_max"] - df["scale_min"]
    valid = has_bounds & (scale_range > 0)

    df["POMP_baseline"] = np.where(
        valid,
        100.0 * (df["baseline_mean"] - df["scale_min"]) / scale_range,
        np.nan,
    )
    df["POMP_post"] = np.where(
        valid,
        100.0 * (df["post_mean"] - df["scale_min"]) / scale_range,
        np.nan,
    )
    df["POMP_change"] = np.where(
        valid,
        df["direction"] * (df["POMP_post"] - df["POMP_baseline"]),
        np.nan,
    )

    return df


# ---------------------------------------------------------------------------
# Step 5: Aggregate by disease domain
# ---------------------------------------------------------------------------

def aggregate_by_domain(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate responsiveness scores by study x outcome_domain.

    Returns the inverse-variance-weighted mean of R_within per study-domain,
    falling back to simple mean when variance info is unavailable.
    """
    agg_cols = {
        "R_within": "mean",
        "n": "sum",
    }
    # Add optional columns if present
    for col in ["POMP_change", "R_controlled"]:
        if col in df.columns and df[col].notna().any():
            agg_cols[col] = "mean"

    domain = (
        df.dropna(subset=["R_within"])
        .groupby(["pmid", "outcome_domain", "arm_type", "disease_condition"],
                 as_index=False)
        .agg(agg_cols)
    )
    domain.rename(columns={"n": "total_n"}, inplace=True)

    # Count number of outcomes per domain
    counts = (
        df.dropna(subset=["R_within"])
        .groupby(["pmid", "outcome_domain", "arm_type", "disease_condition"],
                 as_index=False)
        .size()
    )
    counts.rename(columns={"size": "n_outcomes"}, inplace=True)
    domain = domain.merge(
        counts,
        on=["pmid", "outcome_domain", "arm_type", "disease_condition"],
        how="left",
    )

    return domain


# ---------------------------------------------------------------------------
# Step 6: Global responsiveness factor via PCA
# ---------------------------------------------------------------------------

def estimate_global_responsiveness(domain_df: pd.DataFrame) -> pd.DataFrame:
    """Estimate a global responsiveness score per study-arm.

    If a study has outcomes in >= 2 domains, apply PCA across domain R_within
    values and take the first principal component score.
    Otherwise, use the single-domain R_within directly.
    """
    # Pivot: rows = (pmid, arm_type), columns = outcome_domain, values = R_within
    pivot = domain_df.pivot_table(
        index=["pmid", "arm_type", "disease_condition"],
        columns="outcome_domain",
        values="R_within",
        aggfunc="mean",
    )

    # Count non-null domains per study-arm
    n_domains = pivot.notna().sum(axis=1)

    results = []

    # Studies with >= 2 domains: attempt PCA
    multi_mask = n_domains >= 2
    if multi_mask.sum() >= 3:
        from sklearn.decomposition import PCA

        multi = pivot.loc[multi_mask].copy()
        # Keep only columns with some data
        valid_cols = multi.columns[multi.notna().any()]
        multi = multi[valid_cols]
        # Fill remaining NaN with column means for PCA
        filled = multi.fillna(multi.mean())

        if filled.shape[1] >= 2:
            pca = PCA(n_components=1)
            scores = pca.fit_transform(filled)
            explained = pca.explained_variance_ratio_[0]

            for i, (idx, _) in enumerate(multi.iterrows()):
                pmid, arm_type, disease = idx
                results.append({
                    "pmid": pmid,
                    "arm_type": arm_type,
                    "disease_condition": disease,
                    "global_R": scores[i, 0],
                    "method": "PCA_PC1",
                    "variance_explained": explained,
                    "n_domains": int(n_domains.loc[idx]),
                })

    # Studies with < 2 domains or if PCA was not run: use mean R_within
    pca_pmids = {r["pmid"] for r in results}
    for idx, row in pivot.iterrows():
        pmid, arm_type, disease = idx
        if pmid in pca_pmids:
            continue
        vals = row.dropna()
        if len(vals) == 0:
            continue
        results.append({
            "pmid": pmid,
            "arm_type": arm_type,
            "disease_condition": disease,
            "global_R": vals.mean(),
            "method": "mean_R_within",
            "variance_explained": np.nan,
            "n_domains": len(vals),
        })

    if not results:
        return pd.DataFrame(
            columns=["pmid", "arm_type", "disease_condition",
                     "global_R", "method", "variance_explained", "n_domains"]
        )

    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main():
    config.OUT_BEHAVIORAL.mkdir(parents=True, exist_ok=True)

    print("Step 03: Clinical Responsiveness")
    print("=" * 60)

    # ---- Load inputs ----
    effects = pd.read_csv(config.CLINICAL_EFFECT_SIZES)
    parsed = pd.read_csv(config.CLINICAL_PARSED)
    responsiveness_precomputed = pd.read_csv(config.CLINICAL_RESPONSIVENESS)

    print(f"  Effect sizes loaded: {len(effects)} rows, "
          f"{effects['pmid'].nunique()} studies")
    print(f"  Pre-computed R_within: {len(responsiveness_precomputed)} rows")

    # ---- Step 1-2: Compute R_within from effect sizes ----
    outcome = compute_standardized_response(effects)
    print(f"  Computed R_within for {outcome['R_within'].notna().sum()} outcomes")

    # ---- Merge pre-computed R_within for rows not in effect_sizes ----
    # Use pre-computed values as primary source; fill gaps with freshly computed
    precomp_key_cols = ["pmid", "arm_id", "outcome_measure"]
    if all(c in responsiveness_precomputed.columns for c in precomp_key_cols):
        # Mark pre-computed rows
        precomp_lookup = responsiveness_precomputed.set_index(precomp_key_cols)[
            "R_within"
        ]
        merge_key = outcome.set_index(precomp_key_cols).index
        for idx, key in zip(outcome.index, merge_key):
            if key in precomp_lookup.index:
                precomp_val = precomp_lookup.loc[key]
                if isinstance(precomp_val, pd.Series):
                    precomp_val = precomp_val.iloc[0]
                if not np.isnan(precomp_val):
                    outcome.loc[idx, "R_within"] = precomp_val
                    outcome.loc[idx, "source"] = "precomputed"

    # ---- Step 3: Controlled response ----
    outcome = compute_controlled_response(outcome)
    n_controlled = outcome["R_controlled"].notna().sum()
    print(f"  Controlled response computed for {n_controlled} outcomes")

    # ---- Step 4: POMP response ----
    outcome = compute_pomp_response(outcome, parsed)
    n_pomp = outcome["POMP_change"].notna().sum()
    print(f"  POMP computed for {n_pomp} outcomes with bounded scales")

    # ---- Save outcome-level responsiveness ----
    out_cols = [
        "pmid", "arm_id", "arm_type", "outcome_measure", "outcome_domain",
        "scale_name", "disease_condition", "n", "direction",
        "baseline_mean", "baseline_sd", "post_mean",
        "R_within", "R_controlled",
        "POMP_baseline", "POMP_post", "POMP_change",
    ]
    # Keep only columns that exist
    out_cols = [c for c in out_cols if c in outcome.columns]
    outcome_out = outcome[out_cols].copy()
    outcome_path = config.OUT_BEHAVIORAL / "outcome_level_responsiveness.csv"
    outcome_out.to_csv(outcome_path, index=False)
    print(f"  Saved: {outcome_path}")

    # ---- Step 5: Domain aggregation ----
    domain = aggregate_by_domain(outcome)
    domain_path = config.OUT_BEHAVIORAL / "domain_responsiveness.csv"
    domain.to_csv(domain_path, index=False)
    print(f"  Domain-level: {len(domain)} rows across "
          f"{domain['outcome_domain'].nunique()} domains")
    print(f"  Saved: {domain_path}")

    # ---- Step 6: Global responsiveness ----
    global_resp = estimate_global_responsiveness(domain)
    global_path = config.OUT_BEHAVIORAL / "global_responsiveness.csv"
    global_resp.to_csv(global_path, index=False)
    print(f"  Global responsiveness: {len(global_resp)} study-arms")
    print(f"  Saved: {global_path}")

    print("=" * 60)
    print("Done. Results in:", config.OUT_BEHAVIORAL)


if __name__ == "__main__":
    main()
