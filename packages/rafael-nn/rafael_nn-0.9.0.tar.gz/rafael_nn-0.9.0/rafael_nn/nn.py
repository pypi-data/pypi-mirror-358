import numpy as np
from numpy.typing import NDArray
from rafael_nn.common import FloatArr

from rafael_nn.layer import Layer
from rafael_nn.lossfn import LossFunction
from rafael_nn.optimizer import Optimizer

np.random.seed(42)

class NeuralNetwork:
    # I like adding types. Its easier to know that what im doing will work, also easier to debug
    # want to update this to use functional programming
    layers: list[Layer]
    optimizer:Optimizer
    layers_output: list[NDArray[np.float64]]
    loss_fn:LossFunction

    def __init__(self, layers:list[Layer], optimizer:Optimizer, loss_fn:LossFunction):
        self.layers = layers
        self.optimizer = optimizer
        self.loss_fn = loss_fn

    def __call__(self, x: np.ndarray) -> np.ndarray:
        return self._forward(x)[0]

    def train(self, x: FloatArr, target:FloatArr, epochs = 1000, err = 1e-4):
        cur_err = np.inf
        i = 0
        while epochs > 0 and cur_err > err:
            final = self(x[i])
            cur_err = self.loss_fn(final,target[i])
            all_dl_bias,all_dl_weights = self._backward(final, target[i])

            print("ERROR",cur_err)
            for i in range(len(self.layers)):
                layer = self.layers[i]
                layer.biases = self.optimizer(layer.biases,all_dl_bias[i])
                layer.weights = self.optimizer(layer.weights,all_dl_weights[i])
            i+=1

    def backward(self, prediction:FloatArr, target:FloatArr) -> tuple[list[FloatArr],list[FloatArr]]:
        return self._backward(prediction,target)

    # this is almos the same implementation as the 7_2 notebook
    def _forward(self, x: FloatArr) -> tuple[FloatArr, list[FloatArr], list[FloatArr]]:
        all_h, all_f = [], []
        # all layers but the last one apply activation fn
        for i in range(len(self.layers) - 1):
            layer = self.layers[i]
            h, f = layer(x if i == 0 else all_h[i-1])

            all_h.append(h)
            all_f.append(f)

        # last layer outputs result y
        _,res = self.layers[-1](all_h[-1])
        all_f.append(res)

        return res, all_h, all_f

    def _backward(self, prediction:FloatArr, target:FloatArr) -> tuple[list[FloatArr],list[FloatArr]]:
        layers_n = len(self.layers)
        all_dl_bias, all_dl_weights = [None] * layers_n, [None] * layers_n

        dl_b, prev_dl_f, dl_w = self.layers[-1].backward(prev_dl_f=self.loss_fn.backward(prediction,target))
        all_dl_bias[-1] = dl_b
        all_dl_weights[-1] = dl_w

        for i in range(layers_n - 2,-1,-1):
            # here had an anoying error because prev_w was already transposed on this line
            prev_w = self.layers[i+1].weights
            dl_b, prev_dl_f, dl_w = self.layers[i].backward(weights_dl_f=prev_w.T @ prev_dl_f)
            all_dl_bias[i] = dl_b
            all_dl_weights[i] = dl_w

        return all_dl_bias, all_dl_weights

    def update(self, optimizer: Optimizer) -> None:
        pass

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int, batch_size: int, loss_fn, optimizer: Optimizer) -> None:
        pass

    def predict(self, X: np.ndarray) -> np.ndarray:
        pass
