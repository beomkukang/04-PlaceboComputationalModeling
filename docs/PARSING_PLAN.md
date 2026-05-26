# Parsing Plan: Deqi/Sensory and Clinical Data

## Problem

Our raw extraction JSONs store behavioral values as free-text strings:
```
"value_exact": "3.2 ± 1.1"
"value_exact": "median 4 [IQR 3-6]"
"value_exact": "deqi sensation elicited"
"value_exact": "Pre: 52.00 + 7.14; Post: 46.71 + 7.25"
```

The analysis plan requires structured numerics:
```
value_mean: 3.2, value_sd: 1.1, n: 20, reporting_format: "mean_sd"
```

Without parsing, we cannot compute standardized effect sizes, perturbation indices, RSA distances, or any gradient analysis.

---

## Data Inventory

### Deqi / Sensory (159 papers)

**STATUS: Deqi will NOT be used as a separate analysis space or continuous meta-regression covariate.**

#### Why

Investigation of the raw data revealed fatal heterogeneity:

1. **Instrument inconsistency**: MASS (~79 instances across variants), VAS (22), NRS (12), custom scales, plus narrative-only entries. No single instrument dominates enough for cross-study normalization.

2. **MASS subscale reporting varies per study**: studies report different subsets of subscales (4 to 13 subscales). No consistent composite (MASS Index) can be computed across studies because the denominator changes.

3. **Scale anchors differ**: 0-10, 0-20, 0-100, categorical — POMP normalization assumes scale boundaries are known but many are ambiguous.

4. **Coverage breakdown (159 studies)**:
   - ~71% narrative only ("deqi was elicited")
   - ~9% fully structured numeric (parseable subscales)
   - ~6% mixed numeric + narrative
   - ~13% not reported

5. **Consequence**: No defensible way to produce a single normalized deqi intensity score or multidimensional sensory profile that is comparable across studies.

#### What we WILL do with deqi

| Output | N studies | Use |
|---|---|---|
| `deqi_present` (binary 0/1) | ~150 | SDM meta-regression covariate; descriptive table |
| `deqi_subscale_table` (raw parsed) | ~25 | Descriptive reporting only; not used in formal analysis |
| Narrative summary per study | all | Supplementary table |

#### What we will NOT do

- ~~Continuous deqi intensity covariate for meta-regression~~ (too few comparable values)
- ~~Multidimensional sensory space for RSA~~ (inconsistent subscale coverage)
- ~~POMP normalization across instruments~~ (incomparable scales)
- ~~MASS Index computation from subscales~~ (variable subscale sets per study)

#### Parsing approach (simplified)

Deqi parsing reduces to:
1. **Binary classification** (regex): detect "deqi achieved/elicited" vs "no deqi" → `deqi_present: 0/1`
2. **Raw numeric extraction** (regex): extract whatever numbers are reported with their instrument name → descriptive table only
3. No Claude API needed for deqi — binary classification is sufficient for the covariate

### Clinical Outcomes (134 papers, ~300 entries)

| Format | Count | Parseable? | Output |
|---|---|---|---|
| mean ± SD ("16.17 ± 5.28") | 225 | **Yes — regex** | mean, sd |
| median [IQR] | 17 | **Yes — regex** | median, iqr_low, iqr_high |
| narrative ("improved") | 22 | **No** | exclude from quantitative |
| mean (95% CI) | 10 | **Yes — regex** | mean, ci_low, ci_high |
| count/percentage | 17 | **Yes — regex** | count, pct |
| mean ± SE | 7 | **Yes — regex** | mean, se |
| change score ("-3.87; 95% CI...") | 5 | **Yes — regex** | change, ci |
| p-value only | 7 | **No** | flag as insufficient |
| other complex formats | ~20 | **Claude API** | varies |

**Realistic yield:**
- Parseable to mean + SD (or convertible): ~250 entries
- Unparseable: ~50 entries

---

## Parsing Strategy

### Step 1: Regex Parser (local, $0)

Python regex functions that handle known formats:

