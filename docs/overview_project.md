# Component-Resolved Acupuncture fMRI Meta-analysis: Research Overview and Manuscript Blueprint

## 1. Main Research Question

**Can acupuncture-related neural and clinical effects be better understood as graded responses within a multidimensional embodied perturbation space, rather than as categorical effects of verum versus sham acupuncture?**

Specifically, the paper asks:

> Do bodily afferent input, deqi/interoceptive response, and cognitive-perceptual modulation explain variation in distributed fMRI response patterns and normalized clinical responsiveness across acupuncture neuroimaging studies?

This reframes acupuncture fMRI meta-analysis away from the classic question:

> “Which brain region was activated by verum or sham acupuncture?”

and toward a space-based mechanistic question:

> “How do intervention components map onto graded neural and clinical response spaces?”

## 1.1 Origin of the study

This study began from a specific empirical problem: fMRI signals, especially in sham acupuncture conditions, appear heterogeneous across studies. The traditional explanation is that this heterogeneity may reflect nonspecific, cognitive, or placebo-related effects, but the mechanisms remain underspecified.

Our framework treats this heterogeneity as a target of analysis rather than as noise. We hypothesize that sham-acupuncture neural responses differ because the same nominal sham category can vary in:

- physical afferent input;
- deqi/interoceptive salience;
- expectancy and credibility;
- perceived authenticity or perceived allocation;
- prior acupuncture experience;
- attentional and interpretive anchoring of bodily sensations;
- clinical context and ritual strength.

Thus, a participant receiving a nonpenetrating sham procedure may still experience a credible, bodily salient, treatment-like event. Another participant receiving a similar nominal sham may experience little sensation, low credibility, or a different interpretation of the stimulus. These differences may produce different activation and deactivation patterns.

---

## 2. Central Theses

This paper can have multiple linked central theses. They should be presented as a coherent theoretical sequence rather than as separate claims.

### Thesis 1. Verum and sham are graded perturbations, not categorical opposites

> Verum and sham acupuncture are not categorical opposites. They are graded embodied perturbations that differ in bodily afferent input, sensory-interoceptive/deqi response, and cognitive-perceptual anchoring.

### Thesis 2. Sham heterogeneity is a mechanistic signal, not just noise

> Heterogeneity in sham-acupuncture fMRI signals may arise because sham procedures differ in afferent load, deqi/interoceptive salience, perceived authenticity, prior experience, expectancy, credibility, and contextual anchoring.

### Thesis 3. “Specific” and “nonspecific” effects are not necessarily additive or separable

The traditional model treats acupuncture response as:

```text
specific afferent effect + nonspecific cognitive/contextual effect
```

This paper proposes a more flexible model:

```text
afferent input × cognitive-perceptual anchoring
        ↓
deqi / interoceptive salience
        ↓
distributed neural-response gradients
        ↓
normalized clinical responsiveness
```

Thus, afferent and cognitive-perceptual components may amplify one another, compensate for one another, saturate one another, or converge onto shared neural systems. Deqi may serve as an integration point where bodily evidence and cognitive-perceptual appraisal meet.

### Thesis 4. Neural responses are better described as gradients than isolated activations

> Acupuncture-related fMRI findings should be interpreted as distributed neural-response gradients across sensorimotor, interoceptive, salience, attentional, valuation, default-mode, and disease-relevant systems, rather than as isolated “activated regions.”

### Thesis 5. Clinical effects should be modeled as normalized responsiveness

> Because acupuncture fMRI studies span many disease domains, clinical effects should be modeled as direction-corrected standardized responsiveness within disease-relevant outcome spaces, rather than as a single raw clinical endpoint.

Together, these theses make the paper more than a coordinate-based meta-analysis. It becomes a component-resolved systems-neuroscience synthesis of acupuncture, sham, placebo-like effects, and responsiveness.

---

## 3. Conceptual Innovation

### 3.1 From brain-region activation to neural-response gradients

