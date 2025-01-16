import matplotlib.pyplot as plt

# 1. Define the diameter values (x-axis)
diameters = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5]

# 2. Define the threshold values for each method
abott = [-0.02511, -0.02130, -0.01949, -0.01495, -0.01205, -0.01350, -0.01163, -0.01731]
burst = [-0.02372, -0.01949, -0.01659, -0.01465, -0.01326, -0.01338, -0.01163, -0.01743]
conv  = [-0.02378, -0.01918, -0.01616, -0.01465, -0.01296, -0.01338, -0.01139, -0.01737]
conv_passive = [-0.02323, -0.02003, -0.01858, -0.01441, -0.01520, -0.01320, -0.01526, -0.01749]
fast  = [-0.02378, -0.01918, -0.01616, -0.01465, -0.01296, -0.01338, -0.01139, -0.01737]
fast_passive = [-0.02378, -0.02045, -0.01894, -0.01465, -0.01544, -0.01338, -0.01586, -0.01779]

# 3. Create a figure and plot each method with a different marker/color
plt.figure(figsize=(8, 5))


plt.plot(diameters, conv,          marker='s', label='Conventional')
plt.plot(diameters, conv_passive, linestyle='--',  marker='d', label='Conventional Passive')

plt.plot(diameters, fast,          marker='>', label='Fast')
plt.plot(diameters, fast_passive, linestyle='--',  marker='<', label='Fast Passive')

plt.plot(diameters, burst,         marker='^', label='Burst')
plt.plot(diameters, abott, linestyle='--',         marker='o', label='Abott')

# 4. Labeling and cosmetics
plt.title('Activation Threshold vs. Diameter', fontsize=14)
plt.xlabel('Diameter (μm)', fontsize=12)
plt.ylabel('Threshold (mA)', fontsize=12)
plt.grid(True)
plt.legend(fontsize=10)
plt.tight_layout()

# 5. Show the plot
plt.show()
