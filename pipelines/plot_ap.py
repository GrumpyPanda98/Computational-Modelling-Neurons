import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from openpyxl.styles import Alignment

import seaborn as sns

# Define the base directory
base_dir = "C:/Users/nicko/Documents/GitHub/Computational-Modelling-Neurons/pipelines/runs/stim_multiplier_highstimstep"  # Adjust this if needed

# Define a color palette using seaborn
palette = sns.color_palette("Set1", n_colors=3)  # 3 colors for Conventional, Fast, Burst

# Define step parameters for sub-sampling
# Set step values to 1 to include all data points,
# 2 to skip every other, 3 to skip every third, etc.
action_potentials_step = 2  # Change this value as needed
last_ap_times_step = 2       # Change this value as needed

# ============================
# Processing Action Potentials
# ============================

# Initialize data storage
action_data = []

# Walk through the folder structure
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file == "action_potentials.json":
            # Extract diameter folder name from path
            path_parts = root.split(os.sep)
            folder_name = path_parts[-1]  # e.g. '2.0' or '2_5', etc.

            # Attempt to parse as float; if it fails, just keep the string
            try:
                diameter_value = float(folder_name)
            except ValueError:
                diameter_value = folder_name

            # Read the JSON file
            json_path = os.path.join(root, file)
            with open(json_path, "r") as f:
                thresholds = json.load(f)

            # Append data to the list for each waveform type
            for waveform, value in thresholds.items():
                action_data.append({
                    "Diameter": diameter_value,
                    "Waveform": waveform,
                    "Threshold Value": value
                })

# Convert data to a DataFrame
action_df = pd.DataFrame(action_data)

# If needed, you can round the threshold values
# action_df["Threshold Value"] = action_df["Threshold Value"].round(5)

# Pivot the table for better visualization
action_table = action_df.pivot_table(
    index="Diameter", 
    columns="Waveform", 
    values="Threshold Value"
)

# Rename the columns to the desired names (adjust if needed)
action_table.columns = ["Abott", 
                        "Burst", 
                        "Conventional", 
                        "Conventional Passive", 
                        "Fast", 
                        "Fast Passive"]

# Sort table by Diameter if they are numeric
action_table.sort_index(inplace=True)

# Sub-sample the data based on the step parameter
action_table_subset = action_table.iloc[::action_potentials_step]

# Create a figure and plot each method with a different marker/color
plt.figure(figsize=(8, 5))

# Extract diameters as your x-axis and scale as needed
x_vals = action_table_subset.index * 100  # Adjust scaling if necessary

plt.plot(x_vals, 100 * action_table_subset["Conventional"] / 8,          marker='s', label='Conventional', color=palette[0])
plt.plot(x_vals, 100 * action_table_subset["Conventional Passive"] / 8, linestyle='--',  marker='o', label='Conventional Passive', color=palette[0])

plt.plot(x_vals, 100 * action_table_subset["Fast"] / 18,          marker='s', label='Fast', color=palette[1])
plt.plot(x_vals, 100 * action_table_subset["Fast Passive"] / 18, linestyle='--',  marker='o', label='Fast Passive', color=palette[1])

plt.plot(x_vals, 100 * action_table_subset["Burst"] / 40,         marker='s', label='Burst', color=palette[2])
plt.plot(x_vals, 100 * action_table_subset["Abott"] / 40, linestyle='--',         marker='o', label='Burst Passive', color=palette[2])

# Labeling and cosmetics
plt.title('Fidelity vs. Stimulation Amplitude', fontsize=14)
plt.xlabel('Stimulation Amplitude (% activation threshold)', fontsize=12)
plt.ylabel('Fidelity (%)', fontsize=12)
plt.grid(True)
plt.legend(fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(base_dir, "ap.svg"))
plt.show()

#%% ============================
# Last AP
# ============================

# Initialize data storage
cv_data = []

# Walk through the folder structure
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file == "last_ap_times.json":
            # Extract diameter folder name from path
            path_parts = root.split(os.sep)
            folder_name = path_parts[-1]  # e.g. '2.0' or '2_5', etc.

            # Attempt to parse as float; if it fails, just keep the string
            try:
                diameter_value = float(folder_name)
            except ValueError:
                diameter_value = folder_name

            # Read the JSON file
            json_path = os.path.join(root, file)
            with open(json_path, "r") as f:
                thresholds = json.load(f)

            # Append data to the list for each waveform type
            for waveform, value in thresholds.items():
                cv_data.append({
                    "Diameter": diameter_value,
                    "Waveform": waveform,
                    "Threshold Value": value
                })

# Convert data to a DataFrame
cv_df = pd.DataFrame(cv_data)

