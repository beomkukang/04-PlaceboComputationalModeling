# Analysis Pipeline

## Overview

Each acupuncture-like intervention is positioned in a multidimensional perturbation space defined by bodily afferent input, deqi/interoceptive response, and cognitive-perceptual modulation. The pipeline tests whether these components explain graded neural-response patterns and clinical responsiveness.

## Steps

| # | Directory | What | Status |
|---|-----------|------|--------|
| 00 | `00_literature_search/` | PRISMA systematic search (PubMed, Embase, WoS) | Complete |
| 01 | `01_pdf_extraction/` | Claude API extraction from 159 PDFs | Complete |
| 02 | `02_contrast_classification/` | Contrast categorization + tissue level coding | Complete |
| 03 | `03_coordinate_preparation/` | Stat conversion, MNI harmonization, SDM/MACM files | Complete |
| 04 | `04_covariate_encoding/` | Meta-regression predictors, perturbation space, sensory/deqi | Complete |
| 05 | `05_clinical_outcomes/` | Clinical parsing, effect sizes, responsiveness | Complete |
| 06 | `06_sdm_meta_analysis/` | SDM-PSI: preprocessing, mean, FWE, threshold, meta-regression | **In progress** |
| 07 | `07_data_validation/` | QC: missing IDs, duplicates, outliers, scale validity | Ready |
| 08 | `08_perturbation_space/` | PCA, Gower distances, RSA dissimilarity matrices | Ready |
| 09 | `09_clinical_responsiveness/` | Domain-aggregated and global responsiveness | Ready |
| 10 | `10_neural_space/` | Atlas parcellation of SDM z-maps → neural features | Needs step 06 |
| 11 | `11_gradient_analysis/` | PCA on neural features → neural gradients | Needs step 10 |
| 12 | `12_component_regression/` | Mixed-effects: components → neural + clinical outcomes | Needs steps 09-11 |
| 13 | `13_component_interaction/` | Additive vs amplification vs substitution vs overlap | Needs steps 09-11 |
| 14 | `14_sham_heterogeneity/` | Explain sham neural variation via component covariates | Needs steps 08-11 |
| 15 | `15_rsa/` | Mantel tests: perturbation ↔ neural ↔ clinical distances | Needs steps 08-10 |
| 16 | `16_sensitivity/` | Leave-one-out, imaging family, population robustness | Needs all prior |
| 17 | `17_figures_tables/` | Publication figures (9) and tables (8) | Needs all prior |

## Data flow

```
data/pdfs/ (159 papers)
    ↓ step 01
data/raw_extractions/ (158 JSONs)
    ↓ step 02
pipeline/02_*/contrast_classifications.csv
    ↓ step 03
pipeline/03_*/sdm/ (coordinates) + macm/ (pooled DB)
    ↓ steps 04-05
pipeline/04_*/ (covariates, sensory) + pipeline/05_*/clinical/
    ↓ step 06
pipeline/06_*/sdm_projects/ (z-maps, corrp_tfce)
    ↓ steps 07-17
outputs/ (qc, behavioral, neural, gradients, models, figures, tables)
```

## Configuration

All paths defined in `pipeline/config.py`. Every analysis script imports it automatically.

## Running

Steps 00-05 are complete (outputs only, scripts archived).

For step 06 (SDM), run on a machine with sufficient RAM:
```bash
cd pipeline/06_sdm_meta_analysis
./production_sdm.sh          # all steps
./step2_mean_analysis.sh     # or individual steps
```

For steps 07-17 (Python), run from project root:
```bash
python pipeline/07_data_validation/validate.py
python pipeline/08_perturbation_space/perturbation.py
# etc.
```
