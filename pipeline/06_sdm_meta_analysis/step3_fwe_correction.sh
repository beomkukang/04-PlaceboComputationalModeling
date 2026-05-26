#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# ==============================================================
# Step 3: FWE Correction (perm)
#
# Runs permutation-based family-wise error correction.
# This is the MOST EXPENSIVE step — hours per analysis with 5000 perms.
# Requires Step 2 (mean analysis) to be complete.
# Produces: analysis_<name>_mean/corrp_tfce.nii.gz
#
# Usage:
#   ./step3_fwe_correction.sh                 # all analyses
#   ./step3_fwe_correction.sh sham_gt_rest    # one analysis
#   ./step3_fwe_correction.sh --dry-run       # show plan
#   ./step3_fwe_correction.sh --force         # rerun even if done
#
# Tip: If Docker exits with code 137, increase DOCKER_MEMORY in sdm_config.sh
# ==============================================================

source "$(dirname "${BASH_SOURCE[0]}")/sdm_config.sh"

STEP_NAME="perm"
LOGFILE="$LOGDIR/step3_fwe_$(date '+%Y%m%d_%H%M%S').log"

usage() {
    echo "Step 3: FWE Correction"
    echo "Usage: $0 [analysis_name] [--dry-run] [--force]"
    echo ""
    echo "Analyses: ${ALL_ANALYSES[*]}"
}

run_fwe_correction() {
    local name="$1"
    local dir="$PROJECT_DIR/$name"

    validate_name "$name" || return 1

    if [ ! -d "$dir" ]; then
        log "  SKIP: $dir does not exist"
        return 1
    fi

    # Check prerequisite: mean analysis
    local mean_output="$dir/analysis_${name}_mean/${name}_mean_z.nii.gz"
    if ! is_done "$dir" "mi"; then
        if [ -f "$mean_output" ] && [ -s "$mean_output" ]; then
            log "  NOTE: $name — mean output exists but no sentinel. Marking mi done."
            mark_done "$dir" "mi"
        else
            log "  ERROR: $name — mean analysis not complete. Run step2 first."
            return 1
        fi
    fi

    if $FORCE; then
        rm -f "$dir/.${STEP_NAME}.done" 2>/dev/null || true
    fi

    local fwe_output="$dir/analysis_${name}_mean/corrp_tfce.nii.gz"

    if is_done "$dir" "$STEP_NAME"; then
        log "  SKIP: $name — already done (sentinel found). Use --force to rerun."
        return 0
    fi

    if [ -f "$fwe_output" ] && [ -s "$fwe_output" ]; then
        log "  $name — output exists from prior run, marking done."
        mark_done "$dir" "$STEP_NAME"
        return 0
    fi

    # Clean up partial FWE directory
    rm -rf "$dir/analysis_${name}_mean/fwe" 2>/dev/null || true

    local n_studies
    n_studies=$(count_studies "$dir")
    log "  FWE correction: $name ($n_studies studies, $PERMUTATIONS permutations, $NTHREADS threads)..."
    log "  This may take a long time..."
    if ! run_sdm "$dir" "perm ${name}_mean,${PERMUTATIONS},${NTHREADS}"; then
        log "  ERROR: FWE failed for $name (exit 137 = needs more Docker memory)"
        return 1
    fi

    # Verify output
    if ! ${DRY_RUN:-false} && { [ ! -f "$fwe_output" ] || [ ! -s "$fwe_output" ]; }; then
        log "  ERROR: FWE completed but output missing: $fwe_output"
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
log "STEP 3: FWE Correction (perm, $PERMUTATIONS permutations)"
log "============================================================"
if $DRY_RUN; then log "*** DRY RUN ***"; fi
if $FORCE; then log "*** FORCE MODE ***"; fi
log ""

# Single analysis
if [[ -n "${1:-}" ]]; then
    run_fwe_correction "$1"
    exit $?
fi

# All analyses
COMPLETED=0
FAILED=0

for name in "${ALL_ANALYSES[@]}"; do
    if run_fwe_correction "$name"; then
        COMPLETED=$((COMPLETED + 1))
    else
        FAILED=$((FAILED + 1))
    fi
done

log ""
log "Step 3 complete: $COMPLETED ok, $FAILED failed"
[ "$FAILED" -gt 0 ] && exit 1 || exit 0
