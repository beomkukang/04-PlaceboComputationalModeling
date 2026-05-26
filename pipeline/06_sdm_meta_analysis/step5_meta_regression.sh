#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# ==============================================================
# Step 5: Meta-Regression
#
# Runs meta-regression of tissue_level on sham_gt_rest
# (penetration_effect analysis).
# Requires sham_gt_rest preprocessing (step1) to be complete.
#
# This step runs its own pipeline: linear model → FWE → threshold.
#
# Usage:
#   ./step5_meta_regression.sh               # run
#   ./step5_meta_regression.sh --dry-run     # show plan
#   ./step5_meta_regression.sh --force       # rerun all sub-steps
# ==============================================================

source "$(dirname "${BASH_SOURCE[0]}")/sdm_config.sh"

# Meta-regression configuration
BASE_ANALYSIS="sham_gt_rest"
COVARIATE="tissue_level"
REG_NAME="penetration_effect"

LOGFILE="$LOGDIR/step5_meta_regression_$(date '+%Y%m%d_%H%M%S').log"

usage() {
    echo "Step 5: Meta-Regression"
    echo "Usage: $0 [--dry-run] [--force]"
    echo ""
    echo "Runs: $REG_NAME = mi_lm $COVARIATE on $BASE_ANALYSIS"
}

# --- Main ---

parse_common_flags "$@" || { usage; exit 0; }
check_prerequisites

DIR="$PROJECT_DIR/$BASE_ANALYSIS"

log "============================================================"
log "STEP 5: Meta-Regression ($REG_NAME)"
log "  Base: $BASE_ANALYSIS"
log "  Covariate: $COVARIATE"
log "  Imputations: $IMPUTATIONS, Permutations: $PERMUTATIONS"
log "============================================================"
if $DRY_RUN; then log "*** DRY RUN ***"; fi
if $FORCE; then log "*** FORCE MODE ***"; fi
log ""

# Validate prerequisites
if [ ! -d "$DIR/pp" ]; then
    log "ERROR: Preprocessing not done for $BASE_ANALYSIS. Run step1 first."
    exit 1
fi

# Validate covariate exists in sdm_table.txt
if [ ! -f "$DIR/sdm_table.txt" ]; then
    log "ERROR: sdm_table.txt not found in $DIR"
    exit 1
fi

HEADER=$(head -1 "$DIR/sdm_table.txt")
if ! echo "$HEADER" | grep -qw "$COVARIATE"; then
    log "ERROR: Covariate '$COVARIATE' not found in sdm_table.txt columns: $HEADER"
    exit 1
fi

if $FORCE; then
    rm -f "$DIR/.mr_${REG_NAME}_lm.done" \
          "$DIR/.mr_${REG_NAME}_perm.done" \
          "$DIR/.mr_${REG_NAME}_threshold.done" 2>/dev/null || true
fi

# Sub-step 1: Linear model
if [ -f "$DIR/.mr_${REG_NAME}_lm.done" ]; then
    log "  [1/3] Linear model — skipping (sentinel found)."
else
    log "  [1/3] Linear model ($IMPUTATIONS imputations)..."
    if ! run_sdm "$DIR" "${REG_NAME} = mi_lm ${COVARIATE},0+1,${IMPUTATIONS}"; then
        log "  ERROR: Linear model failed"
        exit 1
    fi
    touch "$DIR/.mr_${REG_NAME}_lm.done"
    log "  [1/3] Done."
fi

# Sub-step 2: FWE correction
if [ -f "$DIR/.mr_${REG_NAME}_perm.done" ]; then
    log "  [2/3] FWE correction — skipping (sentinel found)."
else
    rm -rf "$DIR/analysis_${REG_NAME}/fwe" 2>/dev/null || true
    log "  [2/3] FWE correction ($PERMUTATIONS permutations, $NTHREADS threads)..."
    log "  This may take a long time..."
    if ! run_sdm "$DIR" "perm ${REG_NAME},${PERMUTATIONS},${NTHREADS}"; then
        log "  ERROR: FWE correction failed"
        exit 1
    fi
    touch "$DIR/.mr_${REG_NAME}_perm.done"
    log "  [2/3] Done."
fi

# Sub-step 3: Thresholding (always rerun)
log "  [3/3] Thresholding (p<${P_THRESHOLD}, k>=${VOXEL_EXTENT})..."
if ! run_sdm "$DIR" "threshold analysis_${REG_NAME}/corrp_tfce,analysis_${REG_NAME}/${REG_NAME}_z,${P_THRESHOLD},${VOXEL_EXTENT}"; then
    log "  ERROR: Thresholding failed"
    exit 1
fi
touch "$DIR/.mr_${REG_NAME}_threshold.done"
log "  [3/3] Done."

log ""
log "STEP 5 COMPLETE: $REG_NAME"
log "  Results: $DIR/analysis_${REG_NAME}/"
log "============================================================"
