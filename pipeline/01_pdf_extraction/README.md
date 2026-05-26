# Step 01: PDF Extraction

Structured data extraction from 159 acupuncture-fMRI PDFs using Claude API.

## Method
- Claude API (Files API + Batch API) with structured extraction schema
- Extracted: study metadata, intervention arms, contrasts, peak coordinates, clinical outcomes, deqi/sensory data, blinding/credibility
- Multiple extraction passes: initial extraction, coordinate re-extraction, tissue level classification, sham-rest targeted extraction

## PMID fix (2026-05-25)
137/159 PDFs were filed under wrong PMID filenames. Fixed by title matching against the master study list. Correction map: `data/pmid_correction_map.csv`. Backups in `archive/pmid_fix_backups/`.

## Outputs
- 158 JSON files in `data/raw_extractions/` (one per paper)
- 5 removed extractions in `data/removed_raw_extractions/`

## Scripts (archived)
Original extraction scripts in `archive/scripts/data_extraction/`.

## Status: Complete
