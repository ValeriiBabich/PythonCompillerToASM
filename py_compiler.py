"""
Author: IO-02 Babich Valerii
"""


"""Main compiller function"""
from .dispatcher import Dispatcher
from .dbg import dbg
import compiler as native_parser

class Compiler():
    def __init__(self, parser=native_parser):
        self.dispatcher = Dispatcher()
        self.parser = parser

    def compile(self, source_code, filename=None):
        
        syntax_tree = self.parser.parse(source_code)

        dbg.log("Parsed AST:", syntax_tree)

        self.dispatcher.dispatch(syntax_tree)

        self.dispatcher.write_out(filename=filename)

    def compileFile(self, filename):
        if filename.endswith(".py"):
            filename = filename[:-3]

        py_infile = filename + ".py"
        asm_outfile = filename + '.asm'

        with open(py_infile, 'r') as in_file:
            code = in_file.read()

        self.compile(code, filename=asm_outfile)
