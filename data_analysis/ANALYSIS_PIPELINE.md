# Full Analysis Pipeline

## Overview

All SDM-PSI analyses run via Docker (Linux binary) because the Mac binary crashes.
Each analysis goes through: Preprocessing → Mean (50 imputations) → FWE (1000 permutations) → Threshold.

## Learned requirements

- **Docker memory**: minimum 8GB (TFCE step loads ~2GB of imputations)
- **Perm syntax**: `perm model_name,n_permutations` (model FIRST, comma, then count)
- **Threads**: sdm_parse ignores XML nThreads — must be passed differently (TBD)
- **Statistics**: all converted to t-values before SDM input (z→t, F→t, r→t)
- **ICA studies excluded**: ICA z-scores incompatible with SDM-PSI

## Analyses to run

| # | Analysis | Studies | Peaks | Priority | Hypothesis |
|---|---|---|---|---|---|
| 1 | sham_gt_rest | 21 | 668 | **Primary** | What does sham activate? |
| 2 | verum_gt_sham | 39 | 708 | **Primary** | What does verum add? |
| 3 | verum_gt_rest | 31 | 823 | **Primary** | Full acupuncture effect |
| 4 | sham_gt_rest_penetrating | 11 | 349 | Subgroup | H1: bodily input |
| 5 | sham_gt_rest_nonpenetrating | 9 | 170 | Subgroup | H1: bodily input |
| 6 | verum_post_gt_pre | 50 | 702 | Secondary | Longitudinal change |
| 7 | sham_post_gt_pre | 18 | 204 | Secondary | Placebo longitudinal |
| 8 | deactivation | 51 | 1047 | Secondary | Signal decreases |
| 9 | group_comparison | 53 | 1045 | Exploratory | Multi-group |
| 10 | correlation_clinical | 12 | 126 | Exploratory | H5: clinical link |

## After SDM-PSI

| Step | Tool | Input | Output |
|---|---|---|---|
| Visualize brain maps | Python/Nilearn | corrp_tfce.nii.gz | Publication figures |
| Extract peak coordinates | Python/Nibabel | Thresholded maps | Results tables |
| Meta-regression | SDM-PSI linear model | sdm_table + predictors | Regression maps |
| MACM | Python | Coordinate database | Co-activation profiles |
| RSA | Python | Dissimilarity matrices | Mantel test results |

## Scripts needed

```
data_analysis/
├── ANALYSIS_PIPELINE.md              # This file
├── SDM_PSI_DIRECTIONS.md             # Detailed SDM-PSI tutorial
├── 01_sdm_preparation/
│   ├── prepare_sdm.py                # Convert our data → SDM format
│   ├── run_sdm_docker.sh             # Run all SDM analyses via Docker
│   ├── Dockerfile                    # SDM-PSI Linux container
│   └── sdm_projects/                 # Generated SDM project dirs
├── 02_visualize_results/
│   ├── plot_brain_maps.py            # Nilearn visualization
│   ├── extract_peaks.py              # Extract significant clusters/coords
│   └── compare_maps.py              # Pen vs non-pen comparison
├── 03_meta_regression/
│   ├── run_regression.sh             # SDM linear model via Docker
│   └── plot_regression.py            # Visualize regression results
├── 04_macm/
│   └── run_macm.py                   # Co-activation analysis
├── 05_rsa/
│   └── run_rsa.py                    # Representational similarity
├── 06_sensory_analysis/
│   └── analyze_deqi.py               # Deqi mediation (after fixing 05-08)
├── 07_clinical_analysis/
│   └── analyze_clinical.py           # Brain-clinical correlations
└── 08_figures/
    └── generate_figures.py           # Publication-ready figures
```

## Execution order

### Phase 1: SDM-PSI brain maps (current)
```bash
# Run all 10 analyses
caffeinate -i ./data_analysis/01_sdm_preparation/run_sdm_docker.sh
```

### Phase 2: Visualize and extract results
```bash
uv run python data_analysis/02_visualize_results/plot_brain_maps.py
uv run python data_analysis/02_visualize_results/extract_peaks.py
uv run python data_analysis/02_visualize_results/compare_maps.py
```

### Phase 3: Meta-regression (requires SDM-PSI)
```bash
caffeinate -i ./data_analysis/03_meta_regression/run_regression.sh
uv run python data_analysis/03_meta_regression/plot_regression.py
```

### Phase 4: Python analyses (no SDM needed)
```bash
uv run python data_analysis/04_macm/run_macm.py
uv run python data_analysis/05_rsa/run_rsa.py
```

### Phase 5: Sensory and clinical (after fixing data_processing 05-08)
```bash
uv run python data_analysis/06_sensory_analysis/analyze_deqi.py
uv run python data_analysis/07_clinical_analysis/analyze_clinical.py
```

### Phase 6: Publication figures
```bash
uv run python data_analysis/08_figures/generate_figures.py
```

## Estimated time

| Phase | Duration | Notes |
|---|---|---|
| Phase 1 (SDM-PSI) | ~12-24 hours | 10 analyses × 1-3 hrs each |
| Phase 2 (Visualize) | ~30 min | Local Python |
| Phase 3 (Regression) | ~3-6 hours | 2-3 regression models via Docker |
| Phase 4 (MACM/RSA) | ~1 hour | Local Python |
| Phase 5 (Sensory/Clinical) | TBD | Needs data processing fixes first |
| Phase 6 (Figures) | ~1 hour | Local Python |
