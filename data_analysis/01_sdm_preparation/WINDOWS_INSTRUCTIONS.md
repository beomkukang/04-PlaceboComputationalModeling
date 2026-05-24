# Running SDM-PSI on Windows

## Setup

### 1. Download SDM-PSI for Windows
- Go to https://www.sdmproject.com/software/
- Download the Windows 64-bit version
- Extract to `C:\SDM\` (or wherever you prefer)

### 2. Pull this repo
```powershell
git pull
```

### 3. Navigate to the project
```powershell
cd data_analysis\01_sdm_preparation\sdm_projects\sham_gt_rest
```

## Run SDM-PSI (PowerShell)

Set the SDM path (adjust if you extracted elsewhere):
```powershell
$SDM = "C:\SDM\SdmPsiGui-win64-v6.23\sdm.bat"
```

### Step 1: Preprocessing (~10 min)
```powershell
& $SDM pp gray_matter,1.0,20,gray_matter,2
```
- Creates `pp/` folder with brain images
- Check `pp/pp.htm` to verify peak locations

### Step 2: Mean analysis (~10-30 min)
```powershell
& $SDM "sham_gt_rest_mean = mi 50"
```
- 50 imputations, random-effects model
- Creates `analysis_sham_gt_rest_mean/` folder

### Step 3: FWE correction (~1-3 hours)
```powershell
& $SDM "perm sham_gt_rest_mean,1000,6"
```
- 1000 permutations, 6 threads
- Adjust thread count based on your CPU cores
- Creates `corrp_tfce.nii.gz` (TFCE-corrected p-values)

### Step 4: Threshold
```powershell
& $SDM "threshold analysis_sham_gt_rest_mean/corrp_tfce,analysis_sham_gt_rest_mean/sham_gt_rest_mean_z,0.05,10"
```
- p < 0.05 FWE-corrected, minimum 10 voxels
- Opens MRIcron automatically to display results
- Creates results HTML with coordinates and brain regions

## Run all analyses

Repeat Steps 1-4 for each directory:
```
sham_gt_rest               (PRIMARY - 21 studies)
verum_gt_sham              (PRIMARY - 39 studies)
verum_gt_rest              (PRIMARY - 31 studies)
sham_gt_rest_penetrating   (SUBGROUP - 11 studies)
sham_gt_rest_nonpenetrating (SUBGROUP - 9 studies)
verum_post_gt_pre          (SECONDARY - 50 studies)
sham_post_gt_pre           (SECONDARY - 18 studies)
deactivation               (SECONDARY - 51 studies)
group_comparison           (EXPLORATORY - 53 studies)
correlation_clinical       (EXPLORATORY - 12 studies)
```

### Batch script (run all at once):
Save as `run_all.bat` in the `sdm_projects` folder:
```batch
@echo off
set SDM=C:\SDM\SdmPsiGui-win64-v6.23\sdm.bat

for %%d in (sham_gt_rest verum_gt_sham verum_gt_rest sham_gt_rest_penetrating sham_gt_rest_nonpenetrating verum_post_gt_pre sham_post_gt_pre deactivation group_comparison correlation_clinical) do (
    echo ============================================================
    echo Running: %%d
    echo ============================================================
    cd %%d
    call %SDM% pp gray_matter,1.0,20,gray_matter,2
    call %SDM% "%%d_mean = mi 50"
    call %SDM% "perm %%d_mean,1000,6"
    call %SDM% "threshold analysis_%%d_mean/corrp_tfce,analysis_%%d_mean/%%d_mean_z,0.05,10"
    cd ..
)
echo DONE
```

## After running

### Copy results back to Mac
Push from Windows:
```powershell
git add -A
git commit -m "SDM-PSI results from Windows"
git push
```

Then pull on Mac:
```bash
git pull
```

### Key output files per analysis:
- `analysis_*_mean/*_z.nii.gz` — z-value map (unthresholded)
- `analysis_*_mean/corrp_tfce.nii.gz` — TFCE-corrected p-values
- `analysis_*_mean/*_tfceCorrected_*.nii.gz` — thresholded significant clusters
- `analysis_*_mean/*_tfceCorrected_*.htm` — results table (open in browser)

## Meta-regression (tissue level)

After sham_gt_rest completes:
```powershell
cd sham_gt_rest
& $SDM "penetration_effect = lm_mi tissue_level,0+1,50"
& $SDM "perm penetration_effect,1000,6"
& $SDM "threshold analysis_penetration_effect/corrp_tfce,analysis_penetration_effect/penetration_effect_z,0.05,10"
```

## Parameters used
- Modality: fMRI-BOLD
- Template: gray matter
- FWHM: 20mm
- Anisotropy: 1.0
- Voxel size: 2mm
- Imputations: 50
- Permutations: 1000 (use 5000 for publication)
- Threshold: p < 0.05 FWE (TFCE), k ≥ 10
