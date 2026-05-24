# Analysis Plan: Embodied Placebo Neuroscience

## Conceptual Framework

The project models acupuncture-like interventions as points in a structured perturbation space, and maps them onto three response spaces. The central claim is that placebo-related responses emerge from the brain's integration of bodily afferent evidence (Axis A) and treatment meaning (Axis B), not from either alone.

```
PERTURBATION SPACE                    RESPONSE SPACES
(what was done)                       (what happened)

Axis A: Bodily input ──┐
                       ├──→  Space 1: Neural response (fMRI)
Axis B: Treatment      │         ↕
        meaning    ────┘     Space 2: Sensory / interoceptive response
                                 ↕
                             Space 3: Clinical / behavioral response
```

Each "space" is literally a data matrix. Each study or study-arm is a point (row) in that space. The columns are the measured variables. The analyses ask how positions in the perturbation space predict positions in the response spaces.

---

## The Spaces

### Perturbation Space (Intervention Component Space)

**What it is**: A multidimensional characterization of every intervention arm across all studies. Each arm is a point in this space.

**Axes**:

Axis A — Bodily afferent evidence (what the body received):
- Penetration level (none → superficial → standard → deep)
- Stimulation modality (manual / electro / laser / sham device)
- Electrical parameters (frequency, intensity)
- Manipulation intensity (none → mild → vigorous)
- Number of needles
- Number of sessions
- Needle retention duration
- Anatomical location relevance (disease-relevant vs not)
- Deqi intended (yes/no)

Axis B — Treatment meaning (what the participant believed/was told):
- Blinding method and quality
- Credibility of the procedure
- Expectancy level
- Prior acupuncture experience
- Verbal instructions / rationale given
- Practitioner interaction level
- Ritual context

**Key feature**: Sham arms are NOT at the origin. A Streitberger needle at real acupoints with a convincing rationale has moderate Axis A (skin contact, no penetration) and high Axis B (credible device, real points). A waitlist arm has zero on both axes.

**Visualization**: 
- 2D scatter: Axis A summary score × Axis B summary score, each point = one study arm
- Heatmap: arms × component variables
- PCA/MDS: reduce the full component matrix to 2-3 dimensions

**Data file**: `perturbation_space/arm_components.csv`

---

### Space 1: Neural Response Space

**What it is**: Brain activation and connectivity patterns evoked by or associated with the intervention. This is the primary outcome space.

**Dimensions**:
- Peak coordinates (x, y, z in MNI space) — where in the brain
- Activation direction (increase / decrease)
- Statistic magnitude (t/z value) — how strongly
- Analysis type (activation / connectivity / correlation)
- Contrast type (what comparison produced this result)

**Subspaces by contrast type**:

Each contrast type asks a different question and produces a different neural map:

| Contrast family | Question answered | Hypothesis tested |
|---|---|---|
| Verum > non-penetrating sham | What does real needling add beyond skin touch + meaning? | H1 (bodily input) |
| Verum > superficial sham | What does deep needling add beyond shallow needling? | H1 (graded bodily input) |
| Verum > off-point | Does acupoint location matter? | H1 (spatial specificity) |
| Sham > rest | What does sham alone activate? | H2 (meaning + minimal body) |
| Penetrating > non-penetrating sham | What does needle penetration alone do? | H1 (pure penetration) |
| Pre > post verum | How does the brain change after verum treatment? | H5 (downstream) |
| Pre > post sham | How does the brain change after sham treatment? | H5 (placebo longitudinal) |
| Deqi ~ brain | Where scales with interoceptive sensation? | H4 (deqi = salience) |
| Expectancy ~ brain | Where scales with belief? | H2 (treatment meaning) |
| Clinical change ~ brain | Where predicts symptom improvement? | H5 (clinical validation) |
| Responders > non-responders | What distinguishes who benefits? | H5 + H6 |

**Visualization**:
- SDM-PSI maps per contrast family (standard brain images)
- Conjunction / difference maps across contrast families
- MACM connectivity profiles from consistently activated seeds
- Meta-regression maps (where does penetration depth predict activation?)

**Data files**: `sdm/*.txt`, `macm/*.csv`

---

### Space 2: Sensory / Interoceptive Response Space

**What it is**: What participants reported feeling during or after the intervention. This space sits between the perturbation space and the neural space — it reflects how bodily input was consciously perceived.

