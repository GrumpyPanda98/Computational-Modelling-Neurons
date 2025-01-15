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
from pyfibers import build_fiber, FiberModel, ScaledStim
from multiprocessing import Manager

# Parallel simulation setup (use Manager to share dictionaries between processes)
manager = Manager()
shared_results = manager.dict()

# Consolidated simulation parameters
simulation_parameters = {
    "time_step": 0.01,              # ms
    "time_stop": 200,               # ms
    "pre_stim": 10,                 # ms, zeros before stimulation
    "length": 1e6,                  # micrometers
    "diameter": 3,                  # micrometers, example diameter
    "temperature": 37,              # Celsius
    "fiber_model": FiberModel.SMALL_MRG_INTERPOLATION,  # Fiber model used for simulation
    "exit_t_shift": 5,              # ms, exit time shift
    "thresh_num_aps": 1,            # n ap needed for threshold search
    "stim_multiplier": 1.2,         # multiplier for stimulus strength
    "conductivity": 0.15            # S/m, conductivity of the medium
}

# Efficient Fiber Creation
def create_fiber(fiber_model, length, diameter, temperature):
    return build_fiber(fiber_model=fiber_model, length=length, diameter=diameter, temperature=temperature)

# Generate waveforms once
def generate_waveforms(time_step, time_stop, pre_stim):
    from functions.waveforms import conventional, conventional_passive, burst, burst_abott_linear
    import numpy as np
    
    waveform_configs = [
        {"title": "Conventional Biphasic", "generator": conventional, "params": {"frequency": 40, "pulse_width": 1, "interphase_interval": 0.1, "time_stop": time_stop, "time_step": time_step}},
        {"title": "Conventional Passive", "generator": conventional_passive, "params": {"frequency": 40, "pulse_width": 1, "interphase_interval": 0.1, "time_stop": time_stop, "time_step": time_step, "tau": 0.5}},
        {"title": "Fast Biphasic", "generator": conventional, "params": {"frequency": 90, "pulse_width": 1, "interphase_interval": 0.001, "time_stop": time_stop, "time_step": time_step}},
        {"title": "Fast Passive", "generator": conventional_passive, "params": {"frequency": 90, "pulse_width": 1, "interphase_interval": 0.001, "time_stop": time_stop, "time_step": time_step, "tau": 0.5}},
        {"title": "Burst Wave", "generator": burst, "params": {"frequency": 40, "burst_frequency": 500, "pulse_width": 1, "interphase_interval": 0.001, "time_stop": time_stop, "time_step": time_step}},
        {"title": "Burst Abott Wave", "generator": burst_abott_linear, "params": {"frequency": 40, "burst_frequency": 500, "pulse_width": 1, "interphase_interval": 0.001, "time_stop": time_stop, "time_step": time_step, "tau": 0.5}}
    ]
    
    # Generate waveforms
    waveforms = {}
    for config in waveform_configs:
        t, wave = config["generator"](**config["params"])
        t_zero = np.linspace(0, pre_stim, int(pre_stim / time_step))
        t = np.concatenate([t_zero, t + t_zero[-1]])
        wave = np.concatenate([np.zeros(len(t_zero)), wave])
        waveforms[config["title"]] = (t, wave)
    
    return waveforms

# Efficient Simulation Execution
def run_single_simulation(main_folder, title, t, waveform, time_step, time_stop, exit_t_shift, thresh_num_aps, conductivity, start_threshold, diameter, shared_results):
    from pipelines.functions.pipeline_functions import plot_simulation_results
    import pickle
    
    print(f"Running simulation for: {title}")
    
    # Folder creation moved outside the simulation to avoid redundancy
    folder_name = os.path.join(main_folder, title.replace(" ", "_"))
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    # Create fiber model (minimize redundant calculations)
    fiber = create_fiber(simulation_parameters["fiber_model"], simulation_parameters["length"], diameter, simulation_parameters["temperature"])
    
    # Calculate extracellular potentials
    anode = fiber.point_source_potentials(0, 250, fiber.length / 2, start_threshold, conductivity)
    cathode = fiber.point_source_potentials(0, 250, fiber.length / 2 + 3000, -start_threshold, conductivity)
    
    fiber.potentials = cathode + anode
    
    # Initialize stimulation and run
    stimulation = ScaledStim(waveform=waveform, dt=time_step, tstop=time_stop)
    amp, ap = stimulation.find_threshold(fiber, exit_t_shift=exit_t_shift, thresh_num_aps=thresh_num_aps)
    stim_amp = amp * simulation_parameters["stim_multiplier"]
    
    # Save results in shared dictionary
    shared_results[title] = amp
    
    # Save fiber and stimulation objects to disk (avoid excessive disk I/O)
    pickle.dump(fiber, open(os.path.join(folder_name, "fiber.pkl"), "wb"))
    pickle.dump(stimulation, open(os.path.join(folder_name, "stimulation.pkl"), "wb"))
    
    return title, amp

# Parallel execution of simulations
def run_simulation_parallel(main_folder, waveforms, time_step, time_stop, diameter, shared_results):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(run_single_simulation, main_folder, title, t, waveform, time_step, time_stop, simulation_parameters["exit_t_shift"], simulation_parameters["thresh_num_aps"], simulation_parameters["conductivity"], simulation_parameters["start_threshold"], diameter, shared_results)
            for title, (t, waveform) in waveforms.items()
        ]
        
        # Collect results
        concurrent.futures.wait(futures)
    
    # Save results once
    with open(os.path.join(main_folder, "activation_thresholds.json"), "w") as f:
        json.dump(shared_results, f)

# Main execution
if __name__ == "__main__":
    start_time = time.time()
    
    # Directory structure setup
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = f"runs\\diameter\\{simulation_parameters['diameter']}"
    os.makedirs(folder_name, exist_ok=True)
    
    # Generate waveforms only once
    waveforms = generate_waveforms(simulation_parameters["time_step"], simulation_parameters["time_stop"], simulation_parameters["pre_stim"])
    
    # Parallel simulation
    run_simulation_parallel(folder_name, waveforms, simulation_parameters["time_step"], simulation_parameters["time_stop"] + simulation_parameters["pre_stim"], simulation_parameters["diameter"], shared_results)
    
    # Save simulation parameters and duration
    simulation_parameters["Duration"] = f"{time.time() - start_time} s"
    with open(os.path.join(folder_name, "simulation_parameters.json"), "w") as f:
        json.dump(simulation_parameters, f, indent=4)
    
    print(f"Time elapsed {time.time() - start_time} s")
