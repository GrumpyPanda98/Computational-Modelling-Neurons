#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 20:35:02 2024

@author: gz57nm
"""
import time
from datetime import datetime
import concurrent.futures
import os
import json
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pyfibers import build_fiber, FiberModel, ScaledStim


#%% Simulation Parameters
time_step = 0.01          # ms, time step for simulation
time_stop = 100           # ms, total simulation duration
pre_stim = 10              # ms, duration of zeros at the start of stimulation
length = 1e5              # micrometers, length of the fiber
diameter = 4             # micrometers, diameter of the fiber
temperature = 37          # Celsius, temperature of the simulation
fiber_model = FiberModel.SMALL_MRG_INTERPOLATION  # Fiber model used for simulation
exit_t_shift = 5          # ms, exit time shift
thresh_num_aps = 1        # n ap needed for threshold search
stim_multiplier = 1.2     # multiplier for stimulus strength
start_threshold = 1       # mA, starting threshold for stimulation
conductivity = 0.15       # S/m, conductivity of the medium

# Consolidated simulation parameters
simulation_parameters = {
    "time_step": time_step,              # ms
    "time_stop": time_stop,              # ms
    "pre_stim": pre_stim,                # ms, zeros before stimulation
    "length": length,                    # micrometers
    "diameter": diameter,                # micrometers
    "temperature": temperature,          # Celsius
    "fiber_model": f'{fiber_model}',     # Fiber model name
    "exit_t_shift": exit_t_shift,        # ms
    "thresh_num_aps": thresh_num_aps,    # Action potentials threshold
    "stim_multiplier": stim_multiplier, # Multiplier for stimulation
    "conductivity": conductivity         # S/m
}


# Create a timestamped folder
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
folder_name = f"simulation_results_{timestamp}"

#%% Define the function to create a fiber model
def create_fiber(fiber_model=fiber_model, length=length, diameter=diameter, temperature=temperature):
    return build_fiber(fiber_model=fiber_model, length=length, diameter=diameter, temperature=temperature)


#%% Generate and Plot All Waveforms
def generate_waveforms(time_step, time_stop, pre_stim=0):
    from functions.waveforms import conventional, conventional_passive, burst, burst_abott
    import numpy as np
    import matplotlib.pyplot as plt
    import os
    
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
            "zoom_range": (time_stop-25, time_stop)
        },
        {
            "title": "Conventional Passive Charge Balance",
            "generator": conventional_passive,
            "params": {
                "frequency": 40,
                "pulse_width": 0.2,
                "interphase_interval": 0.1,
                "time_stop": time_stop,
                "time_step": time_step,
                "tau": 0.5,
                "discharge_time_factor": 80
            },
            "zoom_range": (time_stop-25, time_stop)
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
            "zoom_range": (time_stop-25, time_stop)
        },
        {
            "title": "Fast Passive Charge Balance",
            "generator": conventional_passive,
            "params": {
                "frequency": 90,
                "pulse_width": 1,
                "interphase_interval": 0.001,
                "time_stop": time_stop,
                "time_step": time_step,
                "tau": 0.5,
                "discharge_time_factor": 80
            },
            "zoom_range": (time_stop-25, time_stop)
        },
        
        {
            "title": "Burst Wave",
            "generator": burst,
            "params": {
                "frequency": 40,
                "burst_frequency": 500,
                "pulse_width": 1,
                "interphase_interval": 0.001,
                "time_stop": time_stop,
                "time_step": time_step,
            },
            "zoom_range": (time_stop-25, time_stop)
        },
        
        {
            "title": "Burst Abott Wave",
            "generator": burst_abott,
            "params": {
                "frequency": 40,
                "burst_frequency": 500,
                "pulse_width": 1,
                "interphase_interval": 0.001,
                "time_stop": time_stop,
                "time_step": time_step,
                "tau": 0.5,
                "discharge_length": 800
            },
            "zoom_range": (time_stop-25, time_stop)
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

        # Calculate the time vector for the zeros (pre_stim)
        t_zero = np.linspace(0, pre_stim, int(pre_stim / time_step))
        # Extend the time vector by concatenating the original waveform time vector
        t = np.concatenate([t_zero, t + t_zero[-1]])

        # Create the waveform with zeros at the start
        wave = np.concatenate([np.zeros(len(t_zero)), wave])

        # Store the time vector and waveform in the dictionary
        waveforms[config["title"]] = (t, wave)

        # Plot full waveform
        axes[i, 0].plot(t, wave)
        axes[i, 0].set_title(f"{config['title']} (Full)")
        axes[i, 0].set_xlim(0, 100+pre_stim)
        axes[i, 0].grid(True)

        # Plot zoomed-in waveform
        axes[i, 1].plot(t, wave)
        axes[i, 1].set_title(f"{config['title']} (Zoomed)")
        axes[i, 1].set_xlim(*config["zoom_range"])
        axes[i, 1].grid(True)

    plt.savefig(os.path.join(folder_name, "waveform_plots.png"))
    plt.show()

    for config in waveform_configs:
        config["generator"] = config["generator"].__name__  # Convert function to its name

    return waveforms, config

#%% Function to run a single simulation
def run_single_simulation(main_folder, title, t, waveform, time_step, time_stop, exit_t_shift, thresh_num_aps, conductivity, start_threshold):
    print(f"Running simulation for: {title}")

    # Create folder for this waveform
    folder_name = os.path.join(main_folder, title.replace(" ", "_"))
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        
    # Paths for saving plots
    plot_path = os.path.join(folder_name, f"{title.replace(' ', '_')}_voltage_stimulation.png")
    heatmap_path = os.path.join(folder_name, f"{title.replace(' ', '_')}_voltage_heatmap.png")
    gating_path = os.path.join(folder_name, f"{title.replace(' ', '_')}_gating_variables.png")
    currents_path = os.path.join(folder_name, f"{title.replace(' ', '_')}_currents.png")

    # Create the fiber model
    fiber = create_fiber()

    # Calculate extracellular potentials for each electrode
    anode = fiber.point_source_potentials(0, 250, fiber.length / 2, start_threshold, conductivity)
    cathode = fiber.point_source_potentials(0, 250, fiber.length / 2+3000, -start_threshold, conductivity)
    

    fiber.potentials = cathode + anode

    # Initialize stimulation
    stimulation = ScaledStim(waveform=waveform, dt=time_step, tstop=time_stop)
    
    # Find the activation threshold
    amp, ap = stimulation.find_threshold(fiber, exit_t_shift=exit_t_shift, thresh_num_aps=thresh_num_aps)
    print(f'Activation threshold: {amp} mA')
    
    stim_amp=amp*stim_multiplier
    
    # Save recording
    fiber.record_vm()
    fiber.record_gating()
    fiber.record_im()
    
    # Run the simulation
    ap, time = stimulation.run_sim(stim_amp, fiber)
    print(f'Number of action potentials detected: {ap}')
    print(f'Time of last action potential detection: {time} ms')


    # Plot and save the transmembrane voltage
    end_node = 1
    center_node = int(np.floor(0.5 * (1 + (len(fiber.sections) - 1) / 11)))
    sns.set(font_scale=1.5, style='whitegrid', palette='colorblind')

    plt.figure(figsize=(12, 8), dpi=300)  # Increased figsize and dpi
    plt.plot(
        np.array(stimulation.time), list(fiber.vm[end_node]), label='end node', color='royalblue', linewidth=2
    )
    plt.plot(
        np.array(stimulation.time), list(fiber.vm[center_node]), label='center node', color='mediumturquoise', linewidth=2
    )
    plt.legend()
    plt.xlabel('Time (ms)')
    plt.ylabel("V_m (mV)")
    ax2 = plt.gca().twinx()
    ax2.plot(np.array(stimulation.time)[:len(waveform)], stim_amp* waveform[:], 'k--', label='Stimulus', alpha=0.3)
    ax2.legend(loc=4)
    ax2.grid(False)
    plt.ylabel('Stimulation amplitude (mA)')
    plt.title(f"{title}: Transmembrane Voltage and Stimulation")
    plt.tight_layout()
    plt.savefig(plot_path)
    # plt.show()
    plt.close()

    # Plot and save the membrane voltage heatmap
    data = pd.DataFrame(np.array(fiber.vm[1:-1]))
    vrest = fiber[0].e_pas
    print('Membrane rest voltage:', vrest)
    plt.figure(figsize=(14, 10), dpi=300)  # Increased figsize and dpi
    g = sns.heatmap(
        data, cbar_kws={'label': '$V_m$ $(mV)$'}, cmap='seismic',
        vmax=np.amax(data.values) + vrest, vmin=-np.amax(data.values) + vrest
    )
    plt.ylabel('Node index')
    plt.xlabel('Time (ms)')
    tick_locs = np.linspace(0, len(np.array(stimulation.time)[:-1]), 9)
    labels = [round(np.array(stimulation.time)[int(ind)], 2) for ind in tick_locs]
    g.set_xticks(ticks=tick_locs, labels=labels)
    plt.title(f"{title}: Membrane Voltage Over Time\n Red=depolarized, Blue=hyperpolarized \n Number of action potentials detected: {ap} \n Time of last action potential detection: {time} ms")
    plt.tight_layout()
    plt.savefig(heatmap_path)
    # plt.show()
    plt.close()

    # Plot and save the gating variables
    plt.figure(figsize=(12, 8), dpi=300)  # Increased figsize and dpi
    for var in fiber.gating:
        plt.plot(np.array(stimulation.time), list(fiber.gating[var][center_node]), label=var)
    plt.legend()
    plt.xlabel('Time (ms)')
    plt.ylabel('Gating probability')
    ax2 = plt.gca().twinx()
    ax2.plot(np.array(stimulation.time)[:-1], stim_amp * waveform[:], 'k--', label='Stimulus', alpha=0.3)
    ax2.legend(loc=4)
    ax2.grid(False)
    plt.ylabel('Stimulation amplitude (mA)')
    plt.title(f"{title}: Gating Variables and Stimulation")
    plt.tight_layout()
    plt.savefig(gating_path)
    # plt.show()
    plt.close()

    # Plot and save the transmembrane currents
    fig, axs = plt.subplots(3, 1, figsize=(12, 10), dpi=300, sharex=True, gridspec_kw={'hspace': 0.3})  # Increased figsize and dpi
    axs[0].plot(np.array(stimulation.time)[:-1], stim_amp * waveform, 'k--', label='Stimulus', alpha=0.3)
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
    plt.tight_layout() 
    plt.savefig(currents_path) 
    # plt.show() 
    plt.close()
    

    
    return title, amp



#%% Function to run all simulations in parallel using all CPU cores
def run_simulation_parallel(main_folder, waveforms, time_step, time_stop):
    activation_thresholds = {}

    # Use ThreadPoolExecutor for CPU-bound tasks
    with concurrent.futures.ProcessPoolExecutor(max_workers=16) as executor:
        # Submit all simulations to the executor
        futures = [
            executor.submit(run_single_simulation, main_folder, title, t, waveform, time_step, time_stop, exit_t_shift, thresh_num_aps, conductivity, start_threshold)
            for title, (t, waveform) in waveforms.items()
        ]

        # Collect the results as they complete
        for future in concurrent.futures.as_completed(futures):
            title, amp = future.result()
            activation_thresholds[title] = amp
            

    with open(os.path.join(folder_name, "activation_thresholds.json"), "w") as f:
        json.dump(activation_thresholds, f)

    return activation_thresholds

#%% Execute the Simulation
if __name__ == "__main__":
    tic=time.time()
    
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    waveforms, waveform_configs = generate_waveforms(time_step, time_stop, pre_stim)
    activation_thresholds = run_simulation_parallel(folder_name, waveforms, time_step, time_stop+pre_stim)
    
    toc=time.time()
    
    simulation_parameters["Duration"] = f"{toc-tic} s"

    with open(os.path.join(folder_name, "waveform_configs.json"), "w") as json_file:
        json.dump(waveform_configs, json_file, indent=4)
    
    with open(os.path.join(folder_name, "simulation_parameters.json"), "w") as json_file:
        json.dump(simulation_parameters, json_file, indent=4)
    
    print(f"Time elapsed {toc-tic} s")
    
    
    
    