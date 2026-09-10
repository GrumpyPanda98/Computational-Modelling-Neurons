"""Render a lightweight waveform preview without pyfibers or NEURON."""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from functions.waveforms import conventional, conventional_passive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("outputs/waveforms.png"))
    args = parser.parse_args()
    settings = dict(
        frequency=40,
        pulse_width=0.2,
        interphase_interval=0,
        time_stop=30,
        time_step=0.01,
    )
    fig, axes = plt.subplots(2, 1, figsize=(8, 5), sharex=True)
    variants = [
        ("Conventional active recharge", conventional(**settings)),
        ("Conventional passive recharge", conventional_passive(**settings, tau=0.5)),
    ]
    for ax, (label, (time, amplitude)) in zip(axes, variants):
        ax.plot(time, amplitude, linewidth=1)
        ax.set(title=label, ylabel="Normalised amplitude")
        ax.grid(alpha=0.2)
    axes[-1].set_xlabel("Time (ms)")
    fig.tight_layout()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=150)
    plt.close(fig)
    print(args.output)


if __name__ == "__main__":
    main()
