import matplotlib.pyplot as plt
from brian2 import *

start_scope()

eqs = """
dv/dt = (I - v) / tau : 1
I : 1
tau : second
"""

# [0] -> forward, [1] -> backward, [2] -> left, [3] -> right
#Input group : where it as been hit
#Output group : where it want to go (also controled by user, altered by stimulus)
input_group = NeuronGroup(4, eqs, threshold='v>1', reset='v=0', method='euler', name='input')
output_group = NeuronGroup(4, eqs, threshold='v>1', reset='v=0', method='euler', name='output')

input_group.tau = 10*ms
output_group.tau = 10*ms

inib = Synapses(input_group, output_group, on_pre='v_post -= 1')
exci = Synapses(input_group, output_group, on_pre='v_post += 1.2')

inib.connect(i=[0,1,2,3], j=[0,1,2,3])
exci.connect(i=[0,1,2,3], j=[1,0,3,2])

spikes_i = SpikeMonitor(input_group)
spikes_o = SpikeMonitor(output_group)

state_i = StateMonitor(input_group, 'v', record=True)
state_o = StateMonitor(output_group, 'v', record=True)

input_group.I = [2,0,0,0]
output_group.I = [1.1,0,0,0]
run(100*ms)
input_group.I = [0,2,0,0]
output_group.I = [0,1.1,0,0]
run(100*ms)
input_group.I = [0,0,2,0]
output_group.I = [0,0,1.1,0]
run(100*ms)
input_group.I = [0,0,0,2]
output_group.I = [0,0,0,1.1]
run(100*ms)

v_i = state_i.v
v_o = state_o.v

ti = state_i.t/ms
to = state_o.t/ms

subplot(2,1,1)
title("Input")
plot(ti, v_i[0], label='Forward', color='tab:olive')
plot(ti, v_i[1], label='Backward', color='tab:pink')
plot(ti, v_i[2], label='Left', color='tab:blue')
plot(ti, v_i[3], label='Right', color='tab:orange')
xlabel("Temps (ms)")
ylabel("Potentiel membranaire")
legend(loc='best')
grid(True)

subplot(2,1,2)
title("Input")
plot(to, v_o[0], label='Forward', color='tab:olive')
plot(to, v_o[1], label='Backward', color='tab:pink')
plot(to, v_o[2], label='Left', color='tab:blue')
plot(to, v_o[3], label='Right', color='tab:orange')
xlabel("Temps (ms)")
ylabel("Potentiel membranaire")
legend(loc='best')
grid(True)

tight_layout()
show()

subplot(2,1,1)
plot(spikes_i.t/ms, spikes_i.i, '.k')
title(f"Input")
xlabel("Temps (ms)")
ylabel("Spike")
axvline(100)
axvline(200)
axvline(300)
xlim(0,400)
grid(True)

subplot(2,1,2)
plot(spikes_o.t/ms, spikes_o.i, '.k')
title("Output")
xlabel("Temps (ms)")
ylabel("Spike")
axvline(100)
axvline(200)
axvline(300)
xlim(0,400)
grid(True)

tight_layout()
show()