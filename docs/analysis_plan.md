# Component-Resolved Acupuncture fMRI Meta-analysis: Analysis Plan

## 0. Core Research Question

**Main research question**

> Can acupuncture-related neural and clinical effects be better understood as graded responses within a multidimensional embodied perturbation space, rather than as categorical effects of verum versus sham acupuncture?

More specifically:

> Do bodily afferent input, deqi/interoceptive response, and cognitive-perceptual modulation explain variation in distributed fMRI response patterns and normalized clinical responsiveness across acupuncture neuroimaging studies?

This project intentionally moves away from the question, “Which brain region was activated in this condition?” and toward the question, “How do interventions occupy a multidimensional space, and how do neural and clinical responses vary along gradients within that space?”

---

## 1. Conceptual Model

### 1.1 Primary framework

Each acupuncture-like intervention is treated as a **perturbation**, not as a binary label.

Each intervention arm or contrast is positioned in a multidimensional **Embodied Perturbation Space** defined by:

1. **Bodily afferent input**
   - Penetration depth.
   - Skin contact.
   - Manual manipulation.
   - Electrical stimulation.
   - Needle number.
   - Needle retention duration.
   - Acupoint or non-acupoint location.
   - Anatomical/disease relevance of stimulation site.
   - Treatment dose and number of sessions.

2. **Deqi / sensory-interoceptive response**
   - Deqi presence/absence.
   - Total deqi intensity.
   - MASS, VAS, NRS, or custom deqi ratings.
   - Sensory qualities: aching, soreness, heaviness, numbness, tingling, warmth, pressure, spreading.
   - Sharp pain or unpleasantness, coded separately from canonical deqi.
   - Perceived intensity and perceived bodily salience.

3. **Cognitive-perceptual modulation**
   - Expectancy.
   - Credibility.
   - Perceived authenticity.
   - Perceived allocation.
   - Prior acupuncture experience.
   - Attention to body.
   - Visual ritual.
   - Practitioner interaction.
   - Verbal rationale or treatment context.
   - Blinding quality.

The term **cognitive-perceptual modulation** should not be reduced to “treatment meaning” alone. It is broader and includes expectation, attention, interpretation of bodily sensation, perceived realness, prior experience, and contextual appraisal. Many studies only partially observe this construct.

### 1.2 Response spaces

The project maps perturbations onto three linked response spaces:

1. **Neural Response Space**
   - SDM-PSI meta-analytic maps.
   - Peak coordinate distributions.
   - Directionality of activation/deactivation or increased/decreased connectivity/local activity.
   - Network-level summary scores.
   - Gradient scores derived from neural maps.

2. **Sensory / Interoceptive Response Space**
   - Deqi presence, intensity, and quality.
   - Pain-like versus non-pain-like sensation.
   - Perceived penetration and bodily salience.

3. **Clinical Responsiveness Space**
   - Direction-corrected standardized improvement across disease-relevant outcomes.
   - Domain-specific responsiveness.
   - Global responsiveness factor when data permit.

### 1.3 Sham fMRI heterogeneity as analyzable signal

This project began from the observation that fMRI responses to sham acupuncture are highly heterogeneous across studies. Rather than treating this heterogeneity as noise, the study treats it as a central phenomenon to be explained.

The working hypothesis is that sham-acupuncture neural responses differ because sham procedures vary not only in physical stimulation, but also in how participants perceive, interpret, and anchor the intervention. Thus, the same nominal sham category can produce different activation or deactivation patterns depending on:

- **Afferent load:** skin contact, penetration, manipulation, electrical stimulation, number of needles, dose, and anatomical relevance.
- **Interoceptive/deqi salience:** intensity and quality of sensations, perceived penetration, spreading sensation, non-pain deqi versus sharp pain.
- **Cognitive-perceptual anchoring:** prior acupuncture experience, expectancy, credibility, perceived realness, perceived allocation, attention to bodily sensation, visual ritual, treatment rationale, and practitioner interaction.

This module asks whether sham heterogeneity can be explained by component-level covariates and their interactions, rather than by the label “sham” itself. In particular, prior acupuncture experience is treated as an **experiential anchoring variable**: prior exposure may alter how ambiguous touch, visual cues, or mild sensations are interpreted, which may in turn alter deqi reports and neural responses.

### 1.4 Component interaction and overlap model

A central theoretical revision is that acupuncture should not be modeled as a simple linear sum of “specific” afferent effects and “nonspecific” cognitive/contextual effects.

The conventional additive model is:

```text
acupuncture response = specific afferent effect + nonspecific cognitive/contextual effect
```

This project instead treats afferent and cognitive-perceptual components as **interactive, partially overlapping, and dynamically reweighted**. Physical stimulation is not processed by the brain as raw sensory input alone; it is interpreted through expectation, attention, prior experience, perceived authenticity, contextual appraisal, and symptom relevance. Likewise, cognitive-perceptual modulation is not disembodied; it can alter how bodily signals are attended to, labeled, and experienced as deqi or therapeutic sensation.

Thus, the working model is:

```text
afferent input × cognitive-perceptual anchoring
        ↓
deqi / interoceptive salience
        ↓
distributed neural-response gradient
        ↓
normalized clinical responsiveness
```

This model allows several possible relationships between components:

