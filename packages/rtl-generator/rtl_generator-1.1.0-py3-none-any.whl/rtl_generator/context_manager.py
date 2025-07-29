"""
Manage the context for the RTL generator.

Handles the context for generating RTL code, including which arguments are used and variable values across the generation process.
"""

import inspect
from typing import Generator


def generator_context(gen: Generator) -> str:
    """
    Decorator context manager for the RTL generator.
    
    This function manages the context for generating RTL code, including which arguments are used and variable values across the generation process.
    It calls the provided generator function and returns the result, along with the updated context.

    A Python Generator function usable in this context should yield a single value, a string for the RTL that function creates.
    It should also return a dict containing any values calculated within that function that should be maintained throughout the process of running the RTL generator.

    Args:
        gen (Generator): The generator function to call within the context.
        ignore_keys (Set): A set of keys to ignore when updating 
    Returns:
        str: Result of the called generator function
    """
    def wrapper(*args, used_args: set=set(), **kwargs):
        def add_return_caller_frame_var(k, v):
            caller_frame_vars[k] = v
            if "__returned_dict__" not in caller_frame_vars:
                caller_frame_vars["__returned_dict__"] = {}
            caller_frame_vars["__returned_dict__"][k] = v

        caller_frame_vars = inspect.currentframe().f_back.f_locals
        gen_argnames = set(inspect.signature(gen).parameters.keys())
        g = gen(*args, used_args=used_args, **kwargs)
        used_args |= gen_argnames & set(caller_frame_vars.get("kwargs", {}).keys())
        g_vars = inspect.getgeneratorlocals(g)

        try:
            while True:
                str_out = next(g)
                g_vars = inspect.getgeneratorlocals(g)
        except StopIteration as ret:
            for k, v in list(ret.value.items()) + list(g_vars.get("__returned_dict__", {}).items()):
                if k in kwargs:
                    kwargs[k] = v
                    caller_frame_vars["kwargs"] = kwargs
                add_return_caller_frame_var(k, v)

            caller_frame_vars["used_args"] = g_vars.get("used_args", set()) | used_args

        return str_out
    wrapper.__wrapped__ = gen
    return wrapper