**Dimensions**:
- Deqi total intensity
- Deqi subscales (soreness, heaviness, numbness, tingling, warmth, pressure, sharp pain)
- Pain intensity
- Unpleasantness
- Perceived penetration (did they think the needle went in?)
- Perceived realness (did they think the treatment was real?)
- Guessed allocation (did blinding work?)
- Credibility / expectancy ratings (post-treatment)

**Key theoretical role**: Deqi is treated not as an acupuncture-specific outcome but as an index of interoceptive-somatosensory salience — how much the body's signals reached conscious awareness. The interaction between bodily input (Axis A) and treatment meaning (Axis B) may be expressed through changes in this space.

**Analyses**:
- Deqi as mediator: Does bodily input → deqi → neural response? (mediation)
- Blinding as moderator: Does perceived realness change how bodily input maps to neural response? (moderation)
- Deqi-neural correlation: Which brain regions scale with deqi? (maps to SDM deqi_correlation)
- Between-arm sensation differences: Do verum and sham differ in sensation profile?

**Visualization**:
- Radar/spider plots: sensation profiles per arm type
- Scatter: deqi intensity vs neural activation in key ROIs
- Bar charts: blinding success across sham types

**Data files**: `sensory/deqi_summary_by_arm.csv`, `sensory/deqi_subscales.csv`, `sensory/blinding_assessment.csv`

---

### Space 3: Clinical / Behavioral Response Space

**What it is**: Downstream symptom and functional changes. This space is the translational validation layer — it tests whether neural and sensory placebo signatures actually predict clinical benefit.

**Dimensions**:
- Symptom change (pain, function, severity — varies by condition)
- Responder status
- Time course (immediate, post-treatment, follow-up)
- Disease domain (pain, migraine, IBS, stroke, insomnia, etc.)

**Key theoretical role**: Clinical response is downstream of embodied inference. The hypothesis is that it depends not just on physical stimulation or expectation alone, but on their integration through neural systems encoding bodily meaning, symptom appraisal, and descending regulation.

**Analyses**:
- Brain-clinical correlation: Which neural changes predict symptom improvement?
- Sensory-clinical link: Does deqi predict clinical outcome?
- Component-clinical link: Do Axis A or Axis B features predict clinical response?
- Responder neural profiles: Do responders show different brain patterns?

**Visualization**:
- Forest plots: clinical outcomes by contrast family
- Scatter: neural activation in key ROIs vs clinical change
- Mediation diagrams: intervention → neural → clinical

**Data files**: `clinical/outcomes_by_arm.csv`, `clinical/brain_clinical_correlations.csv`, `clinical/responder_data.csv`

---

## Cross-Space Analyses

The most important analyses are not within one space but across spaces:

### 1. Perturbation → Neural (meta-regression)
**Question**: Do Axis A/B features predict where the brain activates?

Method: SDM meta-regression with `study_predictors.csv` as covariates

Expected results:
- Axis A (penetration, stimulation) → S1, S2, thalamus, posterior insula
- Axis B (credibility, expectancy) → dlPFC, vmPFC, striatum, ACC
- Interaction → anterior insula, salience network, PAG

### 2. Perturbation → Sensory → Neural (mediation)
**Question**: Does deqi mediate the relationship between bodily input and neural response?

Method: Multi-level mediation across studies
- Path a: penetration level → deqi intensity
- Path b: deqi intensity → neural activation (from deqi_correlation SDM)
- Path c': penetration level → neural activation (from meta-regression)

### 3. Neural → Clinical (prediction)
**Question**: Do embodied placebo neural signatures predict clinical improvement?

Method: Overlap analysis between SDM maps and brain_clinical_correlations
- Do regions from verum > sham SDM overlap with regions correlating with clinical improvement?
- Do sham > rest SDM regions predict placebo response?

### 4. Full path: Perturbation → Neural → Clinical (mediation chain)
**Question**: Does the brain mediate the intervention-to-outcome relationship?

Method: Component-level mediation
- Axis A features → neural change → clinical improvement
- Axis B features → neural change → clinical improvement
- Interaction → neural change → clinical improvement

---

## Meta-Analytic Connectivity Modeling (MACM)

MACM extends the coordinate-based meta-analysis by asking: given that a region consistently activates, what else co-activates with it?

