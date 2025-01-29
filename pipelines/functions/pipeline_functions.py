# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 15:22:37 2025

@author: nicko
"""


import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import h5py


# def save_plot_simulation_results(folder_name, title, stimulation, fiber, waveform, stim_amp, ap, time, format):
#     """
#     Creates and saves all plots for a neural simulation.
    
#     Parameters:
#     -----------
#     folder_name : str
#         Directory where plots should be saved
#     title : str
#         Title prefix for all plots
#     stimulation : object
#         Stimulation object containing time data
#     fiber : object
#         Fiber object containing voltage, gating, and current data
#     waveform : array-like
#         Stimulation waveform data
#     stim_amp : float
#         Stimulation amplitude
#     ap : int
#         Number of action potentials detected
#     time : float
#         Time of last action potential detection
#     """
#     # Define paths for saving plots
#     plot_path = f"{folder_name}/{title.replace(' ', '_')}_voltage_stimulation.{format}"
#     heatmap_path = f"{folder_name}/{title.replace(' ', '_')}_voltage_heatmap.{format}"
#     gating_path = f"{folder_name}/{title.replace(' ', '_')}_gating_variables.{format}"
#     currents_path = f"{folder_name}/{title.replace(' ', '_')}_currents.{format}"
    
#     # Get node indices
#     end_node = 1
#     center_node = int(np.floor(0.5 * (1 + (len(fiber.sections) - 1) / 11)))
    
#     # Set plot style
#     sns.set(font_scale=1.5, style='whitegrid', palette='colorblind')
    
#     # Plot 1: Transmembrane voltage
#     plt.figure(figsize=(12, 8), dpi=300)
#     plt.plot(
#         np.array(stimulation.time), 
#         list(fiber.vm[end_node]), 
#         label='end node', 
#         color='royalblue', 
#         linewidth=2
#     )
#     plt.plot(
#         np.array(stimulation.time), 
#         list(fiber.vm[center_node]), 
#         label='center node', 
#         color='mediumturquoise', 
#         linewidth=2
#     )
#     plt.legend()
#     plt.xlabel('Time (ms)')
#     plt.ylabel("V_m (mV)")
#     ax2 = plt.gca().twinx()
#     ax2.plot(np.array(stimulation.time)[:len(waveform)], stim_amp * waveform[:], 'k--', label='Stimulus', alpha=0.3)
#     ax2.legend(loc=4)
#     ax2.grid(False)
#     plt.ylabel('Stimulation amplitude (mA)')
#     plt.title(f"{title}: Transmembrane Voltage and Stimulation")
#     plt.tight_layout()
#     plt.savefig(plot_path)
#     plt.close()
    
#     # Plot 2: Membrane voltage heatmap
#     data = pd.DataFrame(np.array(fiber.vm[1:-1]))
#     vrest = fiber[0].e_pas
#     plt.figure(figsize=(14, 10), dpi=300)
#     g = sns.heatmap(
#         data, 
#         cbar_kws={'label': '$V_m$ $(mV)$'}, 
#         cmap='seismic',
#         vmax=np.amax(data.values) + vrest, 
#         vmin=-np.amax(data.values) + vrest,
#         rasterized=True
#     )
#     plt.ylabel('Node index')
#     plt.xlabel('Time (ms)')
#     tick_locs = np.linspace(0, len(np.array(stimulation.time)[:-1]), 9)
#     labels = [round(np.array(stimulation.time)[int(ind)], 2) for ind in tick_locs]
#     g.set_xticks(ticks=tick_locs, labels=labels)
#     plt.title(f"{title}: Membrane Voltage Over Time\n Red=depolarized, Blue=hyperpolarized \n"
#               f"Number of action potentials detected: {ap} \n"
#               f"Time of last action potential detection: {time} ms")
#     plt.tight_layout()
#     plt.savefig(heatmap_path)
#     plt.close()
    
#     # Plot 3: Gating variables
#     plt.figure(figsize=(12, 8), dpi=300)
#     for var in fiber.gating:
#         plt.plot(np.array(stimulation.time), list(fiber.gating[var][center_node]), label=var)
#     plt.legend()
#     plt.xlabel('Time (ms)')
#     plt.ylabel('Gating probability')
#     ax2 = plt.gca().twinx()
#     ax2.plot(np.array(stimulation.time)[:-1], stim_amp * waveform[:], 'k--', label='Stimulus', alpha=0.3)
#     ax2.legend(loc=4)
#     ax2.grid(False)
#     plt.ylabel('Stimulation amplitude (mA)')
#     plt.title(f"{title}: Gating Variables and Stimulation")
#     plt.tight_layout()
#     plt.savefig(gating_path)
#     plt.close()
    
