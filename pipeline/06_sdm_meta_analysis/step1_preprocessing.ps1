# ==============================================================
# Step 1: Preprocessing (pp)  -- Windows / PowerShell port
#
# Creates the pp/ directory and sdmpsi_params.xml for each analysis.
# This is the fastest step -- typically a few minutes per analysis.
#
# Usage:
#   .\step1_preprocessing.ps1                      # all analyses
#   .\step1_preprocessing.ps1 -Analysis sham_gt_rest
#   .\step1_preprocessing.ps1 -DryRun              # show plan
#   .\step1_preprocessing.ps1 -Force               # rerun even if done
#   .\step1_preprocessing.ps1 -Sdm C:\path\sdm.bat # override SDM path
# ==============================================================
[CmdletBinding()]
param(
    [string]$Analysis,
    [switch]$DryRun,
    [switch]$Force,
    [string]$Sdm
)

. "$PSScriptRoot\sdm_config.ps1"

$StepName = "pp"
$LogFile  = Join-Path $LogDir ("step1_preprocessing_{0}.log" -f (Get-Date -Format 'yyyyMMdd_HHmmss'))

function Invoke-Preprocessing {
    param([string]$Name)
    $dir = Join-Path $ProjectDir $Name

    if (-not (Test-SdmName $Name)) { return $false }

    if (-not (Test-Path $dir)) { Write-SdmLog "  SKIP: $dir does not exist"; return $false }
    if (-not (Test-Path (Join-Path $dir "sdm_table.txt"))) {
        Write-SdmLog "  ERROR: $dir\sdm_table.txt not found"; return $false
    }

    $n = Get-StudyCount $dir
    if ($n -eq 0) { Write-SdmLog "  SKIP: no studies in sdm_table.txt for $Name"; return $false }
    if ($n -lt $MinStudies) {
        Write-SdmLog "  WARNING: $Name has only $n studies (recommended minimum: $MinStudies)"
    }

    if ($Force) { Reset-SdmStep $dir $StepName $Name }   # delete pp output + sentinel, recompute

    if (Test-SdmDone $dir $StepName) {
        Write-SdmLog "  SKIP: $Name -- already done (sentinel found). Use -Force to rerun."
        return $true
    }

    # No sentinel => the unit is not trusted as complete. Clear any fragmented
    # pp output before rerunning so partial files can't linger.
    if (Test-Path (Join-Path $dir "pp")) {
        Write-SdmLog "  $Name -- no sentinel; clearing fragmented pp output before rerun."
        Reset-SdmStep $dir $StepName $Name
    }

    Write-SdmLog "  Preprocessing $Name ($n studies)..."
    if (-not (Invoke-Sdm $dir "pp $PpParams")) {
        Write-SdmLog "  ERROR: Preprocessing failed for $Name"; return $false
    }

    # Verify output before trusting it. SDM writes <study>_lower.nii.gz and
    # <study>_upper.nii.gz bound maps. The count is NOT a fixed multiple of
    # $n: studies with no peaks (empty *.no_peaks.txt) are listed in
    # sdm_table.txt but may yield no maps, while t-image studies can yield
    # extra maps. So fail only on the genuine failure -- zero maps, as seen
    # when a run is killed mid-way -- and merely warn if the count looks low.
    if (-not $DryRun) {
        $ppDir = Join-Path $dir "pp"
        $lower = @(Get-ChildItem $ppDir -Filter "*_lower.nii.gz" -ErrorAction SilentlyContinue).Count
        $upper = @(Get-ChildItem $ppDir -Filter "*_upper.nii.gz" -ErrorAction SilentlyContinue).Count
        if ($lower -eq 0 -or $upper -eq 0) {
            Write-SdmLog "  ERROR: $Name -- pp produced no bound maps ($lower lower / $upper upper). Not marking done."
            return $false
        }
        $noPeaks = @(Get-ChildItem $dir -Filter "*.no_peaks.txt" -ErrorAction SilentlyContinue).Count
        $minExpected = $n - $noPeaks
        if ($lower -lt $minExpected -or $upper -lt $minExpected) {
            Write-SdmLog "  WARNING: $Name -- fewer pp maps than expected ($lower/$upper vs >= $minExpected peak studies); marking done, please verify."
        }
    }

    Set-SdmDone $dir $StepName
    Write-SdmLog "  DONE: $Name"
    return $true
}

# --- Main ---
Test-SdmPrereq

Write-SdmLog "============================================================"
Write-SdmLog "STEP 1: Preprocessing (pp $PpParams)"
Write-SdmLog "============================================================"
if ($DryRun) { Write-SdmLog "*** DRY RUN ***" }
if ($Force)  { Write-SdmLog "*** FORCE MODE ***" }
Write-SdmLog ""

if ($Analysis) {
    if (Invoke-Preprocessing $Analysis) { exit 0 } else { exit 1 }
}

$completed = 0; $failed = 0
foreach ($name in $AllAnalyses) {
    if (Invoke-Preprocessing $name) { $completed++ } else { $failed++ }
}

Write-SdmLog ""
Write-SdmLog "Step 1 complete: $completed ok, $failed failed"
if ($failed -gt 0) { exit 1 } else { exit 0 }
