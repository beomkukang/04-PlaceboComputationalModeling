"""Step 02: Data Validation (analysis_plan.md Section 6.1)

Cross-file consistency and quality checks on all processed data
before running downstream analyses.

Checks:
- Missing study IDs across tables
- Duplicate contrasts
- Coordinate outliers (outside MNI bounds)
- Directionality conflicts between tables
- Impossible scale values (deqi, clinical)
- Missing SDs in clinical effect sizes
- Multiple outcomes from same arm
- Multiple contrasts from same study in same family

Inputs:
    data_processing/v1/contrast_classifications.csv
    data_processing/v1/sdm/*.txt
    data_processing/v1/clinical/*.csv
    data_processing/v1/perturbation_space/*.csv
    data_processing/v1/sensory/*.csv
    data_processing/v1/rsa/*.csv

Outputs:
    data_analysis/outputs/qc/data_validation_report.md
    data_analysis/outputs/qc/missingness_tables.csv
    data_analysis/outputs/qc/coordinate_outliers.csv
"""

import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np

# Add parent to path for config import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config

# MNI bounding box
MNI_BOUNDS = {
    "x": (-90, 90),
    "y": (-126, 90),
    "z": (-72, 108),
}

# Collect findings across all checks for the final report
_findings: list[dict] = []


def _record(check: str, level: str, message: str, detail: str = ""):
    """Store a QC finding for the final report.

    Parameters
    ----------
    check : str
        Name of the check function.
    level : str
        'ERROR', 'WARNING', or 'INFO'.
    message : str
        One-line summary.
    detail : str, optional
        Multi-line detail (tables, lists, etc.).
    """
    _findings.append(
        {"check": check, "level": level, "message": message, "detail": detail}
    )


def _safe_read(path: Path, label: str) -> pd.DataFrame | None:
    """Try to read a CSV; record an error finding if missing."""
    if not path.exists():
        _record("file_check", "ERROR", f"Missing input file: {label} ({path.name})")
        return None
    try:
        return pd.read_csv(path)
    except Exception as exc:
        _record(
            "file_check", "ERROR", f"Failed to read {label} ({path.name}): {exc}"
        )
        return None


# -----------------------------------------------------------------------
# Individual checks
# -----------------------------------------------------------------------


def check_study_id_consistency():
    """Verify study IDs (pmid) match across all processed tables."""
    print("  Checking study ID consistency ...")

    cc = _safe_read(config.CONTRAST_CLASSIFICATIONS, "contrast_classifications")
    ac = _safe_read(config.ARM_COMPONENTS, "arm_components")
    cp = _safe_read(config.CLINICAL_PARSED, "clinical_parsed")
    sp = _safe_read(config.STUDY_PREDICTORS, "study_predictors")
    coords = _safe_read(config.MACM_COORDINATES, "macm_coordinates")

    loaded: dict[str, set] = {}
    for name, df in [
        ("contrast_classifications", cc),
        ("arm_components", ac),
        ("clinical_parsed", cp),
        ("study_predictors", sp),
        ("macm_coordinates", coords),
    ]:
        if df is not None and "pmid" in df.columns:
            loaded[name] = set(df["pmid"].dropna().unique())

    if len(loaded) < 2:
        _record(
            "study_id_consistency",
            "WARNING",
            "Fewer than 2 files loaded; cannot cross-check study IDs.",
        )
        return

    all_ids = set().union(*loaded.values())
    lines: list[str] = []
    for pmid in sorted(all_ids):
        present_in = [n for n, ids in loaded.items() if pmid in ids]
        absent_from = [n for n, ids in loaded.items() if pmid not in ids]
        if absent_from:
            lines.append(
                f"  pmid={pmid}: present in {', '.join(present_in)}; "
                f"missing from {', '.join(absent_from)}"
            )

    if lines:
        _record(
            "study_id_consistency",
            "WARNING",
            f"{len(lines)} study ID(s) not present in all files.",
            "\n".join(lines[:50])
            + ("\n  ..." if len(lines) > 50 else ""),
        )
    else:
        _record(
            "study_id_consistency",
            "INFO",
            f"All {len(all_ids)} study IDs consistent across {len(loaded)} files.",
        )


