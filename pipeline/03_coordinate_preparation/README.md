# Step 03: Coordinate Preparation

Built SDM-PSI coordinate input files and MACM database from classified contrasts.

## Method
- All statistics standardized and converted to t-values (z->t, F->t, r->t, p->t)
- Talairach coordinates converted to MNI via Lancaster transform
- MNI bounds checked (-90<x<90, -126<y<90, -72<z<108)
- One coordinate file per contrast category

## Outputs
- `sdm/` — 17 coordinate files for SDM-PSI (one per contrast family + tissue level subgroups)
- `macm/all_coordinates_pooled.csv` — master coordinate database (all peaks)
- `macm/study_contrast_index.csv` — study-contrast index
- `stat_conversion_log.csv` — debugging log for all stat conversions

## Scripts (archived)
`archive/scripts/data_processing_v1/02_build_sdm_files.py`, `03_build_macm_files.py`

## Status: Complete
