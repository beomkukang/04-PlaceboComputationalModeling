# Data Validation Report

Generated: 2026-05-25 19:29:33

## Summary

- **Errors:** 0
- **Warnings:** 5
- **Info:** 1

## Warnings

### [study_id_consistency] 65 study ID(s) not present in all files.

```
  pmid=16790551: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=19559684: present in contrast_classifications, arm_components, study_predictors, macm_coordinates; missing from clinical_parsed
  pmid=20423216: present in contrast_classifications, arm_components, study_predictors, macm_coordinates; missing from clinical_parsed
  pmid=21794103: present in contrast_classifications, arm_components, study_predictors; missing from clinical_parsed, macm_coordinates
  pmid=22291848: present in contrast_classifications, arm_components, study_predictors, macm_coordinates; missing from clinical_parsed
  pmid=22761766: present in contrast_classifications, arm_components, study_predictors; missing from clinical_parsed, macm_coordinates
  pmid=23666154: present in contrast_classifications, arm_components, study_predictors; missing from clinical_parsed, macm_coordinates
  pmid=23691237: present in contrast_classifications, arm_components, study_predictors, macm_coordinates; missing from clinical_parsed
  pmid=23840533: present in contrast_classifications, arm_components, study_predictors, macm_coordinates; missing from clinical_parsed
  pmid=23935686: present in contrast_classifications, arm_components, study_predictors; missing from clinical_parsed, macm_coordinates
  pmid=24062782: present in contrast_classifications, arm_components, study_predictors, macm_coordinates; missing from clinical_parsed
  pmid=24459533: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=24963329: present in contrast_classifications, arm_components, study_predictors, macm_coordinates; missing from clinical_parsed
  pmid=25525442: present in contrast_classifications, arm_components, study_predictors, macm_coordinates; missing from clinical_parsed
  pmid=25741269: present in contrast_classifications, arm_components, study_predictors, macm_coordinates; missing from clinical_parsed
  pmid=25821486: present in contrast_classifications, arm_components, study_predictors; missing from clinical_parsed, macm_coordinates
  pmid=25916336: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=26467429: present in contrast_classifications, arm_components, study_predictors, macm_coordinates; missing from clinical_parsed
  pmid=27242911: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=27803655: present in contrast_classifications, arm_components, study_predictors, macm_coordinates; missing from clinical_parsed
  pmid=28053642: present in arm_components, clinical_parsed, study_predictors; missing from contrast_classifications, macm_coordinates
  pmid=28480365: present in contrast_classifications, arm_components, study_predictors, macm_coordinates; missing from clinical_parsed
  pmid=29204113: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=30914909: present in contrast_classifications, arm_components, study_predictors, macm_coordinates; missing from clinical_parsed
  pmid=31011330: present in arm_components, clinical_parsed, study_predictors; missing from contrast_classifications, macm_coordinates
  pmid=32612281: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=32908491: present in clinical_parsed; missing from contrast_classifications, arm_components, study_predictors, macm_coordinates
  pmid=33013312: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=33314799: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=33384580: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=33551385: present in contrast_classifications, arm_components, study_predictors; missing from clinical_parsed, macm_coordinates
  pmid=33560579: present in contrast_classifications, arm_components, study_predictors, macm_coordinates; missing from clinical_parsed
  pmid=33664320: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=34720908: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=35096130: present in contrast_classifications, arm_components, study_predictors, macm_coordinates; missing from clinical_parsed
  pmid=35153654: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=35310583: present in contrast_classifications, arm_components, study_predictors; missing from clinical_parsed, macm_coordinates
  pmid=35312785: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=35557556: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=35959405: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=35965072: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=35968386: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=36102803: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=37025199: present in clinical_parsed; missing from contrast_classifications, arm_components, study_predictors, macm_coordinates
  pmid=37206312: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=37274194: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=37383656: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=37408438: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  pmid=37415858: present in arm_components, clinical_parsed, study_predictors; missing from contrast_classifications, macm_coordinates
  pmid=37584456: present in contrast_classifications, arm_components, clinical_parsed, study_predictors; missing from macm_coordinates
  ...
```

### [duplicate_contrasts] 416 study-category pairs have multiple contrasts.