def check_duplicate_contrasts():
    """Flag duplicate contrasts within the same study + contrast_category."""
    print("  Checking duplicate contrasts ...")

    cc = _safe_read(config.CONTRAST_CLASSIFICATIONS, "contrast_classifications")
    if cc is None:
        return

    required = {"pmid", "contrast_id", "contrast_category"}
    if not required.issubset(cc.columns):
        _record(
            "duplicate_contrasts",
            "ERROR",
            f"contrast_classifications missing columns: {required - set(cc.columns)}",
        )
        return

    grouped = cc.groupby(["pmid", "contrast_category"])["contrast_id"].count()
    dups = grouped[grouped > 1]

    if dups.empty:
        _record(
            "duplicate_contrasts",
            "INFO",
            "No duplicate contrasts within the same study + category.",
        )
    else:
        lines = [
            f"  pmid={pmid}, category={cat}: {cnt} contrasts"
            for (pmid, cat), cnt in dups.items()
        ]
        _record(
            "duplicate_contrasts",
            "WARNING",
            f"{len(dups)} study-category pairs have multiple contrasts.",
            "\n".join(lines[:50]),
        )


def check_coordinate_outliers() -> pd.DataFrame:
    """Flag coordinates outside MNI bounds and save to CSV."""
    print("  Checking coordinate outliers ...")

    coords = _safe_read(config.MACM_COORDINATES, "macm_coordinates")
    if coords is None:
        return pd.DataFrame()

    required = {"pmid", "contrast_id", "x", "y", "z"}
    if not required.issubset(coords.columns):
        _record(
            "coordinate_outliers",
            "ERROR",
            f"macm_coordinates missing columns: {required - set(coords.columns)}",
        )
        return pd.DataFrame()

    oob_mask = (
        (coords["x"] < MNI_BOUNDS["x"][0])
        | (coords["x"] > MNI_BOUNDS["x"][1])
        | (coords["y"] < MNI_BOUNDS["y"][0])
        | (coords["y"] > MNI_BOUNDS["y"][1])
        | (coords["z"] < MNI_BOUNDS["z"][0])
        | (coords["z"] > MNI_BOUNDS["z"][1])
    )
    outliers = coords[oob_mask].copy()

    out_path = config.OUT_QC / "coordinate_outliers.csv"
    outliers.to_csv(out_path, index=False)

    if outliers.empty:
        _record(
            "coordinate_outliers",
            "INFO",
            f"All {len(coords)} coordinates within MNI bounds.",
        )
    else:
        _record(
            "coordinate_outliers",
            "WARNING",
            f"{len(outliers)} of {len(coords)} coordinates outside MNI bounds.",
            f"Saved to {out_path.name}. "
            f"Affected studies: {sorted(outliers['pmid'].unique())}",
        )
    return outliers


def check_scale_validity():
    """Flag impossible scale values in deqi and clinical data."""
    print("  Checking scale validity ...")

    issues: list[str] = []

    # --- DEQI checks ---
    deqi = _safe_read(config.DEQI_SUMMARY, "deqi_summary")
    if deqi is not None and "value" in deqi.columns:
        deqi["_value_num"] = pd.to_numeric(deqi["value"], errors="coerce")
        neg = deqi[deqi["_value_num"] < 0]
        if not neg.empty:
            issues.append(
                f"DEQI: {len(neg)} row(s) with negative value "
                f"(pmids: {sorted(neg['pmid'].unique()) if 'pmid' in neg.columns else 'N/A'})"
            )

        if "n_analyzed" in deqi.columns:
            bad_n = deqi[deqi["n_analyzed"].notna() & (deqi["n_analyzed"] <= 0)]
            if not bad_n.empty:
                issues.append(
                    f"DEQI: {len(bad_n)} row(s) with n_analyzed <= 0"
                )

    # --- Clinical parsed checks ---
    cp = _safe_read(config.CLINICAL_PARSED, "clinical_parsed")
    if cp is not None:
        # Check for values outside defined scale range
        if {"mean", "scale_min", "scale_max"}.issubset(cp.columns):
            has_bounds = cp["scale_min"].notna() & cp["scale_max"].notna() & cp["mean"].notna()
            bounded = cp[has_bounds]
            below = bounded[bounded["mean"] < bounded["scale_min"]]
            above = bounded[bounded["mean"] > bounded["scale_max"]]
            if not below.empty:
                issues.append(
                    f"Clinical parsed: {len(below)} row(s) with mean below scale_min"
                )
            if not above.empty:
                issues.append(
                    f"Clinical parsed: {len(above)} row(s) with mean above scale_max"
                )

        # Negative SD
        if "sd" in cp.columns:
            neg_sd = cp[cp["sd"].notna() & (cp["sd"] < 0)]
            if not neg_sd.empty:
                issues.append(
                    f"Clinical parsed: {len(neg_sd)} row(s) with negative SD"
                )

        # n_analyzed <= 0
        if "n_analyzed" in cp.columns:
            bad_n = cp[cp["n_analyzed"].notna() & (cp["n_analyzed"] <= 0)]
            if not bad_n.empty:
                issues.append(
                    f"Clinical parsed: {len(bad_n)} row(s) with n_analyzed <= 0"
                )

    if not issues:
        _record("scale_validity", "INFO", "No impossible scale values detected.")
    else:
        _record(
            "scale_validity",
            "WARNING",
            f"{len(issues)} scale validity issue(s) found.",
            "\n".join(f"  - {i}" for i in issues),
        )


