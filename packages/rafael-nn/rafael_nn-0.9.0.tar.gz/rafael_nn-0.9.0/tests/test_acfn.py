import unittest
import numpy as np
from rafael_nn.acfn import ReLU

class TestReLU(unittest.TestCase):

    def test_forward_positive(self):
        relu = ReLU(1)
        x = np.array([1, -1, 0, 5])
        output = relu(x)
        expected = np.array([1, 0, 0, 5])
        np.testing.assert_array_equal(output, expected)

if __name__ == '__main__':
    unittest.main()

