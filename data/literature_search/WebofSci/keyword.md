Web of Science Step 1 — Broad/core search

Use this as the main Web of Science search:

TS=(
acupuncture
OR electroacupuncture
OR "electro-acupuncture"
OR "manual acupuncture"
OR "acupuncture stimulation"
OR needling
OR "needle stimulation"
OR acupoint*
OR meridian*
)
AND
TS=(
fMRI
OR "functional MRI"
OR "functional magnetic resonance imaging"
OR BOLD
OR neuroimaging
OR "brain activation"
OR "brain response"
OR "brain activity"
OR "cerebral activation"
OR "resting state"
OR "resting-state"
OR "functional connectivity"
OR connectivity
OR ALFF
OR fALFF
OR ReHo
OR "regional homogeneity"
)

This is your main capture search. Do not add sham/placebo/deqi terms here, because that may make the search too narrow.

Web of Science Step 2 — Sham/placebo acupuncture supplementary search

Use this to capture sham-controlled acupuncture neuroimaging studies:

TS=(
acupuncture
OR electroacupuncture
OR "electro-acupuncture"
OR "manual acupuncture"
OR "acupuncture stimulation"
OR acupoint\*
)
AND
TS=(
"sham acupuncture"
OR "placebo acupuncture"
OR "placebo needle"
OR "sham needle"
OR nonpenetrating
OR "non-penetrating"
OR "retractable needle"
OR Streitberger
OR "Park sham"
OR "superficial acupuncture"
OR "superficial needling"
OR "minimal acupuncture"
OR "off-point acupuncture"
OR "non-acupoint"
OR nonacupoint
OR "tactile control"
)
AND
TS=(
fMRI
OR "functional MRI"
OR "functional magnetic resonance imaging"
OR BOLD
OR neuroimaging
OR "brain activation"
OR "functional connectivity"
)
Web of Science Step 3 — Placebo/deqi/mechanism supplementary search

Use this to find studies that discuss placebo, expectancy, credibility, blinding, deqi, needle sensation, bodily sensation, pain, or analgesia:

TS=(
acupuncture
OR electroacupuncture
OR "electro-acupuncture"
OR "acupuncture stimulation"
OR "sham acupuncture"
OR "placebo acupuncture"
OR acupoint*
)
AND
TS=(
fMRI
OR "functional MRI"
OR "functional magnetic resonance imaging"
OR BOLD
OR neuroimaging
OR "functional connectivity"
OR "resting-state"
)
AND
TS=(
placebo
OR "placebo effect"
OR sham
OR expectancy
OR expectation*
OR credibility
OR blinding
OR belief
OR "treatment belief"
OR "perceived assignment"
OR "perceived realness"
OR deqi
OR "de qi"
OR "needle sensation"
OR "acupuncture sensation"
OR "bodily sensation"
OR somatosensory
OR interoception
OR interoceptive
OR pain
OR analgesia
)
Web of Science Step 4 — Coordinate/result-focused supplementary search

Use this for coordinate-based meta-analysis eligibility, such as ALE or SDM:

TS=(
acupuncture
OR electroacupuncture
OR "sham acupuncture"
OR "placebo acupuncture"
OR "acupuncture stimulation"
)
AND
TS=(
fMRI
OR "functional MRI"
OR "functional magnetic resonance imaging"
OR BOLD
OR neuroimaging
)
AND
TS=(
activation
OR coordinate*
OR voxel*
OR cluster*
OR "whole brain"
OR "whole-brain"
OR contrast*
OR MNI
OR Talairach
)

Keep this as a supplementary search, not the main search. Some eligible papers may report coordinates in tables or supplements without mentioning “coordinate,” “MNI,” or “Talairach” in the abstract.

Web of Science Step 5 — Named sham-device search

Use this as a final safety search:

TS=(
acupuncture
OR "sham acupuncture"
OR "placebo acupuncture"
)
AND
TS=(
Streitberger
OR "Park sham"
OR "placebo needle"
OR "sham needle"
OR "nonpenetrating needle"
OR "non-penetrating needle"
OR "retractable needle"
OR "blunt needle"
)
AND
TS=(
fMRI
OR "functional magnetic resonance imaging"
OR BOLD
OR neuroimaging
)
