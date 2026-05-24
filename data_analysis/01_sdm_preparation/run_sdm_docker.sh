#!/bin/bash
# ==============================================================
# SDM-PSI Analysis Pipeline via Docker (Linux)
#
# Runs preprocessing, mean analysis, FWE correction, and
# thresholding for all contrast group directories using the
# Linux SDM-PSI binary inside Docker.
#
# Usage:
#   chmod +x run_sdm_docker.sh
#   ./run_sdm_docker.sh                    # run all analyses
#   ./run_sdm_docker.sh sham_gt_rest       # run one specific analysis
#
# Preliminary: 1000 permutations
# Publication: change PERMUTATIONS=5000
# ==============================================================

# --- Configuration ---
DOCKER_IMAGE="sdm-psi"
PLATFORM="linux/amd64"
PROJECT_DIR="$(cd "$(dirname "$0")/sdm_projects" && pwd)"
IMPUTATIONS=20
PERMUTATIONS=100
P_THRESHOLD=0.05
VOXEL_EXTENT=10

# Preprocessing parameters
PP_PARAMS="gray_matter,1.0,20,gray_matter,2"

# --- Analysis directories in priority order ---
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

# --- Functions ---

NTHREADS=6

run_sdm() {
    local workdir="$1"
    shift
    local cmd="$@"

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
        /opt/sdm/bin/linux64/sdm_parse $cmd"
}

