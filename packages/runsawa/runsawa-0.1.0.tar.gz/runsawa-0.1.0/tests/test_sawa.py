import unittest
from runsawa import runsawa


class Testrunsawa(unittest.TestCase):

    def test_runsawa(self):
        items = list(range(10))
        identity_func = lambda x: x
        result = sorted(list(runsawa(identity_func, items, workers=2)))
        self.assertEqual(items, result)


if __name__ == "__main__":
    unittest.main()