### Seed regions of interest (from framework's neural systems table):

| Seed | Rationale |
|---|---|
| Anterior insula | Integration of bodily and contextual salience |
| ACC / MCC | Salience, affective appraisal |
| dlPFC | Expectation, cognitive control |
| vmPFC / OFC | Value, belief updating |
| PAG | Descending pain modulation |
| S1 / S2 | Somatosensory input |
| Posterior insula | Interoceptive representation |
| Striatum | Reward prediction, treatment value |
| Thalamus | Sensory relay |

### MACM procedure:
1. From the master coordinate database, identify all studies with a peak within the seed ROI
2. Collect all other peaks from those studies
3. Run ALE/SDM on the collected peaks
4. Result: functional co-activation profile of the seed

### MACM comparisons:
- MACM for seed X across all contrasts → general co-activation
- MACM for seed X in verum contrasts only → acupuncture-specific network
- MACM for seed X in sham contrasts only → placebo-specific network
- Difference: verum MACM vs sham MACM → differential connectivity

---

## Hypothesis Testing Summary

| Hypothesis | Primary analysis | Data files needed |
|---|---|---|
| H1: Bodily input → somatosensory | SDM for verum > sham (by sham type) + meta-regression with Axis A | `sdm/verum_vs_*.txt` + `meta_regression/study_predictors.csv` |
| H2: Treatment meaning → valuation/salience | SDM for sham > rest + meta-regression with Axis B + expectancy_correlation SDM | `sdm/sham_vs_rest.txt` + `sdm/expectancy_correlation.txt` |
| H3: Interaction is central | Meta-regression with Axis A × B interaction terms + MACM of integration regions | `meta_regression/study_predictors.csv` + `macm/*.csv` |
| H4: Deqi = interoceptive salience | SDM deqi_correlation + deqi-neural mediation | `sdm/deqi_correlation.txt` + `sensory/deqi_summary_by_arm.csv` |
| H5: Clinical response is downstream | Brain-clinical correlation analysis + mediation | `clinical/brain_clinical_correlations.csv` + `sdm/clinical_correlation.txt` |
| H6: Embodied neural signatures predict outcome | Overlap of SDM maps with clinical correlation regions | Cross-map comparison |
| H7: Procedures separable in neural space | Compare SDM maps across contrast families + perturbation space clustering | All `sdm/*.txt` + `perturbation_space/arm_components.csv` |

---

## Representational Similarity Analysis (RSA)

RSA tests whether the similarity structure of interventions is preserved in neural, sensory, and clinical response spaces. If two interventions are similar in their body-meaning profile, do they also produce similar brain patterns?

This directly tests Hypothesis 7: "Are different acupuncture-like procedures separable in neural-response space according to their body-meaning profiles?"

### RSA logic

```
For each pair of studies (or study-arms):
  1. Compute distance in perturbation space (how different are the interventions?)
  2. Compute distance in neural space (how different are the brain responses?)
  3. Correlate the two distance matrices

If correlated → the brain's response geometry mirrors the intervention geometry
```

### RSA variants

| RSA comparison | Matrix 1 (model) | Matrix 2 (data) | Hypothesis |
|---|---|---|---|
| Body → Brain | Axis A distances | Neural pattern distances | H1: bodily input structure preserved in brain |
| Meaning → Brain | Axis B distances | Neural pattern distances | H2: belief structure preserved in brain |
| Full perturbation → Brain | Axis A+B distances | Neural pattern distances | H3: integrated body×meaning structure in brain |
| Body → Sensation | Axis A distances | Deqi/sensation distances | H4: bodily input drives interoceptive salience |
| Sensation → Brain | Sensation distances | Neural pattern distances | H4: sensation geometry maps to brain geometry |
| Brain → Clinical | Neural pattern distances | Clinical outcome distances | H5: neural similarity predicts clinical similarity |
| Full chain | Perturbation distances | Clinical distances | H5: do similar interventions produce similar outcomes? |

### Computing the dissimilarity matrices

**Perturbation dissimilarity** (Axis A, Axis B, combined):
- Euclidean or Gower distance across coded intervention features
- Computed from `arm_components.csv`

**Neural dissimilarity**:
- At the meta-analytic level, computed from coordinate overlap or spatial correlation between study-level SDM maps
- Alternative: Jaccard similarity of activated region sets
- Alternative: Euclidean distance between peak coordinate centroids

