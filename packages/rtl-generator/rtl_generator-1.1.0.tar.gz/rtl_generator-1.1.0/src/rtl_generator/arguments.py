"""
Handle all things related to arguments
"""
import argparse
import builtins
from importlib import import_module
from pathlib import Path
from typing import Tuple, Dict

import yaml

from .format import get_pretty_name
from .heirarchy import get_subdirs


def update_scope(updates: dict, scope: dict) -> Tuple[Dict, Dict]:
    for k in filter(lambda k: k in updates, scope.keys()):
        scope[k] = updates.pop(k)
    
    return scope, updates


def module_in_out_args(rtl_name: str, proj_path: Path, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """
    Add input and output arguments for the module
    """
    pretty_rtl_name = get_pretty_name(rtl_name)
    parser.add_argument(f"--{rtl_name}_input", type=str, help=f"{pretty_rtl_name} Input file path", default=str(Path(proj_path, f"{rtl_name}.sv")))
    parser.add_argument(f"--{rtl_name}_output", type=str, help=f"{pretty_rtl_name} Output file path", default=str(Path(proj_path, f"{rtl_name}.sv")))
    return parser


def add_args(rtl_name: str, proj_path: Path, parser: argparse.ArgumentParser | None = None) -> argparse.ArgumentParser:
    """
    Add arguments to the parser
    """
    # import the module to get the YAML_PATH
    module = import_module(f"gen_{rtl_name}")

    if YAML_PATH := vars(module).get("YAML_PATH", None):
        with open(YAML_PATH, "r") as f:
            args = yaml.safe_load(f)
    else:
        args = {}

    del module

    # Add the arguments to the parser
    if parser is None:
        parser = argparse.ArgumentParser(description=f"Generate {get_pretty_name(rtl_name)} RTL code")

    for arg, arg_info in args.items():
        if 'type' in arg_info:
            arg_info['type'] = getattr(builtins, arg_info['type'])
        try:
            parser.add_argument(f"--{arg}", **arg_info)
        except argparse.ArgumentError:
            pass
    
    parser.add_argument("--replace_includes", help="Replace include statements with the contents of the file. \
                        If false, include statement(s) will be left in the file, and the included file(s) will be generated separately",\
                        action="store_true")
    
    # Add module & submodule arguments
    available_mods = [proj_path]
    while available_mods:
        mod_path = available_mods.pop()
        parser = module_in_out_args(mod_path.name, mod_path, parser)
        available_mods.extend(get_subdirs(mod_path))
    
    return parser
