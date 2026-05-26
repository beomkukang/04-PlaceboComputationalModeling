"""Step 05: Neural Response-Space Construction (analysis_plan.md Section 6.4)

Builds study-level neural profiles from reported peak coordinates.
Each study gets a vector of peak counts per brain region using the
Harvard-Oxford cortical + subcortical atlas for full-brain coverage.

Inputs:
    data_processing/v1/macm/all_coordinates_pooled.csv

Outputs:
    data_analysis/outputs/neural/neural_feature_matrix.csv
    data_analysis/outputs/neural/neural_distance_matrix.csv
    data_analysis/outputs/neural/network_summary_scores.csv
    data_analysis/outputs/neural/coordinates_with_assignments.csv
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import nibabel as nib
from nilearn import datasets

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config

# Network mappings: Harvard-Oxford label substrings → network
NETWORK_MAP = {
    "Sensorimotor": [
        "Precentral Gyrus", "Postcentral Gyrus",
        "Juxtapositional Lobule",  # SMA
        "Parietal Opercular Cortex", "Central Opercular Cortex",  # SII
    ],
    "Salience": [
        "Insular Cortex",
        "Cingulate Gyrus, anterior division", "Paracingulate Gyrus",
    ],
    "DMN": [
        "Frontal Medial Cortex", "Subcallosal Cortex",  # mPFC
        "Precuneous Cortex",
        "Cingulate Gyrus, posterior division",  # PCC
        "Angular Gyrus",
    ],
    "Frontoparietal": [
        "Middle Frontal Gyrus",
        "Inferior Frontal Gyrus, pars opercularis",
        "Inferior Frontal Gyrus, pars triangularis",
        "Superior Frontal Gyrus", "Frontal Pole",
        "Superior Parietal Lobule", "Supramarginal Gyrus",
    ],
    "Limbic": [
        "Amygdala", "Hippocampus",
        "Parahippocampal Gyrus",
        "Frontal Orbital Cortex",
    ],
    "Temporal": [
        "Superior Temporal Gyrus", "Middle Temporal Gyrus",
        "Inferior Temporal Gyrus", "Temporal Pole",
        "Temporal Fusiform Cortex", "Temporal Occipital Fusiform",
        "Planum Polare", "Planum Temporale", "Heschl",
    ],
    "Subcortical": [
        "Thalamus", "Caudate", "Putamen", "Pallidum",
        "Accumbens", "Brain-Stem",
    ],
    "Occipital": [
        "Lateral Occipital Cortex", "Occipital Pole",
        "Occipital Fusiform", "Intracalcarine", "Supracalcarine",
        "Cuneal Cortex", "Lingual Gyrus",
    ],
}


def load_atlas():
    """Load Harvard-Oxford cortical + subcortical atlases."""
    atlas_cort = datasets.fetch_atlas_harvard_oxford('cort-maxprob-thr25-2mm')
    atlas_sub = datasets.fetch_atlas_harvard_oxford('sub-maxprob-thr25-2mm')

    cort_img = (atlas_cort['maps'] if isinstance(atlas_cort['maps'], nib.Nifti1Image)
                else nib.load(atlas_cort['maps']))
    sub_img = (atlas_sub['maps'] if isinstance(atlas_sub['maps'], nib.Nifti1Image)
               else nib.load(atlas_sub['maps']))

    return {
        "cort_data": np.asarray(cort_img.dataobj).astype(int),
        "cort_affine": cort_img.affine,
        "cort_labels": atlas_cort['labels'],
        "sub_data": np.asarray(sub_img.dataobj).astype(int),
        "sub_affine": sub_img.affine,
        "sub_labels": atlas_sub['labels'],
    }


def load_coordinates() -> pd.DataFrame:
    """Load and harmonize all peak coordinates to MNI."""
    coords = pd.read_csv(config.MACM_COORDINATES)
    print(f"  Loaded {len(coords)} coordinates from {coords['pmid'].nunique()} studies")

    # Harmonize coordinate space
    coords["_space"] = coords["coordinate_space"].fillna("").str.lower()
    is_tal = coords["_space"].str.contains("tal")

    # Lancaster tal2mni approximation
    if is_tal.any():
        n_tal = is_tal.sum()
        tal_x = coords.loc[is_tal, "x"].values
        tal_y = coords.loc[is_tal, "y"].values
        tal_z = coords.loc[is_tal, "z"].values
        coords.loc[is_tal, "x_mni"] = tal_x * 0.9900 + tal_z * 0.0396
        coords.loc[is_tal, "y_mni"] = tal_y * 0.9688 + tal_z * 0.0460
        coords.loc[is_tal, "z_mni"] = tal_y * -0.0485 + tal_z * 0.9189
        print(f"  Converted {n_tal} Talairach coordinates to MNI")

    is_mni = ~is_tal
    coords.loc[is_mni, "x_mni"] = coords.loc[is_mni, "x"]
    coords.loc[is_mni, "y_mni"] = coords.loc[is_mni, "y"]
    coords.loc[is_mni, "z_mni"] = coords.loc[is_mni, "z"]

    coords.drop(columns=["_space"], inplace=True)
    return coords


def assign_peaks_to_regions(coords: pd.DataFrame, atlas: dict) -> pd.DataFrame:
    """Assign each peak to a Harvard-Oxford region."""
    print("  Assigning peaks to Harvard-Oxford atlas regions...")

    cort_data = atlas["cort_data"]
    cort_affine = atlas["cort_affine"]
    cort_labels = atlas["cort_labels"]
    sub_data = atlas["sub_data"]
    sub_affine = atlas["sub_affine"]
    sub_labels = atlas["sub_labels"]

    inv_cort = np.linalg.inv(cort_affine)
    inv_sub = np.linalg.inv(sub_affine)

    assignments = []
    for _, row in coords.iterrows():
        x, y, z = row["x_mni"], row["y_mni"], row["z_mni"]
        if np.isnan(x) or np.isnan(y) or np.isnan(z):
            assignments.append("unassigned")
            continue

        # Try cortical atlas first
        vox = np.round(inv_cort[:3, :3] @ [x, y, z] + inv_cort[:3, 3]).astype(int)
        label = None
        if all(0 <= vox[i] < cort_data.shape[i] for i in range(3)):
            idx = int(cort_data[vox[0], vox[1], vox[2]])
            if 0 < idx < len(cort_labels):
                label = f"Cort_{cort_labels[idx]}"

        # If cortical is background, try subcortical
        if label is None:
            vox_s = np.round(inv_sub[:3, :3] @ [x, y, z] + inv_sub[:3, 3]).astype(int)
            if all(0 <= vox_s[i] < sub_data.shape[i] for i in range(3)):
                idx_s = int(sub_data[vox_s[0], vox_s[1], vox_s[2]])
                if 0 < idx_s < len(sub_labels):
                    sub_lbl = sub_labels[idx_s]
                    # Skip generic labels
                    if sub_lbl not in ("Left Cerebral White Matter",
                                       "Right Cerebral White Matter",
                                       "Left Cerebral Cortex",
                                       "Right Cerebral Cortex",
                                       "Left Lateral Ventricle",
                                       "Right Lateral Ventricle"):
                        label = f"Sub_{sub_lbl}"

        assignments.append(label if label else "unassigned")

    coords["region_assigned"] = assignments

    n_assigned = sum(1 for a in assignments if a != "unassigned")
    n_total = len(assignments)
    print(f"  Assigned {n_assigned}/{n_total} peaks ({n_assigned/n_total*100:.0f}%) to atlas regions")

    # Show assignment distribution
    region_counts = pd.Series(assignments).value_counts()
    n_regions = (region_counts.index != "unassigned").sum()
    print(f"  Unique regions hit: {n_regions}")
    if "unassigned" in region_counts:
        print(f"  Unassigned: {region_counts['unassigned']} peaks")

    return coords


def build_study_profiles(coords: pd.DataFrame) -> pd.DataFrame:
    """Build peak-density vectors per study (proportional counts per region)."""
    assigned = coords[coords["region_assigned"] != "unassigned"].copy()

    # Pivot: rows=pmid, columns=regions, values=count
    profiles = assigned.groupby(["pmid", "region_assigned"]).size().unstack(fill_value=0)

    # Normalize to proportional density (peaks per region / total peaks)
    row_sums = profiles.sum(axis=1)
    profiles_norm = profiles.div(row_sums.replace(0, 1), axis=0)

    print(f"  Study profiles: {profiles_norm.shape[0]} studies x {profiles_norm.shape[1]} regions")
    return profiles_norm


def compute_network_summaries(profiles: pd.DataFrame) -> pd.DataFrame:
    """Aggregate region profiles into canonical network scores."""
    network_scores = {}

    for network, keywords in NETWORK_MAP.items():
        matching_cols = [
            col for col in profiles.columns
            if any(kw in col for kw in keywords)
        ]
        if matching_cols:
            network_scores[network] = profiles[matching_cols].sum(axis=1)
        else:
            network_scores[network] = 0.0

    df = pd.DataFrame(network_scores, index=profiles.index)
    print(f"  Network summaries: {df.shape[0]} studies x {df.shape[1]} networks")
    return df


def compute_neural_distances(profiles: pd.DataFrame) -> pd.DataFrame:
    """Compute pairwise correlation distance between study neural profiles."""
    studies = profiles.index.tolist()
    n = len(studies)
    values = profiles.values.astype(float)

    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            vi, vj = values[i], values[j]
            if vi.std() == 0 or vj.std() == 0:
                dist_matrix[i, j] = dist_matrix[j, i] = 1.0
            else:
                r = np.corrcoef(vi, vj)[0, 1]
                dist_matrix[i, j] = dist_matrix[j, i] = 1.0 - r

    return pd.DataFrame(dist_matrix, index=studies, columns=studies)


def main():
    config.OUT_NEURAL.mkdir(parents=True, exist_ok=True)

    print("Step 05: Neural Response-Space Construction")
    print("=" * 60)

    print("\n[1] Loading atlas...")
    atlas = load_atlas()

    print("\n[2] Loading coordinates...")
    coords = load_coordinates()

    print("\n[3] Assigning peaks to brain regions...")
    coords = assign_peaks_to_regions(coords, atlas)

    print("\n[4] Building study-level neural profiles...")
    profiles = build_study_profiles(coords)

    print("\n[5] Computing network summaries...")
    networks = compute_network_summaries(profiles)

    print("\n[6] Computing neural distances...")
    distances = compute_neural_distances(profiles)
    print(f"  Distance matrix: {distances.shape[0]} x {distances.shape[1]}")

    # Save
    profiles.to_csv(config.OUT_NEURAL / "neural_feature_matrix.csv")
    networks.to_csv(config.OUT_NEURAL / "network_summary_scores.csv")
    distances.to_csv(config.OUT_NEURAL / "neural_distance_matrix.csv")
    coords.to_csv(config.OUT_NEURAL / "coordinates_with_assignments.csv", index=False)

    print(f"\n  Summary:")
    print(f"    Studies: {len(profiles)}")
    print(f"    Regions: {profiles.shape[1]}")
    print(f"    Networks: {networks.shape[1]}")

    print(f"\n  Network mean peak density:")
    for col in networks.columns:
        print(f"    {col}: {networks[col].mean():.3f}")

    print(f"\n  Done. Results in: {config.OUT_NEURAL}")


if __name__ == "__main__":
    main()