Traditional acupuncture fMRI reviews often ask whether acupuncture activates or deactivates specific regions such as the insula, ACC, thalamus, S1/S2, prefrontal cortex, or default mode network.

This project instead asks whether neural responses are organized along gradients, such as:

- low-to-high afferent input;
- low-to-high deqi/interoceptive salience;
- low-to-high cognitive-perceptual modulation;
- sham-like to verum-like perturbation profiles;
- sensory-dominant to appraisal-dominant neural responses;
- local somatosensory response to distributed salience/default-mode/frontoparietal response.

### 3.2 From verum-versus-sham to perturbation space

The paper argues that the binary contrast of verum versus sham is insufficient because sham interventions differ substantially.

Different sham procedures may include:

- no somatosensory input but high visual/ritual credibility;
- skin contact without penetration;
- superficial penetration;
- deep or active off-point needling;
- non-acupoint stimulation;
- real acupoint stimulation without intended therapeutic rationale;
- variable levels of deqi and perceived authenticity.

Thus, placebo-like or nonspecific treatment-related effects are expected to differ across sham procedures because the procedures differ in afferent, deqi, and cognitive-perceptual covariates. Importantly, this heterogeneity may also arise from **participant-level anchoring**: prior acupuncture experience, expectation, credibility, perceived authenticity, and the interpretation of ambiguous bodily sensations may change how the same sham procedure is neurally processed.

### 3.3 From additive decomposition to component interaction

Before, acupuncture was often conceptualized as the sum of:

```text
specific afferent effects + nonspecific cognitive/contextual effects
```

This project treats that decomposition as an empirical question rather than an assumption. The so-called specific and nonspecific components may be:

1. **Additive** — each contributes independently.
2. **Amplifying** — cognitive-perceptual anchoring increases the impact of afferent input.
3. **Substitutive or compensatory** — cognitive-perceptual anchoring produces meaningful responses when afferent input is weak.
4. **Competitive or saturating** — strong afferent input may dominate neural processing, reducing the apparent contribution of cognitive-perceptual factors.
5. **Overlapping** — afferent and cognitive-perceptual components may converge onto shared salience, interoceptive, attentional, valuation, and default-mode systems.

This is important because deqi may not be merely a sensory byproduct of needling. It may be the subjective integration of bodily input, attention, expectation, prior experience, and perceived treatment authenticity.

Therefore, the paper should not only ask whether verum differs from sham. It should ask which model best explains the observed neural and clinical data: additive, interactive, deqi-bridging, compensatory, or overlapping.

### 3.4 From sham inconsistency to sham heterogeneity modeling

The paper should explicitly argue that heterogeneity in sham-acupuncture fMRI is not merely a limitation of the field. It is a mechanistically meaningful signal.

The core sham-heterogeneity claim is:

> Sham acupuncture responses vary because sham procedures differ in afferent load, interoceptive/deqi salience, and cognitive-perceptual anchoring. Therefore, sham responses should be modeled as graded neural phenomena, not as a single placebo category.

This creates a dedicated analysis module:

1. Build a sham-only dataset.
2. Code sham afferent load, deqi, and cognitive-perceptual anchoring.
3. Test whether these variables explain neural activation/deactivation gradients better than sham labels alone.
4. Test whether deqi and prior experience moderate the link between sham procedure and neural response.
5. Test whether sham neural gradients map onto normalized clinical responsiveness.

### 3.5 Cognitive-perceptual anchoring

The term cognitive-perceptual anchoring is used to avoid overclaiming that we have decomposed cognition itself. It refers to observable or design-inferable factors that shape how a participant interprets acupuncture-like stimulation.

Examples include:

- expectancy;
- credibility;
- blinding success;
- perceived allocation;
- perceived realness/authenticity;
- prior acupuncture experience;
- attention to bodily sensations;
- visual exposure to needling;
- treatment rationale;
- practitioner interaction.