1. **Additive model**
   Afferent input and cognitive-perceptual anchoring independently contribute to neural and clinical responses.

2. **Amplification model**
   Cognitive-perceptual anchoring amplifies the neural or clinical effect of bodily afferent input.

3. **Substitution / compensation model**
   When afferent input is weak, credibility, expectancy, prior experience, or perceived authenticity may partly compensate, producing meaningful sham responses.

4. **Competition / saturation model**
   When afferent input is strong, sensory-interoceptive processing may dominate and cognitive-perceptual contributions may become smaller or less detectable.

5. **Overlap / shared-implementation model**
   Afferent and cognitive-perceptual components may converge onto shared neural systems, especially salience, interoceptive, attentional, appraisal, valuation, and default-mode networks. In this case, “specific” and “nonspecific” effects are not cleanly separable at the neural level.

Deqi/interoceptive salience is treated as a potential **integration point** where bodily input and cognitive-perceptual anchoring meet. The study therefore tests not only whether afferent and cognitive variables have separate effects, but also whether their interactions explain neural-response gradients and clinical responsiveness better than either component alone.

---

## 2. Primary Hypotheses

### H1. Perturbation-space hypothesis

Verum and sham acupuncture procedures are not categorical opposites. They are distributed across a multidimensional perturbation space defined by afferent input, deqi/interoceptive response, and cognitive-perceptual modulation.

### H2. Neural-gradient hypothesis

Distributed neural responses vary along graded dimensions of perturbation space. Higher afferent input is expected to align more strongly with sensorimotor, somatosensory, thalamic, insular, and secondary somatosensory systems. Cognitive-perceptual modulation is expected to align more strongly with prefrontal, salience, appraisal, attentional, and valuation systems.

### H3. Sham cognitive-interoceptive heterogeneity hypothesis

Sham-acupuncture fMRI heterogeneity is not merely methodological noise. Sham responses are expected to vary systematically as a function of afferent load, deqi/interoceptive salience, and cognitive-perceptual anchoring factors such as prior acupuncture experience, expectancy, credibility, perceived authenticity, perceived allocation, attention, and interpretation of bodily sensation.

This hypothesis explicitly allows activation and deactivation patterns to differ across individuals and studies even under the same nominal sham modality. The analytic goal is to test whether component-level covariates explain sham neural-response gradients better than sham labels alone.

### H4. Deqi/interoceptive hypothesis

Deqi is an intermediate sensory-interoceptive response that may link physical stimulation to neural response gradients and clinical responsiveness. Deqi should be treated as multidimensional rather than binary.

### H5. Responsiveness hypothesis

Normalized clinical responsiveness across disease domains is better explained by perturbation-space position and neural-response gradients than by categorical labels such as verum, sham, penetrating, or nonpenetrating.

### H6. Component interaction and overlap hypothesis

Acupuncture effects are not expected to equal a simple sum of “specific” afferent and “nonspecific” cognitive effects. Instead, bodily afferent input and cognitive-perceptual anchoring may interact, amplify one another, compensate for one another, saturate one another, or converge onto shared neural systems. Deqi/interoceptive salience is expected to index part of this convergence.

This hypothesis is tested by comparing additive, interaction, deqi-bridging, substitution/compensation, and overlap/shared-network models.

---

## 3. Data Architecture

Create the following relational tables. Use stable IDs for all studies, arms, contrasts, peaks, and outcomes.

### 3.1 `studies.csv`

One row per study.

Required columns:

- `study_id`
- `first_author`
- `year`
- `doi`
- `population_type`: healthy / clinical / mixed
- `clinical_condition`
- `disease_domain`: pain / motor / mood / cognition / sleep / tinnitus / gastrointestinal / metabolic / other
- `sample_size_total`
- `sample_size_imaging`
- `scanner_field_strength`
- `paradigm`: resting_state / task_block / task_event / mixed
- `analysis_family`: GLM_activation / ALFF / fALFF / ReHo / seed_FC / graph / CBF / other
- `risk_of_bias_clinical`
- `risk_of_bias_imaging`
- `notes`

### 3.2 `arms.csv`

One row per intervention arm.

Required columns:

- `arm_id`
- `study_id`
- `arm_label_original`
- `arm_class`: verum / sham / waitlist / no_treatment / healthy_control / other
- `procedure_type`: manual_acupuncture / electroacupuncture / nonpenetrating_sham / superficial_sham / penetrating_offpoint / visual_phantom / laser / moxibustion / other
- `penetration_level`: none / touch_only / superficial / standard / deep / unclear
- `skin_contact`: yes / no / unclear
- `manual_manipulation`: yes / no / unclear
- `electrical_stimulation`: yes / no / unclear
- `needle_number`
- `retention_minutes`
- `sessions_total`
- `treatment_duration_weeks`
- `acupoint_relevance`: disease_relevant / same_acupoint / non_acupoint / unrelated / unclear
- `deqi_intended`: yes / no / unclear
- `expectancy_measured`: yes / no
- `expectancy_value`
- `credibility_measured`: yes / no
- `credibility_value`
- `blinding_assessed`: yes / no
- `blinding_success_value`
- `perceived_allocation`: verum / sham / unsure / not_reported
- `perceived_authenticity_value`
- `prior_acupuncture_experience`: excluded / allowed / measured / unclear
- `prior_acupuncture_experience_value`: percentage or mean if reported
- `visual_ritual`: yes / no / unclear
- `verbal_rationale_strength`: low / moderate / high / unclear
- `practitioner_interaction_matched`: yes / no / unclear

