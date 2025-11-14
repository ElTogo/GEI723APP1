from brian2 import *

# paramètres globaux et setup des neurones commun
N = 1000
taum = 10*ms
Ee = 0*mV
vt = -54*mV
vr = -60*mV
El = -74*mV
taue = 5*ms
F = 6*Hz # Changer la fréquence pour 10 et 6 Hz pour la partie I.2.
gmax = .01

eqs_neurons = '''dv/dt = (ge * (Ee-v) + El - v) / taum : volt
                 dge/dt = -ge / taue : 1'''
poisson_input = PoissonGroup(N, rates=F)
neurons = NeuronGroup(1, eqs_neurons, threshold='v>vt', reset='v = vr',
                      method='euler')

# aI, classique comme exemple de base fournit de brian2 (https://brian2.readthedocs.io/en/latest/examples/synapses.STDP.html)
taupre_aI = 20*ms
taupost_aI = 20*ms
dApre_aI = .01 * gmax
dApost_aI = -dApre_aI * taupre_aI / taupost_aI * 1.05 * gmax

eqs_aI = '''w : 1
            dApre/dt = -Apre / taupre_aI : 1 (event-driven)
            dApost/dt = -Apost / taupost_aI : 1 (event-driven)'''
on_pre_aI = '''ge += w
                Apre += dApre_aI
                w = clip(w + Apost, 0, gmax)'''
on_post_aI = '''Apost += dApost_aI
                w = clip(w + Apre, 0, gmax)'''

# aII, adaptation coneptuelle
# slow et fast permet de faire la courbe descendante rapide et remontante lente dans le post
tau_fast = 5*ms
tau_slow = 50*ms
dA_fast = 0.005 * gmax
dA_slow = 0.005 * gmax

eqs_aII = '''w : 1
             dA_slow/dt = -A_slow / tau_slow : 1 (event-driven)
             dA_fast/dt = -A_fast / tau_fast : 1 (event-driven)'''
on_pre_aII = '''ge += w
                A_slow += dA_slow
                w = clip(w + A_fast, 0, gmax)'''
on_post_aII = '''A_fast += dA_fast
                w = clip(w - A_slow, 0, gmax)'''

# bI, potentiation symétrique-
tau_bI = 10*ms
dA_bI = .01 * gmax

eqs_bI = '''w : 1
            dA/dt = -A / tau_bI : 1 (event-driven)'''
on_pre_bI = '''ge += w
                A += dA_bI
                w = clip(w + A, 0, gmax)'''
on_post_bI = '''A += dA_bI
                w = clip(w + A, 0, gmax)'''

# bII, Anti-Hebbian
tau_bII = 20*ms
dApre_LTD = -.01 * gmax
dApost_LTP = .01 * gmax

eqs_bII = '''w : 1
             dApre/dt = -Apre / tau_bII : 1 (event-driven)
             dApost/dt = -Apost / tau_bII : 1 (event-driven)'''
on_pre_bII = '''ge += w
                Apre += dApre_LTD
                w = clip(w + Apost, 0, gmax)'''
on_post_bII = '''Apost += dApost_LTP
                w = clip(w + Apre, 0, gmax)'''


# Changer eqs_x, on_pre_x et on_post_x pour changer de STDP
S = Synapses(poisson_input, neurons, eqs_aII, on_pre=on_pre_aII, on_post=on_post_aII)

S.connect()
S.w = 'rand() * gmax'
mon = StateMonitor(S, 'w', record=[0, 1])
s_mon = SpikeMonitor(poisson_input)

run(100*second, report='text')

subplot(311)
plot(S.w / gmax, '.k')
ylabel('Weight / gmax')
xlabel('Synapse index')
subplot(312)
hist(S.w / gmax, 20)
xlabel('Weight / gmax')
subplot(313)
plot(mon.t/second, mon.w.T/gmax)
xlabel('Time (s)')
ylabel('Weight / gmax')
tight_layout()
show()