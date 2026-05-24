#!/bin/bash
# ==============================================================
# SDM-PSI Production Pipeline via Docker
#
# Usage:
#   ./production_sdm.sh                    # run all analyses
#   ./production_sdm.sh sham_gt_rest       # run one analysis
#   ./production_sdm.sh --skip-to 4        # skip first 3, start at #4
#
# Requirements:
#   - Docker Desktop running with ≥8GB memory allocated
#   - sdm-psi Docker image built
# ==============================================================

DOCKER_IMAGE="sdm-psi"
PLATFORM="linux/amd64"
PROJECT_DIR="$(cd "$(dirname "$0")/sdm_projects" && pwd)"
IMPUTATIONS=50
PERMUTATIONS=5000       # Change to 5000 for publication
P_THRESHOLD=0.05
VOXEL_EXTENT=10
PP_PARAMS="gray_matter,1.0,20,gray_matter,2"

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

NTHREADS=6  # Use 6 of 8 cores

run_sdm() {
    local workdir="$1"
    shift
    docker run --rm \
        --platform "$PLATFORM" \
        --memory=8g \
        --cpus=6 \
        -v "$workdir:/data" \
        "$DOCKER_IMAGE" \
        bash -c "cd /data && \
        if [ -f sdmpsi_params.xml ]; then \
            sed -i 's/<nThreads>[0-9]*</<nThreads>${NTHREADS}</' sdmpsi_params.xml; \
        fi && \
        /opt/sdm/bin/linux64/sdm_parse $@"
}

run_analysis() {
    local name="$1"
    local dir="$PROJECT_DIR/$name"

    if [ ! -d "$dir" ]; then
        echo "  SKIP: $dir does not exist"
        return 1
    fi

    local n_files=$(ls "$dir"/*.txt 2>/dev/null | grep -v sdm_table | grep -v README | wc -l | tr -d ' ')

    echo ""
    echo "============================================================"
    echo "  ANALYSIS: $name ($n_files studies)"
    echo "============================================================"

    # Step 1: Preprocessing
    if [ -d "$dir/pp" ] && [ -f "$dir/sdmpsi_params.xml" ]; then
        echo "  [1/4] Preprocessing — skipping (already done)."
    else
        echo "  [1/4] Preprocessing..."
        run_sdm "$dir" "pp $PP_PARAMS"
        if [ $? -ne 0 ]; then echo "  ERROR: Preprocessing failed"; return 1; fi
        echo "  [1/4] Done."
    fi

    # Step 2: Mean analysis
    if [ -f "$dir/analysis_${name}_mean/${name}_mean_z.nii.gz" ]; then
        echo "  [2/4] Mean analysis — skipping (already done)."
    else
        echo "  [2/4] Mean analysis ($IMPUTATIONS imputations)..."
        run_sdm "$dir" "${name}_mean = mi ${IMPUTATIONS}"
        if [ $? -ne 0 ]; then echo "  ERROR: Mean analysis failed"; return 1; fi
        echo "  [2/4] Done."
    fi

    # Step 3: FWE correction
    if [ -f "$dir/analysis_${name}_mean/corrp_tfce.nii.gz" ]; then
        echo "  [3/4] FWE correction — skipping (already done)."
    else
        rm -rf "$dir/analysis_${name}_mean/fwe" 2>/dev/null
        echo "  [3/4] FWE correction ($PERMUTATIONS permutations)..."
        echo "         Syntax: perm ${name}_mean,${PERMUTATIONS}"
        run_sdm "$dir" "perm ${name}_mean,${PERMUTATIONS},${NTHREADS}"
        if [ $? -ne 0 ]; then
            echo "  ERROR: FWE failed (exit 137 = needs more Docker memory)"
            return 1
        fi
        echo "  [3/4] Done."
    fi

    # Step 4: Threshold
    echo "  [4/4] Thresholding (p<${P_THRESHOLD}, k≥${VOXEL_EXTENT})..."
    run_sdm "$dir" "threshold analysis_${name}_mean/corrp_tfce,analysis_${name}_mean/${name}_mean_z,${P_THRESHOLD},${VOXEL_EXTENT}"
    if [ $? -ne 0 ]; then
        echo "  WARNING: Thresholding may have failed"
    else
        echo "  [4/4] Done."
    fi

    echo "  COMPLETE: $name"
    echo "============================================================"
    return 0
}

run_meta_regression() {
    local name="$1"
    local covariate="$2"
    local reg_name="$3"
    local dir="$PROJECT_DIR/$name"

    if [ ! -d "$dir/pp" ]; then
        echo "  ERROR: Run main analysis first"
        return 1
    fi

    echo ""
    echo "============================================================"
    echo "  META-REGRESSION: $reg_name ($covariate on $name)"
    echo "============================================================"

    echo "  [1/3] Linear model..."
    run_sdm "$dir" "${reg_name} = lm_mi ${covariate},0+1,${IMPUTATIONS}"
    if [ $? -ne 0 ]; then echo "  ERROR"; return 1; fi

    rm -rf "$dir/analysis_${reg_name}/fwe" 2>/dev/null
    echo "  [2/3] FWE correction..."
    run_sdm "$dir" "perm ${reg_name},${PERMUTATIONS},${NTHREADS}"
    if [ $? -ne 0 ]; then echo "  ERROR"; return 1; fi

    echo "  [3/3] Thresholding..."
    run_sdm "$dir" "threshold analysis_${reg_name}/corrp_tfce,analysis_${reg_name}/${reg_name}_z,${P_THRESHOLD},${VOXEL_EXTENT}"

    echo "  COMPLETE: $reg_name"
    echo "============================================================"
}

# --- Main ---

echo "============================================================"
echo "SDM-PSI Production Pipeline (Docker)"
echo "============================================================"
echo "MI=${IMPUTATIONS}, Perm=${PERMUTATIONS}, p<${P_THRESHOLD}, k≥${VOXEL_EXTENT}"

docker info > /dev/null 2>&1 || { echo "ERROR: Docker not running"; exit 1; }
echo "Docker memory: $(docker info 2>/dev/null | grep 'Total Memory' | awk '{print $3}')"
echo ""

# Parse args
SKIP_TO=0
if [ "$1" == "--skip-to" ]; then
    SKIP_TO=$2
    shift 2
fi

# Single analysis
if [ -n "$1" ]; then
    run_analysis "$1"
    exit $?
fi

# All analyses
COMPLETED=0
FAILED=0
START=$(date +%s)

for i in "${!ALL_ANALYSES[@]}"; do
    num=$((i + 1))
    [ $num -le $SKIP_TO ] && { echo "Skipping #$num: ${ALL_ANALYSES[$i]}"; continue; }

    run_analysis "${ALL_ANALYSES[$i]}"
    [ $? -eq 0 ] && COMPLETED=$((COMPLETED + 1)) || FAILED=$((FAILED + 1))
    echo "Progress: $COMPLETED done, $FAILED failed"
done

# Meta-regression
run_meta_regression "sham_gt_rest" "tissue_level" "penetration_effect"

ELAPSED=$(( ($(date +%s) - START) / 60 ))
echo ""
echo "============================================================"
echo "DONE: $COMPLETED/${#ALL_ANALYSES[@]} ($FAILED failed) in ${ELAPSED}min"
echo "============================================================"
