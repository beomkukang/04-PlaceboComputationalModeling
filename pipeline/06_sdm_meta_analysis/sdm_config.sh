#!/bin/bash
# ==============================================================
# SDM-PSI Shared Configuration
#
# Sourced by all step scripts. Do not run directly.
# Edit parameters here — all steps pick them up automatically.
# ==============================================================

# --- Docker ---
DOCKER_IMAGE="sdm-psi"
PLATFORM="linux/amd64"
DOCKER_MEMORY="8g"

# --- Paths ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[1]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/sdm_projects"
LOGDIR="$PROJECT_DIR/logs"

# --- SDM parameters ---
IMPUTATIONS=50
PERMUTATIONS=5000       # Publication-grade; use lower only for debugging
P_THRESHOLD=0.05
VOXEL_EXTENT=10
PP_PARAMS="gray_matter,1.0,20,gray_matter,2"
NTHREADS=6              # Use 6 of 8 cores
MIN_STUDIES=10           # Warn if fewer studies than this

# --- All analyses in pipeline order ---
ALL_ANALYSES=(
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

log() {
    local msg
    msg="$(date '+%Y-%m-%d %H:%M:%S')  $*"
    echo "$msg"
    if [ -n "${LOGFILE:-}" ]; then
        echo "$msg" >> "$LOGFILE"
    fi
}

validate_name() {
    local name="$1"
    if [[ ! "$name" =~ ^[A-Za-z0-9_.-]+$ ]]; then
        log "ERROR: Invalid name '$name' (only A-Z, a-z, 0-9, _, ., - allowed)"
        return 1
    fi
}

count_studies() {
    local dir="$1"
    local table="$dir/sdm_table.txt"
    if [ -f "$table" ]; then
        tail -n +2 "$table" | wc -l | tr -d ' '
    else
        echo "0"
    fi
}

# Sentinel files mark successful step completion
mark_done()  { touch "$1/.${2}.done"; }
is_done()    { [ -f "$1/.${2}.done" ]; }

run_sdm() {
    local workdir="$1"
    shift
    local cmd="$*"

    if ${DRY_RUN:-false}; then
        log "  [DRY-RUN] sdm_parse $cmd"
        return 0
    fi

    docker run --rm \
        --platform "$PLATFORM" \
        --memory="$DOCKER_MEMORY" \
        --cpus="$NTHREADS" \
        -v "$workdir:/data" \
        "$DOCKER_IMAGE" \
        bash -c "cd /data && \
        if [ -f sdmpsi_params.xml ]; then \
            sed -i 's/<nThreads>[0-9]\\+<\\/nThreads>/<nThreads>$NTHREADS<\\/nThreads>/' sdmpsi_params.xml; \
        fi && \
        /opt/sdm/bin/linux64/sdm_parse $cmd"
}

check_prerequisites() {
    if [ ! -d "$PROJECT_DIR" ]; then
        echo "ERROR: sdm_projects directory not found at $PROJECT_DIR"
        exit 1
    fi
    docker info > /dev/null 2>&1 || { echo "ERROR: Docker not running"; exit 1; }
    if ! docker image inspect "$DOCKER_IMAGE" > /dev/null 2>&1; then
        echo "ERROR: Docker image '$DOCKER_IMAGE' not found. Build it first."
        exit 1
    fi
    mkdir -p "$LOGDIR"
}

# Parse common flags (--dry-run, --force, --help)
parse_common_flags() {
    DRY_RUN=false
    FORCE=false
    REMAINING_ARGS=()

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dry-run) DRY_RUN=true; shift ;;
            --force)   FORCE=true; shift ;;
            --help|-h) return 1 ;;  # caller should print usage
            *)         REMAINING_ARGS+=("$1"); shift ;;
        esac
    done
    set -- "${REMAINING_ARGS[@]+"${REMAINING_ARGS[@]}"}"
}
