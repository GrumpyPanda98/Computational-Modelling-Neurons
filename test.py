# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from pyfibers import build_fiber, FiberModel, ScaledStim
import numpy as np
import matplotlib.pyplot as plt
import functions 

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

n_sections = 265

fiber = build_fiber(
    fiber_model=FiberModel.MRG_DISCRETE,
    n_sections=n_sections,
    diameter=10, # micrometer for rats?
    temperature=35
)

#%% Create a biphasic square waveform for stimulation, similar to multichannel stim software.

# Setup for simulation
time_step = 0.001  # ms
time_stop = 100  # ms
frequency = 40  # Hz
pulse_width = 0.2  # ms
interphase_interval = 0.1  # ms (interval between positive and negative pulses)

# Calculate period and number of time points for each pulse
period = 1000 / frequency  # ms (one full cycle duration)
pulse_points = int(pulse_width / time_step)  # number of points for the pulse width
half_pulse_points = pulse_points // 2  # half of the pulse width for biphasic pulse
gap_points = int(interphase_interval / time_step)  # number of points for the interphase interval
points_per_period = int(period / time_step)  # number of points in one cycle

# Create time vector
t = np.arange(0, time_stop, time_step)  # ms

# Create a single biphasic pulse: first half positive, then gap, then second half negative
biphasic_pulse = np.concatenate([
    np.ones(half_pulse_points), 
    np.zeros(gap_points), 
    -np.ones(half_pulse_points)
])

# Create the full waveform by repeating the biphasic pulse and adding zeros for the rest of the period
waveform = np.zeros_like(t)
for i in range(0, len(t), points_per_period):
    waveform[i:i + len(biphasic_pulse)] = biphasic_pulse[:len(waveform[i:i + len(biphasic_pulse)])]

# Plot the waveform
plt.plot(t, waveform)
plt.title('Biphasic Stimulation Waveform with Interphase Interval (40 Hz, 0.2 ms pulse width)')
plt.xlabel('Time (ms)')
plt.ylabel('Amplitude')
plt.show()

#%% Create a biphasic square waveform for stimulation with passive charge balance

import numpy as np
import matplotlib.pyplot as plt

# Setup for simulation
time_step = 0.001  # ms
time_stop = 1  # ms
frequency = 40  # Hz
pulse_width = 0.2  # ms
interphase_interval = 0.05  # ms (interval between positive and negative pulses)
tau = 0.05  # ms (time constant for exponential decay)

# Calculate period and number of time points for each pulse
period = 1000 / frequency  # ms (one full cycle duration)
pulse_points = int(pulse_width / time_step)  # number of points for the pulse width
gap_points = int(interphase_interval / time_step)  # number of points for the interphase interval
points_per_period = int(period / time_step)  # number of points in one cycle

# Create time vector
t = np.arange(0, time_stop, time_step)  # ms

# Create the positive phase with an exponential decay
t_exp = np.arange(0, pulse_width / 2, time_step)  # time vector for the decay phase
positive_phase = np.exp(-t_exp / tau)

# Normalize the exponential so it starts at 1 and ends closer to zero
positive_phase = (positive_phase - positive_phase[-1]) / (positive_phase[0] - positive_phase[-1])

# Create the negative phase (rectangular pulse)
half_pulse_points = len(t_exp)  # match length of positive phase for symmetry
negative_phase = -np.ones(half_pulse_points)

# Create the biphasic pulse: positive phase (exponential decay), gap, negative phase
biphasic_pulse = np.concatenate([
    positive_phase,
    np.zeros(gap_points),
    negative_phase
])

# Create the full waveform by repeating the biphasic pulse and adding zeros for the rest of the period
waveform = np.zeros_like(t)
for i in range(0, len(t), points_per_period):
    waveform[i:i + len(biphasic_pulse)] = biphasic_pulse[:len(waveform[i:i + len(biphasic_pulse)])]