#     # Plot 4: Transmembrane currents
#     fig, axs = plt.subplots(3, 1, figsize=(12, 10), dpi=300, sharex=True, gridspec_kw={'hspace': 0.3})
#     axs[0].plot(np.array(stimulation.time)[:-1], stim_amp * waveform, 'k--', label='Stimulus', alpha=0.3)
#     axs[0].set_title(f"{title}: Stimulus")
#     axs[1].plot(np.array(stimulation.time), list(fiber.vm[center_node]), color='mediumturquoise', linewidth=2, label='$V_m$')
#     axs[1].plot(np.array(stimulation.time), list(fiber.im[center_node]), color='mediumturquoise', linewidth=2, label='$I_m$', ls='--')
#     axs[1].set_title('Center node')
#     axs[1].legend()
#     axs[2].plot(np.array(stimulation.time), list(fiber.vm[end_node]), color='royalblue', linewidth=2, label='$V_m$')
#     axs[2].plot(np.array(stimulation.time), list(fiber.im[end_node]), color='royalblue', linewidth=2, label='$I_m$', ls='--')
#     axs[2].set_title('End node')
#     axs[2].legend()
#     axs[2].set_xlabel('Time (ms)')
#     plt.tight_layout()
#     plt.savefig(currents_path)
#     plt.close()



