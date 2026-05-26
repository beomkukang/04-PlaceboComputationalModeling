"""Unified configuration for the analysis pipeline.

All paths are relative to PROJECT_ROOT. Every script imports this file.
"""

from pathlib import Path

# --- Root paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PIPELINE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# --- Data directory ---
DATA_DIR = PROJECT_ROOT / "data"
PDF_DIR = DATA_DIR / "pdfs"
RAW_EXTRACTIONS_DIR = DATA_DIR / "raw_extractions"
MASTER_STUDY_LIST = DATA_DIR / "master_study_list.csv"
EXTRACTION_RESULTS = DATA_DIR / "extraction_results.json"
PMID_CORRECTION_MAP = DATA_DIR / "pmid_correction_map.csv"

# --- Pipeline step outputs (completed steps) ---

# 02: Contrast classification
CONTRAST_CLASSIFICATIONS = PIPELINE_DIR / "02_contrast_classification" / "contrast_classifications.csv"

# 03: Coordinate preparation
SDM_INPUT_DIR = PIPELINE_DIR / "03_coordinate_preparation" / "sdm"
MACM_DIR = PIPELINE_DIR / "03_coordinate_preparation" / "macm"
MACM_COORDINATES = MACM_DIR / "all_coordinates_pooled.csv"
MACM_INDEX = MACM_DIR / "study_contrast_index.csv"
STAT_CONVERSION_LOG = PIPELINE_DIR / "03_coordinate_preparation" / "stat_conversion_log.csv"

# 04: Covariate encoding
META_REG_DIR = PIPELINE_DIR / "04_covariate_encoding" / "meta_regression"
STUDY_PREDICTORS = META_REG_DIR / "study_predictors.csv"
INTERACTION_TERMS = META_REG_DIR / "interaction_terms.csv"
PERTURBATION_INPUT_DIR = PIPELINE_DIR / "04_covariate_encoding" / "perturbation_space"
ARM_COMPONENTS = PERTURBATION_INPUT_DIR / "arm_components.csv"
SHAM_DECOMPOSITION = PERTURBATION_INPUT_DIR / "sham_decomposition.csv"
SENSORY_INPUT_DIR = PIPELINE_DIR / "04_covariate_encoding" / "sensory"
DEQI_SUMMARY = SENSORY_INPUT_DIR / "deqi_summary_by_arm.csv"
DEQI_SUBSCALES = SENSORY_INPUT_DIR / "deqi_subscales.csv"
BLINDING_ASSESSMENT = SENSORY_INPUT_DIR / "blinding_assessment.csv"
SENSATION_COMPARISON = SENSORY_INPUT_DIR / "sensation_verum_vs_sham.csv"

# 05: Clinical outcomes
CLINICAL_INPUT_DIR = PIPELINE_DIR / "05_clinical_outcomes" / "clinical"
CLINICAL_PARSED = CLINICAL_INPUT_DIR / "clinical_parsed.csv"
CLINICAL_EFFECT_SIZES = CLINICAL_INPUT_DIR / "clinical_effect_sizes.csv"
CLINICAL_RESPONSIVENESS = CLINICAL_INPUT_DIR / "clinical_responsiveness.csv"
BRAIN_CLINICAL_CORRELATIONS = CLINICAL_INPUT_DIR / "brain_clinical_correlations.csv"
OUTCOMES_BY_ARM = CLINICAL_INPUT_DIR / "outcomes_by_arm.csv"

# 06: SDM meta-analysis
SDM_PROJECTS_DIR = PIPELINE_DIR / "06_sdm_meta_analysis" / "sdm_projects"

# 08: Perturbation space / RSA inputs
RSA_INPUT_DIR = PIPELINE_DIR / "08_perturbation_space" / "rsa"
PERTURBATION_DISSIM_A = RSA_INPUT_DIR / "perturbation_dissimilarity_axisA.csv"
PERTURBATION_DISSIM_B = RSA_INPUT_DIR / "perturbation_dissimilarity_axisB.csv"
PERTURBATION_DISSIM_COMBINED = RSA_INPUT_DIR / "perturbation_dissimilarity_combined.csv"
SENSORY_DISSIM = RSA_INPUT_DIR / "sensory_dissimilarity.csv"
CLINICAL_DISSIM = RSA_INPUT_DIR / "clinical_dissimilarity.csv"
NEURAL_DISSIM = RSA_INPUT_DIR / "neural_dissimilarity.csv"

# --- SDM helpers ---

SDM_ANALYSES = [
    "sham_gt_rest",
    "verum_gt_sham",
    "verum_gt_rest",
    "sham_gt_rest_penetrating",
    "sham_gt_rest_nonpenetrating",
    "verum_post_gt_pre",
    "sham_post_gt_pre",
    "deactivation",
    "group_comparison",
    "correlation_clinical",
]


def sdm_output_dir(analysis_name: str) -> Path:
    return SDM_PROJECTS_DIR / analysis_name


def sdm_z_map(analysis_name: str) -> Path:
    return (
        SDM_PROJECTS_DIR / analysis_name
        / f"analysis_{analysis_name}_mean"
        / f"{analysis_name}_mean_z.nii.gz"
    )


def sdm_corrp_map(analysis_name: str) -> Path:
    return (
        SDM_PROJECTS_DIR / analysis_name
        / f"analysis_{analysis_name}_mean"
        / "corrp_tfce.nii.gz"
    )


# --- Analysis outputs ---

OUT_QC = OUTPUTS_DIR / "qc"
OUT_BEHAVIORAL = OUTPUTS_DIR / "behavioral"
OUT_PERTURBATION = OUTPUTS_DIR / "perturbation"
OUT_NEURAL = OUTPUTS_DIR / "neural"
OUT_GRADIENTS = OUTPUTS_DIR / "gradients"
OUT_MODELS = OUTPUTS_DIR / "models"
OUT_SHAM = OUTPUTS_DIR / "sham"
OUT_RSA = OUTPUTS_DIR / "rsa"
OUT_FIGURES = OUTPUTS_DIR / "figures"
OUT_TABLES = OUTPUTS_DIR / "tables"

# --- Common parameters ---

P_THRESHOLD = 0.05
VOXEL_EXTENT = 10
MIN_STUDIES_PRIMARY = 10
MIN_STUDIES_EXPLORATORY = 5

# --- API settings (for extraction scripts, if rerun needed) ---

MODEL = "claude-sonnet-4-6"

# --- Contrast categories ---

CONTRAST_CATEGORIES = [
    "sham_gt_rest",
    "verum_gt_sham",
    "verum_gt_rest",
    "sham_post_gt_pre",
    "verum_post_gt_pre",
    "group_comparison",
    "deactivation",
    "correlation_deqi",
    "correlation_expectancy",
    "correlation_clinical",
    "other",
]

TISSUE_LEVELS = ["1", "2", "3", "4"]

MNI_BOUNDS = {"x": (-90, 90), "y": (-126, 90), "z": (-72, 108)}