```python
def parse_mean_sd(text):
    """Parse '16.17 ± 5.28' or '3.07 + 0.51' or '13.10± 2.22 (10-16)'"""
    # Handle unicode ± and +
    # Handle optional trailing (range) or , p<value
    # Return: {"mean": float, "sd": float}

def parse_mean_se(text):
    """Parse 'mean ± SE' when explicitly labeled"""
    # Return: {"mean": float, "se": float}

def parse_median_iqr(text):
    """Parse 'median 4 [IQR 3-6]' or '5.2 [3.1, 7.8]'"""
    # Return: {"median": float, "iqr_low": float, "iqr_high": float}

def parse_mean_ci(text):
    """Parse '-3.87; 95% CI, -2.21 to -7.32'"""
    # Return: {"mean": float, "ci_low": float, "ci_high": float}

def parse_count_pct(text):
    """Parse '23 (85.2%)' or '6 of 9'"""
    # Return: {"count": int, "pct": float, "total": int}

def parse_pre_post(text):
    """Parse 'Pre: 3.07 + 0.51; Post: 2.43 + 0.36'"""
    # Return: {"pre_mean": float, "pre_sd": float, "post_mean": float, "post_sd": float}

def parse_narrative_deqi(text):
    """Parse narrative deqi descriptions for binary presence"""
    # Keywords: "deqi", "de qi", "achieved", "elicited", "sensation"
    # Negative: "no deqi", "without deqi", "did not achieve"
    # Return: {"deqi_present": 0 or 1}
```

**Format detection priority:**
1. Try `parse_mean_sd` first (most common)
2. Try `parse_median_iqr`
3. Try `parse_mean_ci`
4. Try `parse_count_pct`
5. Try `parse_pre_post`
6. Try `parse_mean_se`
7. If all fail → mark as `unparseable`

### Step 2: Claude API for Unparseable Cases (~$1-2)

Send the ~50-70 unparseable entries to Claude with:

```
Given this reported value and its context, extract structured numerics:

Value: "-21.3 ± 22.0% (mean ± SD)"
Measure: "BCTQ symptom severity scale"
Format: "change_score"

Return JSON: {"value_mean": -21.3, "value_sd": 22.0, "is_percentage": true, "is_change": true}
```

### Step 3: Compute Derived Variables (local, $0)

#### Deqi Derived Variables

```python
# Binary only — see "Deqi / Sensory" status above
deqi_present = 1 if any deqi keywords in narrative, else 0
# No continuous intensity or subscale composites (data too heterogeneous)
```

#### Clinical Derived Variables

```python
# Within-arm standardized response (Hedges' g)
# direction: +1 if higher=better, -1 if lower=better
R_within = direction * (post_mean - baseline_mean) / baseline_sd

# Apply Hedges correction for small samples
J = 1 - 3 / (4 * (n - 1) - 1)
R_within_corrected = J * R_within

# POMP (Percentage of Maximum Possible score)
POMP = 100 * (score - scale_min) / (scale_max - scale_min)
POMP_change = POMP_post - POMP_baseline

# Controlled response (when both verum and sham arms exist)
R_controlled = direction * [(post_v - base_v) - (post_s - base_s)] / pooled_sd

# Derivability flag
derivable = True if (mean AND sd AND n are available for both timepoints)
```

#### SE → SD Conversion

```python
# When SE is reported instead of SD
sd = se * sqrt(n)
```

#### Median/IQR → Mean/SD Approximation

```python
# Wan et al. (2014) method for meta-analysis
# When median (m) and IQR (q1, q3) are reported:
mean_approx = (q1 + m + q3) / 3
sd_approx = (q3 - q1) / 1.35
```

---

## Output Files

### Deqi / Sensory

**`data_processing/v1/sensory/deqi_parsed.csv`**

```
pmid, arm_id, arm_type, measure, instrument,
deqi_present,           # 0/1 (from all 150 papers)
value_mean,             # numeric (from ~42 papers)
value_sd,               # numeric
value_se,               # numeric
value_median,           # numeric
value_iqr_low,          # numeric
value_iqr_high,         # numeric
n_analyzed,             # integer
scale_min,              # numeric
scale_max,              # numeric
reporting_format,       # mean_sd / mean_se / median_iqr / narrative / other
parse_method,           # regex / claude / manual
parse_confidence,       # high / medium / low
original_value_exact    # preserved original string
```

**`data_processing/v1/sensory/deqi_subscales_parsed.csv`**

```
pmid, arm_id, sensation,
value_mean, value_sd, n_analyzed,
original_value_exact
```

Sensations: soreness, heaviness, numbness, tingling, warmth, pressure, sharp_pain, spreading, fullness, aching

**`data_processing/v1/sensory/deqi_derived.csv`**

```
pmid, arm_id,
deqi_present,           # binary
deqi_total_intensity,   # continuous (where available)
nonpain_deqi_score,     # mean of non-pain subscales
sharp_pain_score,       # separate
n_subscales_available,  # how many subscales were reported
data_quality            # complete / partial / binary_only
```

### Clinical Outcomes

**`data_processing/v1/clinical/clinical_parsed.csv`**

