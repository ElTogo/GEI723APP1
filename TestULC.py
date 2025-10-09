import unittest
import brian2
import matplotlib.pyplot as plt
from brian2 import NeuronGroup
from brian2.codegen.cpp_prefs import output
import UnitaryLegControl


class MyTestCase(unittest.TestCase):
    def test_controle(self):
        eqs = """
        dv/dt = I/tau : 1
        tau : second
        I : 1
        th : 1
        """
        input = NeuronGroup(3, eqs, threshold='v>=th', reset='v=0', method='euler')
        output - NeuronGroup(4, eqs, threshold='v>=th', reset='v=0', method='euler')
        ULC = UnitaryLegControl(input, output)
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