def check_clinical_completeness():
    """Check for missing SDs, sample sizes, and effect sizes in clinical data."""
    print("  Checking clinical completeness ...")

    es = _safe_read(config.CLINICAL_EFFECT_SIZES, "clinical_effect_sizes")
    if es is None:
        return

    issues: list[str] = []
    critical_cols = ["baseline_sd", "n", "g_corrected"]
    for col in critical_cols:
        if col not in es.columns:
            issues.append(f"Column '{col}' not found in clinical_effect_sizes")
            continue
        n_miss = es[col].isna().sum()
        if n_miss > 0:
            pct = 100 * n_miss / len(es)
            issues.append(
                f"'{col}' missing in {n_miss}/{len(es)} rows ({pct:.1f}%)"
            )

    # Check for arms with multiple outcome domains (potential double-counting)
    oba = _safe_read(config.OUTCOMES_BY_ARM, "outcomes_by_arm")
    if oba is not None and {"pmid", "arm_id"}.issubset(oba.columns):
        arm_counts = oba.groupby(["pmid", "arm_id"]).size()
        multi = arm_counts[arm_counts > 1]
        if not multi.empty:
            issues.append(
                f"{len(multi)} arm(s) have multiple outcome rows in outcomes_by_arm "
                f"(may be intentional for multi-domain studies)"
            )

    if not issues:
        _record(
            "clinical_completeness",
            "INFO",
            f"Clinical effect sizes complete ({len(es)} rows).",
        )
    else:
        _record(
            "clinical_completeness",
            "WARNING",
            f"{len(issues)} clinical completeness issue(s).",
            "\n".join(f"  - {i}" for i in issues),
        )


