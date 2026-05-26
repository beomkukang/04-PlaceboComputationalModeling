# Step 05: Clinical Outcomes

Parsed clinical outcome values, computed standardized effect sizes, and built analysis-ready clinical CSVs.

## Method
- Parsed free-text clinical values into structured numeric format (means, SDs, sample sizes)
- Computed Hedges' g effect sizes with small-sample correction
- Computed within-arm and between-arm responsiveness scores
- Direction-corrected all outcomes (positive = improvement)
- See `clinical/CLINICAL_METHODS.md` for full methodology

## Outputs
- `clinical/clinical_parsed.csv` — all parsed outcome values
- `clinical/clinical_effect_sizes.csv` — standardized effect sizes
- `clinical/clinical_responsiveness.csv` — pre-computed responsiveness scores
- `clinical/brain_clinical_correlations.csv` — brain-clinical correlation data
- `clinical/outcomes_by_arm.csv` — outcomes organized by arm
- `clinical/responder_data.csv` — responder analysis data
- `clinical/parse_report.txt` — parsing quality report
- `clinical/CLINICAL_METHODS.md` — detailed methods documentation

## Scripts (archived)
`archive/scripts/data_processing_v1/07_build_clinical_files.py`

## Status: Complete