Prior acupuncture experience is especially important because it may provide a sensory and conceptual template for interpreting ambiguous sensations during sham procedures. Deqi may then function as a bodily anchor that strengthens perceived treatment authenticity and salience.

### 3.6 From clinical efficacy to normalized clinical responsiveness

Because the dataset spans multiple diseases, the paper should not restrict itself to pain alone and should not pool raw clinical outcomes directly.

Instead, the paper defines:

> **Clinical responsiveness = direction-corrected standardized improvement within disease-relevant outcome space.**

This allows the analysis to compare responsiveness across pain, migraine, stroke, depression, cognitive impairment, insomnia, tinnitus, IBS, metabolic disease, and other conditions while preserving domain-specific information.

---

## 4. Proposed Paper Title Options

1. **Acupuncture and sham procedures as graded embodied perturbations: a component-resolved fMRI meta-analysis**
2. **Neural-response gradients of acupuncture and sham acupuncture across embodied perturbation space**
3. **Beyond verum versus sham: component-resolved neural and clinical responsiveness in acupuncture fMRI**
4. **Afferent, interoceptive, and cognitive-perceptual dimensions of acupuncture-related brain responses**
5. **Mapping acupuncture placebo heterogeneity through neural gradients and clinical responsiveness**

---

## 5. Abstract-Level Summary

Acupuncture neuroimaging studies have traditionally contrasted verum and sham procedures as categorical conditions. However, sham procedures vary in penetration, skin contact, manipulation, credibility, deqi, perceived authenticity, and participant anchoring factors such as prior acupuncture experience, making the verum-sham distinction mechanistically underspecified. This project began from the observation that sham-acupuncture fMRI signals are heterogeneous across studies. We treat this heterogeneity as an analyzable signal rather than as noise. We perform a component-resolved coordinate-based and behavioral meta-analysis of acupuncture fMRI studies to test whether interventions are better modeled as graded perturbations in an embodied treatment space. We code each intervention according to bodily afferent input, deqi/interoceptive response, and cognitive-perceptual anchoring, and map these dimensions onto SDM-PSI neural convergence maps, neural-response gradients, and normalized clinical responsiveness across disease domains. We expect that afferent input will preferentially explain sensorimotor, somatosensory, thalamic, and insular responses, whereas cognitive-perceptual anchoring will explain prefrontal, salience, attentional, appraisal, and valuation-related responses. We further expect that sham heterogeneity will be explained by component-level covariates, deqi, and anchoring variables better than by sham labels alone, and that models allowing afferent and cognitive-perceptual components to interact or overlap will explain neural-response gradients better than a simple additive specific-plus-nonspecific model. This framework provides a systems-level account of acupuncture and placebo-like responses as graded neural and clinical phenomena emerging from interactions among body input, interoception, and cognitive-perceptual appraisal.

---

## 6. Manuscript Structure

## 6.1 Introduction

### Core points to include

1. Acupuncture is a complex intervention involving bodily stimulation, interoceptive sensation, ritual, expectation, attention, and clinical context.
2. fMRI studies have reported heterogeneous findings across brain regions, diseases, paradigms, and sham types.
3. Prior meta-analyses often treat verum and sham acupuncture as categorical contrasts.
4. This categorical framing is insufficient because sham procedures are not inert and differ in afferent and cognitive-perceptual load.
5. A component-resolved framework can model interventions as points in perturbation space.
6. The key scientific question is whether positions in this space predict neural-response gradients and clinical responsiveness.

### Suggested final paragraph of introduction

> Here, we asked whether acupuncture-related neural and clinical effects are better understood as graded responses within a multidimensional embodied perturbation space, rather than as categorical effects of verum versus sham acupuncture. We coded verum and sham procedures according to bodily afferent input, deqi/interoceptive response, and cognitive-perceptual modulation, and tested whether these dimensions explain variation in distributed fMRI response patterns and normalized clinical responsiveness across acupuncture neuroimaging studies.

