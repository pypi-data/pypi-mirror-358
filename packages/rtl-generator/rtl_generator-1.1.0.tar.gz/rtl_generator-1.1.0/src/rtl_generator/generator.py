"""
Handle RTL generation
"""
# Necessary imports, path setup, and global variables
import inspect
import os
import re
from itertools import product
from pathlib import Path
from typing import Dict, Generator, Optional
from functools import reduce

import prettytable

from .context_manager import generator_context
from .format import get_pretty_name
from .header import add_headers, remove_headers
from .heirarchy import remove_previously_included
from .languages import Language

PRESERVING_REGEXES = [
    # These regexes preserve the parameter tag that identifies the parameter
    re.compile(r"//[^\n]*#{\((?P<parameter_name>\w*)\)}\s*(?P<replace>.*?)\s*//[^\n]*#{/\((?P=parameter_name)\)}", re.MULTILINE | re.DOTALL),
    re.compile(r"/\*[^\n]*#{\((?P<parameter_name>\w*)\)}[^\n]*\*/\s*(?P<replace>.*?)\s*/\*[^\n]*#{/\((?P=parameter_name)\)}[^\n]*\*/", re.MULTILINE | re.DOTALL),
]

DESTROYING_REGEXES = [
    # These regexes destroy the parameter tag that identifies the parameter
    re.compile(r"(?P<replace>#{\((?P<parameter_name>\w+?)\)})"),
]


#####################################################################################################
# Base methods needed for all RTL generators                                                        #
#####################################################################################################
def make_substitution(template: str, context: str, replace_str: str, replace_with: str) -> str:
    """
    Make a substitution in the context string.
    """
    replace_with = replace_with.strip()
    assert template
    if not context or not replace_str or not replace_with:
        return template
    
    replaced = context.replace(replace_str, replace_with)
    return template.replace(context, replaced)


@generator_context
def fill_in_template(template: str, used_args: set=set(), lang: Optional[Language]=None, **kwargs) -> Generator[str, None, Dict]:
    """
    Fill in the template with the arguments and variables.

    Looks for keys in the arguments, variables, and global functions, in that order.
    """
    performed_replacements = set()
    preserving = True
    for match_regexes in [lang.PRESERVING_REGEXES if lang else PRESERVING_REGEXES] + [lang.DESTROYING_REGEXES if lang else DESTROYING_REGEXES]:
        search_start_ix = 0
        while key_matches := list(filter(None, map(lambda m: m.search(template, pos=search_start_ix), match_regexes))):
            key_match = min(key_matches, key=lambda m: m.start())
            context = key_match.group()
            parameter_name = key_match.group("parameter_name")
            replace_str = key_match.group("replace")

            if parameter_name in performed_replacements:
                search_start_ix = key_match.end("parameter_name")
                continue
            
            used_args.add(parameter_name)
            performed_replacements.add(parameter_name)
            replace_with = None
            for ctx in (locals(), kwargs, globals()):
                if parameter_name in ctx:
                    p_res = ctx[parameter_name]

                    if callable(p_res):
                        # If the parameter is a function, call it with the current context
                        ignore_args = ["used_args", "lang", "kwargs"]
                        local_vars = vars()
                        func_args = dict(map(lambda k: (k, local_vars[k]), filter(lambda k: k not in ignore_args and k not in ctx and k in local_vars, inspect.signature(p_res).parameters)))
                        func_args.update(dict(filter(lambda e: e[0] not in ignore_args, ctx.items())))
                        func_args.update(dict(filter(lambda e: e[0] not in ignore_args, kwargs.items())))
                        replace_with = p_res(used_args=used_args, lang=lang, **func_args)
                    else:
                        # If the parameter is not a function, just use its value
                        replace_with = str(p_res)
                    break

            assert replace_with is not None, f"No way to fill template key: {parameter_name}"            
            template = make_substitution(template, context, replace_str, replace_with)
            
            if preserving:
                search_start_ix = key_match.end("parameter_name")
        
        preserving = not preserving

    yield template
    return_dict = vars().get("__returned_dict__", {})
    return_dict["used_args"] = used_args | return_dict.get("used_args", set())
    return return_dict


