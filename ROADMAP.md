# Development milestones

The first milestone prepares this repository for public inspection. Later milestones are planned work, not implemented features or validated results.

## 01 · Public research-code baseline

Document the implemented waveform and simulation code, add a small preview, remove import-time demo computation, stop tracking editor/cache files, and add synthetic checks. Acceptance: preview renders and waveform checks pass without running fibre simulations; dependency and provenance limitations are explicit.

## 02 · Waveform and dependency provenance

Identify the original pyfibers/NEURON versions and model mechanisms. Specify timing and charge-balance conventions for every waveform, including the conventional gap and burst spacing. Acceptance: documented source/version, numerical waveform reference fixtures, and reviewed comparisons before changing historical definitions.

## 03 · Reproducible fibre experiment

Consolidate one validated simulation entry point with explicit configuration, bounded parallelism, and a saved run manifest. Acceptance: a small reference run reproduces agreed traces/thresholds within documented tolerances; historical tables are linked to their generating configuration or labelled unreproduced.
