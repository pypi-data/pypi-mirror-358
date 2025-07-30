import numpy as np
from abc import ABC, abstractmethod

from rafael_nn.common import FloatArr

class Optimizer(ABC):
    @abstractmethod
    def __call__(self, parameters: FloatArr, gradients: FloatArr) -> FloatArr:
        pass

class GradientDescent(Optimizer):
    def __init__(self, learning_rate: float = 0.01):
        self.learning_rate = learning_rate

    def __call__(self, parameters: FloatArr, gradients: FloatArr) -> FloatArr:
        return parameters - self.learning_rate*gradients

