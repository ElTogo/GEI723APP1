import matplotlib.pyplot as plt
from brian2 import *

start_scope()

eqs = """
dv/dt = (I - v) / tau : 1
I : 1
tau : second
"""


input_group = NeuronGroup(3, eqs, threshold='v>1', reset='v=0', method='euler', name='input')
output_group = NeuronGroup(4, eqs, threshold='v>1', reset='v=0', method='euler', name='output')

input_group.tau = 10*ms
output_group.tau = 10*ms

l1 = NeuronGroup(1, eqs, threshold='v>1', reset='v=0', method='euler')
l2 = NeuronGroup(2, eqs, threshold='v>1', reset='v=0', method='euler')

l1.tau = 10*ms
l2.tau = 8*ms

S_dir_to_inv = Synapses(input_group, l1, on_pre='v_post -= 0.6')
S_dir_to_inv.connect(i=2, j=0)

l1.I = 0.6


S_mov_to_l2 = Synapses(input_group, l2, on_pre='v_post += 0.5')
S_mov_to_l2.connect(i=1, j=0)

S_mov_to_l22 = Synapses(input_group, l2, on_pre='v_post += 0.5')
S_mov_to_l22.connect(i=1, j=1)

S_dir_to_l2 = Synapses(input_group, l2, on_pre='v_post += 0.5')
S_dir_to_l2.connect(i=2, j=1)

S_inv_to_l2 = Synapses(l1, l2, on_pre='v_post += 0.5')
S_inv_to_l2.connect(i=0, j=0)

S_l2_to_out_ex = Synapses(l2, output_group, on_pre='v_post += 0.5')
S_l2_to_out_ex.connect(i=[0,1], j=[2,3])

S_l2_to_out_in = Synapses(l2, output_group, on_pre='v_post -= 0.6')
S_l2_to_out_in.connect(i=[1,0], j=[2,3])


#Test patte excité
input_group.v = 0
l1.v = 0
l2.v = 0
output_group.v = 0

output_group.I = [0, 0, 1.2, 0]  # neurones en constant excitation
l1.I = [1.2]
l2.I = [0,0]
input_group.I = [0, 0, 0]      # entrée excitée

run(10*ms)
output_group.I = [0, 0, 1.2, 1.2]  # neurones en constant excitation



M_in_mr = StateMonitor(input_group, 'v', record=True)
M_l1_mr = StateMonitor(l1, 'v', record=True)
M_l2_mr = StateMonitor(l2, 'v', record=True)
M_out_mr = StateMonitor(output_group, 'v', record=True)

sp_11 = SpikeMonitor(input_group)
sp_12 = SpikeMonitor(l1)
sp_13 = SpikeMonitor(l2)
sp_14 = SpikeMonitor(output_group)

run(300*ms)

v_in_mr = M_in_mr.v
v_l1_mr = M_l1_mr.v
v_l2_mr = M_l2_mr.v
v_out_mr = M_out_mr.v
t1 = M_out_mr.t / ms

#Test patte repos
# input_group.v = 0
# output_group.v = 0
# output_group.I = [0, 2, 1.5, 1.5] # neurones en constant excitation
input_group.I = [0, 1.9, 0]

M_in_dr = StateMonitor(input_group, 'v', record=True)
M_l1_dr = StateMonitor(l1, 'v', record=True)
M_l2_dr = StateMonitor(l2, 'v', record=True)
M_out_dr = StateMonitor(output_group, 'v', record=True)

sp_21 = SpikeMonitor(input_group)
sp_22 = SpikeMonitor(l1)
sp_23 = SpikeMonitor(l2)
sp_24 = SpikeMonitor(output_group)

run(300*ms)

v_in_dr = M_in_dr.v
v_l1_dr = M_l1_dr.v
v_l2_dr = M_l2_dr.v
v_out_dr = M_out_dr.v
t2 = M_out_dr.t / ms

input_group.I = [0, 1.9, 1.9]

M_in_de = StateMonitor(input_group, 'v', record=True)
M_l1_de = StateMonitor(l1, 'v', record=True)
M_l2_de = StateMonitor(l2, 'v', record=True)
M_out_de = StateMonitor(output_group, 'v', record=True)

sp_31 = SpikeMonitor(input_group)
sp_32 = SpikeMonitor(l1)
sp_33 = SpikeMonitor(l2)
sp_34 = SpikeMonitor(output_group)

run(300*ms)

v_in_de = M_in_de.v
v_l1_de = M_l1_de.v
v_l2_de = M_l2_de.v
v_out_de = M_out_de.v
t3 = M_out_de.t / ms



figure(figsize=(12, 8))

subplot(3,4,1)
title("in mouvement non excitée")
plot(t1, v_in_mr[1], label='Mouvement (sortie 1)', color='tab:orange')
plot(t1, v_in_mr[2], label='Direction (sortie 2)', color='tab:green')
xlabel("Temps (ms)")
ylabel("Potentiel membranaire")
legend(loc='best')
grid(True)

subplot(3,4,2)
title("l1 mouvement non excitée")
plot(t1, v_l1_mr[0], label=' (sortie 0)', color='tab:brown')
xlabel("Temps (ms)")
ylabel("Potentiel membranaire")
legend(loc='best')
grid(True)

subplot(3,4,3)
title("l2 mouvement non excitée")
plot(t1, v_l2_mr[0], label=' (sortie 0)', color='tab:purple')
plot(t1, v_l2_mr[1], label=' (sortie 1)', color='tab:olive')
xlabel("Temps (ms)")
ylabel("Potentiel membranaire")
legend(loc='best')
grid(True)