### 3.3 `contrasts.csv`

One row per imaging contrast.

Required columns:

- `contrast_id`
- `study_id`
- `arm_id_1`
- `arm_id_2`
- `contrast_label_original`
- `contrast_family`: verum_gt_sham / sham_gt_verum / sham_gt_rest / post_gt_pre_verum / post_gt_pre_sham / deqi_correlation / clinical_correlation / other
- `analysis_family`
- `direction`: increase / decrease / positive_correlation / negative_correlation / mixed
- `sample_size_contrast`
- `coordinate_space`: MNI / Talairach / unclear
- `thresholding_method`
- `whole_brain_or_roi`: whole_brain / roi / unclear
- `usable_for_sdm`: yes / no
- `notes`

### 3.4 `peaks.csv`

One row per coordinate peak.

Required columns:

- `peak_id`
- `contrast_id`
- `study_id`
- `x`
- `y`
- `z`
- `coordinate_space_original`
- `x_mni`
- `y_mni`
- `z_mni`
- `statistic_type`: t / z / p / F / beta / unknown
- `statistic_value`
- `direction`
- `brain_region_label_original`
- `notes`

### 3.5 `behavioral_outcomes.csv`

One row per behavioral or clinical outcome.

Required columns:

- `outcome_id`
- `study_id`
- `arm_id`
- `timepoint`: baseline / post / followup / change
- `instrument_original`
- `outcome_domain`: pain_intensity / symptom_frequency / function / mood / cognition / quality_of_life / physiological / deqi / expectancy / credibility / blinding / other
- `mean`
- `sd`
- `n`
- `p_value`
- `higher_is_better`: yes / no
- `scale_min`
- `scale_max`
- `mcid_if_known`
- `notes`

---

## 4. Derived Variables

### 4.1 Afferent Input Index

- Penetration
- Manual manipulation
- Electrical stimulation
- Skin contact
- Needle retention
- Needle number
- Sessions

### 4.2 Cognitive-Perceptual Anchoring Index

Because cognitive-perceptual modulation is only partially observed in published studies, create both **measured** and **design-proxy** versions. Do not code unreported variables as zero. Use `NA = not reported` unless the paper explicitly states absence or low level.

Measured components:

- Expectancy score.
- Credibility score.
- Blinding success.
- Perceived allocation.
- Perceived authenticity or perceived realness.
- Prior acupuncture experience.
- Prior acupuncture response, if reported.
- Attention or bodily-attention ratings, if reported.

Design-proxy components:

- Use of credible sham device.
- Same ritual duration as verum.
- Visual needle ritual or phantom/observational procedure.
- Practitioner interaction matched to verum.
- Verbal rationale or therapeutic framing.
- Sham performed at real acupoints versus non-acupoints.
- Participant acupuncture-naive requirement versus prior experience allowed.

Derived variables:

```text
Cognitive_Anchoring_Measured = z(expectancy) + z(credibility) + z(perceived_authenticity) + blinding_success + prior_experience_score
```

```text
Cognitive_Anchoring_Proxy = credible_device + matched_ritual + visual_ritual + practitioner_matched + verbal_rationale + real_acupoint_context
```

Keep measured and proxy components separate in primary analyses. Combine only in exploratory analyses.

Interpretation:

- This index should not be interpreted as “cognition” in full.
- It represents the observable or inferable degree to which the intervention may be cognitively and perceptually anchored as a plausible acupuncture treatment.
- Prior acupuncture experience should be treated as an experiential anchor, not merely a demographic covariate.

### 4.3 Deqi / Interoceptive Salience Index

Create:

- `deqi_present_binary`
- `deqi_total_intensity`
- `deqi_quality_profile`
- `sharp_pain_score`
- `nonpain_deqi_score`
- `sensory_spread_score` if reported

Separate canonical deqi from sharp pain.

### 4.4 Component Interaction Terms

Create explicit interaction variables to test whether afferent and cognitive-perceptual components are additive or dynamically coupled.

Primary interaction terms:

```text
Afferent_x_Cognitive = Afferent_Input_Index * Cognitive_Anchoring_Measured
Afferent_x_Cognitive_Proxy = Afferent_Input_Index * Cognitive_Anchoring_Proxy
Afferent_x_Deqi = Afferent_Input_Index * Deqi_Interoceptive_Index
Deqi_x_Cognitive = Deqi_Interoceptive_Index * Cognitive_Anchoring_Measured
Deqi_x_Cognitive_Proxy = Deqi_Interoceptive_Index * Cognitive_Anchoring_Proxy
PriorExperience_x_Afferent = Prior_Acupuncture_Experience * Afferent_Input_Index
PriorExperience_x_Deqi = Prior_Acupuncture_Experience * Deqi_Interoceptive_Index
```

Interpretation guide:

- Positive `Afferent_x_Cognitive`: cognitive-perceptual anchoring amplifies afferent effects.
- Negative `Afferent_x_Cognitive`: cognitive-perceptual contribution may be larger when afferent input is weaker, suggesting substitution or saturation.
- Positive `Deqi_x_Cognitive`: bodily sensation becomes more neurally or clinically salient when perceived as authentic or credible.
- Prior-experience interactions: previous acupuncture exposure may alter how ambiguous bodily sensations are interpreted.

