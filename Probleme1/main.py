from brian2 import *
import matplotlib.pyplot as plt


start_scope()

G1 = NeuronGroup(10, 'dv/dt = -v / (10*ms) : 1',
                 threshold='v > 1', reset='v=0.', method='exact')
G1.v = 1.2
G2 = NeuronGroup(10, 'dv/dt = -v / (10*ms) : 1',
                 threshold='v > 1', reset='v=0', method='exact')

syn = Synapses(G1, G2, 'dw/dt = -w / (50*ms): 1 (event-driven)', on_pre='v += w')

syn.connect('i == j', p=0.75)

# Set the delays
syn.delay = '1*ms + i*ms + 0.25*ms * randn()'
# Set the initial values of the synaptic variable
syn.w = 1

mon = StateMonitor(G2, 'v', record=True)
run(20*ms)
plt.plot(mon.t/ms, mon.v.T)
plt.xlabel('Time (ms)')
plt.ylabel('v')
plt.show()


start_scope()

# param
tau = 10*ms
Vt = -50*mV
Vr = -65*mV
El = -65*mV
I_ext = 1.8 * namp

# simple LIF eq
eqs = '''
dv/dt = (El - v + I_ext)/tau : volt
'''

N = 50  # neurones par population

# Deux populations (antagonistes / phase opposée)
A = NeuronGroup(N, eqs, threshold='v>Vt', reset='v=Vr', method='euler', name='popA')
B = NeuronGroup(N, eqs, threshold='v>Vt', reset='v=Vr', method='euler', name='popB')
A.v = Vr
B.v = Vr

# Couplages inhibiteurs entre populations pour produire oscillations de phase opposée
S_ab = Synapses(A, B, on_pre='v_post -= 1.5*mV')
S_ba = Synapses(B, A, on_pre='v_post -= 1.5*mV')
S_ab.connect(p=0.2)
S_ba.connect(p=0.2)

# Record spikes
sa = SpikeMonitor(A)
sb = SpikeMonitor(B)
ra = PopulationRateMonitor(A)
rb = PopulationRateMonitor(B)

run(1*second)

# Convert rate to motor command (simple smoothing)
from scipy.signal import lfilter
import numpy as np

t = ra.t/ms
rateA = ra.smooth_rate(window='flat', width=10*ms)/Hz  # Brian2 helper
rateB = rb.smooth_rate(window='flat', width=10*ms)/Hz

# map (rateA - rateB) -> angle [-30,30] deg
angle = (rateA - rateB)
angle = (angle - angle.min()) / (angle.max() - angle.min() + 1e-9)  # normalize 0..1
angle = (angle*60 - 30)  # degrees

# Angle series prêt à être envoyé vers un contrôleur PWM (ex via serial/RPi)
print("Angle sample:", angle[:10])