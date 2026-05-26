# Running Remaining SDM-PSI Steps on Windows

## Current status (as of 2026-05-26)

All preprocessing (step 1) is complete. Mean analysis (step 2) is complete for 7/10 analyses.

| Analysis | Studies | Step 1 (pp) | Step 2 (mi) | Step 3 (perm) | Step 4 (thr) |
|---|---|---|---|---|---|
| sham_gt_rest | 20 | DONE | DONE | — | — |
| verum_gt_sham | 38 | DONE | DONE | — | — |
| verum_gt_rest | 30 | DONE | DONE | — | — |
| sham_gt_rest_penetrating | 10 | DONE | DONE | — | — |
| sham_gt_rest_nonpenetrating | 8 | DONE | DONE | — | — |
| verum_post_gt_pre | 49 | DONE | DONE | — | — |
| sham_post_gt_pre | 17 | DONE | DONE | — | — |
| **deactivation** | **50** | DONE | **TODO** | — | — |
| **group_comparison** | **51** | DONE | **TODO** | — | — |
| **correlation_clinical** | **10** | DONE | **TODO** | — | — |
| penetration_effect (meta-reg) | — | — | **TODO** | — | — |

## What you need to do on Windows

1. **Step 2** — Mean analysis for 3 remaining analyses (deactivation, group_comparison, correlation_clinical)
2. **Step 3** — FWE correction (5000 permutations) for ALL 10 analyses
3. **Step 4** — Thresholding for ALL 10 analyses
4. **Step 5** — Meta-regression (penetration_effect on sham_gt_rest)

---

## Setup

### 1. Install SDM-PSI for Windows
- Download from https://www.sdmproject.com/software/ (Windows 64-bit)
- Extract to `C:\SDM\` (or wherever you prefer)

### 2. Clone or copy the repo to Windows
Copy the entire `pipeline/06_sdm_meta_analysis/sdm_projects/` folder to the Windows machine. The `pp/` directories and existing `analysis_*/` folders must be included — they contain results from completed steps.

### 3. Open PowerShell and set SDM path
```powershell
$SDM = "C:\SDM\SdmPsiGui-win64-v6.23\sdm.bat"
$PROJECTS = "C:\path\to\sdm_projects"
```

---

## Step 2: Mean analysis (3 remaining)

These 3 analyses failed on Mac due to 8GB RAM limit. Windows needs ≥12GB RAM for the large analyses.

```powershell
# deactivation (50 studies, 50 imputations)
cd "$PROJECTS\deactivation"
& $SDM "deactivation_mean = mi 50"

# group_comparison (51 studies, 50 imputations)
cd "$PROJECTS\group_comparison"
& $SDM "group_comparison_mean = mi 50"

# correlation_clinical (10 studies, 50 imputations)
cd "$PROJECTS\correlation_clinical"
& $SDM "correlation_clinical_mean = mi 50"
```

If deactivation or group_comparison still crash (OOM), reduce to 20 imputations:
```powershell
& $SDM "deactivation_mean = mi 20"
```

**Verify:** Each directory should now have `analysis_{name}_mean/{name}_mean_z.nii.gz`.

---

## Step 3: FWE correction (all 10 analyses)

5000 permutations, publication-grade. Adjust thread count to your CPU cores (e.g., 6 for 8-core, 10 for 12-core).

```powershell
$THREADS = 6
$PERMS = 5000

# --- 7 already have mean analysis ---
cd "$PROJECTS\sham_gt_rest"
& $SDM "perm sham_gt_rest_mean,$PERMS,$THREADS"

cd "$PROJECTS\verum_gt_sham"
& $SDM "perm verum_gt_sham_mean,$PERMS,$THREADS"

cd "$PROJECTS\verum_gt_rest"
& $SDM "perm verum_gt_rest_mean,$PERMS,$THREADS"

cd "$PROJECTS\sham_gt_rest_penetrating"
& $SDM "perm sham_gt_rest_penetrating_mean,$PERMS,$THREADS"

cd "$PROJECTS\sham_gt_rest_nonpenetrating"
& $SDM "perm sham_gt_rest_nonpenetrating_mean,$PERMS,$THREADS"

cd "$PROJECTS\verum_post_gt_pre"
& $SDM "perm verum_post_gt_pre_mean,$PERMS,$THREADS"

cd "$PROJECTS\sham_post_gt_pre"
& $SDM "perm sham_post_gt_pre_mean,$PERMS,$THREADS"

# --- 3 from step 2 above ---
cd "$PROJECTS\deactivation"
& $SDM "perm deactivation_mean,$PERMS,$THREADS"

cd "$PROJECTS\group_comparison"
& $SDM "perm group_comparison_mean,$PERMS,$THREADS"

cd "$PROJECTS\correlation_clinical"
& $SDM "perm correlation_clinical_mean,$PERMS,$THREADS"
```

**Time estimate:** ~1-3 hours per analysis at 5000 permutations. Run overnight if needed.

**Verify:** Each directory should now have `analysis_{name}_mean/corrp_tfce.nii.gz`.

---

## Step 4: Thresholding (all 10 analyses)

p < 0.05 FWE-corrected, minimum cluster extent 10 voxels.

```powershell
cd "$PROJECTS\sham_gt_rest"
& $SDM "threshold analysis_sham_gt_rest_mean/corrp_tfce,analysis_sham_gt_rest_mean/sham_gt_rest_mean_z,0.05,10"

cd "$PROJECTS\verum_gt_sham"
& $SDM "threshold analysis_verum_gt_sham_mean/corrp_tfce,analysis_verum_gt_sham_mean/verum_gt_sham_mean_z,0.05,10"

