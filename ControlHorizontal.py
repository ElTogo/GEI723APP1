from brian2 import *

start_scope()

eqs = """
dv/dt = (I - v) / tau : 1
tau : second
I : 1
"""

input_group = NeuronGroup(3, eqs, threshold='v>1', reset='v=0', method='euler', name='input')
output_group = NeuronGroup(4, eqs, threshold='v>1', reset='v=0', method='euler', name='output')

# Initialisation de tau pour éviter la division par zéro
input_group.tau = 10*ms
output_group.tau = 10*ms

l1 = NeuronGroup(2, eqs, threshold='v>1', reset='v=0', method='euler')
l2 = NeuronGroup(2, eqs, threshold='v>1', reset='v=0', method='euler')

l1.tau = 10*ms
l2.tau = 10*ms

il1e = Synapses(input_group, l1, on_pre='v=0', on_post='v=0')
il1i = Synapses(input_group, l1, on_pre='v=0', on_post='v=0')
l1l2e = Synapses(l1, l2, on_pre='v=0', on_post='v=0')
l1l2i = Synapses(l1, l2, on_pre='v=0', on_post='v=0')
l2ee = Synapses(l2, output_group, on_pre='v=0', on_post='v=0')
l2ei = Synapses(l2, output_group, on_pre='v=0', on_post='v=0')

# exc.connect(i=0, j=0)  # entrée 0 excite l’extenseur
# inh.connect(i=0, j=1)  # entrée 0 inhibe le fléchisseur

il1e.connect(i = 1, j = 0)
il1e.connect(i = 1, j = 1)
il1e.connect(i = 2, j = 1)
il1i.connect(i = 2, j = 0)

l1l2i.connect(i = 0, j = 0)
l1l2e.connect(i = 1, j = 1)

l2ee.connect(i = 0, j = 0)
l2ee.connect(i = 1, j = 1)
l2ei.connect(i = 0, j = 1)
l2ei.connect(i = 1, j = 0)


#Test patte excité
input_group.v = 0
output_group.v = 0
output_group.I = [0, 2, 1.5, 1.5]  # neurones en constant excitation
input_group.I = [0, 0, 0]      # entrée excitée

M_in1 = StateMonitor(input_group, 'v', record=True)
M_out1 = StateMonitor(output_group, 'v', record=True)

run(300*ms)

v_in_excited = M_in1.v
v_out_excited = M_out1.v
t1 = M_out1.t / ms

#Test patte repos
input_group.v = 0
output_group.v = 0
output_group.I = [0, 2, 1.5, 1.5] # neurones en constant excitation
input_group.I = [0, 2, 0]

M_in2 = StateMonitor(input_group, 'v', record=True)
M_out2 = StateMonitor(output_group, 'v', record=True)

run(300*ms)

v_in_idle = M_in2.v
v_out_idle = M_out2.v
t2 = M_out2.t / ms


figure(figsize=(12, 8))

subplot(2,1,1)
title("Patte excitée")
plot(t1, v_out_excited[2], label='Extenseur (sortie 2)', color='tab:blue')
plot(t1, v_out_excited[3], label='Fléchisseur (sortie 3)', color='tab:red')
ylabel("Potentiel membranaire")
legend(loc='best')
grid(True)

subplot(2,1,2)
title("Patte non excitée (repos)")
plot(t2, v_out_idle[2], label='Extenseur (sortie 2)', color='tab:blue')
plot(t2, v_out_idle[3], label='Fléchisseur (sortie 3)', color='tab:red')
xlabel("Temps (ms)")
ylabel("Potentiel membranaire")
legend(loc='best')
grid(True)

tight_layout()
show()