run_analysis() {
    local name="$1"
    local dir="$PROJECT_DIR/$name"

    if [ ! -d "$dir" ]; then
        echo "  SKIP: $dir does not exist"
        return 1
    fi

    local n_files=$(ls "$dir"/*.txt 2>/dev/null | grep -v sdm_table | grep -v README | wc -l | tr -d ' ')
    if [ "$n_files" -eq 0 ]; then
        echo "  SKIP: no coordinate files in $dir"
        return 1
    fi

    echo ""
    echo "============================================================"
    echo "  ANALYSIS: $name"
    echo "  Directory: $dir"
    echo "  Studies: $n_files"
    echo "  Permutations: $PERMUTATIONS"
    echo "============================================================"

    # Step 1: Preprocessing (skip if done)
    echo ""
    if [ -d "$dir/pp" ] && [ -f "$dir/sdmpsi_params.xml" ]; then
        echo "  [1/4] Preprocessing already done. Skipping."
    else
        echo "  [1/4] Preprocessing..."
        run_sdm "$dir" "pp $PP_PARAMS"
        if [ $? -ne 0 ]; then
            echo "  ERROR: Preprocessing failed for $name"
            return 1
        fi
        echo "  [1/4] Preprocessing complete."
    fi

    # Set nThreads in params file (use 6 of 8 cores, leave 2 for system)
    if [ -f "$dir/sdmpsi_params.xml" ]; then
        sed -i.bak 's/<nThreads>0</<nThreads>6</' "$dir/sdmpsi_params.xml"
        sed -i.bak 's/<nThreads>1</<nThreads>6</' "$dir/sdmpsi_params.xml"
        rm -f "$dir/sdmpsi_params.xml.bak"
    fi

    # Step 2: Mean analysis (skip if done)
    echo ""
    if [ -d "$dir/analysis_${name}_mean" ]; then
        echo "  [2/4] Mean analysis already done. Skipping."
    else
        echo "  [2/4] Mean analysis (${IMPUTATIONS} imputations)..."
        run_sdm "$dir" "${name}_mean = mi ${IMPUTATIONS}"
        if [ $? -ne 0 ]; then
            echo "  ERROR: Mean analysis failed for $name"
            return 1
        fi
        echo "  [2/4] Mean analysis complete."
    fi

    # Step 3: FWE correction (skip if done)
    echo ""
    if [ -d "$dir/analysis_${name}_mean/fwe" ]; then
        echo "  [3/4] FWE correction already done. Skipping."
    else
        echo "  [3/4] FWE correction (${PERMUTATIONS} permutations)..."
        # Syntax: perm model_name,n_permutations,n_threads
        run_sdm "$dir" "perm ${name}_mean,${PERMUTATIONS},${NTHREADS}"
        if [ $? -ne 0 ]; then
            echo "  ERROR: FWE correction failed for $name"
            return 1
        fi
        echo "  [3/4] FWE correction complete."
    fi

    # Step 4: Threshold
    echo ""
    echo "  [4/4] Thresholding (p<${P_THRESHOLD}, extent≥${VOXEL_EXTENT})..."
    run_sdm "$dir" "threshold analysis_${name}_mean/corrp_tfce,analysis_${name}_mean/${name}_mean_z,${P_THRESHOLD},${VOXEL_EXTENT}"
    if [ $? -ne 0 ]; then
        echo "  ERROR: Thresholding failed for $name"
        return 1
    fi
    echo "  [4/4] Thresholding complete."

    echo ""
    echo "  DONE: $name"
    echo "  Results: $dir/analysis_${name}_mean/"
    echo "============================================================"
    return 0
}

run_meta_regression() {
    local name="$1"
    local covariate="$2"
    local regression_name="$3"
    local dir="$PROJECT_DIR/$name"

    if [ ! -d "$dir" ]; then
        echo "  SKIP: $dir does not exist"
        return 1
    fi

    if [ ! -d "$dir/pp" ]; then
        echo "  ERROR: Run main analysis first (need preprocessing)"
        return 1
    fi

    echo ""
    echo "============================================================"
    echo "  META-REGRESSION: $regression_name"
    echo "  Base analysis: $name"
    echo "  Covariate: $covariate"
    echo "============================================================"

    echo "  [1/3] Linear model..."
    run_sdm "$dir" "${regression_name} = lm_mi ${covariate},0+1,${IMPUTATIONS}"
    if [ $? -ne 0 ]; then
        echo "  ERROR: Linear model failed"
        return 1
    fi

    echo "  [2/3] FWE correction (${PERMUTATIONS} permutations)..."
    run_sdm "$dir" "perm ${regression_name},${PERMUTATIONS},${NTHREADS}"
    if [ $? -ne 0 ]; then
        echo "  ERROR: FWE correction failed"
        return 1
    fi

    echo "  [3/3] Thresholding..."
    run_sdm "$dir" "threshold analysis_${regression_name}/corrp_tfce,analysis_${regression_name}/${regression_name}_z,${P_THRESHOLD},${VOXEL_EXTENT}"
    if [ $? -ne 0 ]; then
        echo "  ERROR: Thresholding failed"
        return 1
    fi

    echo "  DONE: $regression_name"
    echo "============================================================"
    return 0
}

# --- Main ---

echo "============================================================"
echo "SDM-PSI Analysis Pipeline (Docker)"
echo "============================================================"
echo "Docker image: $DOCKER_IMAGE ($PLATFORM)"
echo "Project dir: $PROJECT_DIR"
echo "Parameters: FWHM=20mm, voxel=2mm, aniso=1.0"
echo "Imputations: ${IMPUTATIONS}, Permutations: ${PERMUTATIONS}"
echo "Threshold: p<${P_THRESHOLD} FWE, extent≥${VOXEL_EXTENT} voxels"
echo ""

# Check Docker is running
docker info > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Docker is not running. Start Docker Desktop first."
    exit 1
fi

# If specific analysis requested
if [ -n "$1" ]; then
    echo "Running single analysis: $1"
    run_analysis "$1"
    exit $?
fi

# Run all analyses
echo "Running all ${#ALL_ANALYSES[@]} analyses..."

COMPLETED=0
FAILED=0
TOTAL=${#ALL_ANALYSES[@]}
START_TIME=$(date +%s)

for analysis in "${ALL_ANALYSES[@]}"; do
    run_analysis "$analysis"
    if [ $? -eq 0 ]; then
        COMPLETED=$((COMPLETED + 1))
    else
        FAILED=$((FAILED + 1))
    fi
    echo "Progress: $COMPLETED completed, $FAILED failed, $((TOTAL - COMPLETED - FAILED)) remaining"
done

# Meta-regression
echo ""
echo "Running meta-regression: tissue_level on sham_gt_rest..."
run_meta_regression "sham_gt_rest" "tissue_level" "penetration_effect"

END_TIME=$(date +%s)
ELAPSED=$(( (END_TIME - START_TIME) / 60 ))

echo ""
echo "============================================================"
echo "ALL ANALYSES COMPLETE"
echo "============================================================"
echo "Completed: $COMPLETED / $TOTAL"
echo "Failed: $FAILED"
echo "Total time: ${ELAPSED} minutes"
echo "============================================================"
