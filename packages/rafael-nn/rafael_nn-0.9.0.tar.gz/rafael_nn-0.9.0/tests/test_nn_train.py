
# THIS CREATES ONLY THE DATASET. following the function found in 7.3

import unittest
import numpy as np
import matplotlib.pyplot as plt

def teaching_function(x, beta, omega):
    return beta[3] + omega[3] * np.cos(
        beta[2] + omega[2] * np.exp(
            beta[1] + omega[1] * np.sin(
                beta[0] + omega[0] * x
            )
        )
    )

# Random but fixed parameters
np.random.seed(42)
beta = np.random.uniform(-1, 1, size=4)
omega = np.random.uniform(-1, 1, size=4)

# Create dataset
x = np.linspace(-5, 5, 200)
y_clean = teaching_function(x, beta, omega)
y_noisy = y_clean + np.random.normal(0, 0.1, size=x.shape)  # add small noise

# Optional: visualize
plt.plot(x, y_clean, label="clean signal")
plt.scatter(x, y_noisy, s=10, alpha=0.6, label="noisy data")
plt.legend()
plt.title("Teaching Function Dataset")
plt.show()

class TestNNGradient(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        layers = 5
        n_by_layer = 6
        layers:list[Layer] = [Linear(1,n_by_layer)] + [Linear(n_by_layer,n_by_layer) for _ in range(layers-1)] + [Linear(n_by_layer,1)]

        self.loss_fn = MeanSquaredError()
        self.nn = NeuralNetwork(layers, optimizer=GradientDescent(), loss_fn=self.loss_fn)
