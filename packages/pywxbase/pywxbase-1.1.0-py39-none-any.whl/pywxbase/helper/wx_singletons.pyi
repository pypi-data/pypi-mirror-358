# Stub file for type hints

import threading

class WXSingletons:
    _instances: dict
    _lock: Any
    def __call__(cls, *args, **kwargs): ...
