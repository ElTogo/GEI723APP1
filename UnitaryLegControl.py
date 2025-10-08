import numpy
import brian2
import matplotlib.pyplot as plt
from brian2 import NeuronGroup


class UnitaryLegControl:
    self.GI = NeuronGroup(4, 'dv/dt = -v / (10*ms) : 1',
                          threshold='v > 1', reset='v=0.', method='exact')