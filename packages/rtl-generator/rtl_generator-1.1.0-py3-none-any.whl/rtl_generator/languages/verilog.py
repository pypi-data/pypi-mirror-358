import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Self

from . import Language


@dataclass
class Verilog(Language):
    extensions: List[str] = field(default_factory=lambda: [".v", ".sv"])
    instantiation_regex: re.Pattern = re.compile(
        r"(?P<module_declaration>module)?\s*(?P<module_name>\w+)\s*#\s*\((?P<params>.*?)\)\s*(?P<instance_name>\w*)\s*\((?P<ports>.*?)\);",
        re.MULTILINE | re.DOTALL
    )

    def __post_init__(self) -> Self:
        self.VERIBLE_FORMAT_PATH = subprocess.run(['which', 'verible-verilog-format'], capture_output=True).stdout.decode().strip()
        assert self.VERIBLE_FORMAT_PATH, "Verible not found in PATH"
        return super().__post_init__()
    
    def format_rtl(self, rtl_code):
        return subprocess.run([
            self.VERIBLE_FORMAT_PATH,
            "-"
        ], input=rtl_code.encode(), capture_output=True).stdout.decode()

    def single_line_comment(self, in_regex: bool=False):
        return super().single_line_comment(in_regex)
    
    def multi_line_comment_start(self, in_regex: bool=False):
        return super().multi_line_comment_start(in_regex)
    
    def multi_line_comment_end(self, in_regex: bool=False):
        return super().multi_line_comment_end(in_regex)

    def include_submodule(self, submod: Optional[Path | str]=None, in_regex = False):
        assert submod or in_regex, "Either submod must be provided or in_regex must be True"
        return f"`include \"{str(submod)}\"" if not in_regex else r"`include \"(\S+?)\""

    def find_module_declaration(self, rtl_code):
        return super().find_module_declaration(rtl_code)
    
    def find_instantiated_submodules(self, rtl_code: str):
        return super().find_instantiated_submodules(rtl_code)