---

## 6.2 Methods

### 6.2.1 Study identification and eligibility

Include:

- search strategy;
- screening procedure;
- inclusion/exclusion criteria;
- handling of 160 gathered papers and 134 eligible studies;
- PRISMA diagram;
- distinction between papers, studies, arms, contrasts, coordinates, and outcomes.

### 6.2.2 Data extraction

Extract four linked databases:

1. Study-level metadata.
2. Intervention/arm-level perturbation variables.
3. Contrast/coordinate-level neural data.
4. Behavioral/deqi/clinical outcome data.

### 6.2.3 Intervention coding

Code each intervention along three axes:

1. Bodily afferent input.
2. Deqi/interoceptive response.
3. Cognitive-perceptual modulation.

Important: cognitive-perceptual modulation should be treated as a partially observed construct, not fully reducible to expectancy or credibility.

### 6.2.4 Neural analysis

Primary neural analyses:

- SDM-PSI coordinate-based meta-analysis.
- MRIcron visualization.
- Separate analyses by contrast family and imaging family.

Main contrast families:

- verum > sham;
- sham > verum;
- sham > rest/waitlist/no treatment;
- post > pre verum;
- post > pre sham;
- high-afferent sham > low-afferent sham;
- deqi-neural correlations;
- clinical-response neural correlations.

### 6.2.5 Neural-gradient construction

Use Python to transform SDM outputs, peak-density features, or atlas/network summaries into neural feature matrices.

Then derive neural gradients using PCA, diffusion embedding, or related dimensionality-reduction methods.

The goal is to identify continuous neural response dimensions rather than isolated brain regions.

### 6.2.6 Clinical responsiveness normalization

Clinical outcomes should be transformed into direction-corrected standardized improvement scores.

Three levels:

1. Outcome-specific responsiveness.
2. Domain-specific responsiveness.
3. Global responsiveness factor, if data permit.

Domains:

- pain/symptom intensity;
- symptom frequency;
- function/disability;
- mood/anxiety;
- cognition;
- quality of life;
- physiological/biomarker outcomes.

### 6.2.7 Component meta-regression

Use Python mixed-effects or robust regression models to test whether perturbation-space dimensions predict:

- deqi/interoceptive response;
- neural gradient scores;
- network-level neural summaries;
- domain-specific responsiveness;
- global responsiveness.

### 6.2.8 Component interaction and overlap modeling

Compare competing models of how afferent and cognitive-perceptual components combine:

1. **Additive model:** afferent and cognitive-perceptual predictors contribute independently.
2. **Interaction model:** the effect of afferent input depends on cognitive-perceptual anchoring.
3. **Deqi-bridging model:** afferent and cognitive-perceptual predictors converge through deqi/interoceptive salience.
4. **Substitution/compensation model:** cognitive-perceptual anchoring has stronger effects when afferent input is weak.
5. **Overlap/shared-network model:** afferent and cognitive-perceptual predictors map onto overlapping neural systems.

These models should be compared using mixed-effects regression, cross-validated prediction error, information criteria, and sensitivity analyses preserving study-level clustering.

### 6.2.9 Sham heterogeneity analysis

Test whether sham effects differ by:

- penetration level;
- skin contact;
- manual/electrical stimulation;
- deqi;
- credibility;
- perceived authenticity;
- treatment context.

Compare models using sham label alone versus component-level covariates.

### 6.2.10 Representational Similarity Analysis

Use RSA to test whether interventions that are closer in perturbation space have more similar neural responses and more similar clinical responsiveness.

Distance matrices:

- perturbation-space distance;
- neural-response distance;
- deqi/interoceptive distance;
- clinical-responsiveness distance.

### 6.2.11 Sensitivity and evidence grading

Include:

- leave-one-study-out;
- leave-one-lab-out;
- leave-one-disease-domain-out;
- imaging-family sensitivity;
- healthy versus clinical sensitivity;
- pain versus non-pain sensitivity;
- ROI-only exclusion;
- risk-of-bias sensitivity.

