
import numpy as np
import unittest
from unittest.mock import MagicMock, patch
from rafael_nn.acfn import ActivationFunction
from rafael_nn.common import FloatArr
from rafael_nn.layer import Layer
from rafael_nn.lossfn import MeanSquaredError

from rafael_nn.nn import NeuralNetwork

class MockActFunction(ActivationFunction):
    """Mock for ActivationFunction."""
    def __call__(self, x: FloatArr) -> FloatArr:
        return x
    def init_sample(self, i: int, j: int) -> float:
        return 0.0

class TestLinear(Layer):
    """Mock for the Linear layer."""
    def __init__(self, prev: int, neurons: int, fn: MockActFunction):
        self.prev = prev
        self.neurons = neurons
        self.fn = fn
        self.weights = np.zeros((neurons, prev)) 

    def backward(self):
        pass

    def __call__(self, input: FloatArr):
        return input + 1, input + 1

class Optimizer:
    """Mock for the Optimizer."""
    def __init__(self):
        pass 
    def optimize(self, params):
        pass

class TestNeuralNetwork(unittest.TestCase):

    def setUp(self):
        """Set up common variables and mocks for tests."""
        self.mock_layer1 = TestLinear(0,0,MockActFunction(1))
        self.mock_layer2 = TestLinear(0,0,MockActFunction(1))
        self.mock_layer3 = TestLinear(0,0,MockActFunction(1))

        self.mock_optimizer = MagicMock(spec=Optimizer)

        self.neural_network = NeuralNetwork(
            layers=[self.mock_layer1, self.mock_layer2, self.mock_layer3],
            optimizer=self.mock_optimizer,
            loss_fn=MeanSquaredError()
        )

    def test_forward_pass_flow_and_output(self):
        initial_input = np.array([5.0, 5.0], dtype=np.float64)

        expected_l1 = initial_input + 1.0
        expected_l2 = expected_l1 + 1.0
        expected_l3 = expected_l2 + 1.0

        output = self.neural_network(initial_input)

        np.testing.assert_array_equal(output, expected_l3)

    def test_optimizer_assignment(self):
        """Test that the optimizer is correctly assigned."""
        self.assertEqual(self.neural_network.optimizer, self.mock_optimizer)

# To run the tests:
if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)

