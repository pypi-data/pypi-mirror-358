import sys
import importlib
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec


class ApiImportHook(MetaPathFinder):
    """Import hook that redirects proto imports"""

    def __init__(self):
        self.redirects = {
            "api": "lib.proto.api",
            "common": "lib.proto.common",
            "error": "lib.proto.error",
            "buf": "lib.proto.buf",
        }
        self.processing = set()

    def find_spec(self, fullname, path=None, target=None):
        if fullname in self.processing:
            return None

        prefix = fullname.split(".")[0]
        if prefix in self.redirects:
            self.processing.add(fullname)
            try:
                redirected = fullname.replace(prefix, self.redirects[prefix], 1)
                try:
                    module = importlib.import_module(redirected)
                    sys.modules[fullname] = module
                    return importlib.util.find_spec(redirected)
                except ImportError:
                    pass
            finally:
                self.processing.remove(fullname)
        return None


def install():
    if not any(isinstance(finder, ApiImportHook) for finder in sys.meta_path):
        sys.meta_path.insert(0, ApiImportHook())
        print("API import hook installed")
