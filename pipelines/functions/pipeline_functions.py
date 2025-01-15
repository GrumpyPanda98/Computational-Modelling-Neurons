# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 15:22:37 2025

@author: nicko
"""


import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def plot_simulation_results(folder_name, title, stimulation, fiber, waveform, stim_amp, ap, time):
    """
    Creates and saves all plots for a neural simulation.
    
    Parameters:
    -----------
    folder_name : str
        Directory where plots should be saved
    title : str
        Title prefix for all plots
    stimulation : object
        Stimulation object containing time data
    fiber : object
        Fiber object containing voltage, gating, and current data
    waveform : array-like
        Stimulation waveform data
    stim_amp : float
        Stimulation amplitude
    ap : int
        Number of action potentials detected
    time : float
        Time of last action potential detection
    """
    # Define paths for saving plots
    plot_path = f"{folder_name}/{title.replace(' ', '_')}_voltage_stimulation.png"
    heatmap_path = f"{folder_name}/{title.replace(' ', '_')}_voltage_heatmap.png"
    gating_path = f"{folder_name}/{title.replace(' ', '_')}_gating_variables.png"
    currents_path = f"{folder_name}/{title.replace(' ', '_')}_currents.png"
    
    # Get node indices
    end_node = 1
    center_node = int(np.floor(0.5 * (1 + (len(fiber.sections) - 1) / 11)))
    
    # Set plot style
    sns.set(font_scale=1.5, style='whitegrid', palette='colorblind')
    
    # Plot 1: Transmembrane voltage
    plt.figure(figsize=(12, 8), dpi=300)
    plt.plot(
        np.array(stimulation.time), 
        list(fiber.vm[end_node]), 
        label='end node', 
        color='royalblue', 
        linewidth=2
    )
    plt.plot(
        np.array(stimulation.time), 
        list(fiber.vm[center_node]), 
        label='center node', 
        color='mediumturquoise', 
        linewidth=2
    )
    plt.legend()
    plt.xlabel('Time (ms)')
    plt.ylabel("V_m (mV)")
    ax2 = plt.gca().twinx()
    ax2.plot(np.array(stimulation.time)[:len(waveform)], stim_amp * waveform[:], 'k--', label='Stimulus', alpha=0.3)
    ax2.legend(loc=4)
    ax2.grid(False)
    plt.ylabel('Stimulation amplitude (mA)')
    plt.title(f"{title}: Transmembrane Voltage and Stimulation")
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()
    
    # Plot 2: Membrane voltage heatmap
    data = pd.DataFrame(np.array(fiber.vm[1:-1]))
    vrest = fiber[0].e_pas
    plt.figure(figsize=(14, 10), dpi=300)
    g = sns.heatmap(
        data, 
        cbar_kws={'label': '$V_m$ $(mV)$'}, 
        cmap='seismic',
        vmax=np.amax(data.values) + vrest, 
        vmin=-np.amax(data.values) + vrest
    )
    plt.ylabel('Node index')
    plt.xlabel('Time (ms)')
    tick_locs = np.linspace(0, len(np.array(stimulation.time)[:-1]), 9)
    labels = [round(np.array(stimulation.time)[int(ind)], 2) for ind in tick_locs]
    g.set_xticks(ticks=tick_locs, labels=labels)
    plt.title(f"{title}: Membrane Voltage Over Time\n Red=depolarized, Blue=hyperpolarized \n"
              f"Number of action potentials detected: {ap} \n"
              f"Time of last action potential detection: {time} ms")
    plt.tight_layout()
    plt.savefig(heatmap_path)
    plt.close()
    
    # Plot 3: Gating variables
    plt.figure(figsize=(12, 8), dpi=300)
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
    plt.close()
    
    # Plot 4: Transmembrane currents
    fig, axs = plt.subplots(3, 1, figsize=(12, 10), dpi=300, sharex=True, gridspec_kw={'hspace': 0.3})
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
    plt.close()