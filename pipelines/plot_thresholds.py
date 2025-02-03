import matplotlib.pyplot as plt

# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 11:06:15 2025

@author: nicko
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from openpyxl.styles import Alignment
import seaborn as sns
# Define the base directory
base_dir = "C:/Users/nicko/Documents/GitHub/Computational-Modelling-Neurons/pipelines/runs/diameterpw0.2"  # Adjust this if needed

# Define a color palette using seaborn
palette = sns.color_palette("Set1", n_colors=3)  # 3 colors for Conventional, Fast, Burst

# Initialize data storage
data = []

# Walk through the folder structure
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file == "activation_thresholds.json":
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
df["Threshold Value"] = df["Threshold Value"].round(3)#*1000 #to micro

# Pivot the table for better visualization
table = df.pivot_table(
    index="Diameter", 
    columns="Waveform", 
    values="Threshold Value"
)

# Rename the columns to the desired names (adjust if needed)
table.columns = ["Burst", 
                  "Burst Passive", 
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

# Define your desired alpha value
alpha_value = 1  # Adjust between 0 (transparent) and 1 (opaque)

plt.figure(figsize=(10, 6))

plt.plot(x_vals, -table["Conventional"],          marker='s', linestyle='-', label='Conventional', color=palette[0])
plt.plot(x_vals, -table["Conventional Passive"], linestyle='--', marker='s', label='Conventional Passive', color=palette[0])

plt.plot(x_vals, -table["Fast"],                marker='^', linestyle='-', label='Fast', color=palette[1])
plt.plot(x_vals, -table["Fast Passive"],        linestyle='--', marker='^', label='Fast Passive', color=palette[1])

plt.plot(x_vals, -table["Burst"],               marker='o', linestyle='-', label='Burst', color=palette[2])
plt.plot(x_vals, -table["Burst Passive"],       linestyle='--', marker='o', label='Burst Passive', color=palette[2])

# Continue with labeling, grid, legend, etc.


# 4. Labeling and cosmetics
plt.title('Activation Threshold vs. Diameter', fontsize=14)
plt.xlabel('Diameter (μm)', fontsize=12)
plt.ylabel('Threshold (μA)', fontsize=12)
plt.grid(True)
plt.legend(fontsize=10)
plt.tight_layout()
plt.savefig(f"{base_dir}/at.svg")
# 5. Show the plot
plt.show()

#%% CV

# Initialize data storage
# data = []

# # Walk through the folder structure
# for root, dirs, files in os.walk(base_dir):
#     for file in files:
#         if file == "conduction_velocity.json":
#             # Extract diameter folder name from path
#             path_parts = root.split(os.sep)
#             folder_name = path_parts[-1]  # e.g. '2.0' or '2_5', etc.

#             # Attempt to parse as float; if it fails, just keep the string
#             try:
#                 diameter_value = float(folder_name)
#             except ValueError:
#                 diameter_value = folder_name

#             # Read the JSON file
#             json_path = os.path.join(root, file)
#             with open(json_path, "r") as f:
#                 thresholds = json.load(f)

#             # Append data to the list for each waveform type
#             for waveform, value in thresholds.items():
#                 data.append({
#                     "Diameter": diameter_value,
#                     "Waveform": waveform,
#                     "Threshold Value": value
#                 })

# # Convert data to a DataFrame
# df = pd.DataFrame(data)

# # Round the threshold values to 5 decimals (or 3, as you had originally)
# df["Threshold Value"] = df["Threshold Value"].round(5)

# # Pivot the table for better visualization
# table = df.pivot_table(
#     index="Diameter", 
#     columns="Waveform", 
#     values="Threshold Value"
# )

# # Rename the columns to the desired names (adjust if needed)
# table.columns = ["Abott", 
#                  "Burst", 
#                  "Conventional", 
#                  "Conventional Passive", 
#                  "Fast", 
#                  "Fast Passive"]

# # Sort table by Diameter if they are numeric
# # (If some diameter folders are strings, the sort might fail or produce unexpected results)
# table.sort_index(inplace=True)


# # 3. Create a figure and plot each method with a different marker/color
# plt.figure(figsize=(8, 5))

# # Extract diameters as your x-axis
# x_vals = table.index

# plt.plot(x_vals, table["Conventional"],          marker='s', label='Conventional')
# plt.plot(x_vals, table["Conventional Passive"], linestyle='--',  marker='d', label='Conventional Passive')

# plt.plot(x_vals, table["Fast"],          marker='>', label='Fast')
# plt.plot(x_vals, table["Fast Passive"], linestyle='--',  marker='<', label='Fast Passive')

# plt.plot(x_vals, table["Burst"],         marker='^', label='Burst')
# plt.plot(x_vals, table["Abott"], linestyle='--',         marker='o', label='Abott')

# # 4. Labeling and cosmetics
# plt.title('Conduction Velocity vs. Diameter', fontsize=14)
# plt.xlabel('Diameter (μm)', fontsize=12)
# plt.ylabel('Conduction Velocity (m/s)', fontsize=12)
# plt.grid(True)
# plt.legend(fontsize=10)
# plt.tight_layout()
# plt.savefig(f"{base_dir}/cv.svg")
# # 5. Show the plot
# plt.show()
