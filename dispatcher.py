"""
Author: IO-02 Babich Valerii
"""

from ast import*  

from .dbg import dbg
from .memory_manager import MemoryManager
from .instruction_pipeline import InstructionPipeline

from handlers import Handler

"""Create new AST"""
class Dispatcher():

    def __init__(self):

        self.instrWriter = InstructionPipeline()
        self.mem = MemoryManager(self.instrWriter)

        self.handler = Handler(self, self.mem, self.instrWriter)

    def dispatch(self, ast):
        dbg.log("Dispatching :", ast)
        operations = {
            Module      : self.handler.doModule,
            Stmt        : self.handler.doStmt,
            Printnl     : self.handler.doPrintnl,
            CallFunc    : self.handler.doCallFunc,
            Assign      : self.handler.doAssign,
            Discard     : self.handler.doDiscard,
            Const       : self.handler.doConst,
            Name        : self.handler.doName,
            Add         : self.handler.doAdd,
            UnarySub    : self.handler.doUnarySub,
            List        : self.handler.doList,
            Or          : self.handler.doOr,
            And         : self.handler.doAnd,
            Compare     : self.handler.doCompare,
            Not         : self.handler.doNot,
            Dict        : self.handler.doDict,
            Subscript   : self.handler.doSubscript,
            IfExp       : self.handler.doIfExp,
        }

        return operations[ast.__class__](ast)

    def dispatch_many(self, ast):
        return [self.dispatch(child) for child in ast.nodes]

    def write_out(self, filename=None):
        self.mem.liveness()
        return self.instrWriter.export(fname=filename)
