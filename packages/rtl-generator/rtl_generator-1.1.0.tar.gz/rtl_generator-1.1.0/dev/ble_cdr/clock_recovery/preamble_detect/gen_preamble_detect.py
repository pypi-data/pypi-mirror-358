"""
Generate Preamble Detect RTL code
"""

import sys
from pathlib import Path
from typing import Generator

sys.path.append(str(Path(__file__).resolve().parent.parent))
from rtl_generator import *
from gen_clock_recovery import *


# User-defined imports, functions, and globals
