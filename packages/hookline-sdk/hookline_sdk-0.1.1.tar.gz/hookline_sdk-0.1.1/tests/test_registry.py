import unittest

from src.hookline_sdk.decorators import plugin_version
from src.hookline_sdk.registry import HooklinePlugin


class SamplePlugin(HooklinePlugin):

    @plugin_version(version="1.2.1")
    def execute1(self, payload, config):
        return f"1.2.1"

    @plugin_version(version="1.2.3")
    def doing_something(self, payload, config):
        return f"1.2.3"

    def ignoring(self):
        return "This is non versioned!"


class TestRegistry(unittest.TestCase):

    def test_method_resolution(self):
        plugin = SamplePlugin(target_version="1.2.3")

        assert '1.2.1' in plugin._method_registry
        assert '1.2.3' in plugin._method_registry

    def test_version_matching(self):
        plugin1 = SamplePlugin(target_version="1.2.1")
        plugin2 = SamplePlugin(target_version="2.0.1")

        r1 = plugin1.start(payload={}, config={})
        assert r1 == "1.2.1"
        self.assertRaises(ValueError, plugin2.start, payload={}, config={})
