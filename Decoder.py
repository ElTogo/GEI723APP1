from brian2 import *

# Define the firing patterns for each input neuron
patterns = {
    0: [0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0],
    1: [0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1],
    2: [1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1],
    3: [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    4: [1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0],
    5: [1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0],
    6: [0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0],
    7: [0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1],
    8: [1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0],
    9: [1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
    10: [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1],
    11: [1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1],
    12: [0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1],
    13: [1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0]
}

# Network parameters
n_input = 14
n_output = 12

# Neuron model (Leaky Integrate-and-Fire)
tau_m = 10 * ms  # Membrane time constant
v_rest = -65 * mV  # Resting potential
v_thresh = -50 * mV  # Spike threshold
v_reset = -65 * mV  # Reset potential
refrac = 2 * ms  # Refractory period

# Output neuron equations
eqs_output = '''
dv/dt = (v_rest - v) / tau_m : volt (unless refractory)
'''

# Create output neuron group
output_neurons = NeuronGroup(n_output, eqs_output,
                             threshold='v > v_thresh',
                             reset='v = v_reset',
                             refractory=refrac,
                             method='exact')
output_neurons.v = v_rest

# Generate spike times for input neurons (each input fires at specific times)
spike_indices = []
spike_times = []
time_step = 50 * ms  # Time between each input test

for input_idx in range(n_input):
    spike_indices.append(input_idx)
    spike_times.append(input_idx * time_step + 5 * ms)

# Create spike generator for inputs
input_spikes = SpikeGeneratorGroup(n_input, spike_indices, spike_times * second)

# Create synaptic connections based on patterns
i_indices = []  # Source (input) neuron indices
j_indices = []  # Target (output) neuron indices

for input_idx in range(n_input):
    pattern = patterns[input_idx]
    for output_idx in range(n_output):
        if pattern[output_idx] == 1:
            i_indices.append(input_idx)
            j_indices.append(output_idx)

# Create synapses with strong weights
synapses = Synapses(input_spikes, output_neurons,
                    model='w : volt',
                    on_pre='v_post += w')
synapses.connect(i=i_indices, j=j_indices)
synapses.w = 20 * mV  # Strong weight to ensure firing

# Monitors
input_monitor = SpikeMonitor(input_spikes)
output_monitor = SpikeMonitor(output_neurons)

# Run simulation
print("Spiking Neural Network Decoder")
print("=" * 50)

simulation_time = n_input * time_step + 20 * ms
run(simulation_time)

# Analyze results for each input
print("\nResults:")
for test_input in range(n_input):
    # Define time window for this input
    t_start = test_input * time_step
    t_end = (test_input + 1) * time_step

    # Find output spikes in this window
    mask = (output_monitor.t >= t_start) & (output_monitor.t < t_end)
    fired_outputs = set(output_monitor.i[mask])

    # Create binary representation
    output_pattern = [1 if i in fired_outputs else 0 for i in range(n_output)]

    # Display results
    expected = patterns[test_input]
    pattern_str = ''.join(map(str, output_pattern))
    expected_str = ''.join(map(str, expected))
    match = "✓" if output_pattern == expected else "✗"

    print(f"Input {test_input:2d} -> Output: {pattern_str} | Expected: {expected_str} {match}")

print("=" * 50)

# Visualize the full simulation
figure(figsize=(14, 8))

subplot(3, 1, 1)
plot(input_monitor.t / ms, input_monitor.i, '.b', markersize=12)
xlabel('Time (ms)')
ylabel('Input Neuron')
title('Input Neuron Spikes')
ylim(-0.5, n_input - 0.5)
yticks(range(n_input))
grid(True, alpha=0.3)

subplot(3, 1, 2)
plot(output_monitor.t / ms, output_monitor.i, '.r', markersize=8)
xlabel('Time (ms)')
ylabel('Output Neuron')
title('Output Neuron Spikes')
ylim(-0.5, n_output - 0.5)
yticks(range(n_output))
grid(True, alpha=0.3)

subplot(3, 1, 3)
# Show a zoomed view of first input (neuron 0)
mask_input = (input_monitor.t >= 0 * ms) & (input_monitor.t < 50 * ms)
mask_output = (output_monitor.t >= 0 * ms) & (output_monitor.t < 50 * ms)
plot(input_monitor.t[mask_input] / ms, input_monitor.i[mask_input], '.b',
     markersize=15, label='Input')
plot(output_monitor.t[mask_output] / ms, output_monitor.i[mask_output], '.r',
     markersize=12, label='Output')
xlabel('Time (ms)')
ylabel('Neuron Index')
title('Detailed View: Input 0 → Expected Output: 010110110010')
legend()
grid(True, alpha=0.3)
xlim(0, 50)

tight_layout()
show()

print("\nSimulation complete!")