def save_plot_simulation_results(folder_name, title, stimulation, fiber, waveform, stim_amp, ap, time, format):
    """
    Creates and saves all plots for a neural simulation with a modern, presentation-ready design.
    
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
    format : str
        File format extension (e.g. 'png', 'pdf', etc.)
    """
    
    # ----------------------------------------------------------------------------
    # 1) Universal style settings for a clean, modern look
    # ----------------------------------------------------------------------------
    sns.set_theme(
        style='whitegrid',   # minimal grid
        context='talk',      # larger fonts suitable for presentations
        palette='Set2',      # pleasant color palette
        font_scale=1.2       # scale up the font slightly
    )
    
    # Optionally, tweak some matplotlib RC params to remove top/right spines:
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.titlepad'] = 14
    plt.rcParams['axes.labelpad'] = 10
    
    # Define plot/save paths
    plot_path = f"{folder_name}/{title.replace(' ', '_')}_voltage_stimulation.{format}"
    heatmap_path = f"{folder_name}/{title.replace(' ', '_')}_voltage_heatmap.{format}"
    gating_path = f"{folder_name}/{title.replace(' ', '_')}_gating_variables.{format}"
    currents_path = f"{folder_name}/{title.replace(' ', '_')}_currents.{format}"

    # Get node indices
    end_node = 1
    # Example logic for "center_node" in your original code:
    center_node = int(np.floor(0.5 * (1 + (len(fiber.sections) - 1) / 11)))
    
    # For consistent coloring, pick specific palette colors 
    # (Set2 provides 8 distinct colors)
    colors = sns.color_palette("Set2", 8)
    color_center = colors[0]  # e.g. greenish
    color_end = colors[1]     # e.g. orange
    color_stim = 'darkgray'   # keep stimulus in a neutral color
    
    # ----------------------------------------------------------------------------
    # 2) Plot 1: Transmembrane Voltage vs. Time, plus the Stimulus on a second axis
    # ----------------------------------------------------------------------------
    plt.figure(figsize=(12, 8), dpi=300)
    plt.plot(
        np.array(stimulation.time),
        fiber.vm[end_node],
        label='End node',
        color=color_end,
        linewidth=2
    )
    plt.plot(
        np.array(stimulation.time),
        fiber.vm[center_node],
        label='Center node',
        color=color_center,
        linewidth=2
    )
    plt.xlabel('Time (ms)')
    plt.ylabel("V$_m$ (mV)")
    plt.title(f"{title}: Transmembrane Voltage and Stimulation", pad=15)
    plt.legend(frameon=False)  # no box around legend
    
    # Twin axis for the stimulus
    ax2 = plt.gca().twinx()
    ax2.plot(
        np.array(stimulation.time)[:len(waveform)],
        stim_amp * waveform,
        linestyle='--',
        color=color_stim,
        alpha=0.5,
        label='Stimulus'
    )
    ax2.set_ylabel('Stimulation (mA)')
    ax2.grid(False)
    ax2.legend(loc='lower right', frameon=False)
    
    plt.tight_layout()
    plt.savefig(plot_path, bbox_inches='tight')
    plt.close()
    
    # ----------------------------------------------------------------------------
    # 3) Plot 2: Membrane Voltage Heatmap Over Time
    # ----------------------------------------------------------------------------
    data = pd.DataFrame(np.array(fiber.vm[1:-1]))
    vrest = fiber[0].e_pas if hasattr(fiber[0], 'e_pas') else 0.0  # fallback if e_pas not found
    
    plt.figure(figsize=(14, 10), dpi=300)
    # You may want to adjust the range so that it’s symmetric around V_rest
    # but you can also keep it simpler by auto-scaling:
    g = sns.heatmap(
        data,
        cmap='RdBu_r',  # a diverging colormap, reversed so red=depol, blue=hyperpol
        cbar_kws={'label': 'V$_m$ (mV)'},
        # Optionally define vmin/vmax if you want a symmetrical range:
        vmax=np.amax(data.values) + vrest, 
        vmin=-np.amax(data.values) + vrest,
        rasterized=True
    )
    g.set_xlabel('Time (ms)')
    g.set_ylabel('Node index')
    
    # Adjust x-ticks to match times
    n_ticks = 9
    time_array = np.array(stimulation.time)[:-1]
    tick_locs = np.linspace(0, len(time_array)-1, n_ticks)
    labels = [f"{time_array[int(ind)]:.2f}" for ind in tick_locs]
    g.set_xticks(tick_locs)
    g.set_xticklabels(labels)
    
    # plt.title(
    #     f"{title}: Membrane Voltage Over Time\n"
    #     f"Red = depolarized, Blue = hyperpolarized\n"
    #     f"Action potentials detected: {ap}\n"
    #     f"Last AP detection time: {time} ms", 
    #     pad=15
    # )
    
    # For a cleaner look, remove the left and bottom spines
    sns.despine(left=True, bottom=True)
    
    plt.tight_layout()
    plt.savefig(heatmap_path, bbox_inches='tight')
    plt.close()
    
    # ----------------------------------------------------------------------------
    # 4) Plot 3: Gating Variables vs. Time, plus Stimulus
    # ----------------------------------------------------------------------------
    plt.figure(figsize=(12, 8), dpi=300)
    # Loop through each gating variable
    for i, var in enumerate(fiber.gating):
        plt.plot(
            np.array(stimulation.time),
            fiber.gating[var][center_node],
            label=var,
            linewidth=2
        )
    plt.xlabel('Time (ms)')
    plt.ylabel('Gating Probability')
    plt.title(f"{title}: Gating Variables and Stimulation", pad=15)
    
    plt.legend(frameon=False, ncol=2)  # multi-column if many gating vars
    
    # Twin axis for the stimulus
    ax2 = plt.gca().twinx()
    ax2.plot(
        np.array(stimulation.time)[:len(waveform)],
        stim_amp * waveform,
        linestyle='--',
        color=color_stim,
        alpha=0.5,
        label='Stimulus'
    )
    ax2.set_ylabel('Stimulation (mA)')
    ax2.grid(False)
    
    # We can also combine legends, but here we keep them separate
    ax2.legend(loc='lower right', frameon=False)
    
    plt.tight_layout()
    plt.savefig(gating_path, bbox_inches='tight')
    plt.close()
    
    # ----------------------------------------------------------------------------
    # 5) Plot 4: Transmembrane Currents
    # ----------------------------------------------------------------------------
    fig, axs = plt.subplots(
        3, 1,
        figsize=(12, 10),
        dpi=300,
        sharex=True,
        gridspec_kw={'hspace': 0.3}
    )
    
    # Top subplot: Stimulus
    axs[0].plot(
        np.array(stimulation.time)[:len(waveform)],
        stim_amp * waveform,
        linestyle='--',
        color=color_stim,
        alpha=0.5,
        label='Stimulus'
    )
    axs[0].set_title(f"{title}: Stimulus", pad=10)
    axs[0].legend(frameon=False)
    
    # Middle subplot: Center node V_m and I_m
    axs[1].plot(
        np.array(stimulation.time),
        fiber.vm[center_node],
        color=color_center,
        linewidth=2,
        label='$V_m$'
    )
    axs[1].plot(
        np.array(stimulation.time),
        fiber.im[center_node],
        color=color_center,
        linewidth=2,
        linestyle='--',
        label='$I_m$'
    )
    axs[1].set_title('Center Node', pad=10)
    axs[1].legend(frameon=False)
    
    # Bottom subplot: End node V_m and I_m
    axs[2].plot(
        np.array(stimulation.time),
        fiber.vm[end_node],
        color=color_end,
        linewidth=2,
        label='$V_m$'
    )
    axs[2].plot(
        np.array(stimulation.time),
        fiber.im[end_node],
        color=color_end,
        linewidth=2,
        linestyle='--',
        label='$I_m$'
    )
    axs[2].set_title('End Node', pad=10)
    axs[2].legend(frameon=False)
    axs[2].set_xlabel('Time (ms)')
    
    # Remove unneeded spines for a cleaner look
    for ax in axs:
        sns.despine(ax=ax, right=True, top=True)
    
    plt.tight_layout()
    plt.savefig(currents_path, bbox_inches='tight')
    plt.close()

    
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
    plt.show()
    
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
    plt.show()
    
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
    plt.show()
    
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
    plt.show()