**Sensory dissimilarity**:
- Euclidean distance across deqi subscale profiles
- Computed from `deqi_subscales.csv`

**Clinical dissimilarity**:
- Standardized effect size differences across matching outcome measures
- Computed from `outcomes_by_arm.csv`

### RSA visualization
- Multidimensional scaling (MDS) plots of each space, colored by intervention type
- Scatter plots: perturbation distance vs neural distance (one point per study pair)
- Correlation matrix heatmaps for each dissimilarity matrix
- Mantel test results for matrix correlations

---

## Hypothesis Testing Summary

| Hypothesis | Primary analysis | Secondary analysis | Data files needed |
|---|---|---|---|
| H1: Bodily input → somatosensory | SDM for verum > sham (by sham type) + meta-regression with Axis A | Body → Brain RSA | `sdm/verum_vs_*.txt` + `meta_regression/study_predictors.csv` + `rsa/` |
| H2: Treatment meaning → valuation/salience | SDM for sham > rest + meta-regression with Axis B | Meaning → Brain RSA | `sdm/sham_vs_rest.txt` + `sdm/expectancy_correlation.txt` + `rsa/` |
| H3: Interaction is central | Meta-regression with Axis A × B interaction + MACM | Full perturbation → Brain RSA | `meta_regression/` + `macm/` + `rsa/` |
| H4: Deqi = interoceptive salience | SDM deqi_correlation + deqi-neural mediation | Body → Sensation RSA, Sensation → Brain RSA | `sdm/deqi_correlation.txt` + `sensory/` + `rsa/` |
| H5: Clinical response is downstream | Brain-clinical correlation + mediation | Brain → Clinical RSA | `clinical/` + `sdm/clinical_correlation.txt` + `rsa/` |
| H6: Embodied neural signatures predict outcome | Overlap of SDM maps with clinical correlation regions | Full chain RSA | Cross-map comparison + `rsa/` |
| H7: Procedures separable in neural space | Compare SDM maps across contrast families | Full perturbation → Brain RSA | All `sdm/*.txt` + `perturbation_space/` + `rsa/` |

---

## Data Files Summary

All analysis-ready files are produced in `data_processing/v1/` from the raw extractions in `data_extraction/raw_extractions/`.

### Contrast Classification Principle

Classification uses **condition_type** (verum/sham/rest/baseline), NOT free-text contrast labels. This is a mechanical rule, not semantic interpretation:

```
condition_1.type == "sham" AND condition_2.type == "rest/baseline"  →  sham_gt_rest
condition_1.type == "verum" AND condition_2.type == "sham"          →  verum_gt_sham
condition_1.type == "verum" AND condition_2.type == "rest/baseline" →  verum_gt_rest
condition_1.type == "sham" AND temporal (post > pre)                →  sham_post_gt_pre
condition_1.type == "verum" AND temporal (post > pre)               →  verum_post_gt_pre
group-level comparison / ANOVA / interaction                       →  group_comparison
signal decrease / negative activation                              →  deactivation
correlation with deqi/clinical/expectancy                          →  correlation
anything else                                                      →  other
```

Tissue level (1/2/3/4) is a **subgrouping variable within** contrast categories, NOT a separate category. For example, `sham_gt_rest` is one SDM pool; tissue_level splits it into subgroups for comparison.

### SDM-PSI File Structure

**Primary SDM analyses** (one file per contrast category):

