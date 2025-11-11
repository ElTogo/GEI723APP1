from brian2 import *
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------
# PARAMÈTRES GÉNÉRAUX
# -------------------------------------------------------
start_scope()
prefs.codegen.target = 'numpy'
defaultclock.dt = 1 * ms
Tsim = 2400 * ms

tau = 20 * ms
v_th = 1.0
v_reset = 0.0
refr = 5 * ms

I_active = 0.92
I_inactive = 0.20

w_inh = -1.1
w_self = 0.05
w_tick = 0.45  # Increased from 0.20 to ensure transitions
w_tr = 1.70

Tmove = 150 * ms
tau_cmd = 500 * ms
A_cmd = 1.0
theta_cmd = 0.4

n_states = 14

# -------------------------------------------------------
# DÉFINITION DES NEURONES D'ÉTAT
# -------------------------------------------------------
eqs_states = '''
dv/dt = (-v + I_base)/tau : 1 (unless refractory)
I_base : 1
g_fwd : 1
g_bwd : 1
g_left : 1
g_right : 1
'''

S = NeuronGroup(n_states, eqs_states,
                threshold='v>v_th',
                reset='v=v_reset',
                refractory=refr,
                method='euler')

S.v = 0
S.I_base = I_inactive
S.I_base[0] = I_active
S.g_fwd = 0
S.g_bwd = 0
S.g_left = 0
S.g_right = 0

# -------------------------------------------------------
# SYNAPSES COMPÉTITIVES ET AUTOEXCITATION
# -------------------------------------------------------
WTA = Synapses(S, S, on_pre='v_post += w_inh', namespace={'w_inh': w_inh})
WTA.connect(condition='i != j')

SelfE = Synapses(S, S, on_pre='v_post += w_self', namespace={'w_self': w_self})
SelfE.connect(i=np.arange(n_states), j=np.arange(n_states))

# -------------------------------------------------------
# CPG LAYER - CENTRAL PATTERN GENERATORS
# -------------------------------------------------------
tau_cpg = 10 * ms
I_cpg = 1.5
w_cpg = 0.30  # Weight from CPG to state neuron
cpg_period = 80 * ms  # Desired oscillation period

eqs_cpg = '''
dv/dt = (-v + enabled * I_cpg)/tau_cpg : 1 (unless refractory)
enabled : 1
'''

CPG = NeuronGroup(n_states, eqs_cpg,
                  threshold='v>v_th',
                  reset='v=v_reset',
                  refractory=5 * ms,
                  method='euler',
                  namespace={'v_th': v_th, 'v_reset': v_reset,
                             'I_cpg': I_cpg, 'tau_cpg': tau_cpg})

CPG.v = 0
CPG.enabled = 0
CPG.enabled[0] = 1  # Start with CPG 0 enabled

# Synapse from CPG to corresponding state neuron
CPG_to_State = Synapses(CPG, S, on_pre='v_post += w_cpg',
                        namespace={'w_cpg': w_cpg})
CPG_to_State.connect(j='i')  # CPG[i] connects to S[i]

print("CPG layer created: 14 oscillators")
print(f"  CPG period: ~{cpg_period / ms:.0f}ms")
print(f"  CPG->State weight: {w_cpg}")
print()

# -------------------------------------------------------
# CONNEXIONS DIRECTIONNELLES (FIXED)
# -------------------------------------------------------
forward_edges = [(0, 1), (1, 2), (2, 3), (3, 13), (13, 4), (4, 5), (5, 6), (6, 0)]
backward_edges = [(0, 6), (6, 5), (5, 4), (4, 13), (13, 3), (3, 2), (2, 1), (1, 0)]
right_edges = [(0, 7), (7, 8), (8, 9), (9, 13), (13, 10), (10, 11), (11, 12), (12, 0)]
left_edges = [(0, 12), (12, 11), (11, 10), (10, 13), (13, 9), (9, 8), (8, 7), (7, 0)]

# Create separate synapse groups for each direction
# Brian2 needs explicit variable names, not f-string interpolation

Syn_fwd = Synapses(S, S,
                   on_pre='''
                   v_post += w_tr * int(g_fwd_pre > theta_cmd)
                   ''',
                   namespace={'w_tr': w_tr, 'theta_cmd': theta_cmd})
if forward_edges:
    pre, post = zip(*forward_edges)
    Syn_fwd.connect(i=pre, j=post)

Syn_bwd = Synapses(S, S,
                   on_pre='''
                   v_post += w_tr * int(g_bwd_pre > theta_cmd)
                   ''',
                   namespace={'w_tr': w_tr, 'theta_cmd': theta_cmd})
if backward_edges:
    pre, post = zip(*backward_edges)
    Syn_bwd.connect(i=pre, j=post)

Syn_right = Synapses(S, S,
                     on_pre='''
                     v_post += w_tr * int(g_right_pre > theta_cmd)
                     ''',
                     namespace={'w_tr': w_tr, 'theta_cmd': theta_cmd})
if right_edges:
    pre, post = zip(*right_edges)
    Syn_right.connect(i=pre, j=post)