These terms should be used cautiously because most studies provide aggregate rather than individual-participant data. Interpret results as cross-study component-gradient evidence, not individual-level causal mediation.

### 4.5 Clinical Responsiveness Scores

All clinical outcomes should be direction-corrected so positive values indicate improvement.

#### Within-arm standardized response

```text
R_within = direction * (post_mean - baseline_mean) / baseline_sd
```

Use Hedges correction when possible.

#### Controlled response

```text
R_controlled = direction * [(post_treatment - baseline_treatment) - (post_control - baseline_control)] / pooled_baseline_sd
```

#### POMP response for bounded scales

```text
POMP = 100 * (score - scale_min) / (scale_max - scale_min)
```

Then calculate direction-corrected POMP change.

#### MCID-scaled response, sensitivity analysis

```text
R_MCID = direction * observed_change / MCID
```

### 4.6 Response-type labels

Each clinical response estimate must be labeled as one of:

- `total_verum_response`
- `total_sham_response`
- `verum_specific_incremental_response`
- `sham_contextual_response`
- `treatment_package_response`
- `natural_history_adjusted_response`
- `unclear_response_type`

---

## 5. Neural Meta-analysis Using SDM-PSI

### 5.1 Software

- SDM-PSI for coordinate-based meta-analysis.
- MRIcron for visualization, coordinate inspection, and map display.
- Optional: Nilearn/Python for post-SDM map processing and network extraction.

### 5.2 Coordinate preparation

1. Convert Talairach coordinates to MNI if needed.
2. Harmonize directionality:
   - activation / increase / positive association.
   - deactivation / decrease / negative association.
3. Split contrasts by analysis family where necessary.
4. Exclude ROI-only coordinates from primary whole-brain SDM unless a separate ROI sensitivity analysis is planned.
5. Track study-level dependence.

### 5.3 Primary SDM-PSI contrast families

Run separate SDM-PSI analyses for each family if there are enough independent studies.

Priority order:

1. `verum_gt_sham`
2. `sham_gt_verum`
3. `sham_gt_rest_or_waitlist`
4. `post_gt_pre_verum`
5. `post_gt_pre_sham`
6. `penetrating_or_high_afferent_gt_nonpenetrating_or_low_afferent_sham`
7. `deqi_positive_correlation`
8. `deqi_negative_correlation`
9. `clinical_response_positive_correlation`
10. `clinical_response_negative_correlation`

Do not pool all imaging families in the primary analysis. Prefer separate analyses for:

- GLM activation.
- ALFF/fALFF.
- ReHo.
- Seed-based FC.
- Graph metrics.
- CBF/ASL.

If study counts are insufficient, downgrade to exploratory synthesis.

### 5.4 SDM-PSI meta-regression

Use SDM-PSI meta-regression for neural moderators where study count permits.

Potential moderators:

- Afferent Input Index.
- Penetration score.
- Deqi total intensity.
- Cognitive-perceptual measured index.
- Credibility score.
- Expectancy score.
- Sessions total.
- Disease domain.
- Healthy vs clinical.
- Task vs resting-state.

Primary caution: SDM meta-regression is vulnerable to ecological inference and low power. Treat as component-gradient evidence, not causal mediation.

### 5.5 SDM-PSI outputs

For every SDM analysis, save:

- Thresholded statistical map.
- Unthresholded map if available.
- Peak table.
- Jackknife sensitivity results.
- Heterogeneity map.
- Publication bias diagnostics if available.
- Inclusion list of studies and contrasts.

Suggested output structure:

```text
outputs/sdm/
  verum_gt_sham/
  sham_gt_rest/
  post_gt_pre_verum/
  post_gt_pre_sham/
  deqi_positive/
  clinical_response_positive/
```

### 5.6 MRIcron visualization

Use MRIcron to:

- Display SDM thresholded maps on standard MNI template.
- Create axial, coronal, and sagittal figures.
- Inspect coordinate locations.
- Export publication-quality images.
- Overlay maps from different contrast families where useful.

Recommended overlays:

- Verum > sham versus sham > rest.
- High-afferent versus low-afferent sham.
- Deqi-correlated map versus clinical-response-correlated map.
- Afferent-regression map versus cognitive-perceptual-regression map.

---

## 6. Python Analyses

Use Python for all non-SDM analyses.

Recommended libraries:

```text
pandas
numpy
scipy
statsmodels
scikit-learn
nilearn
nibabel
matplotlib
seaborn
networkx
pyrsa or rsatoolbox
pingouin
```

### 6.1 Data validation

Create scripts to check:

- Missing study IDs.
- Duplicate contrasts.
- Coordinate outliers.
- Directionality conflicts.
- Impossible scale values.
- Missing SDs.
- Multiple outcomes from same arm.
- Multiple contrasts from same study.

Script:

```text
scripts/01_validate_data.py
```

Outputs:

```text
outputs/qc/data_validation_report.md
outputs/qc/missingness_tables.csv
outputs/qc/coordinate_outliers.csv
```

### 6.2 Clinical responsiveness computation

Script:

```text
scripts/02_compute_responsiveness.py
```

