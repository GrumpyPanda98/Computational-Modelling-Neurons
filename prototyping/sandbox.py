#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 10:05:58 2024

@author: gz57nm
"""

from pyfibers import build_fiber, FiberModel, ScaledStim
import numpy as np
import matplotlib.pyplot as plt
from functions.waveforms import conventional, conventional_passive, burst, burst_passive

#%% Create fiber model

# We can define different parameters of the models such as diameter, 
# sections (as i understand this translates to the amount of nodes), etc..

# Models to choose form:

# FiberModel.MRG_DISCRETE
# FiberModel.MRG_INTERPOLATION
# FiberModel.RATTAY
# FiberModel.SCHILD94
# FiberModel.SCHILD97
# FiberModel.SMALL_MRG_INTERPOLATION
# FiberModel.SUNDT
# FiberModel.TIGERHOLM



fiber = build_fiber(
    fiber_model=FiberModel.MRG_DISCRETE,
    length=2e4,#micro m
    diameter=5.7, # micrometer for rats?
    temperature=37
)


#%% Waveform

time_step=0.05
time_stop=100

# Create cSCS with passive charge balance waveform
t_cp, waveform= conventional_passive(
    frequency=40,          # Frequency of the waveform
    pulse_width=0.2,      # Width of each pulse
    interphase_interval=0.05, # Interval between pulses
    time_stop=time_stop,          # Total time for the waveform
    time_step=time_step,
    tau=0.5,              # Time constant for decay
    discharge_time_factor=80,
    pos_percent=1
)


# # Plot 2: Conventional Passive Charge Balance
# fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 12))
# ax1.plot(t_cp, waveform)
# ax1.set_title('Full')
# ax1.grid(True)

# ax2.plot(t_cp, waveform)
# ax2.set_title('Zoomed')
# ax2.set_xlim(24, 28)
# ax2.grid(True)

# fig2.suptitle('Conventional Passive Charge Balance')
# plt.tight_layout()
# plt.show()

#%% Create fiber potential

fiber.potentials = fiber.point_source_potentials(0, 250, fiber.length / 2, 1, 10) 
# Might need to move the point source to the start of the fiber


# x coord is 0 
# y is 250 microns from fiber, 
# z is fiberlength/2 because we want the potential to be at the center of the node
# current of point source is 1 microAmps
# Conductivity is 10 Siemens/m

# plt.plot(fiber.longitudinal_coordinates, fiber.potentials)
# plt.xlabel('Distance along fiber (μm)')
# plt.ylabel('Electrical potential (mV)')
# plt.title('Extracellular potentials')
# plt.show()

#%% Running simulation

# Create instance of ScaledStim class
stimulation = ScaledStim(waveform=waveform, dt=time_step, tstop=time_stop)

fiber.record_vm()  # save membrane voltage
fiber.record_gating()  # save gating variables
fiber.record_im()  # save membrane current

# Using run_sim method to run sim. Method looks for action potentials at distal end of fiber
stimamp = -1.5  # mA
ap, time = stimulation.run_sim(stimamp, fiber)
print(f'Number of action potentials detected: {ap}')
print(f'Time of last action potential detection: {time} ms')

# Find_threshold returns the stimulation amplitude at which the fiber activates
# and the number of generated action potentials. 

amp, ap = stimulation.find_threshold(fiber)
print(f'Activation threshold: {amp} mA')

# The first current (point source) is associated with modeling the extracellular potential field.
# The second current (stimamp) represents the stimulus amplitude used to excite the fiber and assess its physiological response.

#%% Checking for saved data

# checks if the fiber object has the given attribute:
# transmembrane_potentials (vm), gating variables (gating) and transmembrane currents (im)
saved_vm = fiber.vm is not None
print(f"Saved Vm?\n\t{saved_vm}")

saved_gating = fiber.gating is not None
print(f"Saved gating?\n\t{saved_gating}")

saved_im = fiber.im is not None
print(f"Saved Im?\n\t{saved_im}")


#%% Monitor transmembrane potential

print(fiber.vm)
print(fiber.gating)
print(fiber.im)


#%% Plot of transmembrane voltage for one end compartment and the center compartment to visualize the fiber response to stimulation.

import matplotlib.pyplot as plt
import seaborn as sns

end_node = 1  # not zero since it was passive and therefore has no data to show!
center_node = int(np.floor(0.5 * (1 + (len(fiber.sections) - 1) / 11)))

sns.set(font_scale=1.5, style='whitegrid', palette='colorblind')

# plt.figure()
# plt.plot(
#     np.array(stimulation.time)[:], list(fiber.vm[end_node])[:], label='end node', color='royalblue', linewidth=2
# )
# plt.plot(
#     np.array(stimulation.time)[:],
#     list(fiber.vm[center_node])[:],
#     label='center node',
#     color='mediumturquoise',
#     linewidth=2,
# )
# plt.legend()
# plt.xlabel('Time (ms)')
# plt.ylabel('$V_m$ $(mV)$')
# ax2 = plt.gca().twinx()
# ax2.plot(np.array(stimulation.time)[:-1], stimamp * waveform[:], 'k--', label='Stimulus')
# ax2.legend(loc=4)
# ax2.grid(False)
# plt.ylabel('Stimulation amplitude (mA)')
# plt.show()



#%% Heatmap of membrane potential over compartments

import pandas as pd

data = pd.DataFrame(np.array(fiber.vm[1:-1]))
vrest = fiber[0].e_pas
print('Membrane rest voltage:', vrest)
g = sns.heatmap(
    data,
    cbar_kws={'label': '$V_m$ $(mV)$'},
    cmap='seismic',
    vmax=np.amax(data.values) + vrest,
    vmin=-np.amax(data.values) + vrest,
)
plt.ylabel('Node index')
plt.xlabel('Time (ms)')
tick_locs = np.linspace(0, len(np.array(stimulation.time)[:-1]), 9)
labels = [round(np.array(stimulation.time)[int(ind)], 2) for ind in tick_locs]
g.set_xticks(ticks=tick_locs, labels=labels)
plt.title(
    'Membrane voltage over time\
          \nRed=depolarized, Blue=hyperpolarized'
)
plt.show()


#%% Plot Gating variables

plt.figure()
for var in fiber.gating:
    plt.plot(np.array(stimulation.time)[:], list(fiber.gating[var][center_node])[:], label=var)
plt.legend()
plt.xlabel('Time (ms)')
plt.ylabel('Gating probability')
ax2 = plt.gca().twinx()
ax2.plot(np.array(stimulation.time)[:-1], amp * waveform[:], 'k--', label='Stimulus')
ax2.legend(loc=4)
ax2.grid(False)
plt.ylabel('Stimulation amplitude (mA)')
plt.show()
    
#%% Plotting transmembrane currents    

# plt.figure()
# fig, axs = plt.subplots(3, 1, figsize=(5, 5), sharex=True, gridspec_kw={'hspace': 0.3})
# plt.sca(axs[0])
# # plot stimulus
# plt.plot(np.array(stimulation.time)[:-1], amp * waveform[:], 'k--', label='Stimulus')
# plt.title('Stimulus')
# plt.sca(axs[1])
# # plot membrane voltage
# plt.plot(
#     np.array(stimulation.time)[:],
#     list(fiber.vm[center_node])[:],
#     color='mediumturquoise',
#     linewidth=2,
#     label='$V_m$',
# )
# # plot im
# plt.plot(
#     np.array(stimulation.time)[:],
#     list(fiber.im[center_node])[:],
#     color='mediumturquoise',
#     linewidth=2,
#     label='$I_m$',
#     ls='--',
# )
# plt.title('Center node')
# plt.legend()
# plt.sca(axs[2])
# # plot end node
# plt.plot(
#     np.array(stimulation.time)[:], list(fiber.vm[end_node])[:], color='royalblue', linewidth=2, label='$V_m$'
# )
# plt.plot(
#     np.array(stimulation.time)[:],
#     list(fiber.im[end_node])[:],
#     color='royalblue',
#     linewidth=2,
#     label='$I_m$',
#     ls='--',
# )
# plt.title('End node')
# plt.legend()
# axs[2].set_xlabel('Time (ms)')
# plt.show()

# #%% Animation
# import os
# os.environ["IMAGEIO_FFMPEG_EXE"] = "/opt/homebrew/bin/ffmpeg"  # Replace with the actual path


# from moviepy.editor import VideoClip
# from moviepy.video.io.bindings import mplfig_to_npimage

# fps = 30
# skip = 100  # do every 10th timestep
# stop = 1000 / time_step  # stop after 2 milliseconds

# duration = stop / fps / skip  # milliseconds
# ylim = (np.amin(list(fiber.vm[1:-1]))), np.amax(list(fiber.vm[1:-1]))

# fig, ax = plt.subplots()


# def make_frame(i):
#     """Create frame of video.

#     :param i: index of frame, given to function by moviepy
#     :returns: figure as image
#     """
#     ind = int(i * skip * fps)
#     ax.clear()
#     ax.set_ylim(ylim)
#     ax.plot([v[ind] for v in fiber.vm[1:-1]], lw=3)
#     plt.title(f'Time: {stimulation.time[ind]:0.1f} ms')
#     plt.ylabel('$V_m$')
#     plt.xlabel('Node index')
#     plt.tight_layout()
#     return mplfig_to_npimage(fig)


# animation = VideoClip(make_frame, duration=duration)
# animation.write_videofile('ap.mp4', fps=fps)
# plt.close()

# #%% Display animation
# os.system("open ap.mp4")