Syn_left = Synapses(S, S,
                    on_pre='''
                    v_post += w_tr * int(g_left_pre > theta_cmd)
                    ''',
                    namespace={'w_tr': w_tr, 'theta_cmd': theta_cmd})
if left_edges:
    pre, post = zip(*left_edges)
    Syn_left.connect(i=pre, j=post)

print("Synapse connections:")
print(f"  forward: {len(Syn_fwd.i)} connections")
print(f"  backward: {len(Syn_bwd.i)} connections")
print(f"  right: {len(Syn_right.i)} connections")
print(f"  left: {len(Syn_left.i)} connections")
print()

# -------------------------------------------------------
# TIMER & TICK SYNAPSES
# -------------------------------------------------------
eqs_timer = '''
x : second
armed : 1
just_ticked : 1
'''

AT = NeuronGroup(1, eqs_timer,
                 threshold='(armed>0.5) and (x<=0*ms)',
                 reset='armed=0; just_ticked=1',
                 refractory=1 * ms,
                 method='euler')

Tick = Synapses(AT, S, on_pre='v_post += w_tick', namespace={'w_tick': w_tick})
Tick.connect(True)

# Simple synapse that restarts timer when any state spikes
StartTimer = Synapses(S, AT,
                      on_pre='''
                      x_post = just_ticked_post * Tmove + (1 - just_ticked_post) * x_post
                      armed_post = just_ticked_post + (1 - just_ticked_post) * armed_post
                      just_ticked_post = 0
                      ''',
                      namespace={'Tmove': Tmove})
StartTimer.connect(True)


@network_operation(dt=1 * ms)
def timer_update(t):
    if AT.armed[0] > 0.5:
        AT.x[0] = AT.x[0] - defaultclock.dt


# -------------------------------------------------------
# COMMANDES PLANIFIÉES (FIXED TIMING)
# -------------------------------------------------------
cmd_schedule = [
    ('fwd', 1.0),
    ('fwd', 100.0),
    ('fwd', 200.0),
    ('right', 650.0),
    ('right', 750.0),
    ('right', 850.0),
    ('bwd', 1200.0),
    ('bwd', 1300.0),
    ('bwd', 1400.0),
    ('left', 1700.0),
    ('left', 1800.0),
    ('left', 1900.0)
]

# Track which commands have been executed
cmd_executed = [False] * len(cmd_schedule)


@network_operation(dt=1 * ms)
def update_commands(t):
    t_curr = t / ms
    for idx, (code, t_ms) in enumerate(cmd_schedule):
        # Execute command once when time is reached
        if not cmd_executed[idx] and t_curr >= t_ms and t_curr < t_ms + 1:
            cmd_executed[idx] = True
            if code == 'fwd':
                S.g_fwd = A_cmd
            elif code == 'bwd':
                S.g_bwd = A_cmd
            elif code == 'left':
                S.g_left = A_cmd
            elif code == 'right':
                S.g_right = A_cmd
            print(f"  Command executed: {code} at t={t_curr:.1f}ms")


@network_operation(dt=1 * ms)
def decay_commands(t):
    decay = float((1 * ms) / tau_cmd)
    S.g_fwd[:] *= (1 - decay)
    S.g_bwd[:] *= (1 - decay)
    S.g_left[:] *= (1 - decay)
    S.g_right[:] *= (1 - decay)

    # Clip values
    S.g_fwd[:] = np.clip(S.g_fwd[:], 0, 1.5)
    S.g_bwd[:] = np.clip(S.g_bwd[:], 0, 1.5)
    S.g_left[:] = np.clip(S.g_left[:], 0, 1.5)
    S.g_right[:] = np.clip(S.g_right[:], 0, 1.5)


# Track the currently active state
current_active_state = [0]  # Start with state 0
last_tick_time = [-1000.0]  # Initialize to past time


@network_operation(dt=1 * ms)
def manage_active_state(t):
    """Transfer I_active to the state with highest voltage after a tick."""
    t_curr = t / ms

    # Check if a tick just occurred (within last 2ms)
    tick_mask = (Mt.t / ms >= t_curr - 2) & (Mt.t / ms <= t_curr)
    if np.any(tick_mask) and t_curr > last_tick_time[0] + 100:  # At least 100ms between transitions
        last_tick_time[0] = t_curr

        # Find the state with highest voltage (excluding current active state)
        voltages = np.array(S.v[:])
        voltages[current_active_state[0]] = -999  # Exclude current state

        next_state = np.argmax(voltages)
        max_voltage = voltages[next_state]

        # Only transition if the next state has significant voltage
        if max_voltage > 0.5 and next_state != current_active_state[0]:
            # Transfer activity
            S.I_base[current_active_state[0]] = I_inactive
            S.I_base[next_state] = I_active

            # Transfer CPG activity
            CPG.enabled[current_active_state[0]] = 0
            CPG.enabled[next_state] = 1
            CPG.v[next_state] = 0.5  # Give it a head start

            print(f"  ✓ Transition: {current_active_state[0]} → {next_state} at t={t_curr:.0f}ms (v={max_voltage:.2f})")
            current_active_state[0] = next_state