Every claim should be graded as higher confidence, moderate confidence, exploratory, or speculative.

---

## 6.3 Results

### Result 1. Dataset overview

Report:

- number of papers, eligible studies, arms, contrasts, peaks, outcomes;
- population distribution;
- clinical condition distribution;
- imaging paradigm distribution;
- contrast type distribution;
- deqi/behavioral/clinical data completeness.

Expected interpretation:

> The dataset is large enough to move beyond isolated activation findings and to characterize intervention and response spaces, but heterogeneity requires careful stratification.

### Result 2. Perturbation-space mapping

Show how verum and sham interventions distribute across afferent input, deqi, and cognitive-perceptual dimensions.

Expected result:

> Sham procedures do not cluster at zero. Some sham procedures have substantial afferent and cognitive-perceptual load, whereas others have low afferent input but high credibility or ritual context.

### Result 3. SDM-PSI neural convergence maps

Show meta-analytic neural maps for key contrast families.

Expected result:

> Verum-sham differences may appear in somatosensory, interoceptive, thalamic, and salience regions, but the pattern will depend on sham type and imaging family.

### Result 4. Neural-response gradients

Show gradient dimensions derived from neural features.

Possible expected gradients:

1. Sensorimotor/interoceptive gradient.
2. Salience-prefrontal-appraisal gradient.
3. Default-mode/attentional modulation gradient.
4. Disease-domain or paradigm-related gradient.

Expected result:

> Neural responses vary continuously across component dimensions rather than separating cleanly into verum and sham categories.

### Result 5. Deqi and cognitive-perceptual modulation

Test whether afferent input and cognitive-perceptual variables predict deqi and whether deqi predicts neural gradient position.

Expected result:

> Deqi is likely to be associated with afferent input but may also vary with cognitive-perceptual factors such as perceived authenticity, attention, and expectancy.

### Result 6. Component interaction and overlap models

Compare additive, interaction, deqi-bridging, compensation, and overlap models.

Expected result:

> Neural and clinical responses may be better explained by models allowing afferent input and cognitive-perceptual anchoring to interact or converge through deqi/interoceptive salience, rather than by a simple additive model of specific plus nonspecific effects.

Possible interpretations:

- Amplification: high afferent input and high perceived authenticity produce stronger neural-response gradients.
- Compensation: low-afferent sham with high credibility or prior experience still produces meaningful salience/appraisal responses.
- Saturation: high afferent input reduces the apparent effect of cognitive-perceptual variables.
- Overlap: afferent and cognitive-perceptual predictors both map onto salience/interoceptive/appraisal systems.

### Result 7. Sham heterogeneity

Compare sham labels versus component predictors.

Expected result:

> Sham heterogeneity is better explained by afferent load, deqi/interoceptive salience, prior experience, perceived authenticity, and cognitive-perceptual anchoring than by sham category alone. The same nominal sham modality may produce different activation/deactivation gradients depending on these covariates.

### Result 8. Clinical responsiveness mapping

Map neural gradients to standardized responsiveness across disease domains.

Expected result:

> Domain-normalized responsiveness may align with distributed neural gradients involving salience, interoception, prefrontal appraisal, sensorimotor processing, and disease-relevant networks. Pain may provide the clearest domain, but broader responsiveness should be analyzed across all disease domains.

### Result 9. RSA linking spaces

Test correspondence among perturbation, neural, deqi, and clinical distance matrices.

Expected result:

> Interventions that are closer in perturbation space may show more similar neural responses and, to a weaker degree, more similar clinical responsiveness.

### Result 10. Sensitivity analyses

Report which findings survive:

- study/lab/domain exclusions;
- imaging-family separation;
- population stratification;
- clinical normalization methods;
- risk-of-bias filters.

---

## 7. Discussion Framework

### 7.1 Main interpretation