```
  pmid=16407533, category=correlation_clinical: 3 contrasts
  pmid=16407533, category=deactivation: 4 contrasts
  pmid=16407533, category=sham_post_gt_pre: 7 contrasts
  pmid=16790551, category=verum_gt_rest: 3 contrasts
  pmid=17240066, category=group_comparison: 7 contrasts
  pmid=19559684, category=correlation_deqi: 4 contrasts
  pmid=19559684, category=deactivation: 9 contrasts
  pmid=19559684, category=verum_gt_rest: 3 contrasts
  pmid=19559684, category=verum_gt_sham: 5 contrasts
  pmid=20423216, category=other: 2 contrasts
  pmid=20423216, category=verum_gt_rest: 2 contrasts
  pmid=20838644, category=deactivation: 6 contrasts
  pmid=20838644, category=other: 6 contrasts
  pmid=21080967, category=correlation_expectancy: 6 contrasts
  pmid=21080967, category=deactivation: 2 contrasts
  pmid=21080967, category=group_comparison: 5 contrasts
  pmid=21080967, category=sham_gt_rest: 2 contrasts
  pmid=21080967, category=verum_gt_sham: 6 contrasts
  pmid=21794103, category=deactivation: 4 contrasts
  pmid=21794103, category=other: 12 contrasts
  pmid=21794103, category=verum_gt_rest: 4 contrasts
  pmid=22291848, category=deactivation: 3 contrasts
  pmid=22291848, category=group_comparison: 4 contrasts
  pmid=22291848, category=sham_gt_rest: 2 contrasts
  pmid=22291848, category=verum_gt_rest: 3 contrasts
  pmid=22291848, category=verum_post_gt_pre: 4 contrasts
  pmid=22761766, category=other: 5 contrasts
  pmid=22761766, category=verum_gt_sham: 3 contrasts
  pmid=22761766, category=verum_post_gt_pre: 2 contrasts
  pmid=22916152, category=group_comparison: 12 contrasts
  pmid=23152865, category=correlation_expectancy: 6 contrasts
  pmid=23152865, category=verum_gt_sham: 6 contrasts
  pmid=23316257, category=other: 16 contrasts
  pmid=23666154, category=group_comparison: 4 contrasts
  pmid=23666154, category=sham_gt_rest: 4 contrasts
  pmid=23666154, category=verum_gt_rest: 5 contrasts
  pmid=23691237, category=other: 18 contrasts
  pmid=23691237, category=sham_post_gt_pre: 5 contrasts
  pmid=23691237, category=verum_post_gt_pre: 5 contrasts
  pmid=23840533, category=deactivation: 22 contrasts
  pmid=23840533, category=sham_gt_rest: 6 contrasts
  pmid=23840533, category=verum_gt_rest: 7 contrasts
  pmid=23840533, category=verum_post_gt_pre: 6 contrasts
  pmid=23935686, category=deactivation: 7 contrasts
  pmid=23935686, category=other: 3 contrasts
  pmid=23935686, category=verum_gt_rest: 11 contrasts
  pmid=24062782, category=correlation_deqi: 8 contrasts
  pmid=24459533, category=verum_post_gt_pre: 4 contrasts
  pmid=24603951, category=deactivation: 3 contrasts
  pmid=24603951, category=group_comparison: 6 contrasts
```

### [scale_validity] 2 scale validity issue(s) found.

```
  - Clinical parsed: 81 row(s) with mean below scale_min
  - Clinical parsed: 17 row(s) with mean above scale_max
```

### [clinical_completeness] 1 clinical completeness issue(s).

```
  - 245 arm(s) have multiple outcome rows in outcomes_by_arm (may be intentional for multi-domain studies)
```

### [missingness] 9 variable(s) exceed 20% missingness.

```
  - arm_components.penetration: 20.4% missing (82/401)
  - arm_components.depth: 20.4% missing (82/401)
  - deqi_summary.n_analyzed: 45.5% missing (135/297)
  - clinical_parsed.mean: 33.4% missing (585/1753)
  - clinical_parsed.sd: 33.4% missing (585/1753)
  - clinical_parsed.higher_is_better: 26.6% missing (466/1753)
  - clinical_parsed.scale_min: 51.6% missing (905/1753)
  - clinical_parsed.scale_max: 51.6% missing (905/1753)
  - contrast_classifications.tissue_level: 90.3% missing (1951/2160)
```

## Passed Checks

- **[coordinate_outliers]** All 6089 coordinates within MNI bounds.