Steps:

1. Harmonize direction of all outcomes.
2. Compute within-arm standardized response.
3. Compute controlled response where comparator arms exist.
4. Compute POMP response where valid scale ranges exist.
5. Compute MCID-scaled response when MCID is known.
6. Aggregate by domain.
7. Estimate global responsiveness factor if enough outcomes are available.

Outputs:

```text
outputs/behavioral/outcome_level_responsiveness.csv
outputs/behavioral/domain_responsiveness.csv
outputs/behavioral/global_responsiveness.csv
```

### 6.3 Perturbation-space construction

Script:

```text
scripts/03_build_perturbation_space.py
```

Steps:

1. Encode afferent input variables.
2. Encode cognitive-perceptual variables.
3. Encode deqi/interoceptive variables.
4. Generate composite scores and retain original components.
5. Perform PCA/UMAP/MDS for visualization only.
6. Calculate pairwise distances between interventions.

Recommended distance metrics:

- Gower distance for mixed categorical/continuous data.
- Euclidean distance for standardized numeric variables.
- Mahalanobis distance if covariance is stable.

Outputs:

```text
outputs/perturbation/arm_component_matrix.csv
outputs/perturbation/perturbation_distance_matrix.csv
outputs/perturbation/perturbation_pca_coordinates.csv
```

### 6.4 Neural response-space construction

Script:

```text
scripts/04_build_neural_space.py
```

Possible neural representations:

1. **Peak-density vector**
   - Convert peaks to atlas region counts or weighted statistics.

2. **SDM map-derived vector**
   - Extract values from SDM maps using atlas parcels.

3. **Network-level summary vector**
   - Sensorimotor network.
   - Salience network.
   - Default mode network.
   - Dorsal attention network.
   - Ventral attention network.
   - Frontoparietal control network.
   - Limbic network.
   - Thalamus/basal ganglia/cerebellum.
   - PAG/descending pain modulation regions if coordinates allow.

Outputs:

```text
outputs/neural/neural_feature_matrix.csv
outputs/neural/neural_distance_matrix.csv
outputs/neural/network_summary_scores.csv
```

### 6.5 Gradient analysis

Script:

```text
scripts/05_neural_gradient_analysis.py
```

Goal:

Move from isolated activation peaks to graded response dimensions.

Procedures:

1. Use neural feature matrix as input.
2. Apply PCA or diffusion map embedding to derive neural gradients.
3. Interpret gradients by network loadings.
4. Regress gradient scores on perturbation-space variables.
5. Test whether intervention classes occupy different positions along neural gradients.

Models:

```text
Gradient_k ~ Afferent_Input_Index + Deqi_Index + Cognitive_Perceptual_Index + Disease_Domain + Analysis_Family + Population_Type
```

Use mixed-effects models when multiple contrasts come from the same study:

```text
Gradient_k ~ predictors + (1 | study_id)
```

In Python, use:

- `statsmodels.regression.mixed_linear_model.MixedLM`
- robust standard errors if mixed models fail.

Outputs:

```text
outputs/gradients/neural_gradient_scores.csv
outputs/gradients/neural_gradient_loadings.csv
outputs/gradients/gradient_regression_results.csv
outputs/figures/neural_gradient_scatterplots.png
```

### 6.6 Component meta-regression in Python

Script:

```text
scripts/06_component_meta_regression.py
```

Outcomes:

- Clinical responsiveness.
- Neural gradient scores.
- Network summary scores.
- Deqi/interoceptive scores.

Predictors:

- Afferent input.
- Penetration level.
- Deqi.
- Cognitive-perceptual modulation.
- Sham type.
- Verum/sham label.
- Disease domain.
- Analysis family.
- Study quality.

Model examples:

```text
Responsiveness ~ Afferent_Input + Deqi + Cognitive_Perceptual + Neural_Gradient_1 + Disease_Domain + (1 | study_id)
```

```text
Neural_Gradient_1 ~ Afferent_Input + Cognitive_Perceptual + Deqi + Analysis_Family + Population_Type + (1 | study_id)
```

```text
Deqi ~ Afferent_Input * Cognitive_Perceptual + Population_Type + (1 | study_id)
```

Outputs:

```text
outputs/models/component_meta_regression_results.csv
outputs/models/model_diagnostics.md
```

### 6.7 Component interaction and overlap modeling

Script:

```text
scripts/07_component_interaction_models.py
```

Core question:

> Are acupuncture-related neural and clinical responses better explained by additive component effects, interaction effects, deqi-bridging effects, substitution/compensation, or overlap/shared neural implementation?

This module directly tests the theoretical claim that so-called specific and nonspecific effects are not necessarily separable. It compares models in which afferent and cognitive-perceptual components are independent versus models in which they interact or converge through deqi/interoceptive salience.

#### 6.8.1 Model family A: additive model

```text
Neural_Gradient ~ Afferent_Input_Index + Cognitive_Anchoring + Deqi_Interoceptive_Index + covariates + (1 | study_id)
Clinical_Responsiveness ~ Afferent_Input_Index + Cognitive_Anchoring + Deqi_Interoceptive_Index + covariates + (1 | study_id)
```

Interpretation:

- Afferent and cognitive-perceptual components contribute independently.
- This corresponds most closely to the conventional specific + nonspecific decomposition.

