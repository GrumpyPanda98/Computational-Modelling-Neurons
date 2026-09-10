# Neural Fibre Models for Electrical Stimulation

Python experiments exploring how stimulation waveforms affect modelled nerve-fibre responses. The scripts compare conventional, FAST-labelled, and burst configurations, including active and passive charge-balancing approaches.

This is research code from my work on computational modelling of spinal cord stimulation. It contains waveform generators, activation-threshold sweeps, and plotting utilities. It is not a clinical prediction tool or a packaged reproduction of a published result.

## Start with the waveforms

Python 3.11 is the verification baseline. From the repository root:

```sh
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m examples.waveform_preview --output outputs/waveforms.png
python -m unittest discover -s tests -v
```

The preview generates a small waveform figure without starting a fibre simulation. Time and pulse-width inputs are in milliseconds; frequencies are in hertz. Amplitudes are normalised waveform values, with stimulation amplitude applied by the simulation scripts.

## What is here

| Path | Purpose |
| --- | --- |
| `functions/waveforms.py` | Conventional, passive-recharge, and burst waveform generators |
| `examples/waveform_preview.py` | Small, configurable waveform preview |
| `pipelines/` | Single-process and parallel fibre simulations, threshold searches, and analysis |
| `pipelines/functions/pipeline_functions.py` | Simulation plotting and export helpers |
| `pipelines/tables/` | Historical threshold exports; provenance needs documenting before scientific reuse |
| `prototyping/` | Exploratory scripts retained for context |

## Fibre simulations

The simulation scripts additionally require the `pyfibers` API providing `build_fiber`, `FiberModel`, and `ScaledStim`, with its compatible NEURON mechanisms. That dependency and its exact version are not bundled or pinned here. Installing the preview requirements alone does **not** make the simulations runnable.

Review the parameters in a pipeline before executing it. Some scripts launch parallel sweeps, generate many files, or assume an existing output directory. Run modules from the repository root so the shared `functions` imports resolve. The preview and unit checks do not validate activation thresholds or reproduce the historical tables.

Several waveform variants are exploratory. In particular, `conventional` currently appends its gap after both phases, while other generators place a gap between phases; `burst` does not independently schedule its intraburst spacing. These conventions are preserved pending comparison with the original protocol, rather than silently changed during cleanup.

## Development

See [the milestones](ROADMAP.md) for dependency provenance, waveform validation, and a reproducible simulation entry point. Small fixes and clearer examples are welcome; changes to waveform definitions or model parameters need a documented comparison with the existing behaviour.

[Nickolaj Ajay Atchuthan](https://atchuthan.com/)
