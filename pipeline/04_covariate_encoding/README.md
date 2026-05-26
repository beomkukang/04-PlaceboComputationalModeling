# Step 04: Covariate Encoding

Encoded intervention characteristics into numeric predictors for meta-regression and perturbation space analysis.

## Method
- **Meta-regression predictors** (Claude Batch API): Coded physical properties (penetration, stimulation, manipulation) and treatment meaning (blinding, credibility, expectancy) as numeric Axis A / Axis B variables
- **Perturbation space**: Flattened arm-level intervention details into component matrix; separate sham decomposition table
- **Sensory/deqi data**: Extracted deqi subscales, blinding assessments, sensation comparisons

## Outputs
- `meta_regression/study_predictors.csv` — numeric predictor matrix per arm
- `meta_regression/interaction_terms.csv` — pre-computed interaction terms
- `perturbation_space/arm_components.csv` — full arm component matrix
- `perturbation_space/sham_decomposition.csv` — sham-specific decomposition
- `sensory/deqi_summary_by_arm.csv`, `deqi_subscales.csv`, `blinding_assessment.csv`, `sensation_verum_vs_sham.csv`

## Scripts (archived)
`archive/scripts/data_processing_v1/04_build_meta_regression.py`, `05_build_perturbation_space.py`, `06_build_sensory_files.py`

## Status: Complete
