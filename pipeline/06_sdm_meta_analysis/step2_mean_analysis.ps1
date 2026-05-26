# ==============================================================
# Step 2: Mean Analysis (mi)  -- Windows / PowerShell port
#
# Runs multiple-imputation mean analysis for each contrast.
# Requires Step 1 (preprocessing) to be complete.
# Produces: analysis_<name>_mean\<name>_mean_z.nii.gz
#
# Usage:
#   .\step2_mean_analysis.ps1                       # all analyses
#   .\step2_mean_analysis.ps1 -Analysis sham_gt_rest
#   .\step2_mean_analysis.ps1 -DryRun               # show plan
#   .\step2_mean_analysis.ps1 -Force                # rerun even if done
# ==============================================================
[CmdletBinding()]
param(
    [string]$Analysis,
    [switch]$DryRun,
    [switch]$Force,
    [string]$Sdm
)

. "$PSScriptRoot\sdm_config.ps1"

$StepName = "mi"
$LogFile  = Join-Path $LogDir ("step2_mean_{0}.log" -f (Get-Date -Format 'yyyyMMdd_HHmmss'))

function Invoke-MeanAnalysis {
    param([string]$Name)
    $dir = Join-Path $ProjectDir $Name

    if (-not (Test-SdmName $Name)) { return $false }
    if (-not (Test-Path $dir)) { Write-SdmLog "  SKIP: $dir does not exist"; return $false }

    # Prerequisite: preprocessing
    if (-not (Test-SdmDone $dir "pp")) {
        if ((Test-Path (Join-Path $dir "pp")) -and (Test-Path (Join-Path $dir "sdmpsi_params.xml"))) {
            Write-SdmLog "  NOTE: $Name -- preprocessing output exists but no sentinel. Marking pp done."
            Set-SdmDone $dir "pp"
        } else {
            Write-SdmLog "  ERROR: $Name -- preprocessing not complete. Run step1 first."
            return $false
        }
    }

    if ($Force) { Remove-Item (Join-Path $dir ".$StepName.done") -Force -ErrorAction SilentlyContinue }

    $meanOutput = Join-Path $dir ("analysis_{0}_mean\{0}_mean_z.nii.gz" -f $Name)

    if (Test-SdmDone $dir $StepName) {
        Write-SdmLog "  SKIP: $Name -- already done (sentinel found). Use -Force to rerun."
        return $true
    }

    if ((Test-Path $meanOutput) -and ((Get-Item $meanOutput).Length -gt 0)) {
        Write-SdmLog "  $Name -- output exists from prior run, marking done."
        Set-SdmDone $dir $StepName
        return $true
    }

    # Clean up any partial previous run
    $analysisDir = Join-Path $dir ("analysis_{0}_mean" -f $Name)
    if (Test-Path $analysisDir) {
        Write-SdmLog "  $Name -- cleaning up partial previous run..."
        Remove-Item $analysisDir -Recurse -Force
    }

    $n = Get-StudyCount $dir
    Write-SdmLog "  Mean analysis: $Name ($n studies, $Imputations imputations)..."
    if (-not (Invoke-Sdm $dir ("{0}_mean = mi {1}" -f $Name, $Imputations))) {
        Write-SdmLog "  ERROR: Mean analysis failed for $Name"; return $false
    }

    if ((-not $DryRun) -and (-not ((Test-Path $meanOutput) -and ((Get-Item $meanOutput).Length -gt 0)))) {
        Write-SdmLog "  ERROR: Mean analysis completed but output missing: $meanOutput"
        return $false
    }

    Set-SdmDone $dir $StepName
    Write-SdmLog "  DONE: $Name"
    return $true
}

# --- Main ---
Test-SdmPrereq

Write-SdmLog "============================================================"
Write-SdmLog "STEP 2: Mean Analysis (mi, $Imputations imputations)"
Write-SdmLog "============================================================"
if ($DryRun) { Write-SdmLog "*** DRY RUN ***" }
if ($Force)  { Write-SdmLog "*** FORCE MODE ***" }
Write-SdmLog ""

if ($Analysis) {
    if (Invoke-MeanAnalysis $Analysis) { exit 0 } else { exit 1 }
}

$completed = 0; $failed = 0
foreach ($name in $AllAnalyses) {
    if (Invoke-MeanAnalysis $name) { $completed++ } else { $failed++ }
}

Write-SdmLog ""
Write-SdmLog "Step 2 complete: $completed ok, $failed failed"
if ($failed -gt 0) { exit 1 } else { exit 0 }
