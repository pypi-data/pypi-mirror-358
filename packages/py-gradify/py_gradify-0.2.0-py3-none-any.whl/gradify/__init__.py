from .core import gradify as _gradify

class _GradifyModule:
    def __call__(self, *args, **kwargs):
        return _gradify(*args, **kwargs)

    def __getattr__(self, name):
        raise AttributeError(f"'gradify' module has no attribute '{name}'")

import sys
sys.modules[__name__] = _GradifyModule()
