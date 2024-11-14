#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 10:03:46 2024

@author: gz57nm
"""

import numpy as np
import matplotlib.pyplot as plt

def conventional(frequency, pulse_width, interphase_interval, time_stop, time_step, pos_percent=1):
    period = 1000/ frequency  # ms
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
    gap_points = int(interphase_interval / time_step)  # gap points
    points_per_period = int(period / time_step)  # points in one cycle

    # Create time vector
    t = np.arange(0, time_stop, time_step)

    # Create positive phase with exponential decay (longer time, scaled by discharge_time_factor)
    extended_pulse_width = pulse_width / 2 * discharge_time_factor
    t_exp = np.arange(0, extended_pulse_width, time_step)
    positive_phase = np.exp(-t_exp / tau)
    positive_phase = (positive_phase - positive_phase[-1]) / (positive_phase[0] - positive_phase[-1])

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

    # Create burst pulse
    burst_duration = period_40Hz / 2  # ms (burst duration)
    burst_points = int(burst_duration / time_step)
    burst_pulse = np.zeros(burst_points)

    for i in range(0, burst_points, int(period_500Hz / time_step)):
        burst_pulse[i:i + len(biphasic_pulse)] = biphasic_pulse[:len(burst_pulse[i:i + len(biphasic_pulse)])]

    # Create waveform
    waveform = np.zeros_like(t)
    for i in range(0, len(t), points_per_period_40Hz):
        waveform[i:i + burst_points] = burst_pulse[:len(waveform[i:i + burst_points])]


    return t, waveform



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
    burst_pulse[last_biphasic_end:last_biphasic_end + len(passive_discharge)] = passive_discharge

    # Create waveform
    waveform = np.zeros_like(t)
    for i in range(0, len(t), points_per_period_40Hz):
        waveform[i:i + len(burst_pulse)] = burst_pulse[:len(waveform[i:i + len(burst_pulse)])]

    return t, waveform