#### 6.8.2 Model family B: interaction model

```text
Neural_Gradient ~ Afferent_Input_Index * Cognitive_Anchoring + Deqi_Interoceptive_Index + covariates + (1 | study_id)
Clinical_Responsiveness ~ Afferent_Input_Index * Cognitive_Anchoring + Deqi_Interoceptive_Index + covariates + (1 | study_id)
```

Interpretation:

- The effect of afferent input depends on cognitive-perceptual anchoring.
- Positive interaction suggests amplification.
- Negative interaction may suggest substitution, compensation, or saturation.

#### 6.8.3 Model family C: deqi-bridging / integrative model

```text
Deqi_Interoceptive_Index ~ Afferent_Input_Index + Cognitive_Anchoring + Prior_Acupuncture_Experience + covariates + (1 | study_id)
Neural_Gradient ~ Deqi_Interoceptive_Index + Afferent_Input_Index + Cognitive_Anchoring + covariates + (1 | study_id)
Clinical_Responsiveness ~ Neural_Gradient + Deqi_Interoceptive_Index + Afferent_Input_Index + Cognitive_Anchoring + covariates + (1 | study_id)
```

Interpretation:

- Deqi/interoceptive salience is modeled as an integration point between bodily input and cognitive-perceptual anchoring.
- This is a component-path model, not definitive mediation unless within-study mediation data are available.

#### 6.8.4 Model family D: substitution / compensation model

Test whether cognitive-perceptual anchoring has stronger effects when afferent input is low.

```text
Neural_Gradient ~ Afferent_Input_Index + Cognitive_Anchoring + Afferent_Input_Index * Cognitive_Anchoring + covariates + (1 | study_id)
```

Then probe simple slopes:

```text
Effect of Cognitive_Anchoring at low afferent input
Effect of Cognitive_Anchoring at medium afferent input
Effect of Cognitive_Anchoring at high afferent input
```

Interpretation:

- Strong cognitive slope at low afferent input supports substitution or compensation.
- Weak cognitive slope at high afferent input may support sensory dominance or saturation.

#### 6.8.5 Model family E: overlap / shared-neural-implementation model

Test whether afferent and cognitive-perceptual predictors load onto overlapping neural networks.

Procedure:

1. Extract network-level neural summaries for each contrast or SDM-derived map.
2. Fit separate models predicting network scores from afferent input and cognitive anchoring.
3. Identify networks significantly associated with both predictors.
4. Quantify overlap using Dice/Jaccard overlap across thresholded maps or correlation between network-loading vectors.

Expected shared systems:

- salience network;
- anterior/mid-cingulate cortex;
- anterior and posterior insula;
- thalamus;
- sensorimotor network;
- frontoparietal control network;
- default-mode network;
- valuation/appraisal regions;
- descending pain modulation regions where available.

Interpretation:

- Overlap suggests that “specific” and “nonspecific” components may share neural implementation rather than occupying cleanly separable brain systems.

#### 6.8.6 Model comparison

Compare model families using:

- AIC/BIC;
- adjusted R2 or marginal/conditional R2;
- cross-validated prediction error;
- permutation tests preserving study clustering;
- likelihood-ratio tests for nested models;
- robustness across imaging families and disease domains.

Outputs:

```text
outputs/models/component_interaction_model_comparison.csv
outputs/models/component_interaction_coefficients.csv
outputs/models/deqi_bridging_path_results.csv
outputs/models/shared_network_overlap_results.csv
outputs/figures/additive_vs_interaction_model_fit.png
outputs/figures/afferent_cognitive_interaction_slopes.png
outputs/figures/deqi_bridging_model.png
outputs/figures/shared_network_overlap_map.png
```

### 6.8 Sham heterogeneity and cognitive-interoceptive anchoring analysis

Script:

```text
scripts/08_sham_heterogeneity.py
```

Core question:

> Do heterogeneous sham-acupuncture fMRI responses arise because sham procedures differ in afferent load, deqi/interoceptive salience, and cognitive-perceptual anchoring, including prior acupuncture experience and perceived authenticity?

This analysis is central to the project. It treats sham heterogeneity as a meaningful outcome rather than a nuisance.

#### 6.8.1 Build sham-only analytic dataset

Include all arms or contrasts in which the intervention is coded as sham, placebo acupuncture, nonpenetrating sham, superficial sham, sham acupoint, non-acupoint acupuncture, phantom/visual acupuncture, or other acupuncture-like control.

Required columns:

```text
study_id
arm_id
contrast_id
sham_type
afferent_input_index
deqi_total_intensity
deqi_quality_profile
sharp_pain_score
cognitive_anchoring_measured
cognitive_anchoring_proxy
prior_acupuncture_experience
expectancy_value
credibility_value
perceived_authenticity_value
perceived_allocation
blinding_success_value
disease_domain
population_type
analysis_family
scanner_field_strength
neural_gradient_scores
network_summary_scores
clinical_responsiveness_scores
```

#### 6.8.2 Descriptive tests

Questions:

1. Do different sham types occupy distinct perturbation-space positions?
2. Do nonpenetrating, superficial, off-point, visual/phantom, and other sham designs differ in afferent load?
3. Do sham designs differ in deqi/interoceptive salience?
4. Do sham designs differ in cognitive-perceptual anchoring?
5. Are prior-experience policies associated with deqi or perceived realness?