# Plot the waveform
plt.plot(t, waveform)
plt.title('Biphasic Stimulation Waveform with Passive Charge Balance (40 Hz, 0.2 ms pulse width)')
plt.xlabel('Time (ms)')
plt.ylabel('Amplitude')
plt.show()

#%% Burst biphasic

import numpy as np
import matplotlib.pyplot as plt

# Setup for simulation
time_step = 0.001  # ms
time_stop = 100 # ms
frequency = 40  # Hz (carrier frequency)
burst_frequency = 500  # Hz (burst frequency)
pulse_width = 0.1  # ms
interphase_interval = 0.1  # ms (interval between positive and negative pulses)

# Calculate periods and number of time points
period_40Hz = 1000 / frequency  # ms (one full cycle duration for 40 Hz)
period_500Hz = 1000 / burst_frequency  # ms (one full cycle duration for 500 Hz)
pulse_points = int(pulse_width / time_step)  # number of points for the pulse width
half_pulse_points = pulse_points // 2  # half of the pulse width for biphasic pulse
gap_points = int(interphase_interval / time_step)  # number of points for the interphase interval
points_per_period_40Hz = int(period_40Hz / time_step)  # number of points in one 40 Hz cycle
points_per_period_500Hz = int(period_500Hz / time_step)  # number of points in one 500 Hz cycle

# Create time vector
t = np.arange(0, time_stop, time_step)  # ms

# Create a single biphasic pulse: first half positive, then gap, then second half negative
biphasic_pulse = np.concatenate([
    np.ones(half_pulse_points), 
    np.zeros(gap_points), 
    -np.ones(half_pulse_points)
])

# Create a burst train of biphasic pulses at 500 Hz
burst_duration = period_40Hz / 2  # ms (burst duration is half the 40 Hz period)
burst_points = int(burst_duration / time_step)  # number of points for the burst duration

burst_pulse = np.zeros(burst_points)
for i in range(0, burst_points, points_per_period_500Hz):
    burst_pulse[i:i + len(biphasic_pulse)] = biphasic_pulse[:len(burst_pulse[i:i + len(biphasic_pulse)])]

# Create the full waveform by repeating the burst pulse within each 40 Hz period
waveform = np.zeros_like(t)
for i in range(0, len(t), points_per_period_40Hz):
    waveform[i:i + burst_points] = burst_pulse[:len(waveform[i:i + burst_points])]

# Plot the waveform
plt.plot(t, waveform)
plt.title('Burst SCS Waveform (500 Hz bursts modulated by 40 Hz carrier)')
plt.xlabel('Time (ms)')
plt.ylabel('Amplitude')
plt.show()


#%% BurstDR
import numpy as np
import matplotlib.pyplot as plt

# Parameters
time_stop = 0.1  # Duration of the signal (seconds)
time_step = 0.0001  # Time step (sampling period)
burst_frequency = 500  # Burst frequency (Hz)
carrier_frequency = 45  # Carrier frequency (Hz)
burst_duration_ms = 10  # Duration of each burst in milliseconds (which naturally gives 5 pulses)
discharge_tau = 0.01  # Time constant for passive discharge (10 ms)

# Sampling frequency
fs = 1 / time_step  # Samples per second (10,000 Hz for time_step = 0.0001)

# Time vector
t = np.linspace(0, time_stop, int(fs * time_stop), endpoint=False)

# Create the 500 Hz burst component as a square wave
burst_wave = 0.5 * (1 + np.sign(np.sin(2 * np.pi * burst_frequency * t)))

# Create the 45 Hz carrier wave as a square wave for bursts
carrier_wave = 0.5 * (1 + np.sign(np.sin(2 * np.pi * carrier_frequency * t)))

# Create an empty waveform to fill with bursts
burstdr_waveform = np.zeros_like(t)

# Calculate burst duration in samples (exactly 5 pulses at 500 Hz = 5/500 s)
burst_duration_samples = int(burst_duration_ms * fs / 1000)

# Apply bursts according to the carrier wave
carrier_indices = np.where(np.diff(carrier_wave) > 0)[0]  # Start indices of bursts

