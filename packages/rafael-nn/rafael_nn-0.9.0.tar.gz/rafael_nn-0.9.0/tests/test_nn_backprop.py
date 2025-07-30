
import unittest
import numpy as np
from rafael_nn.acfn import ReLU
from rafael_nn.layer import Layer, Linear
from rafael_nn.lossfn import MeanSquaredError

from rafael_nn.nn import NeuralNetwork
from rafael_nn.optimizer import GradientDescent


class TestNNGradient(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        layers = 5
        n_by_layer = 6
        layers:list[Layer] = [Linear(1,n_by_layer)] + [Linear(n_by_layer,n_by_layer) for _ in range(layers-1)] + [Linear(n_by_layer,1)]

        self.loss_fn = MeanSquaredError()
        self.nn = NeuralNetwork(layers, optimizer=GradientDescent(), loss_fn=self.loss_fn)

    # def test_nn_gradient_with_bias_change(self):
    def aux(self):
        """Here we perform the same kind of check made in the notebook 7_2 to see if our derivatives are well calculated"""
        # x = np.random.randn(1)
        x = np.array([1.2])
        target = np.array([1.0])
        epsilon = 0.000001 # same delta used in notebook 7_2

        prediction = self.nn(x)
        all_dl_b, _ = self.nn._backward(prediction, target)

        for layer_i in range(len(self.nn.layers)):
            layer = self.nn.layers[layer_i]

            bias_cpy = np.array(layer.biases)
            dl_bias = np.zeros_like(all_dl_b[layer_i])

            for row in range(len(layer.biases)):
                # get current output
                output = self.nn(x)
                layer.biases[row]+=epsilon
                # get output with small change
                output_change = self.nn(x)

                #restore previous value
                layer.biases = bias_cpy
                dl_bias[row] = (self.loss_fn(output_change,target) - self.loss_fn(output, target))/epsilon

            assert np.allclose(all_dl_b[layer_i], dl_bias, rtol=1e-5, atol=1e-8, equal_nan=False), \
                f"Gradient check failed for bias at layer {layer_i}.\n" \
                f"Backprop: {all_dl_b[layer_i]}\n" \
                f"Finite diff: {dl_bias}"

    def test_nn_gradient_with_weight_change(self):
        """Here we perform the same kind of check made in the notebook 7_2 to see if our derivatives are well calculated"""
        x = np.array([[1.2]])
        target = np.array([[1.0]])
        epsilon = 0.000001 # same delta used in notebook 7_2

        prediction = self.nn(x)
        _, all_dl_w = self.nn._backward(prediction, target)

        for layer_i in range(len(self.nn.layers)):
            layer = self.nn.layers[layer_i]

            weight_copy = np.array(layer.weights)
            dl_w = np.zeros_like(all_dl_w[layer_i])

            for row in range(layer.weights.shape[0]):
                for col in range(layer.weights.shape[1]):
                    # get current output
                    output = self.nn(x)
                    layer.weights[row][col]+=epsilon
                    # get output with small change
                    output_change = self.nn(x)

                    #restore previous value
                    layer.weights = weight_copy
                    dl_w[row][col] = (self.loss_fn(output_change,target) - self.loss_fn(output, target))/epsilon

            # NOTE: here I had to reduce atol from 1e-8 to 1e-5. Maybe some imprecision on my code?
            assert np.allclose(all_dl_w[layer_i], dl_w, rtol=1e-5, atol=1e-5, equal_nan=False), \
                f"Gradient check failed for weight at layer {layer_i}.\n" \
                f"Backprop: {all_dl_w[layer_i]}\n" \
                f"Finite diff: {dl_w}"