The primary interpretation should be:

> Acupuncture and sham acupuncture produce graded neural and clinical responses that reflect their positions in an embodied perturbation space. This space is structured by bodily afferent input, deqi/interoceptive salience, and cognitive-perceptual modulation.

### 7.2 Implication for placebo theory

Avoid claiming that the study fully explains placebo effects.

Instead say:

> Placebo-like effects in acupuncture are not uniform. They vary with the sensory and cognitive-perceptual properties of the control procedure. Thus, sham acupuncture should not be treated as a single inert comparator but as a family of active perturbations with different neural and behavioral consequences.

### 7.3 Implication for acupuncture mechanisms

The paper can argue:

> Acupuncture effects are unlikely to be captured by a single brain region or network. They emerge from interactions among somatosensory input, interoceptive salience, salience/appraisal systems, and disease-relevant regulatory networks.

### 7.4 Implication for specific versus nonspecific effects

The paper should argue that the conventional decomposition of acupuncture into specific afferent effects and nonspecific cognitive/contextual effects is useful but incomplete. These components may not be separable at the neural level. They may interact through deqi/interoceptive salience and converge on shared salience, appraisal, attention, valuation, and regulatory networks.

Therefore, the relevant question is not only how much of acupuncture is specific versus nonspecific, but how bodily input and cognitive-perceptual anchoring are combined, amplified, substituted, or overlapped in the brain.

### 7.5 Implication for future trials

Future acupuncture fMRI trials should:

- report deqi in detail;
- measure expectancy, credibility, perceived allocation, and prior experience;
- quantify sham sensory load;
- include waitlist/no-treatment arms when possible;
- report coordinates and null findings transparently;
- distinguish sharp pain from canonical deqi;
- design shams based on which component they are intended to control.

---

## 8. Expected Main Claims

### Higher-confidence claims, if supported

1. Verum and sham acupuncture procedures vary substantially in afferent and cognitive-perceptual components.
2. Sham acupuncture is heterogeneous and should not be treated as a single inert placebo condition.
3. Neural responses are better summarized as distributed patterns or gradients than isolated activation peaks.
4. Deqi is a multidimensional sensory-interoceptive response that should be separated from sharp pain.
5. Clinical responsiveness can be normalized across disease domains using direction-corrected standardized improvement.
6. The traditional additive specific-plus-nonspecific framework should be treated as an empirical model to test, not as an assumption.

### Moderate or exploratory claims

1. Afferent input predicts sensorimotor/interoceptive neural gradients.
2. Cognitive-perceptual modulation predicts prefrontal/salience/appraisal gradients.
3. Deqi partially links afferent input and neural response patterns.
4. Neural gradients predict domain-normalized clinical responsiveness.
5. Perturbation-space distances correspond to neural-response distances.
6. Interaction or deqi-bridging models explain neural gradients better than additive models.
7. Afferent and cognitive-perceptual predictors show overlapping neural-network implementation.

### Claims to avoid or qualify

Do not claim:

- sham acupuncture is pure placebo;
- verum effects are purely specific;
- deqi causes clinical improvement unless mediation evidence exists;
- cognitive-perceptual modulation is fully decomposed;
- cross-study mediation proves individual-level mechanisms;
- one brain region explains acupuncture efficacy.

---

## 9. Figure Plan

### Figure 1. Conceptual framework

A diagram showing:

```text
Embodied Perturbation Space
  - afferent input
  - deqi/interoceptive response
  - cognitive-perceptual modulation
        ↓
Neural Response Gradients
        ↓
Clinical Responsiveness Space
```

### Figure 2. Dataset map

Study flow, disease domains, contrast types, imaging methods, behavioral data completeness.

### Figure 3. Perturbation-space scatterplot

Arms plotted by afferent input and cognitive-perceptual modulation, colored by verum/sham/waitlist and shaped by deqi availability.

### Figure 4. SDM-PSI maps