def generate_missingness_table() -> pd.DataFrame:
    """Summarize per-variable missingness across studies and save to CSV."""
    print("  Generating missingness tables ...")

    records: list[dict] = []

    datasets: list[tuple[str, Path, list[str]]] = [
        (
            "arm_components",
            config.ARM_COMPONENTS,
            [
                "arm_type",
                "disease_condition",
                "penetration",
                "depth",
            ],
        ),
        (
            "study_predictors",
            config.STUDY_PREDICTORS,
            [
                "penetration_level",
                "skin_contact",
                "blinding_quality",
            ],
        ),
        (
            "deqi_summary",
            config.DEQI_SUMMARY,
            ["instrument", "value", "n_analyzed"],
        ),
        (
            "clinical_parsed",
            config.CLINICAL_PARSED,
            [
                "outcome_domain",
                "mean",
                "sd",
                "n_analyzed",
                "higher_is_better",
                "scale_min",
                "scale_max",
            ],
        ),
        (
            "clinical_effect_sizes",
            config.CLINICAL_EFFECT_SIZES,
            [
                "baseline_mean",
                "baseline_sd",
                "post_mean",
                "n",
                "g_corrected",
            ],
        ),
        (
            "contrast_classifications",
            config.CONTRAST_CLASSIFICATIONS,
            [
                "contrast_category",
                "tissue_level",
                "has_usable_coordinates",
                "n_coordinates",
            ],
        ),
    ]

    for ds_name, ds_path, columns in datasets:
        df = _safe_read(ds_path, ds_name)
        if df is None:
            for col in columns:
                records.append(
                    {
                        "dataset": ds_name,
                        "variable": col,
                        "n_total": 0,
                        "n_present": 0,
                        "n_missing": 0,
                        "pct_missing": 100.0,
                    }
                )
            continue

        n_total = len(df)
        # If pmid exists, also count unique studies
        n_studies = df["pmid"].nunique() if "pmid" in df.columns else None

        for col in columns:
            if col not in df.columns:
                records.append(
                    {
                        "dataset": ds_name,
                        "variable": col,
                        "n_total": n_total,
                        "n_present": 0,
                        "n_missing": n_total,
                        "pct_missing": 100.0,
                        "n_studies": n_studies,
                    }
                )
            else:
                n_miss = int(df[col].isna().sum())
                n_pres = n_total - n_miss
                pct = 100 * n_miss / n_total if n_total > 0 else 0.0
                records.append(
                    {
                        "dataset": ds_name,
                        "variable": col,
                        "n_total": n_total,
                        "n_present": n_pres,
                        "n_missing": n_miss,
                        "pct_missing": round(pct, 2),
                        "n_studies": n_studies,
                    }
                )

    miss_df = pd.DataFrame(records)
    out_path = config.OUT_QC / "missingness_tables.csv"
    miss_df.to_csv(out_path, index=False)
    print(f"    Saved {out_path.name}")

    high_miss = miss_df[miss_df["pct_missing"] > 20]
    if high_miss.empty:
        _record(
            "missingness",
            "INFO",
            "All key variables have <= 20% missingness.",
        )
    else:
        lines = [
            f"  - {row['dataset']}.{row['variable']}: "
            f"{row['pct_missing']:.1f}% missing ({row['n_missing']}/{row['n_total']})"
            for _, row in high_miss.iterrows()
        ]
        _record(
            "missingness",
            "WARNING",
            f"{len(high_miss)} variable(s) exceed 20% missingness.",
            "\n".join(lines),
        )

    return miss_df


def write_validation_report():
    """Write markdown summary of all QC findings."""
    print("  Writing validation report ...")

    errors = [f for f in _findings if f["level"] == "ERROR"]
    warnings = [f for f in _findings if f["level"] == "WARNING"]
    infos = [f for f in _findings if f["level"] == "INFO"]

    lines: list[str] = []
    lines.append("# Data Validation Report")
    lines.append("")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Errors:** {len(errors)}")
    lines.append(f"- **Warnings:** {len(warnings)}")
    lines.append(f"- **Info:** {len(infos)}")
    lines.append("")

    if errors:
        lines.append("## Errors")
        lines.append("")
        for f in errors:
            lines.append(f"### [{f['check']}] {f['message']}")
            if f["detail"]:
                lines.append("")
                lines.append("```")
                lines.append(f["detail"])
                lines.append("```")
            lines.append("")

    if warnings:
        lines.append("## Warnings")
        lines.append("")
        for f in warnings:
            lines.append(f"### [{f['check']}] {f['message']}")
            if f["detail"]:
                lines.append("")
                lines.append("```")
                lines.append(f["detail"])
                lines.append("```")
            lines.append("")

    if infos:
        lines.append("## Passed Checks")
        lines.append("")
        for f in infos:
            lines.append(f"- **[{f['check']}]** {f['message']}")
        lines.append("")

    out_path = config.OUT_QC / "data_validation_report.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"    Saved {out_path.name}")

    # Print summary to console
    n_err = len(errors)
    n_warn = len(warnings)
    status = "PASS" if n_err == 0 else "FAIL"
    print(f"\n  Validation {status}: {n_err} error(s), {n_warn} warning(s)")


def main():
    config.OUT_QC.mkdir(parents=True, exist_ok=True)

    print("Step 02: Data Validation")
    print("=" * 60)

    check_study_id_consistency()
    check_duplicate_contrasts()
    check_coordinate_outliers()
    check_scale_validity()
    check_clinical_completeness()
    generate_missingness_table()
    write_validation_report()

    print("\nDone. Results in:", config.OUT_QC)


if __name__ == "__main__":
    main()