```
data_processing/v1/
│
├── sdm/                                        # SDM-PSI coordinate input files
│   ├── sham_gt_rest.txt                        # ALL sham > rest (primary analysis)
│   ├── sham_gt_rest_L1.txt                     # Subgroup: penetrating sham > rest
│   ├── sham_gt_rest_L2.txt                     # Subgroup: superficial sham > rest
│   ├── sham_gt_rest_L3.txt                     # Subgroup: non-penetrating sham > rest
│   ├── sham_gt_rest_L4.txt                     # Subgroup: no-contact sham > rest
│   ├── verum_gt_sham.txt                       # ALL verum > sham
│   ├── verum_gt_rest.txt                       # ALL verum > rest
│   ├── sham_post_gt_pre.txt                    # Sham longitudinal
│   ├── verum_post_gt_pre.txt                   # Verum longitudinal
│   ├── group_comparison.txt                    # Group-level (patient vs HC, interactions)
│   ├── deactivation.txt                        # Signal decreases
│   ├── correlation_deqi.txt                    # Brain ~ deqi
│   ├── correlation_expectancy.txt              # Brain ~ expectancy
│   ├── correlation_clinical.txt                # Brain ~ clinical change
│   └── other.txt                               # Unclassified
│
├── macm/                                       # Meta-analytic connectivity modeling
│   ├── all_coordinates_pooled.csv
│   └── study_contrast_index.csv
│
├── meta_regression/                            # SDM meta-regression covariates
│   ├── study_predictors.csv
│   └── interaction_terms.csv
│
├── perturbation_space/                         # Intervention component matrices
│   ├── arm_components.csv
│   └── sham_decomposition.csv
│
├── rsa/                                        # Representational similarity analysis
│   ├── perturbation_dissimilarity_axisA.csv
│   ├── perturbation_dissimilarity_axisB.csv
│   ├── perturbation_dissimilarity_combined.csv
│   ├── neural_dissimilarity.csv
│   ├── sensory_dissimilarity.csv
│   └── clinical_dissimilarity.csv
│
├── sensory/                                    # Sensory and interoceptive data
│   ├── deqi_summary_by_arm.csv
│   ├── deqi_subscales.csv
│   ├── blinding_assessment.csv
│   └── sensation_verum_vs_sham.csv
│
└── clinical/                                   # Clinical outcome data
    ├── outcomes_by_arm.csv
    ├── brain_clinical_correlations.csv
    └── responder_data.csv
```

### File count by analysis

| Analysis | Files | Directory |
|---|---|---|
| SDM-PSI (primary + subgroups) | 15 | `sdm/` |
| MACM | 2 | `macm/` |
| Meta-regression | 2 | `meta_regression/` |
| Perturbation space | 2 | `perturbation_space/` |
| RSA | 6 | `rsa/` |
| Sensory | 4 | `sensory/` |
| Clinical | 3 | `clinical/` |
| **Total** | **34** | |

### Data flow

```
PDF_0519/                          (165 PDFs)
    ↓ [01_raw_extract.py]
data_extraction/raw_extractions/   (159 JSONs — source of truth)
    ↓ [data_processing scripts]
data_processing/v1/                (35 analysis-ready files)
    ↓ [SDM-PSI, R, Python]
analysis results
```

The `data_extraction/` directory stays as-is with raw JSONs. All processing into analysis-ready formats happens in `data_processing/v1/`. If the analysis plan changes, create `data_processing/v2/` — the raw extractions never change.

---

## Data Processing Pipeline

### Overview

Processing transforms 159 raw extraction JSONs into 35 analysis-ready files. Most steps are local Python (structural flattening). Two steps use Claude API for semantic classification tasks that require understanding free-text contrast descriptions and intervention details.

```
data_processing/v1/
├── config.py                          # paths, constants
├── 01_classify_contrasts.py           # Claude API: sort contrasts into analysis families
├── 02_build_sdm_files.py              # local: coordinates → SDM-PSI text files
├── 03_build_macm_files.py             # local: master coordinate database
├── 04_build_meta_regression.py        # Claude API + local: code physical properties into predictors
├── 05_build_perturbation_space.py     # local: flatten intervention components
├── 06_build_sensory_files.py          # local: flatten deqi/sensation data
├── 07_build_clinical_files.py         # local: flatten clinical outcomes
├── 08_build_rsa_matrices.py           # local: compute dissimilarity matrices
├── 09_validate.py                     # local: cross-file checks
```

### Step 01: Classify Contrasts (Claude API — ~$2-3)

Classification uses **condition_type** mechanically, not free-text label interpretation:

**A) Contrast category** — determines which SDM-PSI file it enters:

