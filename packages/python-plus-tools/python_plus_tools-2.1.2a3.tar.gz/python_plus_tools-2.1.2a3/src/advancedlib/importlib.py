from importlib import *
from site import *
from modulelib import *

class LazyImport:
    def __init__(self, module_name):
        self.module_name = module_name
        self._module = None

    def __getattr__(self, name):
        if self._module is None:
            self._module = import_module(self.module_name)
        return getattr(self._module, name)