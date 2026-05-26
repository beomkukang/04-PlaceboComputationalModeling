# Clinical Data Processing: Methods Documentation

This document describes the methodology for parsing and standardizing clinical outcome data from the included studies. It is written for direct adaptation into the manuscript Methods section.

---

## Methods Text (for manuscript)

### Clinical outcome extraction and standardization

Clinical and behavioral outcomes were extracted verbatim from each included study, preserving the original reported values, instruments, timepoints, and sample sizes. A total of 1,809 clinical outcome entries were identified across 159 studies.

#### Value parsing

Reported values were parsed from free-text strings into structured numerics using automated regex-based parsers. The following reporting formats were handled:

- **Mean ± SD** (63.8% of entries): Extracted directly.
- **Mean ± SE/SEM** (2.9%): SE converted to SD via SD = SE × √n.
- **Mean (95% CI)** (6.4%): SD estimated via SD = (CI_upper − CI_lower) / (2 × 1.96) × √n.
- **Median [IQR]** (6.5%): Mean and SD approximated using the method of Wan et al. (2014): mean ≈ (Q1 + median + Q3) / 3; SD ≈ (Q3 − Q1) / 1.35.
- **Count/percentage** (4.6%): Preserved as-is for responder analyses.
- **Pre/post compound values**: Both timepoints extracted from single entries.

Unicode characters (minus signs U+2212, en-dashes U+2013, plus-minus signs U+00B1) were normalized prior to parsing.

#### Timepoint classification

Each outcome entry was classified into baseline, post-treatment, follow-up, during treatment, or other based on the reported timepoint description.

#### Instrument direction coding

The direction of clinical improvement (higher_is_better vs. lower_is_better) was coded for each outcome instrument using a manually curated lookup table covering the 50+ instruments in the dataset. This is necessary because some scales improve by increasing (e.g., MMSE cognitive score, 0–30) while others improve by decreasing (e.g., VAS pain, 0–10). The direction determines the sign of the standardized effect size.

#### Within-arm standardized effect size (R_within)

For studies reporting both baseline and post-treatment values for the same outcome measure within the same treatment arm, a within-arm standardized effect size was computed as:

R_within = direction × (post_mean − baseline_mean) / baseline_SD

where direction = +1 if higher scores indicate improvement, and −1 if lower scores indicate improvement. The Hedges small-sample correction factor was applied:

J = 1 − 3 / (4(n − 1) − 1)

R_within_corrected = J × R_within

This produces a unit-free effect size where positive values indicate clinical improvement, regardless of the original instrument or disease domain. This approach standardizes across heterogeneous outcome measures (e.g., pain VAS, depression scales, cognitive tests, disability indices) by expressing each study's clinical change relative to its own baseline variability.

#### Study-level clinical responsiveness

For each study, a single clinical responsiveness value was derived from the corrected R_within of the primary clinical outcome. When multiple outcomes were available, selection followed a domain priority hierarchy: pain > symptom severity > mood > function > cognition > quality of life. Verum/acupuncture arms were preferred over sham arms when both were available. This study-level responsiveness score was used as a meta-regression covariate in SDM-PSI analyses.

#### Exclusions

- Entries reported as narrative only (e.g., "significant improvement observed") were excluded from quantitative effect size computation.
- Entries reporting only p-values without group means or SDs were excluded.
- Studies with healthy volunteers only (no disease-relevant clinical outcomes) were excluded from clinical responsiveness computation.
- Physiological measures (e.g., polysomnography parameters, blood pressure, heart rate variability, chromatographic peak areas) were parsed but not included in the primary clinical responsiveness covariate, as these represent mechanistic rather than clinical endpoints.

### References

Wan, X., Wang, W., Liu, J., & Tong, T. (2014). Estimating the sample mean and standard deviation from the sample size, median, range and/or interquartile range. *BMC Medical Research Methodology*, 14, 135. https://doi.org/10.1186/1471-2288-14-135

---

## Implementation Details (not for manuscript)

### Pipeline: `07_build_clinical_files.py`

**Inputs:**
- `data_extraction/raw_extractions/*.json` — 159 raw extraction files
- `data_processing/v1/parse_utils.py` — regex parsers + instrument lookup

**Outputs:**
- `clinical/clinical_parsed.csv` — all outcomes with parsed numerics (1,809 rows)
- `clinical/clinical_effect_sizes.csv` — within-arm Hedges' g per study-arm-outcome pair
- `clinical/clinical_responsiveness.csv` — one R_within per study (for SDM meta-regression)
- `clinical/brain_clinical_correlations.csv` — neural contrasts correlated with clinical outcomes
- `clinical/responder_data.csv` — responder count data
- `clinical/parse_report.txt` — parsing success/failure summary + unmatched instruments

### Instrument lookup table: `parse_utils.py → INSTRUMENT_LOOKUP`

Manually curated dictionary mapping 60+ instrument name variants to:
- `higher_is_better` (bool): direction of clinical improvement
- `scale_min`, `scale_max` (float): scale bounds (for optional POMP computation)
- `domain` (str): clinical domain

Matching uses exact match, case-insensitive match, and abbreviation-based fuzzy matching (e.g., "VAS" → Visual Analog Scale).

### Unmatched instruments

Instruments not in the lookup table are flagged in `parse_report.txt`. These can be:
1. Added to `INSTRUMENT_LOOKUP` manually
2. Sent to Claude API for direction coding (~$1)
3. Excluded from effect size computation

### Conversion formulas

| Input format | Conversion | Reference |
|---|---|---|
| SE → SD | SD = SE × √n | Standard |
| 95% CI → SD | SD = (CI_hi − CI_lo) / 3.92 × √n | Standard |
| Median + IQR → Mean + SD | mean ≈ (Q1 + M + Q3) / 3; SD ≈ (Q3 − Q1) / 1.35 | Wan et al. 2014 |