| Category | Rule | SDM file |
|---|---|---|
| `sham_gt_rest` | condition_1=sham, condition_2=rest/baseline | `sham_gt_rest.txt` (+ tissue level subgroups) |
| `verum_gt_sham` | condition_1=verum, condition_2=sham | `verum_gt_sham.txt` |
| `verum_gt_rest` | condition_1=verum, condition_2=rest/baseline | `verum_gt_rest.txt` |
| `sham_post_gt_pre` | sham arm, post > pre temporally | `sham_post_gt_pre.txt` |
| `verum_post_gt_pre` | verum arm, post > pre temporally | `verum_post_gt_pre.txt` |
| `group_comparison` | Multi-group ANOVA, interaction, patient vs HC | `group_comparison.txt` |
| `deactivation` | Signal decrease / negative activation | `deactivation.txt` |
| `correlation_deqi` | Brain ~ deqi/sensation intensity | `correlation_deqi.txt` |
| `correlation_expectancy` | Brain ~ expectancy/credibility | `correlation_expectancy.txt` |
| `correlation_clinical` | Brain ~ clinical outcome change | `correlation_clinical.txt` |
| `other` | Doesn't fit above | `other.txt` |

**Key change from previous approach**: sham tissue level (1/2/3/4) is a **subgrouping variable within `sham_gt_rest`**, not a separate category. This allows:
- Main SDM: all sham > rest pooled
- Subgroup SDM: L1 sham > rest vs L3 sham > rest
- Meta-regression: tissue_level as continuous covariate

**B) Method category**: whole_brain_activation / seed_based_fc / roi_fc / network_ica / graph_theory / correlation_brain_behavior / multivariate / other

**C) Usability flag**: `usable_for_sdm` — true only if contrast has coordinates with x, y, z values.

**Output**: `contrast_classifications.csv`

### Step 02: Build SDM Files (local)

For each analysis family with usable contrasts:
1. Collect coordinates from classified contrasts
2. Validate: x, y, z present, statistic value present
3. Convert Talairach → MNI where needed (Lancaster transform)
4. Write SDM-PSI format per family
5. Report: N studies and N foci per file

Papers with multiple contrasts in the same family → combine coordinates (SDM handles within-study clustering).

Papers with no usable coordinates → excluded from that SDM file but still appear in other analyses.

**Output**: 16 `.txt` files in `sdm/`

### Step 03: Build MACM Files (local)

Produce a master coordinate database for meta-analytic connectivity modeling:

- `all_coordinates_pooled.csv`: every coordinate from every contrast, with pmid, contrast_id, analysis_family, arm info, x, y, z, statistic, coordinate_space
- `study_contrast_index.csv`: one row per contrast, linking to study metadata, arms, sham type, method category

These serve as lookup tables for MACM seed queries.

**Output**: 2 `.csv` files in `macm/`

### Step 04: Build Meta-Regression Predictors (Claude API + local — ~$1-2)

Code intervention features into numeric predictors for SDM meta-regression. The key principle: **code physical properties, not device brand names**.

**Axis A coding (bodily input — from intervention descriptions):**

| Property | Coding | Source field |
|---|---|---|
| `penetration_level` | 0=none, 1=superficial (<5mm), 2=standard, 3=deep (>30mm) | penetration_exact, depth_exact |
| `skin_contact` | 0=no, 1=yes | from sham/intervention description |
| `electrical_stim` | 0=no, 1=yes | electrical_stimulation |
| `electrical_frequency_hz` | continuous (2, 15, 100, etc.) | electrical_frequency_exact |
| `n_needles` | continuous | number reported |
| `n_sessions` | continuous | number reported |
| `needle_retention_min` | continuous | needle_retention_min_numeric |
| `manipulation_intensity` | 0=none, 1=mild, 2=vigorous | manipulation_exact |
| `deqi_intended` | 0=no, 1=yes | deqi_intended_exact |
| `deqi_reported_mean` | continuous (from sensory data) | deqi_total_score |
| `acupoint_disease_relevant` | 0=no, 1=yes | from acupoints + disease context |

**Axis B coding (treatment meaning — from intervention descriptions):**

| Property | Coding | Source field |
|---|---|---|
| `blinding_present` | 0=no, 1=yes | blinding_method |
| `blinding_quality` | 0=none, 1=single, 2=double | from study design |
| `credibility_score` | continuous (if measured) | credibility rating |
| `expectancy_score` | continuous (if measured) | expectancy rating |
| `prior_experience_naive` | 0=experienced, 1=naive | prior_acupuncture_experience |
| `practitioner_interaction` | 0=minimal, 1=standard, 2=enhanced | practitioner_description |
| `treatment_rationale_given` | 0=no, 1=yes | treatment_rationale_given_exact |

