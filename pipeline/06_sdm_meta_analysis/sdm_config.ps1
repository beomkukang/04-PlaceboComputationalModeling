# ==============================================================
# SDM-PSI Shared Configuration (Windows / PowerShell, no Docker)
#
# PowerShell port of sdm_config.sh. Instead of running sdm_parse
# inside a Docker container, this calls the native Windows SDM-PSI
# command-line entry point (sdm.bat) directly.
#
# Dot-source from each step script:
#     . "$PSScriptRoot\sdm_config.ps1"
#
# Edit parameters here -- all steps pick them up automatically.
# ==============================================================

# --- SDM executable ---
# Resolution order: -Sdm parameter > $env:SDM > default install path.
if (-not $Sdm) { $Sdm = $env:SDM }
if (-not $Sdm) { $Sdm = "C:\SdmPsiGui-win64-v6.23\sdm.bat" }
$SDM = $Sdm

# --- Paths ---
$ScriptDir  = $PSScriptRoot
$ProjectDir = Join-Path $ScriptDir "sdm_projects"
$LogDir     = Join-Path $ProjectDir "logs"

# --- SDM parameters (mirror sdm_config.sh) ---
$Imputations  = 50
$Permutations = 5000        # Publication-grade; use lower only for debugging
$PThreshold   = 0.05
$VoxelExtent  = 10
$PpParams     = "gray_matter,1.0,20,gray_matter,2"
$NThreads     = 6           # Use 6 of 8 cores
$MinStudies   = 10          # Warn if fewer studies than this

# --- All analyses in pipeline order ---
$AllAnalyses = @(
    "sham_gt_rest"
    "verum_gt_sham"
    "verum_gt_rest"
    "sham_gt_rest_penetrating"
    "sham_gt_rest_nonpenetrating"
    "verum_post_gt_pre"
    "sham_post_gt_pre"
    "deactivation"
    "group_comparison"
    "correlation_clinical"
)

# --- Shared functions ---

function Write-SdmLog {
    param([string]$Message)
    $line = "{0}  {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Message
    Write-Host $line
    if ($LogFile) { Add-Content -Path $LogFile -Value $line -Encoding utf8 }
}

function Test-SdmName {
    param([string]$Name)
    if ($Name -notmatch '^[A-Za-z0-9_.-]+$') {
        Write-SdmLog "ERROR: Invalid name '$Name' (only A-Z, a-z, 0-9, _, ., - allowed)"
        return $false
    }
    return $true
}

function Get-StudyCount {
    param([string]$Dir)
    $table = Join-Path $Dir "sdm_table.txt"
    if (Test-Path $table) {
        @(Get-Content $table | Select-Object -Skip 1).Count
    } else {
        0
    }
}

# Sentinel files mark successful step completion (gitignored via .*.done)
function Set-SdmDone {
    param([string]$Dir, [string]$Step)
    if ($DryRun) { return }   # never write sentinels during a dry run
    $f = Join-Path $Dir ".$Step.done"
    if (Test-Path $f) { (Get-Item $f).LastWriteTime = Get-Date }
    else { New-Item -ItemType File -Path $f | Out-Null }
}

function Test-SdmDone {
    param([string]$Dir, [string]$Step)
    Test-Path (Join-Path $Dir ".$Step.done")
}

# Run an SDM command in $WorkDir by calling sdm.bat directly.
# Returns $true on success ($LASTEXITCODE -eq 0), $false otherwise.
function Invoke-Sdm {
    param([string]$WorkDir, [string]$Cmd)

    if ($DryRun) {
        Write-SdmLog "  [DRY-RUN] sdm $Cmd"
        return $true
    }

    Push-Location $WorkDir
    try {
        # Keep thread count in sync (sdmpsi_params.xml exists after preprocessing).
        $xml = Join-Path $WorkDir "sdmpsi_params.xml"
        if (Test-Path $xml) {
            $content = [System.IO.File]::ReadAllText($xml)
            $content = $content -replace '<nThreads>\d+</nThreads>', "<nThreads>$NThreads</nThreads>"
            # Write back without BOM so SDM's XML parser is unaffected.
            [System.IO.File]::WriteAllText($xml, $content, (New-Object System.Text.UTF8Encoding($false)))
        }
        & $SDM $Cmd
        return ($LASTEXITCODE -eq 0)
    } finally {
        Pop-Location
    }
}

function Test-SdmPrereq {
    if (-not (Test-Path $ProjectDir)) {
        Write-Host "ERROR: sdm_projects directory not found at $ProjectDir"
        exit 1
    }
    if (-not (Test-Path $SDM)) {
        Write-Host "ERROR: SDM executable not found at $SDM"
        Write-Host "       Set it with:  `$env:SDM = 'C:\path\to\sdm.bat'   (or pass -Sdm)"
        exit 1
    }
    if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }
}
