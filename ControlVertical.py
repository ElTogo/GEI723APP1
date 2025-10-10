from brian2 import *

start_scope()

eqs = """
dv/dt = (I - v) / tau : 1
tau : second
I : 1
"""

input_group = NeuronGroup(3, eqs, threshold='v>1', reset='v=0', method='euler', name='input') #Input : repos -> sol, excité -> dans les aires
output_group = NeuronGroup(4, eqs, threshold='v>1', reset='v=0', method='euler', name='output') #0 : fléchiseur, #1 extenseur

# Initialisation de tau pour éviter la division par zéro
input_group.tau = 10*ms
output_group.tau = 10*ms


exc = Synapses(input_group, output_group, on_pre='I_post = 2')  # excitatrice
inh = Synapses(input_group, output_group, on_pre='I_post = 0')  # inhibitrice

exc.connect(i=0, j=0)  # entrée 0 excite l’extenseur
inh.connect(i=0, j=1)  # entrée 0 inhibe le fléchisseur

#Test patte excité
input_group.v = 0
output_group.v = 0
output_group.I = [0, 2, 0, 0]  # neurones en constant excitation
input_group.I = [2, 0, 0]      # entrée excitée

M_in1 = StateMonitor(input_group, 'v', record=True)
M_out1 = StateMonitor(output_group, 'v', record=True)
sp_11 = SpikeMonitor(input_group)
sp_12 = SpikeMonitor(output_group)
run(300*ms)

v_in_excited = M_in1.v
v_out_excited = M_out1.v
t1 = M_out1.t / ms

#Test patte repos
input_group.v = 0
output_group.v = 0
output_group.I = [0, 2, 0, 0] # neurones en constant excitation
input_group.I = [0, 0, 0]

M_in2 = StateMonitor(input_group, 'v', record=True)
M_out2 = StateMonitor(output_group, 'v', record=True)

run(300*ms)

v_in_idle = M_in2.v
v_out_idle = M_out2.v
t2 = M_out2.t / ms


figure(figsize=(12, 8))

subplot(2,1,1)
title("Patte excitée")
plot(t1, v_out_excited[0], label='Extenseur (sortie 0)', color='tab:blue')
plot(t1, v_out_excited[1], label='Fléchisseur (sortie 1)', color='tab:red')
ylabel("Potentiel membranaire")
legend(loc='best')
grid(True)

subplot(2,1,2)
title("Patte non excitée (repos)")
plot(t2, v_out_idle[0], label='Extenseur (sortie 0)', color='tab:blue')
plot(t2, v_out_idle[1], label='Fléchisseur (sortie 1)', color='tab:red')
xlabel("Temps (ms)")
ylabel("Potentiel membranaire")
legend(loc='best')
grid(True)

tight_layout()
show()

all_spikes = [
    sp_11,
    sp_12
]

n_neurons = len(all_spikes)
plt.figure(figsize=(12, 8))

for idx, sp in enumerate(all_spikes):
    plt.subplot(1, 2, idx+1)
    plt.plot(sp.t/ms, sp.i, '.k')
    plt.title(f"Neurone {idx+1}")
    plt.xlabel("Temps (ms)")
    plt.ylabel("Spike")
    plt.axvline(300)
    plt.xlim(0,600)
    plt.grid(True)

tight_layout()
show()
