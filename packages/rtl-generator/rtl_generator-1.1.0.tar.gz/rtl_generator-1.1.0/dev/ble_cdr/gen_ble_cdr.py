"""
Generate Ble Cdr RTL code
"""
from pathlib import Path
from typing import Dict, Generator

from rtl_generator import *

YAML_PATH = Path(Path(__file__).parent, "options.yml").resolve()


# User-defined imports, functions, and globals
import os
import sys

modules_path = Path(os.environ.get("MODULES_PATH", "/home/brandonhippe/west/Research Projects/SCuM BLE/Python/Modules")).resolve()
sys.path.insert(0, str(modules_path))
from phy.demodulation import *
from phy.iq import *


@generator_context
def samples_per_symbol(fsym, clk_freq, **kwargs) -> Generator[str, None, Dict]:
    """
    Calculate the number of samples per symbol based on the symbol rate and clock frequency
    """
    assert clk_freq % fsym == 0, "Clock rate must be an integer multiple of symbol rate"

    samples_per_symbol = clk_freq // fsym
    yield str(samples_per_symbol)
    return dict(samples_per_symbol=samples_per_symbol)
