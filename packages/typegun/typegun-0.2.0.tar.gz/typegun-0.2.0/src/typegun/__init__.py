#!/usr/bin/env python3

"""This is a fairly generic script to run typecheckers for you automatically.
It was initially made by Wyatt S Carpenter and carted around between projects.
The license of this file is public domain, in addition to any other licenses stuck on it."""

from os import system as s, name as os_name
from sys import argv

def pause() -> None:
    input("Press enter to exit...")

def h(string: str) -> None:
    """Print a header for a typechecker section"""
    print(f"---- {string.upper()}:")

def hs(header: str, system_command: str) -> int:
    """Print a header, then run a system command (returning its return code)."""
    h(header)
    return s(system_command)

def main() -> None:
    if "-h" in argv or "--help" in argv:
        print("Just run this script to check the types.")
        return 

    # One of these next two lines will work, depending on your operating system...
    if os_name == 'nt':
        s("set PYRIGHT_PYTHON_FORCE_VERSION=latest")
    else:
        s("export PYRIGHT_PYTHON_FORCE_VERSION=latest")

    hs("ruff", "uv run ruff check --no-cache")
    hs("pyright", "uv run pyright")
    h("mypy")
    #s("uv run mypy --install-types --non-interactive")
    s("uv run mypy . --strict --pretty --warn-unreachable --strict-bytes --enable-error-code explicit-override")
    h("pytype")
    s("uv run pytype .")
    print("---- fin")
    pause()

if __name__ == "__main__":
    main()