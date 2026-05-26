# Component Meta-Regression: Model Diagnostics

## Summary

### responsiveness_mixed_lm

- **N observations**: 113
- **N groups (studies)**: 38
- **AIC**: nan
- **BIC**: nan
- **Converged**: True

| Predictor | Coefficient | p-value | Significance |
|-----------|-------------|---------|--------------|
| Intercept | 0.0940 | 0.8388 |  |
| Afferent_Input_Index | 0.7129 | 0.0309 | * |
| Cognitive_Anchoring | -0.3104 | 0.2219 |  |
| outcome_domain_function | 0.8260 | 0.0993 |  |
| outcome_domain_mood | 0.5471 | 0.2599 |  |
| outcome_domain_pain | 1.3714 | 0.0044 | ** |
| outcome_domain_quality_of_life | 0.7152 | 0.1695 |  |
| outcome_domain_symptom_severity | 0.7180 | 0.1261 |  |

### deqi_mixed_lm

- **N observations**: 43
- **N groups (studies)**: 16
- **AIC**: nan
- **BIC**: nan
- **Converged**: True

| Predictor | Coefficient | p-value | Significance |
|-----------|-------------|---------|--------------|
| Intercept | 10.0235 | 0.0017 | ** |
| Afferent_Input_Index | 4.5139 | 0.2526 |  |
| Cognitive_Anchoring | 2.2562 | 0.5945 |  |
| Afferent_x_Cognitive | 3.2129 | 0.4849 |  |

## Notes

- Models use random intercepts per study (pmid) via MixedLM.
- If MixedLM fails to converge, OLS with clustered standard errors is used.
- Significance codes: *** p<0.001, ** p<0.01, * p<0.05