# Round the threshold values if needed
cv_df["Threshold Value"] = cv_df["Threshold Value"].round(5)

# Pivot the table for better visualization
cv_table = cv_df.pivot_table(
    index="Diameter", 
    columns="Waveform", 
    values="Threshold Value"
)

# Rename the columns to the desired names (adjust if needed)
cv_table.columns = ["Abott", 
                    "Burst", 
                    "Conventional", 
                    "Conventional Passive", 
                    "Fast", 
                    "Fast Passive"]

# Sort table by Diameter if they are numeric
cv_table.sort_index(inplace=True)

# Sub-sample the data based on the step parameter
cv_table_subset = cv_table.iloc[::last_ap_times_step]

# Create a figure and plot each method with a different marker/color
plt.figure(figsize=(8, 5))

# Extract diameters as your x-axis
x_vals_cv = cv_table_subset.index  # Adjust if scaling is needed

plt.plot(x_vals_cv, cv_table_subset["Conventional"],          marker='s', label='Conventional')
plt.plot(x_vals_cv, cv_table_subset["Conventional Passive"], linestyle='--',  marker='d', label='Conventional Passive')

plt.plot(x_vals_cv, cv_table_subset["Fast"],          marker='>', label='Fast')
plt.plot(x_vals_cv, cv_table_subset["Fast Passive"], linestyle='--',  marker='<', label='Fast Passive')

plt.plot(x_vals_cv, cv_table_subset["Burst"],         marker='^', label='Burst')
plt.plot(x_vals_cv, cv_table_subset["Abott"], linestyle='--',         marker='o', label='Burst Passive')

# Labeling and cosmetics
plt.title('Time of Last Action Potential vs. Stimulation Multiplier', fontsize=14)
plt.xlabel('Stimulation Multiplier', fontsize=12)
plt.ylabel('Time of Last Action Potential (ms)', fontsize=12)
plt.grid(True)
plt.legend(fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(base_dir, "time.svg"))
plt.show()


#%% CV

# Initialize data storage
data = []

# Walk through the folder structure
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file == "conduction_velocity.json":
            # Extract diameter folder name from path
            path_parts = root.split(os.sep)
            folder_name = path_parts[-1]  # e.g. '2.0' or '2_5', etc.

            # Attempt to parse as float; if it fails, just keep the string
            try:
                diameter_value = float(folder_name)
            except ValueError:
                diameter_value = folder_name

            # Read the JSON file
            json_path = os.path.join(root, file)
            with open(json_path, "r") as f:
                thresholds = json.load(f)

            # Append data to the list for each waveform type
            for waveform, value in thresholds.items():
                data.append({
                    "Diameter": diameter_value,
                    "Waveform": waveform,
                    "Threshold Value": value
                })

# Convert data to a DataFrame
df = pd.DataFrame(data)

# Round the threshold values to 5 decimals (or 3, as you had originally)
df["Threshold Value"] = df["Threshold Value"].round(5)

# Pivot the table for better visualization
table = df.pivot_table(
    index="Diameter", 
    columns="Waveform", 
    values="Threshold Value"
)

# Rename the columns to the desired names (adjust if needed)
table.columns = ["Abott", 
                 "Burst", 
                 "Conventional", 
                 "Conventional Passive", 
                 "Fast", 
                 "Fast Passive"]

# Sort table by Diameter if they are numeric
# (If some diameter folders are strings, the sort might fail or produce unexpected results)
table.sort_index(inplace=True)


# 3. Create a figure and plot each method with a different marker/color
plt.figure(figsize=(8, 5))

# Extract diameters as your x-axis
x_vals = table.index

plt.plot(x_vals, table["Conventional"],          marker='s', label='Conventional')
plt.plot(x_vals, table["Conventional Passive"], linestyle='--',  marker='d', label='Conventional Passive')

plt.plot(x_vals, table["Fast"],          marker='>', label='Fast')
plt.plot(x_vals, table["Fast Passive"], linestyle='--',  marker='<', label='Fast Passive')

plt.plot(x_vals, table["Burst"],         marker='^', label='Burst')
plt.plot(x_vals, table["Abott"], linestyle='--',         marker='o', label='Abott')

# 4. Labeling and cosmetics
plt.title('Conduction Velocity vs. Stimulation Amplitude', fontsize=14)
plt.xlabel('Stimulation Amplitude (% activation threshold)', fontsize=12)
plt.ylabel('Conduction Velocity (m/s)', fontsize=12)
plt.grid(True)
plt.legend(fontsize=10)
plt.tight_layout()
plt.savefig(f"{base_dir}/cv.svg")
# 5. Show the plot
plt.show()
