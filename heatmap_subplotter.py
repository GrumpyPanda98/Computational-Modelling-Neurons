import os
import matplotlib.pyplot as plt
from xml.etree import ElementTree as ET
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import cairosvg  # For rendering SVG into matplotlib
from io import BytesIO

# Define base directory (Adjust this path)
base_dir = "C:/Users/nicko/Documents/GitHub/Computational-Modelling-Neurons/pipelines/runs/stim_multiplier_highstimstep/1.40"

# List of heatmap files (Extracted from provided image structure)
heatmap_files = [
    "Burst_Abott_Wave/Burst_Abott_Wave_voltage_heatmap.svg",
    "Burst_Wave/Burst_Wave_voltage_heatmap.svg",
    "Conventional_Biphasic_Waveform/Conventional_Biphasic_Waveform_voltage_heatmap.svg",
    "Conventional_Passive_Charge_Balance/Conventional_Passive_Charge_Balance_voltage_heatmap.svg",
    "Fast_Biphasic_Waveform/Fast_Biphasic_Waveform_voltage_heatmap.svg",
    "Fast_Passive_Charge_Balance/Fast_Passive_Charge_Balance_voltage_heatmap.svg"
]

# Titles for each subplot
titles = [
    "Burst Abott Wave", "Burst Wave",
    "Conventional Biphasic", "Conventional Passive",
    "Fast Biphasic", "Fast Passive"
]

# Create a figure with subplots (2x3 grid)
fig, axes = plt.subplots(2, 3, figsize=(12, 8))
fig.suptitle("Voltage Heatmaps for Different Waveforms", fontsize=16, fontweight='bold')

# Flatten axes array for easy iteration
axes = axes.flatten()

# Process each heatmap and modify SVG viewBox
for i, heatmap_file in enumerate(heatmap_files):
    # Construct full file path
    file_path = os.path.join(base_dir, heatmap_file)
    
    # Read SVG file
    with open(file_path, "r", encoding="utf-8") as f:
        svg_data = f.read()
    
    # Parse SVG with ElementTree
    tree = ET.ElementTree(ET.fromstring(svg_data))
    root = tree.getroot()
    
    # Find the viewBox attribute and modify it
    if "viewBox" in root.attrib:
        viewbox = list(map(float, root.attrib["viewBox"].split()))
        viewbox[1] += viewbox[3] * 0  # Crop 20% from the top
        viewbox[3] *= 0.80  # Adjust height after cropping
        root.attrib["viewBox"] = " ".join(map(str, viewbox))

    # Save modified SVG
    cropped_svg_path = file_path.replace(".svg", "_cropped.svg")
    with open(cropped_svg_path, "w", encoding="utf-8") as f:
        f.write(ET.tostring(root, encoding="unicode"))

    # Convert cropped SVG to PNG for visualization in Matplotlib (not saving, just rendering)
    png_data = BytesIO()
    cairosvg.svg2png(url=cropped_svg_path, write_to=png_data)
    
    # Load PNG image and plot in subplot
    image = plt.imread(BytesIO(png_data.getvalue()))
    axes[i].imshow(image)
    axes[i].set_title(titles[i], fontsize=12, fontweight='bold')
    axes[i].axis("off")  # Hide axes for cleaner visuals

# Adjust layout for better spacing
plt.tight_layout()
plt.subplots_adjust(top=0.9)  # Adjust main title position

# Show the figure
plt.show()
