# Analysis Pipeline

## Overview

This pipeline tests whether acupuncture-related neural and clinical effects are better understood as graded responses within a multidimensional perturbation space, rather than as categorical verum vs. sham effects.

**Two-phase architecture:**
- `data_processing/v1/` — Parses raw extractions into analysis-ready tables (complete)
- `data_analysis/` — Runs statistical analyses on those tables (this directory)

## Pipeline Steps

| Step | Directory | Script | What it does | Inputs | Outputs | Status |
|------|-----------|--------|--------------|--------|---------|--------|
| 01 | `01_sdm_preparation/` | `step1-5*.sh` | Coordinate-based meta-analysis (SDM-PSI) | `data_processing/v1/sdm/*.txt` | z-maps, corrp_tfce, thresholded maps per contrast | In progress |
| 02 | `02_data_validation/` | `validate.py` | QC checks: missing IDs, duplicate contrasts, coordinate outliers, scale validity | All `data_processing/v1/` outputs | `outputs/qc/` reports | Not started |
| 03 | `03_clinical_responsiveness/` | `responsiveness.py` | Compute domain-aggregated and global clinical responsiveness | `clinical_parsed.csv`, `clinical_effect_sizes.csv` | `outputs/behavioral/` CSVs | Not started |
| 04 | `04_perturbation_space/` | `perturbation.py` | PCA/UMAP on perturbation space, compute pairwise distances | `arm_components.csv`, `sham_decomposition.csv` | `outputs/perturbation/` CSVs + figures | Not started |
| 05 | `05_neural_space/` | `neural_space.py` | Extract network-level features from SDM maps using atlas parcels | SDM z-maps (step 01) | `outputs/neural/` feature matrix + distance matrix | Not started |
| 06 | `06_gradient_analysis/` | `gradients.py` | PCA/diffusion embedding on neural features → neural gradients | `outputs/neural/` (step 05) | `outputs/gradients/` gradient scores + loadings | Not started |
| 07 | `07_component_meta_regression/` | `regression.py` | Mixed-effects models: component predictors → neural/clinical outcomes | Steps 03-06 outputs, `study_predictors.csv` | `outputs/models/` regression results | Not started |
| 08 | `08_component_interaction/` | `interaction.py` | Compare additive vs. amplification vs. substitution vs. overlap models | Steps 03-06 outputs | `outputs/models/` model comparisons | Not started |
| 09 | `09_sham_heterogeneity/` | `sham.py` | Explain sham neural heterogeneity via component-level covariates | Steps 04-06 outputs, sensory/deqi data | `outputs/sham/` model results | Not started |
| 10 | `10_rsa/` | `rsa.py` | Mantel/partial RSA: perturbation ↔ neural ↔ clinical distances | Dissimilarity matrices from steps 04-06 | `outputs/rsa/` correlation results | Not started |
| 11 | `11_sensitivity/` | `sensitivity.py` | Leave-one-out, imaging-family, population, outcome sensitivity | All prior outputs | `outputs/tables/` sensitivity tables | Not started |
| 12 | `12_figures_tables/` | `figures.py` | Publication figures and tables | All prior outputs | `outputs/figures/`, `outputs/tables/` | Not started |

## Data flow

```
data_extraction/raw_extractions/ (159 JSONs)
        │
        ▼
data_processing/v1/ (scripts 01-09)  ──────────────────────────────────┐
   ├── contrast_classifications.csv                                    │
   ├── sdm/*.txt (coordinates)                                        │
   ├── perturbation_space/ (arm_components, sham_decomposition)        │
   ├── sensory/ (deqi, blinding)                                       │
   ├── clinical/ (effect sizes, responsiveness)                        │
   ├── meta_regression/ (study predictors)                             │
   └── rsa/ (pre-computed dissimilarity matrices)                      │
        │                                                              │
        ▼                                                              │
data_analysis/                                                         │
   ├── 01_sdm_preparation/ ◄── sdm/*.txt                              │
   │      └── sdm_projects/*/analysis_*_mean/*_z.nii.gz                │
   │                │                                                  │
   │                ▼                                                  │
   ├── 02 validate ◄── all processing outputs ─────────────────────────┘
   ├── 03 responsiveness ◄── clinical/
   ├── 04 perturbation ◄── perturbation_space/
   ├── 05 neural space ◄── SDM z-maps (step 01)
   ├── 06 gradients ◄── neural features (step 05)
   ├── 07 component regression ◄── steps 03-06
   ├── 08 interaction models ◄── steps 03-06
   ├── 09 sham heterogeneity ◄── steps 04-06 + sensory/
   ├── 10 RSA ◄── dissimilarity matrices (steps 04-06)
   ├── 11 sensitivity ◄── all prior outputs
   └── 12 figures/tables ◄── all prior outputs
```

## How to run

Each step is independently runnable:

```bash
cd data_analysis/06_gradient_analysis
python gradients.py
```

Steps must be run in order — each depends on prior outputs. The SDM step (01) must complete before step 05 can run. Steps 02-04 can run in parallel since they read independent processing outputs.

## Configuration

All paths and shared parameters are defined in `data_analysis/config.py`.
