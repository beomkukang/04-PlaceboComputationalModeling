#!/usr/bin/env python3
"""
prepare_sdm.py

Convert our SDM coordinate files into SDM-PSI's required format:
- One text file per study: {first_author}{year}.{software}_{space}.txt
- Comma-separated: x,y,z,t-value
- sdm_table.txt with study metadata

Input: data_processing/v1/sdm/*.txt + raw extraction JSONs
Output: data_analysis/01_sdm_preparation/sdm_projects/{analysis}/
"""

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd

from data_processing.v1.config import OUTPUT_DIR, get_all_pmids, load_raw_json

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SDM_INPUT_DIR = PROJECT_ROOT / "data_processing" / "v1" / "sdm"
SDM_OUTPUT_DIR = Path(__file__).resolve().parent / "sdm_projects"
CLS_PATH = OUTPUT_DIR / "contrast_classifications.csv"


def get_study_metadata(pmid: str) -> dict:
    """Extract study-level info needed for sdm_table.txt."""
    data = load_raw_json(pmid)
    study = data.get("study", {})

    first_author = study.get("first_author", pmid)
    year = study.get("year", "")
    # Clean author name
    first_author = re.sub(r"[^a-zA-Z]", "", str(first_author))

    n_total = study.get("n_total_analyzed_neuroimaging") or study.get("n_total_enrolled")
    if n_total:
        try:
            n_total = int(n_total)
        except (ValueError, TypeError):
            n_total = None

    # Software → extension mapping
    software = str(study.get("fmri_software", "") or "").lower()
    if "spm" in software:
        sw = "spm"
    elif "fsl" in software:
        sw = "fsl"
    else:
        sw = "other"

    return {
        "pmid": pmid,
        "study_label": f"{first_author}{year}",
        "first_author": first_author,
        "year": year,
        "n_total": n_total,
        "software": sw,
        "disease": study.get("disease_condition", ""),
    }


def get_software_and_space(pmid: str, coord_space: str = "MNI") -> str:
    """Determine the filename extension based on software and coordinate space."""
    data = load_raw_json(pmid)
    software = str(data.get("study", {}).get("fmri_software", "") or "").lower()

    if "spm" in software:
        sw = "spm"
    elif "fsl" in software:
        sw = "fsl"
    else:
        sw = "other"

    space = "mni"  # default — we already converted Talairach to MNI
    return f"{sw}_{space}"


def parse_our_sdm_file(filepath: Path) -> dict[str, list[tuple]]:
    """Parse our SDM file format into {pmid: [(x,y,z,t), ...]}."""
    studies = {}
    current_pmid = None
    current_n = None

    for line in filepath.read_text().strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("// Reference="):
            current_pmid = line.replace("// Reference=", "").strip()
            studies[current_pmid] = {"n": None, "peaks": []}
        elif line.startswith("// Subjects="):
            n = line.replace("// Subjects=", "").strip()
            if current_pmid and n != "?":
                try:
                    studies[current_pmid]["n"] = int(float(n))
                except (ValueError, TypeError):
                    pass
        elif line.startswith("//"):
            continue
        elif "\t" in line and current_pmid:
            parts = line.split("\t")
            try:
                x = float(parts[0])
                y = float(parts[1])
                z = float(parts[2])
                t = float(parts[3]) if len(parts) > 3 else None
                studies[current_pmid]["peaks"].append((x, y, z, t))
            except (ValueError, IndexError):
                pass

    return studies


def write_study_file(outdir: Path, study_label: str, ext: str, peaks: list[tuple]):
    """Write one SDM-PSI study file."""
    filename = f"{study_label}.{ext}.txt"
    lines = []
    for x, y, z, t in peaks:
        if t is not None:
            lines.append(f"{x},{y},{z},{t}")
        else:
            lines.append(f"{x},{y},{z},p")  # p = positive peak, unknown effect size
    (outdir / filename).write_text("\n".join(lines))
    return filename


def write_no_peaks_file(outdir: Path, study_label: str):
    """Write empty file for studies with no peaks."""
    filename = f"{study_label}.no_peaks.txt"
    (outdir / filename).write_text("")
    return filename


def write_sdm_table(outdir: Path, table_rows: list[dict], extra_cols: list[str] = None):
    """Write sdm_table.txt."""
    cols = ["study", "n1", "n2", "t_thr"]
    if extra_cols:
        cols.extend(extra_cols)

    lines = ["\t".join(cols)]
    for row in table_rows:
        values = [str(row.get(c, "NA")) for c in cols]
        lines.append("\t".join(values))

    (outdir / "sdm_table.txt").write_text("\n".join(lines))


