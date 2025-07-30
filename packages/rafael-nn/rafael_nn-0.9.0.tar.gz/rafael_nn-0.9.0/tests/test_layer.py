import numpy as np
import unittest
from unittest.mock import MagicMock
from rafael_nn.acfn import ActivationFunction
from rafael_nn.layer import Linear

class TestLinear(unittest.TestCase):

    def setUp(self):
        self.prev_neurons = 5
        self.current_neurons = 3
        # here I figured out how to make mocks for classes in python. Following best practices for unit tests
        # In unit tests, bugs in other classes should not affect the testing of the current one, thats why we mock
        self.mock_activation_fn = MagicMock(spec=ActivationFunction)
        self.mock_activation_fn.side_effect = lambda x: x + 1 # identity + 1 function for simplicity 
        self.mock_activation_fn.init_sample.side_effect = lambda: 0.1

        self.linear_layer = Linear(self.prev_neurons, self.current_neurons, self.mock_activation_fn)

    def test_initialization_weights_shape(self):
        "Here we test the shape is correct"
        expected_shape = (self.current_neurons, self.prev_neurons)
        self.assertEqual(self.linear_layer.weights.shape, expected_shape)

    def test_initialization_weights_dtype(self):
        "Here we test the numbers type is correct"
        self.assertEqual(self.linear_layer.weights.dtype, float)

    def test_initialization_biases_shape(self):
        "Here we test the biases shape is correct"
        expected_shape = (self.current_neurons,1)
        self.assertEqual(self.linear_layer.biases.shape, expected_shape)

    def test_initialization_fn_assignment(self):
        "Here we test the used activation function is correct"
        self.assertEqual(self.linear_layer.fn, self.mock_activation_fn)

    def test_initialization_weights_content(self):
        "Here we check the weights are correctly initialized"
        expected_weights = np.array([
            [0.1] * self.linear_layer.weights.shape[1],
            [0.1] * self.linear_layer.weights.shape[1],
            [0.1] * self.linear_layer.weights.shape[1],
        ], dtype=float)
        np.testing.assert_array_equal(self.linear_layer.weights, expected_weights)
        # in a single call should affect all input
        self.assertEqual(self.mock_activation_fn.init_sample.call_count, self.current_neurons * self.prev_neurons)

    def test_initialization_biases_content(self):
        "Here we check the biases are correctly initialized"
        expected_biases = np.array([[0]] * self.linear_layer.weights.shape[0], dtype=float)
        np.testing.assert_array_equal(self.linear_layer.biases, expected_biases)

    def test_forward_pass_output_shape(self):
        "Here we check the shape of the forward pass is correct"
        # test input vector
        input_vector = np.random.normal(size=(self.prev_neurons,1))
        output,_ = self.linear_layer(input_vector)
        self.assertEqual(output.shape, (self.current_neurons,1))

    def test_forward_pass_multiplication_and_activation(self):
        """Test that the forward pass correctly performs multiplication and applies activation."""

        test_input = np.array([[1.0], [2.0], [3.0], [4.0], [5.0]], dtype=float)
        # we multiply [1...5] by [[[0.1] * 5] * 3] and add 1 to each entry
        expected_raw_output = np.array([[1.5], [1.5], [1.5]], dtype=float)

        # here our mock activation fn is x + 1
        expected_final_output = expected_raw_output + 1
        output,_ = self.linear_layer(test_input)

        np.testing.assert_array_almost_equal(output, expected_final_output)
        self.mock_activation_fn.assert_called_once()
        np.testing.assert_array_almost_equal(self.mock_activation_fn.call_args[0][0], expected_raw_output)

# To run the tests:
if __name__ == '__main__':
    unittest.main()
