#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 10:03:46 2024

@author: gz57nm
"""

import numpy as np


def conventional(frequency, pulse_width, interphase_interval, time_stop, time_step):
    period = 1000/ frequency  # ms
    pulse_points = int(pulse_width / time_step)  # number of points for the pulse width
    half_pulse_points = pulse_points // 2  # half of the pulse width
    gap_points = int(interphase_interval / time_step)  # gap points
    points_per_period = int(period / time_step)  # points in one cycle

    # Create time vector
    t = np.arange(0, time_stop, time_step)

    # Create biphasic pulse
    biphasic_pulse = np.concatenate([
        np.ones(half_pulse_points), 
        np.zeros(gap_points), 
        -np.ones(half_pulse_points)
    ])

    # Create waveform
    waveform = np.zeros_like(t)
    for i in range(0, len(t), points_per_period):
        waveform[i:i + len(biphasic_pulse)] = biphasic_pulse[:len(waveform[i:i + len(biphasic_pulse)])]


    return t, waveform

def conventional_passive(frequency, pulse_width, interphase_interval, time_stop, time_step, tau):
    period = 1000 / frequency  # ms
    gap_points = int(interphase_interval / time_step)  # gap points
    points_per_period = int(period / time_step)  # points in one cycle

    # Create time vector
    t = np.arange(0, time_stop, time_step)

    # Create positive phase with exponential decay
    t_exp = np.arange(0, pulse_width / 2, time_step)
    positive_phase = np.exp(-t_exp / tau)
    positive_phase = (positive_phase - positive_phase[-1]) / (positive_phase[0] - positive_phase[-1])

    # Create negative phase
    half_pulse_points = len(t_exp)
    negative_phase = -np.ones(half_pulse_points)

    # Create biphasic pulse
    biphasic_pulse = np.concatenate([
        positive_phase,
        np.zeros(gap_points),
        negative_phase
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
        np.ones(half_pulse_points),
        np.zeros(gap_points),
        -np.ones(half_pulse_points)
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
    burst_duration_samples = int(burst_duration * fs / 1000)
    
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
        envelope = np.exp(-np.abs(np.linspace(0, burst_duration, burst_duration_samples)) / (burst_tau * 1000))  # Mirrored envelope over 5 ms
        
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
    
    
    return t*1000, burstdr_waveform-0.5