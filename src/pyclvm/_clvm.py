#!/usr/bin/env python3

"""
Command Line Utility to connect or redirect ports to a Cloud Virtual Machine
"""


import os
import sys

from dynacli import main as dynamain

cwd = os.path.dirname(os.path.realpath(__file__))


search_path = [cwd]
sys.path.extend(search_path)

_map = {
    "__version__": "1.1.12a",
    "__doc__": """
Command Line Utility to connect or redirect ports to a Cloud Virtual Machine""",
}


def _set_main_attrs(**kwargs):
    _main = sys.modules["__main__"]
    for key, val in kwargs.items():
        setattr(_main, key, val)


# For package distro purposes
def main():
    _set_main_attrs(**_map)
    dynamain(search_path)


if __name__ == "__main__":
    main()
