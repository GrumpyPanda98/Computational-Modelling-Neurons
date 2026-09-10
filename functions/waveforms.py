#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 10:03:46 2024

@author: gz57nm
"""

import numpy as np




def conventional(frequency, pulse_width, interphase_interval, time_stop, time_step, pos_percent=1):
    period = 1000/ frequency  # ms
    pulse_width*=2
    pulse_points = int(pulse_width / time_step)  # number of points for the pulse width
    half_pulse_points = pulse_points // 2  # half of the pulse width
    gap_points = int(interphase_interval / time_step)  # gap points
    points_per_period = int(period / time_step)  # points in one cycle

    # Create time vector
    t = np.arange(0, time_stop, time_step)

    # Create biphasic pulse
    biphasic_pulse = np.concatenate([
        -np.ones(half_pulse_points),
        np.ones(half_pulse_points)*pos_percent, 
        np.zeros(gap_points) 
        
    ])

    # Create waveform
    waveform = np.zeros_like(t)
    for i in range(0, len(t), points_per_period):
        waveform[i:i + len(biphasic_pulse)] = biphasic_pulse[:len(waveform[i:i + len(biphasic_pulse)])]


    return t, waveform

def conventional_passive(frequency, pulse_width, interphase_interval, time_stop, time_step, tau, discharge_time_factor=2,pos_percent=1):
    period = 1000 / frequency  # ms
    pulse_width*=2
    gap_points = int(interphase_interval / time_step)  # gap points
    points_per_period = int(period / time_step)  # points in one cycle

    # Create time vector
    t = np.arange(0, time_stop, time_step)

    # Create positive phase with exponential decay (longer time, scaled by discharge_time_factor)
    extended_pulse_width = pulse_width / 2 * discharge_time_factor
    t_exp = np.arange(0, extended_pulse_width, time_step)
    positive_phase = np.exp(-t_exp / tau)
    positive_phase = (positive_phase - positive_phase[-1]) / (positive_phase[0] - positive_phase[-1])*0.5

    # Create negative phase (same duration as half of original pulse width)
    half_pulse_points = int(pulse_width / 2 / time_step)
    negative_phase = -np.ones(half_pulse_points)

    # Create biphasic pulse with negative first and positive last (longer discharge phase)
    biphasic_pulse = np.concatenate([
        negative_phase,
        np.zeros(gap_points),
        positive_phase * pos_percent
    ])

    # Create waveform
    waveform = np.zeros_like(t)
    for i in range(0, len(t), points_per_period):
        waveform[i:i + len(biphasic_pulse)] = biphasic_pulse[:len(waveform[i:i + len(biphasic_pulse)])]

    return t, waveform

def burst(frequency, burst_frequency, pulse_width, interphase_interval, time_stop, time_step):
    pulse_width*=2
    period_40Hz = 1000 / frequency  # ms (40 Hz)
    period_500Hz = 1000 / burst_frequency  # ms (500 Hz)
    pulse_points = int(pulse_width / time_step)
    half_pulse_points = pulse_points // 2
    gap_points = int(interphase_interval / time_step)
    points_per_period_40Hz = int(period_40Hz / time_step)
    
    # Create time vector
    t = np.arange(0, time_stop, time_step)
    
    # Create biphasic pulse
    biphasic_pulse = np.concatenate([
        -np.ones(half_pulse_points),
        np.zeros(gap_points),
        np.ones(half_pulse_points)
    ])
    
    # Calculate total length of one biphasic pulse
    single_pulse_length = len(biphasic_pulse)
    
    # Create burst pulse
    burst_duration = period_40Hz / 2  # ms (burst duration)
    burst_points = int(burst_duration / time_step)
    burst_pulse = np.zeros(burst_points)
    
    # Calculate number of pulses based on burst frequency
    num_pulses = int(burst_duration / period_500Hz)-1  # This should give us the correct number of pulses for 500Hz
    
    # Place pulses immediately after each other
    for i in range(num_pulses):
        start_idx = i * single_pulse_length
        end_idx = start_idx + single_pulse_length
        if end_idx <= burst_points:
            burst_pulse[start_idx:end_idx] = biphasic_pulse
    
    # Create waveform
    waveform = np.zeros_like(t)
    for i in range(0, len(t), points_per_period_40Hz):
        waveform[i:i + burst_points] = burst_pulse[:len(waveform[i:i + burst_points])]
    
    return t, waveform

def burst_abott_linear(
    frequency,
    burst_frequency,
    pulse_width,
    interphase_interval,  # not currently used, but kept for signature
    time_stop,
    time_step,
    tau,
    discharge_length
):
    """
    Generates a 'burst' pattern at a given frequency. Each burst consists of
    multiple pulses (with linearly increasing amplitudes) in the first half
    of the period, then nothing in the second half. Each pulse has a negative
    half and a small decay back to 0. The final pulse transitions into a
    longer 'final discharge' that also returns to 0, all using the same
    exponential steepness.

    Parameters
    ----------
    frequency : float
        Repetition frequency of the overall burst pattern (Hz).
    burst_frequency : float
        Frequency of pulses *within* a burst (Hz).
    pulse_width : float
        Duration (ms) of each biphasic pulse (negative + decaying part).
    interphase_interval : float
        Currently unused, placeholder for a possible future gap between phases.
    time_stop : float
        Total time (ms) of the waveform.
    time_step : float
        Step size (ms) for the time array.
    tau : float
        Time constant for the exponential decays (ms).
    discharge_length : float
        Duration (ms) of the final discharge after the last pulse in the burst.

    Returns
    -------
    t : ndarray
        Time array from 0 to time_stop (ms).
    waveform : ndarray
        The generated waveform (same length as t).
    """

    # ---------------------------------------------------------
    # 1) Define helper function for a normalized exponential
    #    going from 1 --> 0 over num_pts samples.
    # ---------------------------------------------------------
    def normalized_exponential(num_pts, tau):
        """
        Returns a 1->0 exponential of length `num_pts` using time constant `tau`.
        If num_pts=0, returns an empty array.
        """
        if num_pts <= 0:
            return np.array([])
        # Time array for the decay portion
        decay_t = np.arange(num_pts) * time_step

        # Raw exponential from e^(0) down to e^(-maxTime/tau)
        exp_raw = np.exp(-decay_t / tau)

        # Normalize so that at t=0 => 1.0  and  t=end => 0.0
        exp_norm = (exp_raw - exp_raw[-1]) / (exp_raw[0] - exp_raw[-1])
        return exp_norm

    # ---------------------------------------------------------
    # 2) Main timing and burst parameters
    # ---------------------------------------------------------
    period_ms = 1000.0 / frequency         # ms per full cycle
    points_per_period = int(period_ms / time_step)
    t = np.arange(0, time_stop, time_step)

    # Half of the period is used to place pulses (Abbott-style),
    # the other half is 'quiet.'
    burst_duration = period_ms / 2.0

    # Number of pulses that fit into the first half
    # (they're spaced by 1 / burst_frequency).
    # burst_duration and 1000/burst_frequency are in ms,
    # so we do integer division to see how many pulses fit.
    num_pulses = int(burst_duration / (1000.0 / burst_frequency))-1
    if num_pulses < 1:
        num_pulses = 1

    # Linear range of amplitudes from 0.2 to 1.0
    amps = np.linspace(0.2, 0.8, num_pulses)

    # ---------------------------------------------------------
    # 3) Split each biphasic pulse:
    #    - negative half = first half of pulse_width
    #    - short decay   = second half of pulse_width
    # ---------------------------------------------------------
    pulse_width*=2
    pulse_points = int(pulse_width / time_step)
    neg_pts = pulse_points // 2
    dec_pts = pulse_points - neg_pts

    # ---------------------------------------------------------
    # 4) Small "short decay" function, same steepness
    #    (same normalized exponential for all pulses).
    # ---------------------------------------------------------
    def small_decay(amp):
        exp_norm = normalized_exponential(dec_pts, 0.5)
        return amp * exp_norm  # Scale by 'amp' but keep same shape

    # ---------------------------------------------------------
    # 5) Longer final discharge after last pulse, also same shape
    # ---------------------------------------------------------
    discharge_pts = int(discharge_length / time_step)
    def final_discharge(amp):
        exp_norm = normalized_exponential(discharge_pts, tau)
        return amp * exp_norm

    # ---------------------------------------------------------
    # 6) Build a single burst:
    #    - For each pulse (except last): negative half + small decay
    #    - For last pulse: negative half + final discharge
    # ---------------------------------------------------------
    burst_segments = []
    for amp in amps[:-1]:
        neg_pulse = np.full(neg_pts, -1.0)
        dec = small_decay(amp)
        pulse_segment = np.concatenate((neg_pulse, dec))
        burst_segments.append(pulse_segment)

    # Last pulse has same negative half, but final discharge
    if len(amps) > 0:
        final_amp = amps[-1]
        neg_last = np.full(neg_pts, -1.0)
        discharge = final_discharge(final_amp)
        last_segment = np.concatenate((neg_last, discharge))
        burst_segments.append(last_segment)

    # Join all pulses in this burst
    burst = np.concatenate(burst_segments) if burst_segments else np.array([])

    # ---------------------------------------------------------
    # 7) Tile that burst pattern across total time at 'frequency' Hz
    # ---------------------------------------------------------
    waveform = np.zeros_like(t)
    idx = 0
    while idx < len(t):
        end_idx = idx + len(burst)
        # Place the burst segment into the waveform
        waveform[idx:end_idx] = burst[: len(waveform[idx:end_idx])]
        # Move idx by one full period, so each burst repeats
        idx += points_per_period

    return t, waveform




# # Generate the waveform with linearly increasing amplitude
# t_ab, burstab_wave = burst_abott_linear(
#     frequency=40,          # Carrier frequency of the waveform
#     burst_frequency=500,   # Frequency of the bursts
#     pulse_width=1,      # Width of each pulse
#     interphase_interval=0, # Interval between pulses
#     time_stop=100,         # Total time for the waveform
#     time_step=0.0001,
#     tau=4,              # Time constant for decay
#     discharge_length=800
# )

# # Plot Burst Abott with linearly increasing amplitude
# fig5, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
# ax1.plot(t_ab, burstab_wave)
# ax1.set_title('Burst "Linearly Increasing Amplitude" (Full)')
# ax1.set_xlim(0, 100)
# ax1.grid(True)

# ax2.plot(t_ab, burstab_wave)
# ax2.set_title('Burst "Linearly Increasing Amplitude" (Zoomed)')
# ax2.set_xlim(0, 10)
# ax2.grid(True)

# fig5.suptitle('Burst "Linearly Increasing Amplitude" Waveform')
# plt.tight_layout()
# plt.show()



def burst_passive(burst_frequency, carrier_frequency, time_stop, time_step, burst_duration, burst_tau, discharge_tau):
    
    # Convert time_step and time_stop from milliseconds to seconds
    time_step = time_step / 1000
    time_stop = time_stop / 1000
    
    # Sampling frequency
    fs = 1 / time_step  # Samples per second (e.g., 10,000 Hz for time_step = 0.1 ms)
    
    # Time vector
    t = np.linspace(0, time_stop, int(fs * time_stop), endpoint=False)
    
    # Create alternating DC segments based on your DC values
    dc_values = [-0.61, 0.26, -0.65, 0.34, -0.69, 0.36, -0.74, 0.42, -0.8, 0.28]
    dc_segments = np.concatenate([np.repeat(dc, 1000 * fs / 1000) for dc in dc_values])
    
    # Handle last DC segment of 10 ms
    last_dc_segment = np.repeat(0.28, 10 * fs / 1000)
    
    # Create the exponential fall segment
    exp_length = 13000 / 1000  # 13 seconds
    exp_t = np.arange(0, exp_length, 1/fs)
    exp_fall = 0.65 * np.exp(-4.0 * exp_t)
    
    # Final zero DC segment
    final_dc_segment = np.zeros(int(2990 * fs / 1000))
    
    # Combine all segments into the final waveform
    waveform = np.concatenate([dc_segments, last_dc_segment, exp_fall, final_dc_segment])
    
    # Adjust the length to match time_stop
    waveform = waveform[:len(t)]
    
    return t * 1000, waveform  # Return time in milliseconds and waveform


def burst_abott(frequency, burst_frequency, pulse_width, interphase_interval, time_stop, time_step, tau, discharge_length):
    period_40Hz = 1000 / frequency  # ms (40 Hz)
    period_500Hz = 1000 / burst_frequency  # ms (500 Hz)
    pulse_points = int(pulse_width / time_step)
    half_pulse_points = pulse_points // 2
    gap_points = int(interphase_interval / time_step)
    points_per_period_40Hz = int(period_40Hz / time_step)

    # Create time vector
    t = np.arange(0, time_stop, time_step)

    # Create biphasic pulse (switching positive and negative phases)
    biphasic_pulse = np.concatenate([
        -np.ones(half_pulse_points),  # Negative phase first
        np.zeros(gap_points),         # Gap
        np.ones(half_pulse_points)    # Positive phase last
    ])

    # Create passive discharge phase
    t_exp = np.arange(0, discharge_length, time_step)
    passive_discharge = np.exp(-t_exp / tau)  # Exponential decay for passive discharge
    passive_discharge = (passive_discharge - passive_discharge[-1]) / (passive_discharge[0] - passive_discharge[-1])  # Normalize

    # Create burst pulse
    burst_duration = period_40Hz / 2  # ms (burst duration)
    burst_points = int(burst_duration / time_step)
    burst_pulse = np.zeros(burst_points + len(passive_discharge))  # Include space for passive discharge

    # Add biphasic pulses
    last_biphasic_end = 0  # To track the end of the last biphasic pulse
    for i in range(0, burst_points, int(period_500Hz / time_step)):
        burst_pulse[i:i + len(biphasic_pulse)] = biphasic_pulse[:len(burst_pulse[i:i + len(biphasic_pulse)])]
        last_biphasic_end = i + len(biphasic_pulse)  # Update last biphasic pulse end point

    # Add passive discharge directly after the last biphasic pulse
    slice_end = min(last_biphasic_end + len(passive_discharge), len(burst_pulse))
    discharge_length = slice_end - last_biphasic_end  # Ensure lengths match
    burst_pulse[last_biphasic_end:slice_end] = passive_discharge[:discharge_length]

    # Create waveform
    waveform = np.zeros_like(t)
    for i in range(0, len(t), points_per_period_40Hz):
        waveform[i:i + len(burst_pulse)] = burst_pulse[:len(waveform[i:i + len(burst_pulse)])]

    return t, waveform