# Define the passive discharge (exponential decay) between bursts
passive_discharge = lambda length: np.exp(-np.linspace(0, length, length) / (discharge_tau * fs))

for i, start_idx in enumerate(carrier_indices):
    end_idx = start_idx + burst_duration_samples
    
    # Ensure the burst fits within the time vector
    if end_idx > len(t):
        break
    
    # Envelope: mirrored exponential decay for each burst
    envelope = np.exp(-np.abs(np.linspace(0, burst_duration_ms, burst_duration_samples)) / (-0.005 * 1000))  # Mirrored envelope over 5 ms
    
    # Apply the burst waveform modulated by the mirrored envelope
    burstdr_waveform[start_idx:end_idx] = burst_wave[start_idx:end_idx] * envelope
    
    # Apply passive discharge phase between bursts if there is a gap
    if i < len(carrier_indices) - 1:
        next_start_idx = carrier_indices[i + 1]
        gap_end_idx = min(next_start_idx, len(t))
        gap_length = gap_end_idx - end_idx
        
        # Apply the passive discharge if there is enough gap
        if gap_length > 0:
            burstdr_waveform[end_idx:gap_end_idx] = passive_discharge(gap_length)

# Normalize the waveform so all pulses have a maximum of 1
burstdr_waveform /= np.max(burstdr_waveform)

# Plot the waveform
plt.figure(figsize=(10, 4))
plt.plot(t, burstdr_waveform)
plt.title(f'BurstDR SCS Waveform with Passive Discharge (Burst: {burst_frequency} Hz, Carrier: {carrier_frequency} Hz)')
plt.xlabel('Time (ms)')
plt.ylabel('Amplitude')
plt.grid()
plt.show()

#%% Create fiber potential

fiber.potentials = fiber.point_source_potentials(0, 250, fiber.length / 2, 1, 10)
# x coord is 0 
# y is 250 microns from fiber, 
# z is fiberlength/2 because we want the potential to be at the center of the node
# current of point source is 1 microAmps
# Conductivity is 10 Siemens/m

plt.plot(fiber.longitudinal_coordinates, fiber.potentials)
plt.xlabel('Distance along fiber (μm)')
plt.ylabel('Electrical potential (mV)')
plt.title('Extracellular potentials')
plt.show()

#%% Running simulation

time_step = .001
time_stop = 20

# Create instance of ScaledStim class
stimulation = ScaledStim(waveform=waveform, dt=time_step, tstop=time_stop)

fiber.record_vm()  # save membrane voltage
fiber.record_gating()  # save gating variables
fiber.record_im()  # save membrane current

# Using run_sim method to run sim. Method looks for action potentials at distal end of fiber
stimamp = -0.05  # mA
ap, time = stimulation.run_sim(stimamp, fiber)
print(f'Number of action potentials detected: {ap}')
print(f'Time of last action potential detection: {time} ms')

# Find_threshold returns the stimulation amplitude at which the fiber activates
# and the number of generated action potentials. 

amp, ap = stimulation.find_threshold(fiber)
print(f'Activation threshold: {amp} mA')

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
center_node = int(np.floor(0.5 * (1 + (n_sections - 1) / 11)))

sns.set(font_scale=1.5, style='whitegrid', palette='colorblind')

plt.figure()
plt.plot(
    np.array(stimulation.time)[:2000], list(fiber.vm[end_node])[:2000], label='end node', color='royalblue', linewidth=2
)
plt.plot(
    np.array(stimulation.time)[:2000],
    list(fiber.vm[center_node])[:2000],
    label='center node',
    color='mediumturquoise',
    linewidth=2,
)
plt.legend()
plt.xlabel('Time (ms)')
plt.ylabel('$V_m$ $(mV)$')
ax2 = plt.gca().twinx()
ax2.plot(np.array(stimulation.time)[:2000], stimamp * waveform[:2000], 'k--', label='Stimulus')
ax2.legend(loc=4)
ax2.grid(False)
plt.ylabel('Stimulation amplitude (mA)')
plt.show()



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
plt.xlim([0, 1000])
plt.ylabel('Node index')
plt.xlabel('Time (ms)')
tick_locs = np.linspace(0, len(np.array(stimulation.time)[:1000]), 9)
labels = [round(np.array(stimulation.time)[int(ind)], 2) for ind in tick_locs]
g.set_xticks(ticks=tick_locs, labels=labels)
plt.title(
    'Membrane voltage over time\
          \nRed=depolarized, Blue=hyperpolarized'
)
plt.show()


