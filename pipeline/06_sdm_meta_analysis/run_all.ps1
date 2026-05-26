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
    [string]$Analysis,      # limit steps 1-4 to one contrast (step 5 is always sham_gt_rest)
    [int]$Imputations,      # override step 2 / step 5 imputation count
    [int]$Permutations,     # override step 3 / step 5 permutation count
    [switch]$DryRun,
    [switch]$Force,
    [string]$Sdm,
    [switch]$NoCaffeinate   # by default the PC is kept awake for the whole run
)

$ErrorActionPreference = "Stop"

# --- Keep the machine awake for the duration (Windows "caffeinate") ---
# Uses the Win32 SetThreadExecutionState API. The assertion lives on this
# thread and is released automatically when the script exits; the finally
# block clears it explicitly too. Sleep is blocked while the run is active.
Add-Type -Namespace Win32 -Name Power -MemberDefinition @'
[System.Runtime.InteropServices.DllImport("kernel32.dll", SetLastError = true)]
public static extern uint SetThreadExecutionState(uint esFlags);
'@
$ES_CONTINUOUS       = [uint32]'0x80000000'
$ES_SYSTEM_REQUIRED  = [uint32]'0x00000001'
$ES_DISPLAY_REQUIRED = [uint32]'0x00000002'

function Enable-KeepAwake {
    [void][Win32.Power]::SetThreadExecutionState(
        $ES_CONTINUOUS -bor $ES_SYSTEM_REQUIRED -bor $ES_DISPLAY_REQUIRED)
}
function Disable-KeepAwake {
    [void][Win32.Power]::SetThreadExecutionState($ES_CONTINUOUS)
}

# Flags common to every step
$common = @{}
if ($DryRun) { $common.DryRun = $true }
if ($Force)  { $common.Force  = $true }
if ($Sdm)    { $common.Sdm    = $Sdm }

$steps = @(
    "step1_preprocessing.ps1"
    "step2_mean_analysis.ps1"
    "step3_fwe_correction.ps1"
    "step4_thresholding.ps1"
    "step5_meta_regression.ps1"
)

# Per-step extras -- only the params each step actually accepts, so splatting
# never passes an unknown parameter (e.g. step 5 takes no -Analysis).
$perStep = @{}
foreach ($s in $steps) { $perStep[$s] = @{} }
if ($Analysis) {
    "step1_preprocessing.ps1","step2_mean_analysis.ps1","step3_fwe_correction.ps1","step4_thresholding.ps1" |
        ForEach-Object { $perStep[$_].Analysis = $Analysis }
}
if ($Imputations) {
    $perStep["step2_mean_analysis.ps1"].Imputations   = $Imputations
    $perStep["step5_meta_regression.ps1"].Imputations = $Imputations
}
if ($Permutations) {
    $perStep["step3_fwe_correction.ps1"].Permutations   = $Permutations
    $perStep["step5_meta_regression.ps1"].Permutations  = $Permutations
}

$start = Get-Date

Write-Host "============================================================"
Write-Host "SDM-PSI Production Pipeline"
Write-Host "============================================================"

if (-not $NoCaffeinate) { Enable-KeepAwake; Write-Host "Keep-awake: ON (PC will not sleep until the run finishes)" }

try {
    foreach ($step in $steps) {
        $name = [System.IO.Path]::GetFileNameWithoutExtension($step)

        # Step 5 only applies to sham_gt_rest; skip it when limiting to another contrast.
        if ($step -eq "step5_meta_regression.ps1" -and $Analysis -and $Analysis -ne "sham_gt_rest") {
            Write-Host ""
            Write-Host ">>> Skipping $name (only applies to sham_gt_rest; -Analysis=$Analysis)."
            continue
        }

        Write-Host ""
        Write-Host ">>> Running $name..."
        Write-Host ""

        $flags = $common + $perStep[$step]
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
}
finally {
    if (-not $NoCaffeinate) { Disable-KeepAwake; Write-Host "Keep-awake: released." }
}
