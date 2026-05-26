#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# ==============================================================
# SDM-PSI Production Pipeline — Orchestrator
#
# Runs all 5 steps in sequence. For step-by-step control, use
# the individual scripts directly:
#
#   ./step1_preprocessing.sh     [analysis] [--dry-run] [--force]
#   ./step2_mean_analysis.sh     [analysis] [--dry-run] [--force]
#   ./step3_fwe_correction.sh    [analysis] [--dry-run] [--force]
#   ./step4_thresholding.sh      [analysis] [--dry-run]
#   ./step5_meta_regression.sh              [--dry-run] [--force]
#
# Or run everything at once:
#   ./production_sdm.sh                     # all steps, all analyses
#   ./production_sdm.sh --dry-run           # show plan
#   ./production_sdm.sh --force             # rerun everything
#
# All scripts share configuration from sdm_config.sh.
# ==============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Pass through flags
FLAGS=()
for arg in "$@"; do
    case "$arg" in
        --help|-h)
            echo "SDM-PSI Production Pipeline — runs all 5 steps."
            echo ""
            echo "Usage: $0 [--dry-run] [--force]"
            echo ""
            echo "Steps:"
            echo "  1. Preprocessing     (pp)"
            echo "  2. Mean analysis     (mi, 50 imputations)"
            echo "  3. FWE correction    (perm, 5000 permutations)"
            echo "  4. Thresholding      (p<0.05, k>=10)"
            echo "  5. Meta-regression   (tissue_level on sham_gt_rest)"
            echo ""
            echo "For step-by-step control, run ./stepN_*.sh individually."
            exit 0
            ;;
        --dry-run|--force)
            FLAGS+=("$arg")
            ;;
        *)
            echo "ERROR: Unknown option '$arg'. Use --help for usage."
            exit 1
            ;;
    esac
done

START=$(date +%s)

echo "============================================================"
echo "SDM-PSI Production Pipeline"
echo "============================================================"
echo ""

for step in \
    "$SCRIPT_DIR/step1_preprocessing.sh" \
    "$SCRIPT_DIR/step2_mean_analysis.sh" \
    "$SCRIPT_DIR/step3_fwe_correction.sh" \
    "$SCRIPT_DIR/step4_thresholding.sh" \
    "$SCRIPT_DIR/step5_meta_regression.sh"; do

    step_name=$(basename "$step" .sh)
    echo ""
    echo ">>> Running $step_name..."
    echo ""

    if ! bash "$step" "${FLAGS[@]+"${FLAGS[@]}"}"; then
        echo ""
        echo "ERROR: $step_name failed. Fix the issue and rerun."
        echo "       Completed steps will be skipped (sentinel files)."
        echo "       Or rerun just this step: ./$step_name.sh"
        exit 1
    fi
done

ELAPSED=$(( ($(date +%s) - START) / 60 ))
echo ""
echo "============================================================"
echo "ALL STEPS COMPLETE (${ELAPSED} minutes)"
echo "============================================================"
