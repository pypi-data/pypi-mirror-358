from abc import ABC, abstractmethod
from typing import Optional
import numpy as np
from numpy.typing import NDArray # Import NDArray from numpy.typing

from rafael_nn.acfn import ActivationFunction, ReLU
from rafael_nn.common import FloatArr
from rafael_nn.optimizer import Optimizer

class Layer(ABC):
    weights: NDArray[np.float64]
    biases: NDArray[np.float64]
    fn: ActivationFunction

    f: FloatArr
    h: FloatArr

    @abstractmethod
    def __call__(self, input: FloatArr) -> tuple[FloatArr,FloatArr]:
        """Compute the loss value."""
        pass

    @abstractmethod
    def backward(self, prev_dl_f:Optional[FloatArr] = None, weights_dl_f: Optional[FloatArr] = None) -> tuple[FloatArr,FloatArr,FloatArr]:
        """Compute the gradient of the loss with respect to the prediction."""
        pass

    # for debugging, helped a lot when building backpropagation
    def __str__(self):
        return "Unknown"

    def __repr__(self):
        return "Unknown"

# NOTE: I had a design issue. Each layer was storing its preactivation and activation values.
# but for the first layer the activation value is the input. Because this should be the activation that happened on the PREVIOUS layer
# my design had these values stored on the layer they were executed, 
# so the first layer h value was the first execution of the activation function. And the last one didnt had one

# NOTE: to solve the issue above, just added 'h' as the input value the layer received when called on the forward pass

class Linear(Layer):
    prev:int
    neurons:int

    def __init__(self,prev:int, neurons:int, fn:Optional[ActivationFunction] = None):
        """Initializes linear layer with weights. Initializes biases with 0"""
        self.fn = ReLU(neurons) if fn is None else fn
        weights = [[self.fn.init_sample() for _ in range(prev)] for _ in range(neurons)]
        # TODO, output is 0 if bias is 0. need to check this
        #bug: before I was initializing biases with shape (6,). This was causing issues when added. It turned the vector into a matrix
        biases = [[0] for _ in range(neurons)]

        self.prev = prev
        self.neurons = neurons
        self.weights = np.array(weights, dtype=np.float64)
        self.biases = np.array(biases, dtype=np.float64)

    def __call__(self, input: FloatArr) -> tuple[FloatArr, FloatArr]:
        """Applies the forward pass. Multiplies the given vector by the matrix weights and applies the activation fn"""
        # we need the preactivation for the gradient calc
        self.h = input
        self.f = self.biases + self.weights@input

        return self.fn(self.f), self.f

    def backward(self, prev_dl_f:Optional[FloatArr] = None, weights_dl_f: Optional[FloatArr] = None) -> tuple[FloatArr,FloatArr,FloatArr]:
        """
        Calculates dl_weights, dl_f and dl_bias given arguments. weights_dl_f or prev_dl_f must be passed (one or the other).
        if prev_dl_f is passed, this means this is the LAST layer and the first to calculate dl_f. 
        if weights_dl_f is passed, it means this is a hidden layer
        """
        if prev_dl_f is None:
            dl_f = np.where(self.f > 0, 1, 0)*weights_dl_f
        else:
            dl_f = prev_dl_f

        # dl_bias, dl_f and dl_weight
        return dl_f, dl_f, dl_f@self.h.T

    def __str__(self):
        return f"Linear({self.prev},{self.neurons})"

    def __repr__(self):
        return f"Linear({self.prev},{self.neurons})"