cd "$PROJECTS\verum_gt_rest"
& $SDM "threshold analysis_verum_gt_rest_mean/corrp_tfce,analysis_verum_gt_rest_mean/verum_gt_rest_mean_z,0.05,10"

cd "$PROJECTS\sham_gt_rest_penetrating"
& $SDM "threshold analysis_sham_gt_rest_penetrating_mean/corrp_tfce,analysis_sham_gt_rest_penetrating_mean/sham_gt_rest_penetrating_mean_z,0.05,10"

cd "$PROJECTS\sham_gt_rest_nonpenetrating"
& $SDM "threshold analysis_sham_gt_rest_nonpenetrating_mean/corrp_tfce,analysis_sham_gt_rest_nonpenetrating_mean/sham_gt_rest_nonpenetrating_mean_z,0.05,10"

cd "$PROJECTS\verum_post_gt_pre"
& $SDM "threshold analysis_verum_post_gt_pre_mean/corrp_tfce,analysis_verum_post_gt_pre_mean/verum_post_gt_pre_mean_z,0.05,10"

cd "$PROJECTS\sham_post_gt_pre"
& $SDM "threshold analysis_sham_post_gt_pre_mean/corrp_tfce,analysis_sham_post_gt_pre_mean/sham_post_gt_pre_mean_z,0.05,10"

cd "$PROJECTS\deactivation"
& $SDM "threshold analysis_deactivation_mean/corrp_tfce,analysis_deactivation_mean/deactivation_mean_z,0.05,10"

cd "$PROJECTS\group_comparison"
& $SDM "threshold analysis_group_comparison_mean/corrp_tfce,analysis_group_comparison_mean/group_comparison_mean_z,0.05,10"

cd "$PROJECTS\correlation_clinical"
& $SDM "threshold analysis_correlation_clinical_mean/corrp_tfce,analysis_correlation_clinical_mean/correlation_clinical_mean_z,0.05,10"
```

**Verify:** Each directory should have `analysis_{name}_mean/*_tfceCorrected_*.htm` (open in browser to see results).

---

## Step 5: Meta-regression (penetration_effect)

Tests whether tissue penetration level moderates sham neural responses.

```powershell
cd "$PROJECTS\sham_gt_rest"

# Linear model (50 imputations)
& $SDM "penetration_effect = mi_lm tissue_level,0+1,50"

# FWE correction
& $SDM "perm penetration_effect,$PERMS,$THREADS"

# Threshold
& $SDM "threshold analysis_penetration_effect/corrp_tfce,analysis_penetration_effect/penetration_effect_z,0.05,10"
```

---

## Batch script (run everything at once)

Save as `run_remaining.ps1` in the `sdm_projects` folder:

```powershell
$SDM = "C:\SDM\SdmPsiGui-win64-v6.23\sdm.bat"
$THREADS = 6
$PERMS = 5000
$MI = 50

# --- Step 2: Mean analysis for 3 remaining ---
$step2 = @("deactivation", "group_comparison", "correlation_clinical")
foreach ($name in $step2) {
    Write-Host "========== Step 2: $name =========="
    Set-Location $name
    & $SDM "$($name)_mean = mi $MI"
    Set-Location ..
}

# --- Step 3: FWE correction for all 10 ---
$all = @("sham_gt_rest", "verum_gt_sham", "verum_gt_rest",
         "sham_gt_rest_penetrating", "sham_gt_rest_nonpenetrating",
         "verum_post_gt_pre", "sham_post_gt_pre",
         "deactivation", "group_comparison", "correlation_clinical")
foreach ($name in $all) {
    Write-Host "========== Step 3: $name =========="
    Set-Location $name
    & $SDM "perm $($name)_mean,$PERMS,$THREADS"
    Set-Location ..
}

# --- Step 4: Thresholding for all 10 ---
foreach ($name in $all) {
    Write-Host "========== Step 4: $name =========="
    Set-Location $name
    & $SDM "threshold analysis_$($name)_mean/corrp_tfce,analysis_$($name)_mean/$($name)_mean_z,0.05,10"
    Set-Location ..
}

# --- Step 5: Meta-regression ---
Write-Host "========== Step 5: penetration_effect =========="
Set-Location sham_gt_rest
& $SDM "penetration_effect = mi_lm tissue_level,0+1,$MI"
& $SDM "perm penetration_effect,$PERMS,$THREADS"
& $SDM "threshold analysis_penetration_effect/corrp_tfce,analysis_penetration_effect/penetration_effect_z,0.05,10"
Set-Location ..

Write-Host "========== ALL DONE =========="
```

Run with:
```powershell
cd C:\path\to\sdm_projects
.\run_remaining.ps1
```

---

## After running: copy results back

### Key output files per analysis
- `analysis_*_mean/*_mean_z.nii.gz` — z-value map (unthresholded)
- `analysis_*_mean/corrp_tfce.nii.gz` — TFCE-corrected p-values
- `analysis_*_mean/*_tfceCorrected_*.nii.gz` — thresholded clusters
- `analysis_*_mean/*_tfceCorrected_*.htm` — results table (open in browser)
- `analysis_penetration_effect/` — meta-regression results (same file types)

### Transfer back to Mac
Push from Windows:
```powershell
git add -A
git commit -m "SDM-PSI results from Windows (steps 2-5)"
git push
```

Then pull on Mac:
```bash
git pull
```

Or manually copy the `sdm_projects/` folder back if not using git for large files.

---

## Parameters

| Parameter | Value |
|---|---|
| Modality | fMRI-BOLD |
| Template | gray matter |
| FWHM | 20mm |
| Anisotropy | 1.0 |
| Voxel size | 2mm |
| Imputations | 50 (or 20 if OOM) |
| Permutations | 5000 |
| Threshold | p < 0.05 FWE (TFCE), k ≥ 10 |
