#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Refactored Neural Fiber Simulation Code
"""
import time
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple, List
import concurrent.futures
import json
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pyfibers import build_fiber, FiberModel, ScaledStim

@dataclass
class SimulationParameters:
    """Data class to store simulation parameters"""
    time_step: float = 0.01          # ms, time step for simulation
    time_stop: float = 200           # ms, total simulation duration
    pre_stim: float = 10             # ms, duration of zeros at start
    length: float = 1e5              # micrometers, fiber length
    diameter: float = 4.0            # micrometers, fiber diameter
    temperature: float = 37          # Celsius
    fiber_model: FiberModel = FiberModel.SMALL_MRG_INTERPOLATION
    exit_t_shift: float = 5          # ms, exit time shift
    thresh_num_aps: int = 1          # n ap needed for threshold search
    stim_multiplier: float = 1.2     # multiplier for stimulus strength
    start_threshold: float = 1       # mA, starting threshold
    conductivity: float = 0.15       # S/m, medium conductivity

    def to_dict(self) -> dict:
        """Convert parameters to dictionary for JSON serialization"""
        return {
            **{k: str(v) if isinstance(v, FiberModel) else v 
               for k, v in self.__dict__.items()},
            "Duration": None  # Will be updated after simulation
        }

class PlotManager:
    """Handles all plotting operations for the simulation"""
    def __init__(self, save_path: Path):
        self.save_path = save_path
        sns.set(font_scale=1.5, style='whitegrid', palette='colorblind')

    def save_voltage_stimulation(self, fiber, stimulation, waveform, stim_amp, title):
        end_node = 1
        center_node = int(np.floor(0.5 * (1 + (len(fiber.sections) - 1) / 11)))
        
        plt.figure(figsize=(12, 8), dpi=300)
        plt.plot(np.array(stimulation.time), list(fiber.vm[end_node]), 
                label='end node', color='royalblue', linewidth=2)
        plt.plot(np.array(stimulation.time), list(fiber.vm[center_node]), 
                label='center node', color='mediumturquoise', linewidth=2)
        plt.legend()
        plt.xlabel('Time (ms)')
        plt.ylabel("V_m (mV)")
        
        ax2 = plt.gca().twinx()
        ax2.plot(np.array(stimulation.time)[:len(waveform)], 
                stim_amp * waveform[:], 'k--', label='Stimulus', alpha=0.3)
        ax2.legend(loc=4)
        ax2.grid(False)
        ax2.set_ylabel('Stimulation amplitude (mA)')
        
        plt.title(f"{title}: Transmembrane Voltage and Stimulation")
        plt.tight_layout()
        plt.savefig(self.save_path / f"{title.replace(' ', '_')}_voltage_stimulation.png")
        plt.close()

    def save_voltage_heatmap(self, fiber, stimulation, ap, time, title):
        data = pd.DataFrame(np.array(fiber.vm[1:-1]))
        vrest = fiber[0].e_pas
        
        plt.figure(figsize=(14, 10), dpi=300)
        g = sns.heatmap(data, cbar_kws={'label': '$V_m$ $(mV)$'}, cmap='seismic',
                       vmax=np.amax(data.values) + vrest, 
                       vmin=-np.amax(data.values) + vrest)
        
        plt.ylabel('Node index')
        plt.xlabel('Time (ms)')
        
        tick_locs = np.linspace(0, len(np.array(stimulation.time)[:-1]), 9)
        labels = [round(np.array(stimulation.time)[int(ind)], 2) for ind in tick_locs]
        g.set_xticks(ticks=tick_locs, labels=labels)
        
        plt.title(f"{title}: Membrane Voltage Over Time\n"
                 f"Red=depolarized, Blue=hyperpolarized\n"
                 f"Number of action potentials detected: {ap}\n"
                 f"Time of last action potential detection: {time} ms")
        plt.tight_layout()
        plt.savefig(self.save_path / f"{title.replace(' ', '_')}_voltage_heatmap.png")
        plt.close()

    def save_all_plots(self, title, t, waveform, params):
        plt.figure(figsize=(12, 8), dpi=300)
        plt.plot(t, waveform)
        plt.title(f"{title} (Full)")
        plt.xlim(0, 100 + params.pre_stim)
        plt.grid(True)
        plt.savefig(self.save_path / "waveform_plots_all.png")
        plt.close()

        plt.figure(figsize=(12, 8), dpi=300)
        plt.plot(t, waveform)
        plt.title(f"{title} (Zoomed)")
        plt.xlim(params.time_stop - 25, params.time_stop)
        plt.grid(True)
        plt.savefig(self.save_path / "waveform_plots_zoomed.png")
        plt.close()

class WaveformGenerator:
    """Handles generation of different waveform types"""
    def __init__(self, params: SimulationParameters):
        self.params = params
        
    def generate_all_waveforms(self) -> Tuple[Dict, List[Dict]]:
        from functions.waveforms import (conventional, conventional_passive, 
                                       burst, burst_abott_linear)
        
        waveform_configs = self._get_waveform_configs()
        waveforms = {}
        
        for config in waveform_configs:
            t, wave = self._generate_single_waveform(config)
            waveforms[config["title"]] = (t, wave)
            
            # Plot waveforms
            plot_manager = PlotManager(self.params.base_path)
            plot_manager.save_all_plots(config["title"], t, wave, self.params)
        
        # Convert generator functions to names for JSON serialization
        serializable_configs = []
        for config in waveform_configs:
            config_copy = config.copy()
            config_copy["generator"] = config_copy["generator"].__name__
            serializable_configs.append(config_copy)
        
        return waveforms, serializable_configs

    def _get_waveform_configs(self) -> List[Dict]:
        from functions.waveforms import (conventional, conventional_passive, 
                                       burst, burst_abott_linear)
        
        return [
            {
                "title": "Conventional Biphasic Waveform",     
                "generator": conventional,
                "params": {
                    "frequency": 40,
                    "pulse_width": 1,
                    "interphase_interval": 0.1,
                    "time_stop": self.params.time_stop,
                    "time_step": self.params.time_step
                }
            },
            {
                "title": "Conventional Passive Charge Balance",
                "generator": conventional_passive,
                "params": {
                    "frequency": 40,
                    "pulse_width": 1,
                    "interphase_interval": 0.1,
                    "time_stop": self.params.time_stop,
                    "time_step": self.params.time_step,
                    "tau": 0.5,
                    "discharge_time_factor": 80
                }
            },
            # Add other waveform configurations here...
        ]

    def _generate_single_waveform(self, config: Dict) -> Tuple[np.ndarray, np.ndarray]:
        t, wave = config["generator"](**config["params"])
        t_zero = np.linspace(0, self.params.pre_stim, 
                            int(self.params.pre_stim / self.params.time_step))
        
        t = np.concatenate([t_zero, t + t_zero[-1]])
        wave = np.concatenate([np.zeros(len(t_zero)), wave])
        
        return t, wave

class FiberSimulation:
    """Main simulation class"""
    def __init__(self, params: SimulationParameters):
        self.params = params
        self.base_path = Path(f"runs/diameter/{params.diameter}")
        self.base_path.mkdir(parents=True, exist_ok=True)
        params.base_path = self.base_path  # Add base_path to params for use in other classes
        self.plot_manager = PlotManager(self.base_path)
        
    def run(self):
        start_time = time.time()
        print(f"Starting simulation for diameter: {self.params.diameter}")
        
        # Generate waveforms
        waveform_gen = WaveformGenerator(self.params)
        waveforms, configs = waveform_gen.generate_all_waveforms()
        
        # Run simulations in parallel
        thresholds = self._run_parallel_simulations(waveforms)
        
        # Save results
        self._save_results(configs, thresholds, start_time)
        
    def _run_parallel_simulations(self, waveforms: Dict) -> Dict:
        thresholds = {}
        with concurrent.futures.ProcessPoolExecutor(max_workers=16) as executor:
            futures = [
                executor.submit(self._run_single_simulation, title, t, waveform)
                for title, (t, waveform) in waveforms.items()
            ]
            
            for future in concurrent.futures.as_completed(futures):
                title, amp = future.result()
                thresholds[title] = amp
                
        return thresholds
    
    def _run_single_simulation(self, title: str, t: np.ndarray, 
                             waveform: np.ndarray) -> Tuple[str, float]:
        print(f"Running simulation for: {title}")
        
        # Create the fiber model
        fiber = build_fiber(
            fiber_model=self.params.fiber_model,
            length=self.params.length,
            diameter=self.params.diameter,
            temperature=self.params.temperature
        )
        
        # Calculate extracellular potentials
        anode = fiber.point_source_potentials(
            0, 250, fiber.length / 2, 
            self.params.start_threshold, self.params.conductivity
        )
        cathode = fiber.point_source_potentials(
            0, 250, fiber.length / 2 + 3000, 
            -self.params.start_threshold, self.params.conductivity
        )
        fiber.potentials = cathode + anode
        
        # Run simulation
        stimulation = ScaledStim(
            waveform=waveform,
            dt=self.params.time_step,
            tstop=self.params.time_stop + self.params.pre_stim
        )
        
        amp, ap = stimulation.find_threshold(
            fiber,
            exit_t_shift=self.params.exit_t_shift,
            thresh_num_aps=self.params.thresh_num_aps
        )
        
        # Generate plots
        self.plot_manager.save_voltage_stimulation(
            fiber, stimulation, waveform,
            amp * self.params.stim_multiplier, title
        )
        
        return title, amp

    def _save_results(self, configs: List[Dict], thresholds: Dict, start_time: float):
        duration = time.time() - start_time
        params_dict = self.params.to_dict()
        params_dict["Duration"] = f"{duration} s"
        
        with open(self.base_path / "simulation_parameters.json", "w") as f:
            json.dump(params_dict, f, indent=4)
            
        with open(self.base_path / "waveform_configs.json", "w") as f:
            json.dump(configs, f, indent=4)
            
        with open(self.base_path / "activation_thresholds.json", "w") as f:
            json.dump(thresholds, f, indent=4)
        
        print(f"Simulation completed in {duration:.2f} seconds")

def main():
    """Main entry point"""
    for diameter in np.arange(3, 6, 0.5):
        params = SimulationParameters(diameter=diameter)
        simulation = FiberSimulation(params)
        simulation.run()

if __name__ == "__main__":
    main()