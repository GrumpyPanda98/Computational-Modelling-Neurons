#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulation of nerve fibers using pyfibers.

@author: gz57nm
"""
import time
from pyfibers import build_fiber, FiberModel, ScaledStim
import numpy as np
import matplotlib.pyplot as plt
from functions.waveforms import conventional, conventional_passive
import pandas as pd
import seaborn as sns

#%% Definitions
stim_amp = -1.5
time_step = 0.001
time_stop = 100

#%% Fiber Model Creation Function
def create_fiber(fiber_model=FiberModel.SMALL_MRG_INTERPOLATION, length=500, diameter=10, temperature=37):
    return build_fiber(fiber_model=fiber_model, length=length, diameter=diameter, temperature=temperature)

#%% Generate and Plot All Waveforms
def generate_waveforms(time_step, time_stop):
    # Define parameters for each waveform
    waveform_configs = [
        {
            "title": "Conventional Biphasic Waveform",
            "generator": conventional,
            "params": {
                "frequency": 40,
                "pulse_width": 0.2,
                "interphase_interval": 0.1,
                "time_stop": time_stop,
                "time_step": time_step
            },
            "zoom_range": (24, 28)
        },
        {
            "title": "Conventional Passive Charge Balance",
            "generator": conventional_passive,
            "params": {
                "frequency": 40,
                "pulse_width": 0.2,
                "interphase_interval": 0.05,
                "time_stop": time_stop,
                "time_step": time_step,
                "tau": 0.5,
                "discharge_time_factor": 80
            },
            "zoom_range": (24, 28)
        },
        {
            "title": "Fast Biphasic Waveform",
            "generator": conventional,
            "params": {
                "frequency": 90,
                "pulse_width": 0.25,
                "interphase_interval": 0.001,
                "time_stop": time_stop,
                "time_step": time_step
            },
            "zoom_range": (10.5, 12.5)
        },
        {
            "title": "Fast Passive Charge Balance",
            "generator": conventional_passive,
            "params": {
                "frequency": 90,
                "pulse_width": 0.25,
                "interphase_interval": 0.001,
                "time_stop": time_stop,
                "time_step": time_step,
                "tau": 0.3,
                "discharge_time_factor": 80
            },
            "zoom_range": (10.5, 12.5)
        }
    ]

    # Create a single figure with multiple subplots
    fig, axes = plt.subplots(len(waveform_configs), 2, figsize=(12, 16))
    fig.tight_layout(pad=5)

    # Dictionary to store all time vectors and waveforms
    waveforms = {}

    # Loop through each configuration to generate and plot
    for i, config in enumerate(waveform_configs):
        # Generate waveform
        t, wave = config["generator"](**config["params"])

        # Store the time vector and waveform in the dictionary
        waveforms[config["title"]] = (t, wave)

        # Plot full waveform
        axes[i, 0].plot(t, wave)
        axes[i, 0].set_title(f"{config['title']} (Full)")
        axes[i, 0].set_xlim(0, 100)
        axes[i, 0].grid(True)

        # Plot zoomed-in waveform
        axes[i, 1].plot(t, wave)
        axes[i, 1].set_title(f"{config['title']} (Zoomed)")
        axes[i, 1].set_xlim(*config["zoom_range"])
        axes[i, 1].grid(True)

    # Show the plots
    plt.show()

    return waveforms

#%% Main Simulation Function with Plotting
import os
import json  # For saving dictionary as a JSON file

# Modified run_simulation function with saving functionality
def run_simulation(waveforms, time_step=0.0001, time_stop=100, stim_amp=-1.5):
    # Dictionary to store activation thresholds for each waveform
    activation_thresholds = {}

    # Loop through each waveform for simulation
    for title, (t, waveform) in waveforms.items():
        print(f"Running simulation for: {title}")

        # Create folder for this waveform
        folder_name = title.replace(" ", "_")
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # Create the fiber model
        fiber = create_fiber()
        fiber.potentials = fiber.point_source_potentials(0, 250, fiber.length / 2, 1, 10)

        # Initialize stimulation
        stimulation = ScaledStim(waveform=waveform, dt=time_step, tstop=time_stop)
        fiber.record_vm()
        fiber.record_gating()
        fiber.record_im()

        # Run the simulation
        ap, time = stimulation.run_sim(stim_amp, fiber)
        print(f'Number of action potentials detected: {ap}')
        print(f'Time of last action potential detection: {time} ms')

        # Find the activation threshold
        amp, ap = stimulation.find_threshold(fiber)
        print(f'Activation threshold: {amp} mA')
        activation_thresholds[title] = amp

        # Plot and save the transmembrane voltage
        end_node = 1
        center_node = int(np.floor(0.5 * (1 + (len(fiber.sections) - 1) / 11)))
        sns.set(font_scale=1.5, style='whitegrid', palette='colorblind')

        plt.figure()
        plt.plot(
            np.array(stimulation.time), list(fiber.vm[end_node]), label='end node', color='royalblue', linewidth=2
        )
        plt.plot(
            np.array(stimulation.time), list(fiber.vm[center_node]), label='center node', color='mediumturquoise', linewidth=2
        )
        plt.legend()
        plt.xlabel('Time (ms)')
        plt.ylabel('$V_m$ $(mV)$')
        ax2 = plt.gca().twinx()
        ax2.plot(np.array(stimulation.time)[:-1], amp * waveform[:], 'k--', label='Stimulus')
        ax2.legend(loc=4)
        ax2.grid(False)
        plt.ylabel('Stimulation amplitude (mA)')
        plt.title(f"{title}: Transmembrane Voltage and Stimulation")
        plot_path = os.path.join(folder_name, f"{title.replace(' ', '_')}_voltage_stimulation.png")
        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()

        # Plot and save the membrane voltage heatmap
        data = pd.DataFrame(np.array(fiber.vm[1:-1]))
        vrest = fiber[0].e_pas
        print('Membrane rest voltage:', vrest)
        plt.figure()
        g = sns.heatmap(
            data, cbar_kws={'label': '$V_m$ $(mV)$'}, cmap='seismic',
            vmax=np.amax(data.values) + vrest, vmin=-np.amax(data.values) + vrest
        )
        plt.ylabel('Node index')
        plt.xlabel('Time (ms)')
        tick_locs = np.linspace(0, len(np.array(stimulation.time)[:-1]), 9)
        labels = [round(np.array(stimulation.time)[int(ind)], 2) for ind in tick_locs]
        g.set_xticks(ticks=tick_locs, labels=labels)
        plt.title(f"{title}: Membrane Voltage Over Time\nRed=depolarized, Blue=hyperpolarized")
        heatmap_path = os.path.join(folder_name, f"{title.replace(' ', '_')}_voltage_heatmap.png")
        plt.tight_layout()
        plt.savefig(heatmap_path)
        plt.close()

        # Plot and save the gating variables
        plt.figure()
        for var in fiber.gating:
            plt.plot(np.array(stimulation.time), list(fiber.gating[var][center_node]), label=var)
        plt.legend()
        plt.xlabel('Time (ms)')
        plt.ylabel('Gating probability')
        ax2 = plt.gca().twinx()
        ax2.plot(np.array(stimulation.time)[:-1], amp * waveform[:], 'k--', label='Stimulus')
        ax2.legend(loc=4)
        ax2.grid(False)
        plt.ylabel('Stimulation amplitude (mA)')
        plt.title(f"{title}: Gating Variables and Stimulation")
        gating_path = os.path.join(folder_name, f"{title.replace(' ', '_')}_gating_variables.png")
        plt.tight_layout()
        plt.savefig(gating_path)
        plt.close()

        # Plot and save the transmembrane currents
        fig, axs = plt.subplots(3, 1, figsize=(5, 5), sharex=True, gridspec_kw={'hspace': 0.3})
        axs[0].plot(np.array(stimulation.time)[:-1], amp * waveform, 'k--', label='Stimulus')
        axs[0].set_title(f"{title}: Stimulus")
        axs[1].plot(np.array(stimulation.time), list(fiber.vm[center_node]), color='mediumturquoise', linewidth=2, label='$V_m$')
        axs[1].plot(np.array(stimulation.time), list(fiber.im[center_node]), color='mediumturquoise', linewidth=2, label='$I_m$', ls='--')
        axs[1].set_title('Center node')
        axs[1].legend()
        axs[2].plot(np.array(stimulation.time), list(fiber.vm[end_node]), color='royalblue', linewidth=2, label='$V_m$')
        axs[2].plot(np.array(stimulation.time), list(fiber.im[end_node]), color='royalblue', linewidth=2, label='$I_m$', ls='--')
        axs[2].set_title('End node')
        axs[2].legend()
        axs[2].set_xlabel('Time (ms)')
        currents_path = os.path.join(folder_name, f"{title.replace(' ', '_')}_currents.png")
        plt.tight_layout()
        plt.savefig(currents_path)
        plt.close()

    # Save the activation thresholds dictionary at the end
    with open("activation_thresholds.json", "w") as f:
        json.dump(activation_thresholds, f)

    return activation_thresholds




#%% Execute the Simulation
if __name__ == "__main__":
    tic=time.time()
    waveforms = generate_waveforms(time_step, time_stop)
    activation_thresholds = run_simulation(waveforms, time_step, time_stop, stim_amp)
    toc=time.time()
    print(f"Time elapsed {toc-tic} s")
    
    
    
    
    
    