@network_operation(dt=200 * ms)
def debug_print(t):
    print(f"t={t / ms:.0f}ms | Active={current_active_state[0]} | "
          f"g_fwd={S.g_fwd[0]:.3f} g_right={S.g_right[0]:.3f} "
          f"g_bwd={S.g_bwd[0]:.3f} g_left={S.g_left[0]:.3f}")


# -------------------------------------------------------
# MONITEURS
# -------------------------------------------------------
Ms = SpikeMonitor(S)
Mt = SpikeMonitor(AT)
Mv = StateMonitor(S, 'v', record=True)  # Record all states
Mg = StateMonitor(S, ['g_fwd', 'g_bwd', 'g_left', 'g_right'], record=0)  # Monitor commands
Mcpg = SpikeMonitor(CPG)  # Monitor CPG spikes
Mvcpg = StateMonitor(CPG, 'v', record=[0, 1, 2, 3, 7])  # Monitor some CPG voltages

# -------------------------------------------------------
# EXÉCUTION
# -------------------------------------------------------
AT.x = Tmove
AT.armed = 1

print("Simulation en cours...")
run(Tsim)
print("\nSimulation terminée ✅")

# -------------------------------------------------------
# ANALYSE & AFFICHAGE
# -------------------------------------------------------
ack_times = Mt.t / ms
seq = []
for t_ack in ack_times:
    mask = (Ms.t / ms >= t_ack) & (Ms.t / ms < t_ack + 5)
    if np.any(mask):
        seq.append(int(Ms.i[np.where(mask)[0][0]]))
    else:
        seq.append(None)

print("\n" + "=" * 60)
print("ACK times (ms):", np.round(ack_times, 1))
print("États actifs après chaque ACK:", seq)
print("=" * 60)

# Affichage amélioré
fig = plt.figure(figsize=(16, 14))

# Use gridspec for better control
gs = fig.add_gridspec(5, 1, hspace=0.3)

# Affichage amélioré
fig = plt.figure(figsize=(16, 14))

# Use gridspec for better control
gs = fig.add_gridspec(5, 1, hspace=0.3)

ax1 = fig.add_subplot(gs[0, 0])
plt.plot(Ms.t / ms, Ms.i, '.k', ms=4)
plt.ylabel('État', fontsize=11)
plt.title('Spikes des états (trajectoire dans le graphe)', fontsize=12, fontweight='bold')
plt.yticks(range(n_states))
plt.grid(True, alpha=0.3)
plt.xlim(0, Tsim / ms)

ax2 = fig.add_subplot(gs[1, 0])
plt.plot(Mcpg.t / ms, Mcpg.i, '.b', ms=3, alpha=0.6)
plt.ylabel('CPG', fontsize=11)
plt.title('Spikes des CPG (oscillations rythmiques)', fontsize=12, fontweight='bold')
plt.yticks(range(n_states))
plt.grid(True, alpha=0.3)
plt.xlim(0, Tsim / ms)

ax3 = fig.add_subplot(gs[2, 0])
plt.plot(Mt.t / ms, np.zeros_like(Mt.t / ms), '|r', ms=25, mew=2)
plt.ylabel('ACK', fontsize=11)
plt.ylim(-0.5, 0.5)
plt.grid(True, alpha=0.3)
plt.title('Signaux de TICK du timer', fontsize=12)
plt.xlim(0, Tsim / ms)

ax4 = fig.add_subplot(gs[3, 0])
# Plot all states with different colors
colors = plt.cm.tab20(np.linspace(0, 1, n_states))
for i in range(n_states):
    plt.plot(Mv.t / ms, Mv.v[i], label=f'État {i}', alpha=0.7, linewidth=1, color=colors[i])
plt.axhline(v_th, color='red', linestyle='--', label='Seuil', linewidth=2)
plt.ylabel('Voltage', fontsize=11)
plt.legend(loc='upper right', fontsize=8, ncol=2)
plt.grid(True, alpha=0.3)
plt.title('Tensions de tous les états', fontsize=12)
plt.xlim(0, Tsim / ms)  # Full duration
plt.ylim(-0.2, 1.5)

plt.subplot(4, 1, 4)
# Plot command signals over time
plt.plot(Mg.t / ms, Mg.g_fwd[0], 'b-', label='g_fwd', linewidth=1.5)
plt.plot(Mg.t / ms, Mg.g_right[0], 'r-', label='g_right', linewidth=1.5)
plt.plot(Mg.t / ms, Mg.g_bwd[0], 'g-', label='g_bwd', linewidth=1.5)
plt.plot(Mg.t / ms, Mg.g_left[0], 'm-', label='g_left', linewidth=1.5)
plt.axhline(theta_cmd, color='k', linestyle='--', label='Seuil', linewidth=1)
plt.ylabel('Commandes', fontsize=11)
plt.xlabel('Temps (ms)', fontsize=11)
plt.legend(loc='upper right', fontsize=9)
plt.grid(True, alpha=0.3)
plt.title('Signaux de commande', fontsize=12)
plt.xlim(0, 2000)
plt.ylim(-0.1, 1.2)

plt.show()

