import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Self, Optional
import os
from pathlib import Path
import importlib
import sys


PRESERVING_REGEXES = [
    # These regexes preserve the parameter tag that identifies the parameter
    r"single_line_comment[^\n]*#{\((?P<parameter_name>\w*)\)}\s*(?P<replace>.*?)\s*single_line_comment[^\n]*#{\/\((?P=parameter_name)\)}",
    r"multi_line_comment_start[^\n]*#{\((?P<parameter_name>\w*)\)}[^\n]*multi_line_comment_end\s*(?P<replace>.*?)\s*multi_line_comment_start[^\n]*#{\/\((?P=parameter_name)\)}[^\n]*multi_line_comment_end",
]

DESTROYING_REGEXES = [
    # These regexes destroy the parameter tag that identifies the parameter
    r"(?P<replace>#{\((?P<parameter_name>\w+?)\)})",
]


@dataclass
class Language(ABC):
    extensions: List[str] = field(default_factory=list)
    instantiation_regex: re.Pattern = field(init=False)
    PRESERVING_REGEXES: List[re.Pattern] = field(default_factory=list)
    DESTROYING_REGEXES: List[re.Pattern] = field(default_factory=list)

    def __post_init__(self) -> Self:
        callable_funcs = list(filter(lambda f: callable(getattr(self, f, None)), dir(self)))
        callable_regex = re.compile("|".join(map(lambda f: f"({re.escape(f)})", callable_funcs)), re.MULTILINE | re.DOTALL)
        for pres_re in PRESERVING_REGEXES:
            while m := callable_regex.search(pres_re):
                func_name = m.group()
                f = getattr(self, func_name)
                pres_re = pres_re.replace(func_name, f(in_regex=True))

            self.PRESERVING_REGEXES.append(re.compile(pres_re, re.MULTILINE | re.DOTALL))

        for dest_re in DESTROYING_REGEXES:
            while m := callable_regex.search(dest_re):
                func_name = m.group()
                f = getattr(self, func_name)
                dest_re = dest_re.replace(func_name, f(in_regex=True))

            self.DESTROYING_REGEXES.append(re.compile(dest_re, re.MULTILINE | re.DOTALL))

        self.extensions = [ext if ext.startswith('.') else f".{ext}" for ext in self.extensions]
        return self
    
    @abstractmethod
    def format_rtl(self, rtl_code: str) -> str:
        """
        Format the generated RTL code to be more readable
        """
        pass
    
    @abstractmethod
    def single_line_comment(self, in_regex: bool=False) -> str:
        """ Returns string that indicates or regular expression that matches the start of a single-line comment """
        return "//" if not in_regex else "\/\/"

    @abstractmethod
    def multi_line_comment_start(self, in_regex: bool=False) -> str:
        """ Returns string that indicates or regular expression that matches the start of a multi-line comment """
        return "/*" if not in_regex else "\/\*"

    @abstractmethod
    def multi_line_comment_end(self, in_regex: bool=False) -> str:
        """ Returns string that indicates or regular expression that matches the end of a multi-line comment """
        return "*/" if not in_regex else "\*\/"

    @abstractmethod
    def include_submodule(self, submod: Optional[Path | str]=None, in_regex: bool=False) -> str:
        """ Returns string that indicates or regular expression that matches including a submodule"""
        pass

    @abstractmethod
    def find_module_declaration(self, rtl_code: str) -> Optional[re.Match]:
        """
        Return a match object for the module declaration in the given RTL code.
        If no module declaration is found, return None.
        """
        return next(self.instantiation_regex.finditer(rtl_code), None)

    @abstractmethod
    def find_instantiated_submodules(self, rtl_code: str) -> List[str]:
        """
        Return a list of submodule names included in the given RTL.
        """
        return list(map(lambda m: m.group("module_name"), filter(lambda m: not m.group("module_declaration"), self.instantiation_regex.finditer(rtl_code))))


LANGUAGES = {}
__all__ = ["LANGUAGES"]

for f in filter(lambda f: f.endswith(".py") and not f.startswith("__"), os.listdir(Path(__file__).parent)):
    filename = f.removesuffix(".py")
    class_name = "".join(map(lambda s: s.title(), filename.split("_")))
    modname = f"rtl_generator.languages.{filename}"
    importlib.import_module(modname)

    if class_attr := getattr(sys.modules[modname], class_name, None):
        if issubclass(class_attr, Language):
            __all__.append(class_name)
            class_obj = class_attr()
            vars()[class_name] = class_obj
            for ext in class_obj.extensions:
                LANGUAGES[ext] = class_obj
        
    del modname