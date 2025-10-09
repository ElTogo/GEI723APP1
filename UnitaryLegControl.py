import numpy
import brian2
import matplotlib.pyplot as plt
from brian2 import NeuronGroup


# Devrais recevoir un set de 3 neurones par jambes :
# neurone 1 : 0 si au centre, 1 s'il devrais avoir un mouvement
# neurone 2 : mouvement vers l'avant (0) ou l'arrière (1)
# meurone 2 : 0 si la patte est au sol, 1 si la patte doit être levé

class UnitaryLegControl():
    def __init__(self,neuron_in, neuron_out):
        self.neuron_in = neuron_in
        self.neuron_out = neuron_out
        eqs = """
        dv/dt = (I - v) / tau : 1
        I : 1
        tau : second
        """

        l1 = NeuronGroup(1, eqs, threshold='v>1', reset='v=0', method='euler')
        l2 = NeuronGroup(2, eqs, threshold='v>1', reset='v=0', method='euler')

        l1.tau = 10 * ms
        l2.tau = 8 * ms

        # Inverse le mouvement dans l1
        S_dir_to_inv = Synapses(self.neuron_in, l1, on_pre='v_post -= 0.6')  # inhibition douce
        S_dir_to_inv.connect(i=2, j=0)

        l1.I = 0.6

        #Connexion pleinement connecté de la couche 1
        S_mov_to_l2 = Synapses(self.neuron_in, l2, on_pre='v_post += 0.5')
        S_mov_to_l2.connect(i=1, j=0)

        S_mov_to_l22 = Synapses(self.neuron_in, l2, on_pre='v_post += 0.5')
        S_mov_to_l22.connect(i=1, j=1)

        S_dir_to_l2 = Synapses(self.neuron_in, l2, on_pre='v_post += 0.5')
        S_dir_to_l2.connect(i=2, j=1)

        # Connexion du mouvement inversé
        S_inv_to_l2 = Synapses(l1, l2, on_pre='v_post += 0.5')
        S_inv_to_l2.connect(i=0, j=0)

        #Connexion excitatrice de la dernière couche
        S_l2_to_out_ex = Synapses(l2, self.neuron_out, on_pre='v_post += 0.5')
        S_l2_to_out_ex.connect(i=[0, 1], j=[2, 3])

        # Connexion inibitrice de la dernière couche
        S_l2_to_out_in = Synapses(l2, self.neuron_out, on_pre='v_post -= 0.6')
        S_l2_to_out_in.connect(i=[1, 0], j=[2, 3])

        #Connexion pour le mouvement vertical
        vertical_exc = Synapses(self.neuron_in, self.neuron_out, on_pre='I_post = 2')  # excitatrice
        vertical_inh = Synapses(self.neuron_in, self.neuron_out, on_pre='I_post = 0')  # inhibitrice

        vertical_exc.connect(i=0, j=0)  # entrée 0 excite l’extenseur
        vertical_inh.connect(i=0, j=1)  # entrée 0 inhibe le fléchisseur

        self.output_group[1] = 2
        self.output_group[2] = 1.2
        self.output_group[3] = 1.2

        l1.v = 0
        l2.v = 0

        l1.I = [1.2]
        l2.I = [0, 0]