import numpy as np
import matplotlib.pyplot as plt
from pyfibers import build_fiber, FiberModel, ScaledStim
from functions.waveforms import conventional_passive # Example waveform functions

time_step=0.001
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
)


# Plot 2: Conventional Passive Charge Balance
fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
ax1.plot(t_cp, waveform)
ax1.set_title('Conventional Passive Charge Balance (Full)')
ax1.grid(True)

ax2.plot(t_cp, waveform)
ax2.set_title('Conventional Passive Charge Balance (Zoomed)')
ax2.set_xlim(24, 28)
ax2.grid(True)

fig2.suptitle('Conventional Passive Charge Balance')
plt.tight_layout()
plt.show()

# Number of fibers
n_fibers = 5

# Set up fiber model properties
diameters = np.linspace(8, 12, n_fibers)  # Varying diameters (micrometers)
temperature = 35  # Temperature in degrees Celsius

# Create fibers and store them
fibers = []
for i in range(n_fibers):
    fiber = build_fiber(
        fiber_model=FiberModel.MRG_INTERPOLATION,
        length=2000,
        diameter=diameters[i],  # Vary fiber diameters
        temperature=temperature
    )
    fibers.append(fiber)


# Create waveform and stimulus for each fiber
fiber_responses = []
for i, fiber in enumerate(fibers):

    # Create stimulation instance
    stimulation = ScaledStim(waveform=waveform, dt=time_step, tstop=time_stop)
    
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

    # Record fiber responses
    fiber.record_vm()  # save membrane voltage
    fiber.record_gating()  # save gating variables
    fiber.record_im()  # save membrane current

    # Run simulation for this fiber
    stimamp = 5  # Example stimulation amplitude (constant across fibers)
    ap, time = stimulation.run_sim(stimamp, fiber)

    # Store response for this fiber
    fiber_responses.append(fiber.get_vm())  # Collect membrane voltage for each fiber

# Aggregate fiber responses
bundle_response = np.mean(fiber_responses, axis=0)  # Average responses to simulate a bundle

# Plot the bundle response
plt.plot(bundle_response)
plt.title("Simulated Bundle Response")
plt.xlabel("Time (ms)")
plt.ylabel("Membrane Voltage (mV)")
plt.show()