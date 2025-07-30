from typing import Any
import numpy as np
from abc import ABC, abstractmethod

from rafael_nn.common import FloatArr

class LossFunction(ABC):
    @abstractmethod
    def __call__(self, prediction: FloatArr, target: FloatArr) -> float:
        """Compute the loss value."""
        pass

    @abstractmethod
    def backward(self, prediction: FloatArr, target: FloatArr) -> FloatArr:
        """Compute the gradient of the loss with respect to the prediction."""
        pass

class MeanSquaredError(LossFunction):
    def __call__(self, prediction: FloatArr, target: FloatArr) -> np.floating[Any]:
        return np.mean((prediction - target) ** 2)

    def backward(self, prediction: FloatArr, target: FloatArr) -> FloatArr:
        return 2 * (prediction - target) / prediction.size

