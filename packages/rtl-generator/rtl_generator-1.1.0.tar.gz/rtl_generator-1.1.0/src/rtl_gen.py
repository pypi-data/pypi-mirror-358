import argparse
import os
import subprocess
import sys
from importlib import import_module
from pathlib import Path
from dataclasses import dataclass

from rtl_generator import (add_args, fill_in_template, get_pretty_name,
                           get_subdirs, replace_included, rtl_generator, LANGUAGES)


def run_generator(rtl_name: str, cli_args: argparse.Namespace, mod_str: str="", **kwargs) -> str:
    """
    Run the RTL generator for a given module
    """
    if not mod_str:
        mod_str = f"gen_{rtl_name}"
    import_module(mod_str)
    calling_module = sys.modules[mod_str]
    mod_vars = vars(calling_module)
    
    # try:
    #     import_module(mod_str)
    #     calling_module = sys.modules[mod_str]
    #     mod_vars = vars(calling_module)
    # except ImportError:
    #     warnings.warn(f"Failed to import module {mod_str}", ImportWarning)
    #     mod_vars = {}
        
    return rtl_generator(rtl_name, **vars(cli_args), **mod_vars, **kwargs)


@dataclass
class setup:
    """
    Set up the RTL generation environment.

    Script entry
    """
    cli_args: argparse.Namespace

    def __call__(self, rtl_name: str, proj_path: str | Path) -> None:
        options_yml_path  = Path(__file__).parent / "options.yml"
        top_level_py_path = Path(__file__).parent / "top_level.py"

        proj_options_yml_path = Path(proj_path) / "options.yml"
        proj_top_level_py_path = Path(proj_path) / f"gen_{rtl_name}.py"

        if proj_options_yml_path.exists() and proj_top_level_py_path.exists():
            print("RTL Generator environment already exists")
            return
        
        top_level_name = get_pretty_name(rtl_name)
        print(f"Setting up RTL Generator environment for project: {top_level_name}")
        if not proj_options_yml_path.exists():
            subprocess.run(["cp", str(options_yml_path), str(proj_path)])

        if not proj_top_level_py_path.exists():
            with open(top_level_py_path) as f:
                top_level_py = f.read()

            top_level_py = fill_in_template(top_level_py, **vars())
            with open(proj_top_level_py_path, "w") as f:
                f.write(top_level_py)
        
        update(self.cli_args)(rtl_name, proj_path)

        print(f"\nFinished setting up RTL Generator environment for project: {top_level_name}")
        print('-' * os.get_terminal_size().columns)

    @staticmethod
    def add_args(rtl_name: str, proj_path: str | Path, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        return parser


@dataclass
class update:
    """
    Update the generation scripts in the hierarchy

    Script entry
    """
    cli_args: argparse.Namespace

    def __call__(self, rtl_name: str, proj_path: str | Path) -> None:
        print(f"Updating generators in RTL heirarchy for: {get_pretty_name(rtl_name)}")

        for submod in get_subdirs(proj_path):
            os.chdir(submod)
            submod_name = submod.name
            sub_level_name = get_pretty_name(submod_name)

            gen_path = Path(submod, f"gen_{submod_name}.py")
            if not gen_path.exists():
                with open(Path(Path(__file__).parent, "sub_level.py")) as f:
                    sub_level_py = f.read()
                sub_level_py = fill_in_template(sub_level_py, **vars())
                with open(gen_path, "w") as f:
                    f.write(sub_level_py)

            self(submod_name, submod)

            os.chdir(proj_path)

        print(f"\nFinished updating generators in RTL heirarchy for: {get_pretty_name(rtl_name)}")
        print('-' * os.get_terminal_size().columns)

    @staticmethod
    def add_args(rtl_name: str, proj_path: str | Path, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        return parser


@dataclass
class generate:
    """
    Generate RTL

    Script entry
    """
    cli_args: argparse.Namespace

    def __call__(self, rtl_name: str, proj_path: str | Path) -> None:
        print(f"Generating RTL for project: {get_pretty_name(rtl_name)}")

        rtl_ext = Path(getattr(self.cli_args, f"{rtl_name}_input")).suffix.lower()
        assert rtl_ext in LANGUAGES, f"Unsupported RTL file extension: {rtl_ext}. Supported extensions: {', '.join(LANGUAGES.keys())}"
        lang = LANGUAGES[rtl_ext]

        generated_rtl = run_generator(rtl_name, self.cli_args, lang=lang)
        
        submod_rtls = {}
        available_submods = get_subdirs(proj_path)
        while available_submods:
            submod_path = available_submods.pop()
            # os.chdir(submod_path)

            name = submod_path.name
            rel_path = submod_path.relative_to(proj_path)
            mod_str = ".".join((*rel_path.parts, f"gen_{name}"))

            submod_rtls[name] = run_generator(name, self.cli_args, mod_str=mod_str, lang=lang)

            available_submods.extend(get_subdirs(submod_path))
            # os.chdir(proj_path)

        if getattr(self.cli_args, "replace_includes", False):
            submod_rtls = {rtl_name: replace_included(generated_rtl, submod_rtls, lang)}
        else:
            submod_rtls[rtl_name] = generated_rtl

        print(f"\n{'-' * os.get_terminal_size().columns}\nWriting RTL to files...\n")
        for rtl_name, rtl in submod_rtls.items():
            output_file = getattr(self.cli_args, f"{rtl_name}_output")
            with open(output_file, "w") as f:
                f.write(rtl)
                print(f"Generated RTL for {rtl_name} saved to {f.name}")

        print(f"\nFinished generating RTL for project: {get_pretty_name(rtl_name)}")
        print('-' * os.get_terminal_size().columns)

    @staticmethod
    def add_args(rtl_name: str, proj_path: str | Path, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        return add_args(rtl_name, proj_path, parser)


def main() -> None:
    """
    Main entry point for the script. Creates CLI and calls the function requested by first argument.
    """
    proj_path = Path(os.getcwd())
    if proj_path not in sys.path:
        sys.path.append(str(proj_path))

    rtl_name = proj_path.name

    # Create CLI
    parser = argparse.ArgumentParser(description=f"RTL Generator")
    subparsers = parser.add_subparsers(title="Commands")
    if f := globals().get(sys.argv[1], None):
        if callable(f) and getattr(f, "__doc__", "").strip().endswith("Script entry"):
            command_name = f.__name__
            help_str = "\n".join(filter(None, f.__doc__.strip().splitlines()[:-1]))
            subparser = subparsers.add_parser(command_name, description=f"{command_name}: {help_str}")
            f.add_args(rtl_name, proj_path, subparser)
            subparser.set_defaults(func=f)

    # Parse arguments and run function
    args = parser.parse_args()
    func = args.func(args)
    func(rtl_name, proj_path)


if __name__ == "__main__":
    main()
