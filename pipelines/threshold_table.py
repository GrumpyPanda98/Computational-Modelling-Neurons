# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 11:06:15 2025

@author: nicko
"""

import os
import json
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment

# Define the base directory
base_dir = "C:/Users/nicko/Documents/GitHub/Computational-Modelling-Neurons/pipelines/runs/diameter_200ms_1e5mu_cv"  # Adjust this to the correct path

# Initialize data storage
data = []

# Walk through the folder structure
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file == "activation_thresholds.json":
            # Extract diameter from the folder structure
            path_parts = root.split(os.sep)
            diameter = path_parts[-1]  # Identify 'dia_x'

            # Read the JSON file
            json_path = os.path.join(root, file)
            with open(json_path, "r") as f:
                thresholds = json.load(f)

            # Append data to the list for each waveform type
            for waveform, value in thresholds.items():
                data.append({
                    "Diameter": diameter,
                    "Waveform": waveform,
                    "Threshold Value": value
                })

# Convert data to a DataFrame
df = pd.DataFrame(data)

# Round the threshold values to 3 decimals
df["Threshold Value"] = df["Threshold Value"].round(5)

# Pivot the table for better visualization
table = df.pivot_table(index="Diameter", columns="Waveform", values="Threshold Value")

# Rename the columns to the desired names
table.columns = ["Abott", "Burst", "Conventional", "Conventional Passive", "Fast", "Fast Passive"]

# Save the table to an Excel file
output_path = "activation_thresholds_table.xlsx"
table.to_excel(output_path)

# Load the saved Excel file with openpyxl
wb = load_workbook(output_path)
ws = wb.active

# Set all columns to the same width
column_width = 20  # Set your desired column width
for col in ws.columns:
    max_length = 0
    column = col[0].column_letter  # Get the column name (e.g., 'A')
    for cell in col:
        try:
            if len(str(cell.value)) > max_length:
                max_length = len(cell.value)
        except:
            pass
    adjusted_width = (max_length + 2)  # Add some padding
    ws.column_dimensions[column].width = column_width  # Adjust all columns to the same width

# Center the threshold values in the table
for row in ws.iter_rows(min_row=2, min_col=2, max_row=ws.max_row, max_col=ws.max_column):
    for cell in row:
        cell.alignment = Alignment(horizontal='center', vertical='center')

# Save the changes
wb.save(output_path)

print(f"Table saved to {output_path} with adjusted column widths and centered threshold values.")