def build_analysis_project(analysis_name: str, cls_df: pd.DataFrame,
                           extra_table_cols: list[str] = None):
    """Build one SDM-PSI project directory for an analysis."""
    sdm_file = SDM_INPUT_DIR / f"{analysis_name}.txt"
    if not sdm_file.exists():
        return

    outdir = SDM_OUTPUT_DIR / analysis_name
    outdir.mkdir(parents=True, exist_ok=True)

    # Parse our format
    studies = parse_our_sdm_file(sdm_file)
    if not studies:
        return

    table_rows = []
    study_labels_seen = {}

    for pmid, study_data in sorted(studies.items()):
        peaks = study_data["peaks"]
        meta = get_study_metadata(pmid)
        ext = get_software_and_space(pmid)

        # Use PMID as label
        label = pmid

        if peaks:
            write_study_file(outdir, label, ext, peaks)
        else:
            write_no_peaks_file(outdir, label)

        # Sample size
        n = study_data["n"] or meta["n_total"] or "NA"

        # Threshold — approximate from our data
        # Default conservative: p<0.001 ≈ t=3.1
        t_thr = 3.1

        row = {
            "study": label,
            "n1": n,
            "n2": n,
            "t_thr": t_thr,
        }

        # Add tissue_level for sham analyses
        if extra_table_cols and "tissue_level" in extra_table_cols:
            # Always look up from sham_gt_rest (the base category)
            paper_cls = cls_df[
                (cls_df["pmid"].astype(str) == pmid) &
                (cls_df["contrast_category"] == "sham_gt_rest")
            ]
            tl = paper_cls["tissue_level"].dropna().values
            if len(tl) > 0:
                tl_val = int(tl[0])
                # Code as binary: 1=penetrating (L1+L2), 0=non-penetrating (L3+L4)
                row["tissue_level"] = 1 if tl_val <= 2 else 0
            else:
                row["tissue_level"] = "NA"

        table_rows.append(row)

    write_sdm_table(outdir, table_rows, extra_cols=extra_table_cols)

    # Write README
    n_studies = len(studies)
    n_peaks = sum(len(s["peaks"]) for s in studies.values())
    (outdir / "README.txt").write_text(
        f"Analysis: {analysis_name}\n"
        f"Studies: {n_studies}\n"
        f"Total peaks: {n_peaks}\n"
        f"Coordinate space: MNI (Talairach converted)\n"
        f"Generated from: data_processing/v1/sdm/{analysis_name}.txt\n"
    )

    print(f"  {analysis_name}: {n_studies} studies, {n_peaks} peaks → {outdir}")


def main():
    print("=" * 60)
    print("Prepare SDM-PSI Project Directories")
    print("=" * 60)

    cls_df = pd.read_csv(CLS_PATH) if CLS_PATH.exists() else pd.DataFrame()

    # Create penetrating (L1+L2) and non-penetrating (L3+L4) combined files
    for combo_name, sources in [
        ("sham_gt_rest_penetrating", ["sham_gt_rest_L1", "sham_gt_rest_L2"]),
        ("sham_gt_rest_nonpenetrating", ["sham_gt_rest_L3", "sham_gt_rest_L4"]),
    ]:
        parts = []
        for src in sources:
            src_file = SDM_INPUT_DIR / f"{src}.txt"
            if src_file.exists():
                parts.append(src_file.read_text().strip())
        if parts:
            (SDM_INPUT_DIR / f"{combo_name}.txt").write_text("\n\n".join(parts))

    # Main analyses
    analyses = [
        ("sham_gt_rest", ["tissue_level"]),
        ("sham_gt_rest_penetrating", ["tissue_level"]),
        ("sham_gt_rest_nonpenetrating", ["tissue_level"]),
        ("verum_gt_sham", None),
        ("verum_gt_rest", None),
        ("verum_post_gt_pre", None),
        ("sham_post_gt_pre", None),
        ("deactivation", None),
        ("group_comparison", None),
        ("correlation_clinical", None),
    ]

    for analysis_name, extra_cols in analyses:
        build_analysis_project(analysis_name, cls_df, extra_cols)

    print(f"\nAll projects saved to: {SDM_OUTPUT_DIR}")
    print(f"\nNext: Open SDM-PSI software and follow SDM_PSI_DIRECTIONS.md")


if __name__ == "__main__":
    main()