**Sham physical properties (for verum_vs_sham contrasts):**

| Property | Coding | NOT this |
|---|---|---|
| `sham_penetration_level` | 0=none, 1=superficial | ~~sham_device=Streitberger~~ |
| `sham_skin_contact` | 0=no, 1=yes | ~~sham_type=Park~~ |
| `sham_at_acupoints` | 0=no (off-point), 1=yes (same points) | ~~sham_location=non-meridian~~ |
| `sham_visual_cue` | 0=no, 1=yes (looks like needling) | brand names |
| `sham_deqi_reported` | 0=no, 1=yes | |

Device brand names are recorded in `perturbation_space/sham_decomposition.csv` for reference but NOT used as predictors.

**Interaction terms** (computed locally):
- `body_x_meaning` = penetration_level × blinding_quality
- `deqi_x_expectancy` = deqi_reported_mean × expectancy_score
- `penetration_x_credibility` = penetration_level × credibility_score

**Output**: `meta_regression/study_predictors.csv`, `meta_regression/interaction_terms.csv`

### Step 05: Build Perturbation Space (local)

Flatten all intervention details from raw JSONs:

- `arm_components.csv`: one row per arm per study, all raw Axis A + B fields preserved as-is (not coded). This is the raw perturbation space for visualization and clustering.
- `sham_decomposition.csv`: one row per sham arm, full physical characterization including device names, location, penetration, manipulation, intended sensation.

**Output**: 2 `.csv` files in `perturbation_space/`

### Step 06: Build Sensory Files (local)

Flatten sensory/interoceptive data:

- `deqi_summary_by_arm.csv`: one row per arm, total deqi score + instrument + n
- `deqi_subscales.csv`: one row per sensation per arm (soreness, heaviness, etc.)
- `blinding_assessment.csv`: perceived penetration, guessed allocation, blinding index
- `sensation_verum_vs_sham.csv`: between-arm differences (where reported)

Values preserved in original format (heterogeneous: "3.2 ± 1.1", "median 4 [IQR 3-6]", narrative).

**Output**: 4 `.csv` files in `sensory/`

### Step 07: Build Clinical Files (local)

Flatten clinical outcomes:

- `outcomes_by_arm.csv`: one row per outcome × arm × timepoint, raw values
- `brain_clinical_correlations.csv`: contrasts where neural ~ clinical (filtered from contrast_classifications)
- `responder_data.csv`: studies with responder definitions and rates

**Output**: 3 `.csv` files in `clinical/`

### Step 08: Build RSA Matrices (local)

Compute pairwise dissimilarity matrices from the files built in steps 05-07:

- Perturbation dissimilarity (Axis A, Axis B, combined): Gower distance on coded predictors from `study_predictors.csv`
- Sensory dissimilarity: Euclidean distance on deqi profiles from `deqi_subscales.csv`
- Clinical dissimilarity: distance on outcome measures from `outcomes_by_arm.csv`
- Neural dissimilarity: computed from coordinate overlap metrics from `all_coordinates_pooled.csv`, or updated later from SDM-PSI output maps

**Output**: 6 `.csv` files in `rsa/`

### Step 09: Validate (local)

Cross-file consistency:
- PMIDs consistent across all files
- Arm IDs match between perturbation_space, sensory, clinical
- Contrast IDs match between classifications, SDM files, MACM
- Coordinate bounds (MNI: x∈[-90,90], y∈[-126,90], z∈[-72,108])
- No duplicates within study × contrast
- RSA matrix dimensions match study counts

**Output**: `validation_report.csv`

### Execution

```bash
# API steps
uv run python data_processing/v1/01_classify_contrasts.py
# ── CHECKPOINT: review contrast_classifications.csv ──
uv run python data_processing/v1/04_build_meta_regression.py

# Local steps (fast, no cost)
uv run python data_processing/v1/02_build_sdm_files.py
uv run python data_processing/v1/03_build_macm_files.py
uv run python data_processing/v1/05_build_perturbation_space.py
uv run python data_processing/v1/06_build_sensory_files.py
uv run python data_processing/v1/07_build_clinical_files.py
uv run python data_processing/v1/08_build_rsa_matrices.py
uv run python data_processing/v1/09_validate.py
```

### Cost: ~$3-5 total (Steps 01 + 04 via Batch API)
