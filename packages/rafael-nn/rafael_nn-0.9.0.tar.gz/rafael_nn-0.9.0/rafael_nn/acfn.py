import numpy as np
from abc import ABC, abstractmethod

from rafael_nn.common import FloatArr

class ActivationFunction(ABC):
    def __init__(self, n:int):
        self.n = n

    @abstractmethod
    def __call__(self,x:FloatArr) -> FloatArr:
        pass

    @abstractmethod
    def init_sample(self) -> np.float64:
        pass

# since the best initialization depends on the activation function. We delegate that to its class
class ReLU(ActivationFunction):
    def __call__(self,x:FloatArr):
        return x.clip(0)

    def init_sample(self) -> np.float64:
        return np.float64(np.random.normal(loc=0, scale=2 / self.n))

