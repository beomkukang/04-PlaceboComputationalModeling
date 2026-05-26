# Step 02: Contrast Classification

Classified all contrasts from extracted papers into contrast categories using Claude API.

## Method
- Claude API (claude-sonnet) classified each contrast by condition type (verum/sham/rest) and contrast category
- Categories: sham_gt_rest, verum_gt_sham, verum_gt_rest, sham_post_gt_pre, verum_post_gt_pre, group_comparison, deactivation, correlation_deqi, correlation_expectancy, correlation_clinical, other
- Also assigned tissue_level (1-4) for sham conditions

## Output
- `contrast_classifications.csv` — all contrasts with category, tissue level, usability flag

## Scripts (archived)
`archive/scripts/data_processing_v1/01_classify_contrasts.py`

## Status: Complete
