import inspect

from packaging.version import parse


class HooklinePlugin:

    def __init__(self, target_version):
        self._method_registry = {}  # {version : ref to func}
        self.target_version = target_version
        self._scan_methods()

    def start(self, payload: dict, config: dict):
        func = self._resolve_version()
        return func(payload=payload, config=config)

    def _scan_methods(self):
        for _, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, "hookline_version"):
                self._register_method(method)

    def _register_method(self, func):
        version = func.hookline_version
        parse(version)

        if version in self._method_registry:
            raise ValueError(f"Version {version} already is registered")

        self._method_registry[version] = func

    def _resolve_version(self):
        if self.target_version not in self._method_registry:
            raise ValueError(f"No compatible version found for {self.target_version}")

        func = self._method_registry[self.target_version]
        return func
