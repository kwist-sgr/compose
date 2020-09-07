import gc
import unittest


class TestCase(unittest.TestCase):

    def tearDown(self):
        # Collect garbage on tearDown. (This can print ResourceWarnings.)
        gc.collect()


class ComposeTest(TestCase):

    def test_create(self):
        pass

    def test_compose(self):
        pass

    def test_call(self):
        pass


if __name__ == "__main__":
    unittest.main()
