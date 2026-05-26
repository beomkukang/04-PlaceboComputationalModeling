# ==============================================================
# Step 4: Thresholding  -- Windows / PowerShell port
#
# Applies FWE-corrected threshold to produce final result maps.
# Requires Step 3 (FWE correction) to be complete.
# This step is fast and always reruns (parameters may change).
#
# Usage:
#   .\step4_thresholding.ps1                       # all analyses
#   .\step4_thresholding.ps1 -Analysis sham_gt_rest
#   .\step4_thresholding.ps1 -DryRun               # show plan
# ==============================================================
[CmdletBinding()]
param(
    [string]$Analysis,
    [switch]$DryRun,
    [switch]$Force,
    [string]$Sdm
)

. "$PSScriptRoot\sdm_config.ps1"

$StepName = "threshold"
$LogFile  = Join-Path $LogDir ("step4_threshold_{0}.log" -f (Get-Date -Format 'yyyyMMdd_HHmmss'))

function Invoke-Thresholding {
    param([string]$Name)
    $dir = Join-Path $ProjectDir $Name

    if (-not (Test-SdmName $Name)) { return $false }
    if (-not (Test-Path $dir)) { Write-SdmLog "  SKIP: $dir does not exist"; return $false }

    # Prerequisite: FWE correction
    $fweOutput = Join-Path $dir ("analysis_{0}_mean\corrp_tfce.nii.gz" -f $Name)
    if (-not (Test-SdmDone $dir "perm")) {
        if ((Test-Path $fweOutput) -and ((Get-Item $fweOutput).Length -gt 0)) {
            Write-SdmLog "  NOTE: $Name -- FWE output exists but no sentinel. Marking perm done."
            Set-SdmDone $dir "perm"
        } else {
            Write-SdmLog "  ERROR: $Name -- FWE correction not complete. Run step3 first."
            return $false
        }
    }

    if ($Force) { Reset-SdmStep $dir $StepName $Name }   # clear stale thresholded maps + sentinel

    Write-SdmLog "  Thresholding: $Name (p<$PThreshold, k>=$VoxelExtent)..."
    $cmd = "threshold analysis_{0}_mean/corrp_tfce,analysis_{0}_mean/{0}_mean_z,{1},{2}" -f $Name, $PThreshold, $VoxelExtent
    if (-not (Invoke-Sdm $dir $cmd)) {
        Write-SdmLog "  WARNING: Thresholding may have failed for $Name"
        return $false
    }

    Set-SdmDone $dir $StepName
    Write-SdmLog "  DONE: $Name"
    return $true
}

# --- Main ---
Test-SdmPrereq

Write-SdmLog "============================================================"
Write-SdmLog "STEP 4: Thresholding (p<$PThreshold, k>=$VoxelExtent)"
Write-SdmLog "============================================================"
if ($DryRun) { Write-SdmLog "*** DRY RUN ***" }
Write-SdmLog ""

if ($Analysis) {
    if (Invoke-Thresholding $Analysis) { exit 0 } else { exit 1 }
}

$completed = 0; $failed = 0
foreach ($name in $AllAnalyses) {
    if (Invoke-Thresholding $name) { $completed++ } else { $failed++ }
}

Write-SdmLog ""
Write-SdmLog "Step 4 complete: $completed ok, $failed failed"
if ($failed -gt 0) { exit 1 } else { exit 0 }