subplot(3,4,4)
title("out mouvement non excitée")
plot(t1, v_out_mr[2], label='Extenseur (sortie 2)', color='tab:blue')
plot(t1, v_out_mr[3], label='Fléchisseur (sortie 3)', color='tab:red')
xlabel("Temps (ms)")
ylabel("Potentiel membranaire")
legend(loc='best')
grid(True)


subplot(3,4,5)
title("in direction non excitée")
plot(t1, v_in_dr[1], label='Mouvement (sortie 1)', color='tab:orange')
plot(t1, v_in_dr[2], label='Direction (sortie 2)', color='tab:green')
xlabel("Temps (ms)")
ylabel("Potentiel membranaire")
legend(loc='best')
grid(True)

subplot(3,4,6)
title("l1 direction non excitée")
plot(t1, v_l1_dr[0], label=' (sortie 0)', color='tab:brown')
xlabel("Temps (ms)")
ylabel("Potentiel membranaire")
legend(loc='best')
grid(True)

subplot(3,4,7)
title("l2 direction non excitée")
plot(t1, v_l2_dr[0], label=' (sortie 0)', color='tab:purple')
plot(t1, v_l2_dr[1], label=' (sortie 1)', color='tab:olive')
xlabel("Temps (ms)")
ylabel("Potentiel membranaire")
legend(loc='best')
grid(True)

subplot(3,4,8)
title("out mouvement non excitée")
plot(t1, v_out_dr[2], label='Extenseur (sortie 2)', color='tab:blue')
plot(t1, v_out_dr[3], label='Fléchisseur (sortie 3)', color='tab:red')
xlabel("Temps (ms)")
ylabel("Potentiel membranaire")
legend(loc='best')
grid(True)


subplot(3,4,9)
title("in direction excitée")
plot(t1, v_in_de[1], label='Mouvement (sortie 1)', color='tab:orange')
plot(t1, v_in_de[2], label='Direction (sortie 2)', color='tab:green')
xlabel("Temps (ms)")
ylabel("Potentiel membranaire")
legend(loc='best')
grid(True)

subplot(3,4,10)
title("l1 direction excitée")
plot(t1, v_l1_de[0], label='Extenseur (sortie 0)', color='tab:brown')
xlabel("Temps (ms)")
ylabel("Potentiel membranaire")
legend(loc='best')
grid(True)

subplot(3,4,11)
title("l2 direction excitée")
plot(t1, v_l2_de[1], label='Fléchisseur (sortie 1)', color='tab:olive')
plot(t1, v_l2_de[0], label='Extenseur (sortie 0)', color='tab:purple')
xlabel("Temps (ms)")
ylabel("Potentiel membranaire")
legend(loc='best')
grid(True)

subplot(3,4,12)
title("out mouvement excitée")
plot(t1, v_out_de[2], label='Extenseur (sortie 2)', color='tab:blue')
plot(t1, v_out_de[3], label='Fléchisseur (sortie 3)', color='tab:red')
xlabel("Temps (ms)")
ylabel("Potentiel membranaire")
legend(loc='best')
grid(True)

# subplot(3,4,5)
# title("direction non excité (repos)")
# plot(t2, v_out_dr[2], label='Extenseur (sortie 2)', color='tab:blue')
# plot(t2, v_out_dr[3], label='Fléchisseur (sortie 3)', color='tab:red')
# xlabel("Temps (ms)")
# ylabel("Potentiel membranaire")
# legend(loc='best')
# grid(True)
#
# subplot(3,4,6)
# title("direction excitée (repos)")
# plot(t3, v_out_de[2], label='Extenseur (sortie 2)', color='tab:blue')
# plot(t3, v_out_de[3], label='Fléchisseur (sortie 3)', color='tab:red')
# xlabel("Temps (ms)")
# ylabel("Potentiel membranaire")
# legend(loc='best')
# grid(True)

tight_layout()
show()

# figure(figsize=(12,8))
#
# subplot(3,1,1)
# title(" mouvement non excitée")
# plot(sp_11.t/ms, sp_11.i, '.k')
# plot(sp_12.t/ms, sp_12.i, '.k')
# plot(sp_13.t/ms, sp_13.i, '.k')
# plot(sp_14.t/ms, sp_14.i, '.k')
# xlabel("Temps (ms)")
# ylabel("Potentiel membranaire")
#
# subplot(3,1,2)
# title(" mouvement non excitée")
# plot(sp_21.t/ms, sp_21.i, '.k')
# plot(sp_22.t/ms, sp_22.i, '.k')
# plot(sp_23.t/ms, sp_23.i, '.k')
# plot(sp_24.t/ms, sp_24.i, '.k')
# xlabel("Temps (ms)")
# ylabel("Potentiel membranaire")
#
# subplot(3,1,3)
# title(" mouvement non excitée")
# plot(sp_31.t/ms, sp_31.i, '.k')
# plot(sp_32.t/ms, sp_32.i, '.k')
# plot(sp_33.t/ms, sp_33.i, '.k')
# plot(sp_34.t/ms, sp_34.i, '.k')
# xlabel("Temps (ms)")
# ylabel("Potentiel membranaire")

# tight_layout()
# show()

all_spikes = [
    sp_11,
    # sp_12, sp_13,
    sp_14,
    # sp_21, sp_22, sp_23, sp_24,
    # sp_31, sp_32, sp_33, sp_34
]

n_neurons = len(all_spikes)
plt.figure(figsize=(12, 8))

for idx, sp in enumerate(all_spikes):
    subplot(1, 2, idx+1)
    plot(sp.t/ms, sp.i, '.k')
    title(f"Neurone {idx+1}")
    xlabel("Temps (ms)")
    ylabel("Spike")
    axvline(300)
    axvline(600)
    xlim(0,900)
    grid(True)

tight_layout()
show()