Outputs:

```text
outputs/sham/sham_component_table.csv
outputs/sham/sham_missingness_table.csv
outputs/figures/sham_perturbation_space.png
outputs/figures/sham_deqi_by_type.png
outputs/figures/sham_cognitive_anchor_by_type.png
```

#### 6.8.3 SDM-PSI sham heterogeneity analyses

Run sham-specific SDM-PSI analyses where study counts permit:

```text
Sham > baseline/rest/waitlist
Post-sham > pre-sham
High-afferent sham > low-afferent sham
High-deqi sham > low-deqi sham
High-cognitive-anchor sham > low/unknown-cognitive-anchor sham
Penetrating/superficial sham > nonpenetrating sham
Credible-device sham > low-credibility or unclear sham
```

Run SDM-PSI meta-regressions with the following moderators where feasible:

```text
afferent_input_index
deqi_total_intensity
cognitive_anchoring_measured
cognitive_anchoring_proxy
prior_acupuncture_experience_value
expectancy_value
credibility_value
perceived_authenticity_value
blinding_success_value
sessions_total
retention_minutes
```

Interpretation:

- Regions scaling with afferent input may indicate somatosensory/interoceptive load.
- Regions scaling with cognitive anchoring may indicate appraisal, attention, salience, and valuation components.
- Regions scaling with deqi may indicate bodily salience and interoceptive integration.

#### 6.8.4 Python models: does component coding explain sham neural heterogeneity?

Fit sequential models to test whether component variables explain neural-response variation beyond sham label, disease, and imaging factors.

Model sequence:

```text
Model 0: Neural_Gradient ~ Disease_Domain + Analysis_Family + Population_Type + Scanner_Field_Strength
Model 1: Neural_Gradient ~ Model 0 + Sham_Type
Model 2: Neural_Gradient ~ Model 0 + Afferent_Input_Index
Model 3: Neural_Gradient ~ Model 0 + Afferent_Input_Index + Deqi_Interoceptive_Index
Model 4: Neural_Gradient ~ Model 0 + Afferent_Input_Index + Deqi_Interoceptive_Index + Cognitive_Anchoring_Measured
Model 5: Neural_Gradient ~ Model 0 + Afferent_Input_Index + Deqi_Interoceptive_Index + Cognitive_Anchoring_Proxy
Model 6: Neural_Gradient ~ Model 0 + Afferent_Input_Index * Cognitive_Anchoring + Deqi_Interoceptive_Index * Cognitive_Anchoring
```

Compare models using:

- adjusted R2 / marginal and conditional R2;
- AIC/BIC;
- cross-validated prediction error;
- permutation tests preserving study clustering;
- likelihood-ratio tests where models are nested.

Recommended model formulas:

```text
Neural_Gradient_1 ~ Afferent_Input_Index + Deqi_Interoceptive_Index + Cognitive_Anchoring_Measured + Disease_Domain + Analysis_Family + (1 | study_id)
```

```text
Neural_Gradient_1 ~ Afferent_Input_Index * Cognitive_Anchoring_Proxy + Deqi_Interoceptive_Index + Disease_Domain + Analysis_Family + (1 | study_id)
```

```text
Deqi_Interoceptive_Index ~ Afferent_Input_Index + Cognitive_Anchoring_Measured + Prior_Acupuncture_Experience + Population_Type + (1 | study_id)
```

```text
Clinical_Responsiveness ~ Neural_Gradient_1 + Deqi_Interoceptive_Index + Cognitive_Anchoring_Measured + Afferent_Input_Index + Disease_Domain + (1 | study_id)
```

#### 6.8.5 Anchoring-specific tests

Prior acupuncture experience and perceived authenticity should be handled as cognitive-perceptual anchoring variables.

Primary tests:

```text
Deqi_Interoceptive_Index ~ Afferent_Input_Index + Prior_Acupuncture_Experience
Neural_Gradient ~ Afferent_Input_Index * Prior_Acupuncture_Experience
Neural_Gradient ~ Deqi_Interoceptive_Index * Perceived_Authenticity
Clinical_Responsiveness ~ Neural_Gradient + Prior_Acupuncture_Experience + Perceived_Authenticity
```

Interpretation:

- Prior experience may provide a sensory template for interpreting ambiguous sham stimulation.
- Perceived authenticity may convert weak or ambiguous bodily input into stronger treatment-related salience.
- Deqi may serve as a bodily anchor linking afferent input to cognitive appraisal and neural response.

#### 6.8.6 Missingness strategy

Do not code unreported expectancy, credibility, prior experience, or perceived authenticity as zero. Use three parallel analyses:

1. **Complete-observed analysis:** only studies reporting the variable.
2. **Design-proxy analysis:** use sham design features as proxy variables.
3. **Missingness-aware sensitivity:** include missingness indicators and test whether reporting itself biases results.

Outputs:

```text
outputs/sham/sham_type_summary.csv
outputs/sham/sham_component_models.csv
outputs/sham/sham_model_comparison.csv
outputs/sham/sham_anchoring_tests.csv
outputs/figures/sham_heterogeneity_model_comparison.png
outputs/figures/sham_afferent_deqi_cognitive_interaction.png
```

### 6.9 Representational Similarity Analysis

Script:

