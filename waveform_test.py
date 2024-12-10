#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 10:23:41 2024

@author: gz57nm
"""
import matplotlib.pyplot as plt

from functions.waveforms import conventional, conventional_passive, burst, burst_passive, burst_abott


#%% Create cSCS waveform
t_c, conv_wave = conventional(
    frequency=40,          # Frequency of the waveform
    pulse_width=0.2,      # Width of each pulse
    interphase_interval=0.1, # Interval between pulses
    time_stop=100,         # Total time for the waveform
    time_step= 0.0001
)

# Plot 1: Conventional Biphasic Waveform
fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
ax1.plot(t_c, conv_wave)
ax1.set_title('Conventional Biphasic Waveform (Full)')
ax1.set_xlim(0, 100)
ax1.grid(True)

ax2.plot(t_c, conv_wave)
ax2.set_title('Conventional Biphasic Waveform (Zoomed)')
ax2.set_xlim(24, 28)
ax2.grid(True)

fig1.suptitle('Conventional Biphasic Waveform')
plt.tight_layout()
plt.show()

#%% Create cSCS with passive charge balance waveform
t_cp, convpas_wave = conventional_passive(
    frequency=40,          # Frequency of the waveform
    pulse_width=0.2,      # Width of each pulse
    interphase_interval=0.05, # Interval between pulses
    time_stop=100,          # Total time for the waveform
    time_step= 0.0001,
    tau=0.5,              # Time constant for decay
    discharge_time_factor=80,
)


# Plot 2: Conventional Passive Charge Balance
fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
ax1.plot(t_cp, convpas_wave)
ax1.set_title('Conventional Passive Charge Balance (Full)')
ax1.set_xlim(0, 100)
ax1.grid(True)

ax2.plot(t_cp, convpas_wave)
ax2.set_title('Conventional Passive Charge Balance (Zoomed)')
ax2.set_xlim(24, 28)
ax2.grid(True)

fig2.suptitle('Conventional Passive Charge Balance')
plt.tight_layout()
plt.show()


#%% Create FAST waveform
t_f, fast_wave = conventional(
    frequency=90,          # Frequency of the waveform
    pulse_width=0.25,      # Width of each pulse
    interphase_interval=0.001, # Interval between pulses
    time_stop=100,         # Total time for the waveform
    time_step= 0.0001
)

# Plot 3: Fast Biphasic Waveform
fig3, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
ax1.plot(t_f, fast_wave)
ax1.set_title('Fast Biphasic Waveform (Full)')
ax1.set_xlim(0, 100)
ax1.grid(True)

ax2.plot(t_f, fast_wave)
ax2.set_title('Fast Biphasic Waveform (Zoomed)')
ax2.set_xlim(10.5, 12.5)
ax2.grid(True)

fig3.suptitle('Fast Biphasic Waveform')
plt.tight_layout()
plt.show()

#%% Create FAST passive charge balance waveform
t_fp, fastpas_wave = conventional_passive(
    frequency=90,          # Frequency of the waveform
    pulse_width=0.25,      # Width of each pulse
    interphase_interval=0.001, # Interval between pulses
    time_stop=100,          # Total time for the waveform
    time_step= 0.0001,
    tau=0.3,
    discharge_time_factor=80,
)


# Plot 4: Fast Passive Charge Balance
fig4, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
ax1.plot(t_fp, fastpas_wave)
ax1.set_title('Fast Passive Charge Balance (Full)')
ax1.set_xlim(0, 100)
ax1.grid(True)

ax2.plot(t_fp, fastpas_wave)
ax2.set_title('Fast Passive Charge Balance (Zoomed)')
ax2.set_xlim(10.5, 12.5)
ax2.grid(True)

fig4.suptitle('Fast Passive Charge Balance')
plt.tight_layout()
plt.show()




#%% Create a Burst waveform
t_b, burst_wave = burst(
    frequency=40,          # Carrier frequency of the waveform
    burst_frequency=500,   # Frequency of the bursts
    pulse_width=0.1,      # Width of each pulse
    interphase_interval=0.1, # Interval between pulses
    time_stop=100,         # Total time for the waveform'
    time_step= 0.0001
)

# Plot 5: Burst "Biphasic Waveform"
fig5, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
ax1.plot(t_b, burst_wave)
ax1.set_title('Burst "Biphasic Waveform" (Full)')
ax1.set_xlim(0, 100)
ax1.grid(True)

ax2.plot(t_b, burst_wave)
ax2.set_title('Burst "Biphasic Waveform" (Zoomed)')
ax2.set_xlim(25, 37)
ax2.grid(True)

fig5.suptitle('Burst "Biphasic Waveform"')
plt.tight_layout()
plt.show()

#%% Create a Burst Abott waveform
t_ab, burstab_wave = burst_abott(
    frequency=40,          # Carrier frequency of the waveform
    burst_frequency=500,   # Frequency of the bursts
    pulse_width=0.1,      # Width of each pulse
    interphase_interval=0.1, # Interval between pulses
    time_stop=100,         # Total time for the waveform'
    time_step= 0.0001,
    tau=0.8,              # Time constant for decay
    discharge_length=800
)

# Plot Burst Abott
fig5, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
ax1.plot(t_ab, burstab_wave)
ax1.set_title('Burst "Biphasic Waveform" (Full)')
ax1.set_xlim(0, 100)
ax1.grid(True)

ax2.plot(t_ab, burstab_wave)
ax2.set_title('Burst "Biphasic Waveform" (Zoomed)')
ax2.set_xlim(0, 20)
ax2.grid(True)

fig5.suptitle('Burst "Biphasic Waveform"')
plt.tight_layout()
plt.show()


#%% Create a BurstDR waveform
t_bp, burstpas_wave = burst_passive(
    burst_frequency=500,         # Frequency of the burst
    carrier_frequency=45,        # Frequency of the carrier
    burst_duration=9,    # Duration of each burst
    time_stop=100,            # Total duration of the waveform
    time_step= 0.0001,
    burst_tau= -0.008,
    discharge_tau = 0.005
)


# Plot 6: Burst Passive Charge Balance
fig6, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
ax1.plot(t_bp, burstpas_wave)
ax1.set_title('Burst Passive Charge Balance (Full)')
ax1.grid(True)

ax2.plot(t_bp, burstpas_wave)
ax2.set_title('Burst Passive Charge Balance (Zoomed)')
ax2.set_xlim(18, 40)
ax2.grid(True)

fig6.suptitle('Burst Passive Charge Balance')
plt.tight_layout()
plt.show()


#%% 
