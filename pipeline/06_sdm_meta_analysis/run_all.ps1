# ==============================================================
# SDM-PSI Production Pipeline -- Orchestrator (Windows / PowerShell)
#
# PowerShell port of production_sdm.sh. Runs all 5 steps in sequence.
# For step-by-step control, run the individual scripts directly:
#
#   .\step1_preprocessing.ps1   [-Analysis name] [-DryRun] [-Force]
#   .\step2_mean_analysis.ps1   [-Analysis name] [-DryRun] [-Force]
#   .\step3_fwe_correction.ps1  [-Analysis name] [-DryRun] [-Force]
#   .\step4_thresholding.ps1    [-Analysis name] [-DryRun]
#   .\step5_meta_regression.ps1                  [-DryRun] [-Force]
#
# Or run everything at once:
#   .\run_all.ps1                # all steps, all analyses
#   .\run_all.ps1 -DryRun        # show plan
#   .\run_all.ps1 -Force         # rerun everything
#   .\run_all.ps1 -Sdm C:\path\sdm.bat
#
# All scripts share configuration from sdm_config.ps1.
#
# NOTE: Step 1 (preprocessing) is required and is NOT pre-done in a
# fresh git checkout -- the pp/ outputs are gitignored. This pipeline
# regenerates everything from the *_mni.txt / sdm_table.txt inputs.
# ==============================================================
[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$Force,
    [string]$Sdm
)

$ErrorActionPreference = "Stop"

# Flags forwarded to each step script
$flags = @{}
if ($DryRun) { $flags.DryRun = $true }
if ($Force)  { $flags.Force  = $true }
if ($Sdm)    { $flags.Sdm    = $Sdm }

$steps = @(
    "step1_preprocessing.ps1"
    "step2_mean_analysis.ps1"
    "step3_fwe_correction.ps1"
    "step4_thresholding.ps1"
    "step5_meta_regression.ps1"
)

$start = Get-Date

Write-Host "============================================================"
Write-Host "SDM-PSI Production Pipeline"
Write-Host "============================================================"

foreach ($step in $steps) {
    $name = [System.IO.Path]::GetFileNameWithoutExtension($step)
    Write-Host ""
    Write-Host ">>> Running $name..."
    Write-Host ""

    & "$PSScriptRoot\$step" @flags

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: $name failed (exit $LASTEXITCODE). Fix the issue and rerun."
        Write-Host "       Completed steps will be skipped (sentinel files)."
        Write-Host "       Or rerun just this step: .\$step"
        exit 1
    }
}

$elapsed = [int]((Get-Date) - $start).TotalMinutes
Write-Host ""
Write-Host "============================================================"
Write-Host "ALL STEPS COMPLETE ($elapsed minutes)"
Write-Host "============================================================"
