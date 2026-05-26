#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# ==============================================================
# Step 1: Preprocessing (pp)
#
# Creates the pp/ directory and sdmpsi_params.xml for each analysis.
# This is the fastest step — typically a few minutes per analysis.
#
# Usage:
#   ./step1_preprocessing.sh                 # all analyses
#   ./step1_preprocessing.sh sham_gt_rest    # one analysis
#   ./step1_preprocessing.sh --dry-run       # show plan
#   ./step1_preprocessing.sh --force         # rerun even if done
# ==============================================================

source "$(dirname "${BASH_SOURCE[0]}")/sdm_config.sh"

STEP_NAME="pp"
LOGFILE="$LOGDIR/step1_preprocessing_$(date '+%Y%m%d_%H%M%S').log"

usage() {
    echo "Step 1: Preprocessing"
    echo "Usage: $0 [analysis_name] [--dry-run] [--force]"
    echo ""
    echo "Analyses: ${ALL_ANALYSES[*]}"
}

run_preprocessing() {
    local name="$1"
    local dir="$PROJECT_DIR/$name"

    validate_name "$name" || return 1

    if [ ! -d "$dir" ]; then
        log "  SKIP: $dir does not exist"
        return 1
    fi

    if [ ! -f "$dir/sdm_table.txt" ]; then
        log "  ERROR: $dir/sdm_table.txt not found"
        return 1
    fi

    local n_studies
    n_studies=$(count_studies "$dir")

    if [ "$n_studies" -eq 0 ]; then
        log "  SKIP: no studies in sdm_table.txt for $name"
        return 1
    fi

    if [ "$n_studies" -lt "$MIN_STUDIES" ]; then
        log "  WARNING: $name has only $n_studies studies (recommended minimum: $MIN_STUDIES)"
    fi

    if $FORCE; then
        rm -f "$dir/.${STEP_NAME}.done" 2>/dev/null || true
    fi

    if is_done "$dir" "$STEP_NAME"; then
        log "  SKIP: $name — already done (sentinel found). Use --force to rerun."
        return 0
    fi

    if [ -d "$dir/pp" ] && [ -f "$dir/sdmpsi_params.xml" ]; then
        log "  $name — output exists from prior run, marking done."
        mark_done "$dir" "$STEP_NAME"
        return 0
    fi

    log "  Preprocessing $name ($n_studies studies)..."
    if ! run_sdm "$dir" "pp $PP_PARAMS"; then
        log "  ERROR: Preprocessing failed for $name"
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
log "STEP 1: Preprocessing (pp $PP_PARAMS)"
log "============================================================"
if $DRY_RUN; then log "*** DRY RUN ***"; fi
if $FORCE; then log "*** FORCE MODE ***"; fi
log ""

# Single analysis
if [[ -n "${1:-}" ]]; then
    run_preprocessing "$1"
    exit $?
fi

# All analyses
COMPLETED=0
FAILED=0

for name in "${ALL_ANALYSES[@]}"; do
    if run_preprocessing "$name"; then
        COMPLETED=$((COMPLETED + 1))
    else
        FAILED=$((FAILED + 1))
    fi
done

log ""
log "Step 1 complete: $COMPLETED ok, $FAILED failed"
[ "$FAILED" -gt 0 ] && exit 1 || exit 0