```
pmid, arm_id, arm_type, outcome_measure, outcome_domain, scale_name,
timepoint,              # baseline / post / followup / change
value_mean,             # numeric
value_sd,               # numeric
value_se,               # numeric (before conversion)
value_median,           # numeric
value_iqr_low,          # numeric
value_iqr_high,         # numeric
n_analyzed,             # integer
higher_is_better,       # true / false / unclear
scale_min,              # numeric (if known)
scale_max,              # numeric (if known)
reporting_format,       # mean_sd / median_iqr / count / narrative / other
parse_method,           # regex / claude / manual
parse_confidence,       # high / medium / low
original_value_exact    # preserved original string
```

**`data_processing/v1/clinical/clinical_derived.csv`**

```
pmid, arm_id, outcome_measure, outcome_domain,
R_within,               # within-arm standardized response
R_within_corrected,     # Hedges-corrected
POMP_baseline,          # POMP at baseline
POMP_post,              # POMP at post
POMP_change,            # POMP change
R_controlled,           # controlled effect (where comparator exists)
effect_size_type,       # SMD / hedges_g / POMP / none
derivable,              # true / false
derivation_notes        # what was available / what's missing
```

---

## Known Challenges

### 1. Heterogeneous Formatting

Same statistic reported differently:
- `"3.07 + 0.51"` (uses + instead of ±)
- `"3.07±0.51"` (no spaces)
- `"3.07 ± 0.51 (p<0.05)"` (trailing p-value)
- `"13.10± 2.22 (10–16)"` (trailing range)
- `"Pre-acupuncture: 3.07 + 0.51; Post-acupuncture: 2.43 + 0.36"` (compound)
- `"12.9 (standard deviation, 10.7)"` (SD in parenthetical)

Regex must handle all variants.

### 2. Unicode Characters

- `±` (U+00B1) vs `+` vs `−` (U+2212) vs `-`
- En dash `–` (U+2013) in ranges: `"(10–16)"`
- Must normalize before parsing.

### 3. Ambiguous SD vs SE

Some papers report `mean ± SE` but label it as `mean ± SD`. The `reporting_format` field from extraction helps, but may be wrong. Flag ambiguous cases.

### 4. Missing Sample Sizes

SE → SD conversion requires n. If n is missing, SE cannot be converted. Flag as `derivable: false`.

### 5. Direction of Clinical Outcomes

Higher pain score = worse, but higher function score = better. The `higher_is_better` field determines the sign of R_within. If unclear, flag.

### 6. Multiple Timepoints

Some papers report baseline, post-treatment, and follow-up. Each gets its own row. R_within is computed for each post-treatment timepoint relative to baseline.

### 7. Aggregate vs Individual Deqi

Most papers report group-level deqi (mean across participants). Some report individual-level counts ("6 of 9 reported deqi"). Both are valid but represent different information.

---

---

## SDM-PSI Meta-Regression Requirements

### Current status: NOT possible

SDM-PSI meta-regression requires numeric covariates in `sdm_table.txt`. Currently we only have `tissue_level` (binary). The analysis plan requires testing whether intervention component variables predict voxel-wise neural responses across studies.

### What meta-regression needs

Each covariate must be a single numeric column in `sdm_table.txt`, with one value per study. This means collapsing arm-level and outcome-level data to **one number per study**.

#### Covariates from Axis A (bodily input) — requires `05_build_perturbation_space.py` revision

| Covariate | Source | How to derive study-level value |
|---|---|---|
| `penetration_level` | intervention arms | Verum arm penetration code (0-3) |
| `afferent_index` | intervention arms | Composite of penetration + manipulation + electrical + needles + sessions |
| `n_needles` | intervention arms | Verum arm needle count |
| `n_sessions` | intervention arms | Total treatment sessions |
| `retention_min` | intervention arms | Needle retention duration |
| `electrical_stim` | intervention arms | Binary (0/1) |

**Blocked by**: free-text intervention descriptions → need Claude API to code numerically (~$2)

#### Covariates from Deqi (sensory/interoceptive)

| Covariate | Source | How to derive study-level value |
|---|---|---|
| `deqi_present` | sensory data | Binary: did verum arm report deqi? (0/1) |

**Status**: `deqi_present` (binary) is feasible via regex — simple keyword detection. `deqi_intensity` (continuous) is **dropped** due to cross-study instrument heterogeneity (see Deqi status above).

**Coverage**: `deqi_present` available for ~150 studies

#### Covariates from Axis B (cognitive-perceptual) — requires parsed + coded data

| Covariate | Source | How to derive study-level value |
|---|---|---|
| `blinding_present` | study design | Binary (0/1) |
| `blinding_quality` | study design | 0=none, 1=single, 2=double |
| `expectancy_score` | sensory/behavioral data | Mean expectancy rating |
| `credibility_score` | sensory/behavioral data | Mean credibility rating |
| `prior_experience_naive` | intervention arms | Binary: were participants acupuncture-naive? |
| `cognitive_anchoring_proxy` | intervention arms | Composite of blinding + ritual + rationale + device credibility |