```text
scripts/09_rsa.py
```

Goal:

Test whether distances in perturbation space correspond to distances in neural response space and clinical responsiveness space.

Distance matrices:

- `D_perturbation`
- `D_neural`
- `D_deqi`
- `D_clinical`

Primary tests:

```text
corr(D_perturbation, D_neural)
corr(D_deqi, D_neural)
corr(D_neural, D_clinical)
corr(D_perturbation, D_clinical)
```

Partial RSA:

```text
corr(D_perturbation, D_neural | disease_domain, analysis_family)
```

Permutation strategy:

- Permute study/arm labels while preserving study clustering.
- Use Mantel or partial Mantel tests cautiously.
- Prefer regression on distance matrices with permutation inference.

Outputs:

```text
outputs/rsa/rsa_results.csv
outputs/rsa/distance_matrices/
outputs/figures/rsa_heatmaps.png
```

---

## 7. Sensitivity Analyses

### 7.1 Dependence sensitivity

- Leave-one-study-out.
- Leave-one-lab-out.
- Leave-one-disease-domain-out.
- One contrast per study per family.
- Exclude studies with unclear coordinate space.
- Exclude ROI-only studies.

### 7.2 Imaging-family sensitivity

Repeat key analyses separately for:

- GLM activation.
- ALFF/fALFF.
- ReHo.
- FC.
- CBF.

### 7.3 Population sensitivity

Repeat analyses for:

- Healthy volunteers only.
- Clinical populations only.
- Pain-related clinical populations.
- Non-pain clinical populations.

### 7.4 Outcome sensitivity

Repeat clinical mapping using:

- Standardized mean change.
- Controlled standardized response.
- POMP response.
- MCID-scaled response.
- Domain-specific responsiveness only.
- Global responsiveness factor only.

### 7.5 Cognitive-anchoring missingness sensitivity

Repeat sham heterogeneity models using:

- only studies with directly measured expectancy/credibility/blinding/prior experience;
- design-proxy cognitive anchoring variables;
- missingness indicators for unreported cognitive variables;
- exclusion of studies with no reported deqi or credibility information;
- separate analyses for acupuncture-naive samples versus samples where prior experience was allowed or measured.

---

## 8. Evidence Grading

Every major result should be labeled by evidential strength.

### Higher confidence

- Coordinate convergence from sufficient independent studies.
- Robust to leave-one-study/lab sensitivity.
- Same direction across imaging families or disease domains.
- Supported by behavioral/deqi or clinical-response data.

### Moderate confidence

- Subgroup result with limited but acceptable sample.
- Meta-regression with plausible covariate completeness.
- Robust in some but not all sensitivity checks.

### Exploratory

- Sparse subgroup.
- High missingness.
- RSA or gradient result based on derived features.
- Cross-disease global responsiveness with heterogeneous outcomes.

### Speculative

- Mediation-like interpretation without within-study mediation data.
- Cognitive-perceptual inference based only on sham type.
- Clinical mechanism inferred from pre-post change only.

---

## 9. Key Outputs for Paper

### Figures

1. Conceptual model of perturbation, neural, deqi, and clinical spaces.
2. Distribution of intervention arms in perturbation space.
3. SDM-PSI neural convergence maps by contrast family.
4. Neural gradient plot showing continuous response dimensions.
5. Component interaction figure comparing additive, amplification, substitution/compensation, and overlap models.
6. Sham heterogeneity plot showing same modality differing by afferent/deqi/cognitive-perceptual covariates.
7. Clinical responsiveness space by disease domain.
8. RSA heatmap linking perturbation, neural, deqi, and clinical distance matrices.
9. Sensitivity/evidence-grade summary.

### Tables

1. Included studies and imaging paradigms.
2. Intervention coding taxonomy.
3. Contrast families and study counts.
4. Clinical outcome normalization table.
5. SDM-PSI peak results.
6. Component meta-regression results.
7. Sensitivity analyses.
8. Evidence grading for key claims.

---

## 10. Claude Code / Implementation Prompt

Use this project structure:

```text
project_root/
  data/raw/
  data/processed/
  data/metadata/
  scripts/
  outputs/qc/
  outputs/behavioral/
  outputs/perturbation/
  outputs/neural/
  outputs/gradients/
  outputs/models/
  outputs/rsa/
  outputs/figures/
  outputs/tables/
  outputs/sdm/
```

Implement Python scripts in this order:

1. `01_validate_data.py`
2. `02_compute_responsiveness.py`
3. `03_build_perturbation_space.py`
4. `04_build_neural_space.py`
5. `05_neural_gradient_analysis.py`
6. `06_component_meta_regression.py`
7. `07_component_interaction_models.py`
8. `08_sham_heterogeneity.py`
9. `09_rsa.py`
10. `10_sensitivity_analyses.py`
11. `11_make_figures.py`

Each script should:

- Read from `data/processed/` or outputs from prior scripts.
- Write clean outputs to `outputs/`.
- Save a short markdown log describing what was run.
- Avoid overwriting raw data.
- Use study-level clustering wherever possible.
- Preserve original variables and create derived variables in separate columns.

Main analytic principle:

> Do not ask only whether a condition activates a brain region. Ask whether intervention position in embodied perturbation space predicts graded neural-response patterns and normalized clinical responsiveness.
