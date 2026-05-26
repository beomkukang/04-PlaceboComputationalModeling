#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# ==============================================================
# Step 4: Thresholding
#
# Applies FWE-corrected threshold to produce final result maps.
# Requires Step 3 (FWE correction) to be complete.
# This step is fast and always reruns (parameters may change).
#
# Usage:
#   ./step4_thresholding.sh                 # all analyses
#   ./step4_thresholding.sh sham_gt_rest    # one analysis
#   ./step4_thresholding.sh --dry-run       # show plan
# ==============================================================

source "$(dirname "${BASH_SOURCE[0]}")/sdm_config.sh"

STEP_NAME="threshold"
LOGFILE="$LOGDIR/step4_threshold_$(date '+%Y%m%d_%H%M%S').log"

usage() {
    echo "Step 4: Thresholding"
    echo "Usage: $0 [analysis_name] [--dry-run]"
    echo "Parameters: p<${P_THRESHOLD}, k>=${VOXEL_EXTENT}"
    echo ""
    echo "Analyses: ${ALL_ANALYSES[*]}"
}

run_thresholding() {
    local name="$1"
    local dir="$PROJECT_DIR/$name"

    validate_name "$name" || return 1

    if [ ! -d "$dir" ]; then
        log "  SKIP: $dir does not exist"
        return 1
    fi

    # Check prerequisite: FWE correction
    local fwe_output="$dir/analysis_${name}_mean/corrp_tfce.nii.gz"
    if ! is_done "$dir" "perm"; then
        if [ -f "$fwe_output" ] && [ -s "$fwe_output" ]; then
            log "  NOTE: $name — FWE output exists but no sentinel. Marking perm done."
            mark_done "$dir" "perm"
        else
            log "  ERROR: $name — FWE correction not complete. Run step3 first."
            return 1
        fi
    fi

    log "  Thresholding: $name (p<${P_THRESHOLD}, k>=${VOXEL_EXTENT})..."
    if ! run_sdm "$dir" "threshold analysis_${name}_mean/corrp_tfce,analysis_${name}_mean/${name}_mean_z,${P_THRESHOLD},${VOXEL_EXTENT}"; then
        log "  WARNING: Thresholding may have failed for $name"
        return 1
    fi

    mark_done "$dir" "$STEP_NAME"
    log "  DONE: $name"
    return 0
}

# --- Main ---

parse_common_flags "$@" || { usage; exit 0; }
set -- "${REMAINING_ARGS[@]+"${REMAINING_ARGS[@]}"}"
check_prerequisites

log "============================================================"
log "STEP 4: Thresholding (p<${P_THRESHOLD}, k>=${VOXEL_EXTENT})"
log "============================================================"
if $DRY_RUN; then log "*** DRY RUN ***"; fi
log ""

# Single analysis
if [[ -n "${1:-}" ]]; then
    run_thresholding "$1"
    exit $?
fi

# All analyses
COMPLETED=0
FAILED=0

for name in "${ALL_ANALYSES[@]}"; do
    if run_thresholding "$name"; then
        COMPLETED=$((COMPLETED + 1))
    else
        FAILED=$((FAILED + 1))
    fi
done

log ""
log "Step 4 complete: $COMPLETED ok, $FAILED failed"
[ "$FAILED" -gt 0 ] && exit 1 || exit 0
