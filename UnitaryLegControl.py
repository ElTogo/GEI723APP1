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
        self.synapses_in = neuron_in
        self.neuron_out = neuron_out
        eqs = """
        dv/dt = I/tau : 1
        tau : second
        I : 1
        th : 1
        """
        self.g1 =
    # self.GI = NeuronGroup(4, 'dv/dt = -v / (10*ms) : 1',
    #                       threshold='v > 1', reset='v=0.', method='exact')