@generator_context
def param_table(context: str, replace_str: str, **kwargs) -> Generator[str, None, Dict]:
    """
    Include the used arguments param_table
    """
    yield ""
    return dict(
        param_table_ctx=context[:],
        param_table_replace_str=replace_str[:],
    )


@generator_context
def included_modules(context: str, replace_str: str, **kwargs) -> Generator[str, None, Dict]:
    """
    Include the list of included modules
    """
    yield ""
    return dict(
        included_modules_ctx=context[:],
        included_modules_replace_str=replace_str[:],
    )


def rtl_generator(rtl_name: str, lang: Optional[Language]=None, **kwargs) -> str:
    """
    Generate RTL code
    """
    print("\n" + "-" * os.get_terminal_size().columns)
    print(f"Generating RTL for module: {get_pretty_name(rtl_name)}")

    used_args = set()
    comment_start = lang.single_line_comment() if lang else "//"

    with open(kwargs[f"{rtl_name}_input"], "r", encoding='UTF-8') as f:
        template = remove_previously_included(f.read())
    
    template = remove_headers(template, lang=lang, **kwargs)
    template = add_headers(template, lang=lang, **kwargs)
    generated = fill_in_template(template, lang=lang, used_args=used_args, **kwargs)
    returned_dict = vars().get("__returned_dict__", {})

    if included_modules_ctx := returned_dict.get('included_modules_ctx', None):
        included_modules_replace_str = returned_dict['included_modules_replace_str']
        included_submodules = list(filter(lambda k: f"{k}_output" in kwargs, lang.find_instantiated_submodules(generated) if lang else []))
        if included_submodules:
            included_modules_str = f"{comment_start}! ## Included modules:\n"
            subdirs = dict(map(lambda k: (k, Path(*Path(kwargs.get(f"{k}_output")).parts[-2:])), included_submodules))
            included_modules_str += '\n'.join(map(lambda m: f"{lang.include_submodule(subdirs[m])}\t{comment_start}! - [{get_pretty_name(m)}]({subdirs[m].with_suffix('.md')})", included_submodules))
            included_modules_str += "\n"
        else:
            included_modules_str = f"{comment_start} INCLUDED MODULES GO HERE"

        generated = make_substitution(generated, included_modules_ctx, included_modules_replace_str, included_modules_str)

    arg_table = prettytable.PrettyTable()
    arg_table.field_names = ["Argument", "Value"]
    for arg, value in sorted(map(lambda a: (a, kwargs[a]), filter(lambda a: a in kwargs and not callable(kwargs[a]), used_args))):
        arg_table.add_row([arg, value])

    arg_table.set_style(prettytable.MARKDOWN)
    if param_table_ctx := returned_dict.get('param_table_ctx', None):
        param_table_replace_str = returned_dict['param_table_replace_str']
        if len(arg_table.rows):
            param_table_str = f"{comment_start}! ## Generator arguments:\n"
            param_table_str += '\n'.join(map(lambda l: f"{comment_start}! {l}", arg_table.get_string().splitlines()))
        else:
            param_table_str = f"{comment_start} PARAMETER TABLE GOGES HERE"

        generated = make_substitution(generated, param_table_ctx, param_table_replace_str, param_table_str)

    arg_table.add_row([f"{rtl_name}_output", kwargs[f"{rtl_name}_output"]])
    arg_table.set_style(prettytable.DOUBLE_BORDER)
    print("\nArguments:")
    print(arg_table.get_string())
    print(f"\nFinished generating RTL for module: {get_pretty_name(rtl_name)}")

    return lang.format_rtl(generated)
