#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# ==============================================================
# Step 2: Mean Analysis (mi)
#
# Runs multiple imputation mean analysis for each contrast.
# Requires Step 1 (preprocessing) to be complete.
# Produces: analysis_<name>_mean/<name>_mean_z.nii.gz
#
# Usage:
#   ./step2_mean_analysis.sh                 # all analyses
#   ./step2_mean_analysis.sh sham_gt_rest    # one analysis
#   ./step2_mean_analysis.sh --dry-run       # show plan
#   ./step2_mean_analysis.sh --force         # rerun even if done
# ==============================================================

source "$(dirname "${BASH_SOURCE[0]}")/sdm_config.sh"

STEP_NAME="mi"
LOGFILE="$LOGDIR/step2_mean_$(date '+%Y%m%d_%H%M%S').log"

usage() {
    echo "Step 2: Mean Analysis"
    echo "Usage: $0 [analysis_name] [--dry-run] [--force]"
    echo ""
    echo "Analyses: ${ALL_ANALYSES[*]}"
}

run_mean_analysis() {
    local name="$1"
    local dir="$PROJECT_DIR/$name"

    validate_name "$name" || return 1

    if [ ! -d "$dir" ]; then
        log "  SKIP: $dir does not exist"
        return 1
    fi

    # Check prerequisite: preprocessing
    if ! is_done "$dir" "pp"; then
        if [ -d "$dir/pp" ] && [ -f "$dir/sdmpsi_params.xml" ]; then
            log "  NOTE: $name — preprocessing output exists but no sentinel. Marking pp done."
            mark_done "$dir" "pp"
        else
            log "  ERROR: $name — preprocessing not complete. Run step1 first."
            return 1
        fi
    fi

    if $FORCE; then
        rm -f "$dir/.${STEP_NAME}.done" 2>/dev/null || true
    fi

    local mean_output="$dir/analysis_${name}_mean/${name}_mean_z.nii.gz"

    if is_done "$dir" "$STEP_NAME"; then
        log "  SKIP: $name — already done (sentinel found). Use --force to rerun."
        return 0
    fi

    if [ -f "$mean_output" ] && [ -s "$mean_output" ]; then
        log "  $name — output exists from prior run, marking done."
        mark_done "$dir" "$STEP_NAME"
        return 0
    fi

    # Clean up any partial previous run
    if [ -d "$dir/analysis_${name}_mean" ]; then
        log "  $name — cleaning up partial previous run..."
        rm -rf "$dir/analysis_${name}_mean"
    fi

    local n_studies
    n_studies=$(count_studies "$dir")
    log "  Mean analysis: $name ($n_studies studies, $IMPUTATIONS imputations)..."
    if ! run_sdm "$dir" "${name}_mean = mi ${IMPUTATIONS}"; then
        log "  ERROR: Mean analysis failed for $name"
        return 1
    fi

    # Verify output
    if ! ${DRY_RUN:-false} && { [ ! -f "$mean_output" ] || [ ! -s "$mean_output" ]; }; then
        log "  ERROR: Mean analysis completed but output missing: $mean_output"
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
log "STEP 2: Mean Analysis (mi, $IMPUTATIONS imputations)"
log "============================================================"
if $DRY_RUN; then log "*** DRY RUN ***"; fi
if $FORCE; then log "*** FORCE MODE ***"; fi
log ""

# Single analysis
if [[ -n "${1:-}" ]]; then
    run_mean_analysis "$1"
    exit $?
fi

# All analyses
COMPLETED=0
FAILED=0

for name in "${ALL_ANALYSES[@]}"; do
    if run_mean_analysis "$name"; then
        COMPLETED=$((COMPLETED + 1))
    else
        FAILED=$((FAILED + 1))
    fi
done

log ""
log "Step 2 complete: $COMPLETED ok, $FAILED failed"
[ "$FAILED" -gt 0 ] && exit 1 || exit 0
