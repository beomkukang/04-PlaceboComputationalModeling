# ==============================================================
# Step 5: Meta-Regression  -- Windows / PowerShell port
#
# Runs meta-regression of tissue_level on sham_gt_rest
# (penetration_effect analysis).
# Requires sham_gt_rest preprocessing (step1) to be complete.
#
# This step runs its own pipeline: linear model -> FWE -> threshold.
#
# Usage:
#   .\step5_meta_regression.ps1               # run
#   .\step5_meta_regression.ps1 -DryRun       # show plan
#   .\step5_meta_regression.ps1 -Force        # rerun all sub-steps
# ==============================================================
[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$Force,
    [string]$Sdm
)

. "$PSScriptRoot\sdm_config.ps1"

# Meta-regression configuration
$BaseAnalysis = "sham_gt_rest"
$Covariate    = "tissue_level"
$RegName      = "penetration_effect"

$LogFile = Join-Path $LogDir ("step5_meta_regression_{0}.log" -f (Get-Date -Format 'yyyyMMdd_HHmmss'))

# --- Main ---
Test-SdmPrereq

$dir = Join-Path $ProjectDir $BaseAnalysis

Write-SdmLog "============================================================"
Write-SdmLog "STEP 5: Meta-Regression ($RegName)"
Write-SdmLog "  Base: $BaseAnalysis"
Write-SdmLog "  Covariate: $Covariate"
Write-SdmLog "  Imputations: $Imputations, Permutations: $Permutations"
Write-SdmLog "============================================================"
if ($DryRun) { Write-SdmLog "*** DRY RUN ***" }
if ($Force)  { Write-SdmLog "*** FORCE MODE ***" }
Write-SdmLog ""

# Validate prerequisites
if (-not (Test-Path (Join-Path $dir "pp"))) {
    Write-SdmLog "ERROR: Preprocessing not done for $BaseAnalysis. Run step1 first."
    exit 1
}

$table = Join-Path $dir "sdm_table.txt"
if (-not (Test-Path $table)) {
    Write-SdmLog "ERROR: sdm_table.txt not found in $dir"
    exit 1
}

# Validate covariate exists in sdm_table.txt header (whole-word match)
$header = Get-Content $table -TotalCount 1
if ($header -notmatch "\b$Covariate\b") {
    Write-SdmLog "ERROR: Covariate '$Covariate' not found in sdm_table.txt columns: $header"
    exit 1
}

$lmDone      = Join-Path $dir ".mr_${RegName}_lm.done"
$permDone    = Join-Path $dir ".mr_${RegName}_perm.done"
$threshDone  = Join-Path $dir ".mr_${RegName}_threshold.done"
$regAnalysis = Join-Path $dir ("analysis_{0}" -f $RegName)

if ($Force) {
    # Truly force: drop all sub-sentinels and the whole regression analysis dir.
    Remove-Item $lmDone, $permDone, $threshDone -Force -ErrorAction SilentlyContinue
    if (-not $DryRun) { Remove-Item $regAnalysis -Recurse -Force -ErrorAction SilentlyContinue }
}

# Sub-step 1: Linear model
if (Test-Path $lmDone) {
    Write-SdmLog "  [1/3] Linear model -- skipping (sentinel found)."
} else {
    # No sentinel => not trusted. Clear any previous/partial regression output.
    if ((-not $DryRun) -and (Test-Path $regAnalysis)) {
        Write-SdmLog "  [1/3] no sentinel; clearing previous regression output before rerun."
        Remove-Item $regAnalysis -Recurse -Force -ErrorAction SilentlyContinue
    }
    Write-SdmLog "  [1/3] Linear model ($Imputations imputations)..."
    if (-not (Invoke-Sdm $dir ("{0} = mi_lm {1},0+1,{2}" -f $RegName, $Covariate, $Imputations))) {
        Write-SdmLog "  ERROR: Linear model failed"
        exit 1
    }
    if (-not $DryRun) { New-Item -ItemType File -Path $lmDone -Force | Out-Null }
    Write-SdmLog "  [1/3] Done."
}

# Sub-step 2: FWE correction
if (Test-Path $permDone) {
    Write-SdmLog "  [2/3] FWE correction -- skipping (sentinel found)."
} else {
    $fweDir = Join-Path $dir ("analysis_{0}\fwe" -f $RegName)
    if (Test-Path $fweDir) { Remove-Item $fweDir -Recurse -Force -ErrorAction SilentlyContinue }
    Write-SdmLog "  [2/3] FWE correction ($Permutations permutations, $NThreads threads)..."
    Write-SdmLog "  This may take a long time..."
    if (-not (Invoke-Sdm $dir ("perm {0},{1},{2}" -f $RegName, $Permutations, $NThreads))) {
        Write-SdmLog "  ERROR: FWE correction failed"
        exit 1
    }
    if (-not $DryRun) { New-Item -ItemType File -Path $permDone -Force | Out-Null }
    Write-SdmLog "  [2/3] Done."
}

# Sub-step 3: Thresholding (always rerun)
Write-SdmLog "  [3/3] Thresholding (p<$PThreshold, k>=$VoxelExtent)..."
$cmd = "threshold analysis_{0}/corrp_tfce,analysis_{0}/{0}_z,{1},{2}" -f $RegName, $PThreshold, $VoxelExtent
if (-not (Invoke-Sdm $dir $cmd)) {
    Write-SdmLog "  ERROR: Thresholding failed"
    exit 1
}
if (-not $DryRun) { New-Item -ItemType File -Path $threshDone -Force | Out-Null }
Write-SdmLog "  [3/3] Done."

Write-SdmLog ""
Write-SdmLog "STEP 5 COMPLETE: $RegName"
Write-SdmLog "  Results: $dir\analysis_$RegName\"
Write-SdmLog "============================================================"