#%% Plot Gating variables

# plot gating variables
plt.figure()
for var in fiber.gating:
    plt.plot(np.array(stimulation.time)[:2000], list(fiber.gating[var][6])[:2000], label=var)
plt.legend()
plt.xlabel('Time (ms)')
plt.ylabel('Gating probability')
ax2 = plt.gca().twinx()
ax2.plot(np.array(stimulation.time)[:2000], amp * waveform[:2000], 'k--', label='Stimulus')
ax2.legend(loc=4)
ax2.grid(False)
plt.ylabel('Stimulation amplitude (mA)')
plt.show()
    
#%% Plotting transmembrane currents    

plt.figure()
fig, axs = plt.subplots(3, 1, figsize=(5, 5), sharex=True, gridspec_kw={'hspace': 0.3})
plt.sca(axs[0])
# plot stimulus
plt.plot(np.array(stimulation.time)[:2000], amp * waveform[:2000], 'k--', label='Stimulus')
plt.title('Stimulus')
plt.sca(axs[1])
# plot membrane voltage
plt.plot(
    np.array(stimulation.time)[:2000],
    list(fiber.vm[center_node])[:2000],
    color='mediumturquoise',
    linewidth=2,
    label='$V_m$',
)
# plot im
plt.plot(
    np.array(stimulation.time)[:2000],
    list(fiber.im[center_node])[:2000],
    color='mediumturquoise',
    linewidth=2,
    label='$I_m$',
    ls='--',
)
plt.title('Center node')
plt.legend()
plt.sca(axs[2])
# plot end node
plt.plot(
    np.array(stimulation.time)[:2000], list(fiber.vm[end_node])[:2000], color='royalblue', linewidth=2, label='$V_m$'
)
plt.plot(
    np.array(stimulation.time)[:2000],
    list(fiber.im[end_node])[:2000],
    color='royalblue',
    linewidth=2,
    label='$I_m$',
    ls='--',
)
plt.title('End node')
plt.legend()
plt.xlim([0, 2])
axs[2].set_xlabel('Time (ms)')
plt.show()

#%% Animation
import os
os.environ["IMAGEIO_FFMPEG_EXE"] = "/opt/homebrew/bin/ffmpeg"  # Replace with the actual path


from moviepy.editor import VideoClip
from moviepy.video.io.bindings import mplfig_to_npimage

fps = 30
skip = 10  # do every 10th timestep
stop = 2 / time_step  # stop after 2 milliseconds

duration = stop / fps / skip  # milliseconds
ylim = (np.amin(list(fiber.vm[1:-1]))), np.amax(list(fiber.vm[1:-1]))

fig, ax = plt.subplots()


def make_frame(i):
    """Create frame of video.

    :param i: index of frame, given to function by moviepy
    :returns: figure as image
    """
    ind = int(i * skip * fps)
    ax.clear()
    ax.set_ylim(ylim)
    ax.plot([v[ind] for v in fiber.vm[1:-1]], lw=3)
    plt.title(f'Time: {stimulation.time[ind]:0.1f} ms')
    plt.ylabel('$V_m$')
    plt.xlabel('Node index')
    plt.tight_layout()
    return mplfig_to_npimage(fig)


animation = VideoClip(make_frame, duration=duration)
animation.write_videofile('ap.mp4', fps=fps)
plt.close()

#%% Display animation
os.system("open ap.mp4")

