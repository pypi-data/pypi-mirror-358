"""
Generate #{(top_level_name)} RTL code
"""
from pathlib import Path
from typing import Generator

from rtl_generator import *

YAML_PATH = Path(Path(__file__).parent, "options.yml").resolve()

# User-defined imports, functions, and globals