**Blocked by**: free-text descriptions → need Claude API to code (~$2), plus parsed expectancy/credibility values

**Coverage**: `blinding_present` available for most studies, `expectancy_score` for ~10%, `credibility_score` for ~15%

#### Covariates from Clinical Outcomes — requires parsed clinical data

| Covariate | Source | How to derive study-level value |
|---|---|---|
| `clinical_responsiveness` | clinical outcomes | R_within (standardized pre-post change) for primary outcome |
| `disease_domain` | study metadata | Categorical: pain/motor/mood/cognition/sleep/GI/other |
| `population_type` | study metadata | healthy/clinical |

**Blocked by**: free-text clinical values → need regex parsing (Steps 3-4 of this plan)

#### Study-level covariates (already available)

| Covariate | Source | Status |
|---|---|---|
| `tissue_level` | contrast classifications | **Available** — binary (0=non-penetrating, 1=penetrating) |
| `scanner_field_strength` | study metadata | Available in raw JSONs, needs extraction |
| `sample_size` | sdm_table | **Available** as n1/n2 |

### SDM meta-regression command syntax

After adding covariates to `sdm_table.txt`:

```
study  n1  n2  t_thr  tissue_level  afferent_index  deqi_intensity  blinding_quality
15193624  74  74  3.1  0  3.5  2.1  1
17240066  48  48  3.1  0  2.0  NA  2
...
```

SDM commands:
```bash
# Single covariate
sdm.bat "afferent_reg = mi_lm afferent_index,0+1,50"
sdm.bat "perm afferent_reg,1000,6"
sdm.bat "threshold analysis_afferent_reg/corrp_tfce,analysis_afferent_reg/afferent_reg_z,0.05,10"

# Multiple covariates
sdm.bat "multi_reg = mi_lm afferent_index+blinding_quality,0+1+1,50"
```

### What we can run NOW (without parsing)

| Regression | Covariate | Studies | Feasible? |
|---|---|---|---|
| Tissue level on sham_gt_rest | `tissue_level` (binary) | 21 | **YES** |
| Sample size on any analysis | `n1` (already in table) | all | **YES** |

### What we can run AFTER parsing

| Regression | Covariate | Estimated studies with data | Minimum needed |
|---|---|---|---|
| Afferent index | `afferent_index` | ~all (from intervention descriptions) | 10 |
| Deqi presence | `deqi_present` | ~150 (binary) | 10 |
| ~~Deqi intensity~~ | ~~`deqi_intensity`~~ | ~~~42 (continuous)~~ | **Dropped** — instrument heterogeneity |
| Blinding quality | `blinding_quality` | ~80 | 10 |
| Expectancy | `expectancy_score` | ~15 | **Insufficient** |
| Credibility | `credibility_score` | ~20 | **Marginal** |
| Clinical responsiveness | `R_within` | ~100 | 10 |
| Cognitive anchoring proxy | `cognitive_anchoring_proxy` | ~80 | 10 |

### Summary

Meta-regression is blocked by the same parsing gap as the Python analyses. The implementation order:

1. Parse deqi → `deqi_present` and `deqi_intensity` available as covariates
2. Parse clinical → `R_within` available as covariate
3. Code Axis A numerically (Claude API) → `afferent_index` available
4. Code Axis B numerically (Claude API) → `blinding_quality`, `cognitive_anchoring_proxy` available
5. Update `sdm_table.txt` with new columns
6. Run SDM linear model commands

---

## Implementation Order

```
Step 1: Build regex parser functions (local)
Step 2: Run on all sensory data → deqi_parsed.csv, deqi_derived.csv
Step 3: Run on all clinical data → clinical_parsed.csv, clinical_derived.csv
Step 4: Send unparseable cases to Claude API (~$1-2)
Step 5: Code Axis A/B intervention features numerically (Claude API ~$2)
Step 6: Build meta-regression covariate table (local)
Step 7: Update sdm_table.txt with covariates
Step 8: Update 08_build_rsa_matrices.py with numeric inputs
Step 9: Run SDM meta-regressions
```

## Total Cost: ~$3-4 (Claude API for unparseable values + Axis A/B coding)

## Scripts to Create/Revise

```
data_processing/v1/
├── parse_utils.py              # NEW: regex parsers + format detection
├── 05_build_perturbation_space.py  # REVISE: code Axis A/B numerically (Claude API)
├── 06_build_sensory_files.py   # REVISE: use parse_utils, output parsed CSVs
├── 07_build_clinical_files.py  # REVISE: use parse_utils, compute R_within
├── 08_build_rsa_matrices.py    # REVISE: use numeric inputs
├── 10_build_regression_table.py    # NEW: merge covariates into sdm_table.txt format
```
