# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 06:21:57 2025

Author: nicko
"""

from functions.waveforms import conventional, conventional_passive, burst, burst_abott_linear
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns  # Ensure seaborn is imported before setting styles

# Directory to save the plot
folder_name = r"pipelines"

# Ensure the directory exists
os.makedirs(folder_name, exist_ok=True)

# Simulation parameters
time_step = 0.001         # ms, time step for simulation
time_stop = 200          # ms, total simulation duration
pre_stim = 10            # ms, duration of zeros at the start of stimulation

# Define parameters for each waveform
waveform_configs = [
    # Conventional
    {
        "category": "Conventional",
        "type": "Active Charge Balance",
        "generator": conventional,
        "params": {
            "frequency": 40,
            "pulse_width": 0.2,
            "interphase_interval": 0,
            "time_stop": time_stop,
            "time_step": time_step
        }
    },
    {
        "category": "Conventional",
        "type": "Passive Charge Balance",
        "generator": conventional_passive,
        "params": {
            "frequency": 40,
            "pulse_width": 0.2,
            "interphase_interval": 0,
            "time_stop": time_stop,
            "time_step": time_step,
            "tau": 0.5,
            "discharge_time_factor": 80
        }
    },
    # Fast
    {
        "category": "Fast",
        "type": "Active Charge Balance",
        "generator": conventional,
        "params": {
            "frequency": 90,
            "pulse_width": 0.2,
            "interphase_interval": 0,
            "time_stop": time_stop,
            "time_step": time_step
        }
    },
    {
        "category": "Fast",
        "type": "Passive Charge Balance",
        "generator": conventional_passive,
        "params": {
            "frequency": 90,
            "pulse_width": 0.2,
            "interphase_interval": 0,
            "time_stop": time_stop,
            "time_step": time_step,
            "tau": 0.5,
            "discharge_time_factor": 80
        }
    },
    # Burst
    {
        "category": "Burst",
        "type": "Active Charge Balance",
        "generator": burst,
        "params": {
            "frequency": 40,
            "burst_frequency": 500,
            "pulse_width": 1,
            "interphase_interval": 0,
            "time_stop": time_stop,
            "time_step": time_step,
        }
    },
    {
        "category": "Burst",
        "type": "Passive Charge Balance",
        "generator": burst_abott_linear,
        "params": {
            "frequency": 40,
            "burst_frequency": 500,
            "pulse_width": 1,
            "interphase_interval": 0,
            "time_stop": time_stop,
            "time_step": time_step,
            "tau": 3,
            "discharge_length": 800
        }
    }
]

# Define X-axis limits for each category
xlim_dict = {
    "Conventional": (0, 50),  # 0 to 20 ms
    "Fast": (0, 50),           # 0 to 20 ms
    "Burst": (0, 50)           # 0 to 25 ms
}

# Set a modern Seaborn style with a white background
sns.set_theme(style="whitegrid")  # Changed from 'darkgrid' to 'whitegrid'

# Update Matplotlib parameters for font styles and sizes
# mpl.rcParams['font.family'] = 'sans-serif'
# mpl.rcParams['font.sans-serif'] = ['Helvetica']
mpl.rcParams.update({'font.size': 12})

# Define a color palette using seaborn
palette = sns.color_palette("Set1", n_colors=3)  # 3 colors for Conventional, Fast, Burst
color_dict = {
    "Conventional": palette[0],
    "Fast": palette[1],
    "Burst": palette[2]
}

# Define line styles for Active and Passive
line_styles = {
    "Active Charge Balance": {"linestyle": "-", "linewidth": 2},
    "Passive Charge Balance": {"linestyle": "-", "linewidth": 2}
}

# Create a 2x3 grid of subplots (2 rows for Active/Passive, 3 columns for categories)
fig, axes = plt.subplots(2, 3, figsize=(15, 10), sharey='row')

# Set the figure facecolor to white
fig.patch.set_facecolor('white')

# Adjust layout to accommodate common labels and prevent overlap
fig.tight_layout(pad=3.0)

# Dictionary to store all time vectors and waveforms (optional, can be used for further analysis)
waveforms = {}

# Mapping of categories to columns
category_order = ["Conventional", "Fast", "Burst"]
category_to_col = {category: idx for idx, category in enumerate(category_order)}

# Loop through each configuration to generate and plot
for config in waveform_configs:
    category = config["category"]
    charge_type = config["type"]  # Active or Passive

    # Determine subplot position
    col_idx = category_to_col[category]
    row_idx = 0 if "Active" in charge_type else 1
    ax = axes[row_idx, col_idx]

    # Generate waveform
    try:
        t, wave = config["generator"](**config["params"])
    except Exception as e:
        print(f"Error generating waveform for {category} {charge_type}: {e}")
        continue

    # Calculate the number of zero steps
    num_zero_steps = int(pre_stim / time_step)
    t_zero = np.linspace(0, pre_stim, num_zero_steps, endpoint=False)

    # Extend the time vector by concatenating the original waveform time vector
    t = np.concatenate([t_zero, t + t_zero[-1] + time_step])

    # Create the waveform with zeros at the start
    wave = np.concatenate([np.zeros(len(t_zero)), wave])

    # Store the time vector and waveform in the dictionary
    waveforms[f"{category} {charge_type}"] = (t, wave)

    # Plot the waveform with enhanced styles
    ax.plot(
        t,
        wave,
        label=charge_type,
        color=color_dict[category],
        linestyle=line_styles[charge_type]["linestyle"],
        linewidth=line_styles[charge_type]["linewidth"],
        alpha=0.8
    )

    # Set title with enhanced font size and weight
    ax.set_title(f"{category} - {charge_type}", fontsize=14, fontweight='bold')

    # Set x-axis limits individually based on category
    ax.set_xlim(xlim_dict[category])

    # Conditional axis labeling
    if row_idx == 1:
        ax.set_xlabel("Time (ms)", fontsize=12)
    else:
        ax.set_xlabel("")  # Remove x-axis label for the first row

    if col_idx == 0:
        ax.set_ylabel("Amplitude", fontsize=12)
    else:
        ax.set_ylabel("")  # Remove y-axis label for the second and third columns

    # Conditional tick label visibility and font sizes
    if row_idx == 0:
        ax.tick_params(labelbottom=False, labelsize=10)  # Remove x-axis tick labels for the first row
    else:
        ax.tick_params(labelsize=10)

    if col_idx != 0:
        ax.tick_params(labelleft=False, labelsize=10)    # Remove y-axis tick labels for the second and third columns
    else:
        ax.tick_params(labelsize=10)

    # Enhance grid lines
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

    # Optional: Add legends if multiple lines per subplot
    # ax.legend(fontsize=10)

# Add a main title for the entire figure
fig.suptitle('Waveform Comparisons', fontsize=16, fontweight='bold', y=0.95)

# Optimize layout further to prevent overlap
plt.subplots_adjust(top=0.90, wspace=0.3, hspace=0.4)

# Save the plot with high resolution and white background
plt.savefig(os.path.join(folder_name, "waveform_plots.svg"), bbox_inches='tight')

# Display the plot
plt.show()
