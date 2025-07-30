import unittest
from src.hookline_sdk.decorators import plugin_version

class TestDecorators(unittest.TestCase):
    def test_decorator_adds_data(self):

        @plugin_version(version="1.1.2")
        def myfunction():
            return "testing..."

        assert hasattr(myfunction, "hookline_version")
        assert myfunction.hookline_version == "1.1.2"