Main coordinate-based meta-analysis maps.

### Figure 5. Neural gradients

Gradient plot with interventions positioned along neural-response dimensions.

### Figure 6. Component interaction model

Additive versus interaction versus deqi-bridging model; show whether cognitive-perceptual anchoring amplifies, compensates for, or overlaps with afferent input.

### Figure 7. Sham heterogeneity

Comparison of sham types by afferent input, deqi, neural gradient, and clinical responsiveness.

### Figure 8. Clinical responsiveness space

Domain-specific and global standardized responsiveness across disease domains.

### Figure 9. RSA matrix

Correspondence among perturbation, neural, deqi, and clinical distance matrices.

### Figure 10. Evidence map

Summary of robust, moderate, exploratory, and speculative findings.

---

## 10. Table Plan

### Table 1. Included studies

Study metadata, disease domain, population, imaging paradigm, sample size.

### Table 2. Sham and intervention taxonomy

Verum/sham types coded by afferent input, deqi, and cognitive-perceptual features.

### Table 3. Imaging contrast families

Counts for each contrast type and analysis family.

### Table 4. Clinical outcome normalization

Instrument, domain, direction, scale range, standardized response formula.

### Table 5. SDM-PSI results

Cluster locations, coordinates, effect direction, heterogeneity, sensitivity.

### Table 6. Neural gradient loadings

Networks and regions contributing to each gradient.

### Table 7. Component meta-regression results

Predictors of neural gradients, deqi, and clinical responsiveness.

### Table 8. Component interaction model comparison

Additive, interaction, deqi-bridging, compensation, and overlap/shared-network models.

### Table 9. Sensitivity and evidence grading

Which findings survive which robustness checks.

---

## 11. Suggested Discussion Language

### On the main finding

> Our findings suggest that acupuncture-related brain responses are not well described by a categorical verum-versus-sham distinction. Instead, both verum and sham procedures occupy graded positions in an embodied perturbation space, and their neural consequences vary with afferent, interoceptive, and cognitive-perceptual components.

### On sham heterogeneity

> Sham acupuncture should not be interpreted as a unitary placebo. Nonpenetrating touch, superficial penetration, off-point needling, visual/phantom procedures, and waitlist controls differ in the bodily evidence and cognitive-perceptual context they provide. These differences are likely to shape both neural response and clinical responsiveness.

### On clinical responsiveness

> Because acupuncture fMRI studies span diverse diseases, clinical response cannot be reduced to a single raw outcome. We therefore modeled responsiveness as direction-corrected standardized improvement within disease-relevant outcome domains, enabling cross-domain comparison while preserving domain-specific interpretation.

### On cognitive-perceptual modulation

> Cognitive-perceptual modulation is a partially observed construct that includes expectancy, attention, perceived authenticity, prior experience, credibility, and contextual appraisal. The available literature rarely measures all of these dimensions, making this axis both theoretically important and empirically incomplete.

### On specific versus nonspecific effects

> The conventional distinction between specific afferent and nonspecific cognitive/contextual effects is insufficient if these components interact or share neural implementation. Our framework treats the additive model as only one candidate model and tests whether interaction, compensation, deqi-bridging, or overlap models better explain the observed neural-response gradients.

### On limitations

> The present synthesis is constrained by heterogeneity in imaging paradigms, incomplete reporting of deqi and expectancy, variable sham designs, and the ecological nature of cross-study meta-regression. Therefore, gradient and component analyses should be interpreted as evidence for structured associations rather than individual-level causal mediation.

---

## 12. Final Takeaway

The paper should ultimately argue:

> Acupuncture fMRI should move beyond asking whether verum differs from sham in isolated brain regions. A more mechanistically informative approach is to model acupuncture and sham procedures as graded embodied perturbations and to test how their afferent, interoceptive, and cognitive-perceptual dimensions combine, interact, overlap, and shape distributed neural-response gradients and normalized clinical responsiveness.

