# Stub file for type hints

import os
import sys
from pathlib import Path

class WXPaths:
    @staticmethod
    def project_path(): ...
    @staticmethod
    def resolve_path(input_path: str, base_path: str = None): ...
