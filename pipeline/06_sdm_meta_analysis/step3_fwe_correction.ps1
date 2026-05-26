# ==============================================================
# Step 3: FWE Correction (perm)  -- Windows / PowerShell port
#
# Runs permutation-based family-wise error correction.
# This is the MOST EXPENSIVE step -- hours per analysis with 5000 perms.
# Requires Step 2 (mean analysis) to be complete.
# Produces: analysis_<name>_mean\corrp_tfce.nii.gz
#
# Usage:
#   .\step3_fwe_correction.ps1                       # all analyses
#   .\step3_fwe_correction.ps1 -Analysis sham_gt_rest
#   .\step3_fwe_correction.ps1 -DryRun               # show plan
#   .\step3_fwe_correction.ps1 -Force                # rerun even if done
# ==============================================================
[CmdletBinding()]
param(
    [string]$Analysis,
    [switch]$DryRun,
    [switch]$Force,
    [string]$Sdm,
    [int]$Permutations         # override config default (e.g. for a quick smoke test)
)

. "$PSScriptRoot\sdm_config.ps1"

$StepName = "perm"
$LogFile  = Join-Path $LogDir ("step3_fwe_{0}.log" -f (Get-Date -Format 'yyyyMMdd_HHmmss'))

function Invoke-FweCorrection {
    param([string]$Name)
    $dir = Join-Path $ProjectDir $Name

    if (-not (Test-SdmName $Name)) { return $false }
    if (-not (Test-Path $dir)) { Write-SdmLog "  SKIP: $dir does not exist"; return $false }

    # Prerequisite: mean analysis
    $meanOutput = Join-Path $dir ("analysis_{0}_mean\{0}_mean_z.nii.gz" -f $Name)
    if (-not (Test-SdmDone $dir "mi")) {
        if ((Test-Path $meanOutput) -and ((Get-Item $meanOutput).Length -gt 0)) {
            Write-SdmLog "  NOTE: $Name -- mean output exists but no sentinel. Marking mi done."
            Set-SdmDone $dir "mi"
        } else {
            Write-SdmLog "  ERROR: $Name -- mean analysis not complete. Run step2 first."
            return $false
        }
    }

    if ($Force) { Reset-SdmStep $dir $StepName $Name }   # delete FWE output (keeps mean_z) + sentinel

    $fweOutput = Join-Path $dir ("analysis_{0}_mean\corrp_tfce.nii.gz" -f $Name)

    if (Test-SdmDone $dir $StepName) {
        Write-SdmLog "  SKIP: $Name -- already done (sentinel found). Use -Force to rerun."
        return $true
    }

    # No sentinel => not trusted. Clear any fragmented FWE output, run clean.
    $fweDir = Join-Path $dir ("analysis_{0}_mean\fwe" -f $Name)
    if ((Test-Path $fweDir) -or ((Test-Path $fweOutput) -and ((Get-Item $fweOutput).Length -gt 0))) {
        Write-SdmLog "  $Name -- no sentinel; clearing fragmented FWE output before rerun."
        Reset-SdmStep $dir $StepName $Name
    }

    $n = Get-StudyCount $dir
    Write-SdmLog "  FWE correction: $Name ($n studies, $Permutations permutations, $NThreads threads)..."
    Write-SdmLog "  This may take a long time..."
    if (-not (Invoke-Sdm $dir ("perm {0}_mean,{1},{2}" -f $Name, $Permutations, $NThreads))) {
        Write-SdmLog "  ERROR: FWE failed for $Name"
        return $false
    }

    if ((-not $DryRun) -and (-not ((Test-Path $fweOutput) -and ((Get-Item $fweOutput).Length -gt 0)))) {
        Write-SdmLog "  ERROR: FWE completed but output missing: $fweOutput"
        return $false
    }

    Set-SdmDone $dir $StepName
    Write-SdmLog "  DONE: $Name"
    return $true
}

# --- Main ---
Test-SdmPrereq

Write-SdmLog "============================================================"
Write-SdmLog "STEP 3: FWE Correction (perm, $Permutations permutations)"
Write-SdmLog "============================================================"
if ($DryRun) { Write-SdmLog "*** DRY RUN ***" }
if ($Force)  { Write-SdmLog "*** FORCE MODE ***" }
Write-SdmLog ""

if ($Analysis) {
    if (Invoke-FweCorrection $Analysis) { exit 0 } else { exit 1 }
}

$completed = 0; $failed = 0
foreach ($name in $AllAnalyses) {
    if (Invoke-FweCorrection $name) { $completed++ } else { $failed++ }
}

Write-SdmLog ""
Write-SdmLog "Step 3 complete: $completed ok, $failed failed"
if ($failed -gt 0) { exit 1 } else { exit 0 }
