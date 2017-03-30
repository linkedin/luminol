import unittest
from luminol import exceptions
from luminol import Luminol


class TestLuminol(unittest.TestCase):
    def setUp(self):
        self.anomaly = ['A', 'B']
        self.correlation = {
            'A': ['m1', 'm2', 'm3'],
            'B': ['m2', 'm1', 'm3']
        }
        self.luminol = Luminol(self.anomaly, self.correlation)

    def test_get_result(self):
        self.assertTrue(isinstance(self.luminol.get_root_causes(), dict))
        self.assertEqual(self.luminol.get_root_causes()['A'], 'm1')
        self.assertEqual(self.luminol.get_root_causes()['B'], 'm2')


# if __name__ == '__main__':
#     unittest.main()
