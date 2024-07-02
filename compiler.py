"""
Author: IO-02 Babich Valerii
"""

import sys, os

from .dbg import dbg

from .py_compiler import Compiler

if __name__ == '__main__':

    test_file = sys.argv[1]

    my_compiler = Compiler()

    my_compiler.compileFile(filename=test_file)

