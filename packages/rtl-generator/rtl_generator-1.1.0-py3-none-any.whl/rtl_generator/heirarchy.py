"""
Handle the RTL heirarchy
"""
import os
import re
from pathlib import Path
from typing import Dict, List

from .languages import Language
from .header import remove_headers
from .format import get_pretty_name


def replace_included(generated_rtl: str, submod_rtls: Dict[str, str], lang: Language, top_level: bool=True, **kwargs) -> str:
    """
    Recursively replaces include statements in the generated RTL code with the contents of the included file.

    If an included file exists in generated RTL, includes generated RTL for that file.
    Otherwise, includes the contents of the existing file.
    """
    generated_rtl = generated_rtl.strip()
    if top_level:
        generated_rtl += f"\n\n{lang.single_line_comment()}" + " #{(previously_included)}"
    first_time = top_level
    while include_match := re.search(lang.include_submodule(in_regex=True), generated_rtl):
        start, end = include_match.span()
        last_newline = generated_rtl.rfind('\n', 0, start)
        if last_newline < start:
            start = last_newline

        include_file = include_match.group(1)
        submod_name = str(Path(include_file).stem)

        generated_rtl = f"{generated_rtl[:start].strip()}\n{generated_rtl[end:].strip()}\n"
        if not first_time:
            generated_rtl += "\n"
        
        generated_rtl += f"{lang.single_line_comment()}! ## {get_pretty_name(submod_name)}:\n"
        include_rtl = replace_included(submod_rtls[submod_name], submod_rtls, lang, top_level=False, **kwargs)
        generated_rtl += remove_headers(include_rtl, lang=lang, **kwargs)
        first_time = False
        print(f"Included {submod_name}")

    if top_level:
        return generated_rtl.strip() + f"\n{lang.single_line_comment()}" + " #{/(previously_included)}\n"
    else:
        return generated_rtl.strip()


def remove_previously_included(rtl: str, **kwargs) -> str:
    """
    Remove the previously included submodules
    """
    previously_included_re = re.compile(r"\n[^\n]*?#{\(previously_included\)}[^\n]*\s*.*?\s*#{/\(previously_included\)}[^\n]*", re.MULTILINE | re.DOTALL)
    if m := previously_included_re.search(rtl):
        context = m.group()
        replaced = context.replace(context, "")
        rtl = rtl.replace(context, replaced)

    return rtl


def get_subdirs(module_path: str | Path) -> List[Path]:
    paths = []
    for d in filter(lambda d: Path(module_path, d).is_dir(), os.listdir(module_path)):
        if d in ['sim_build', 'models']:
            continue
        if re.search(r"__$", d) or re.search(r"^\.", d):
            continue

        paths.append(Path(module_path, d))

    return paths
