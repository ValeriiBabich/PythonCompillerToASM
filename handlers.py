"""
Author: IO-02 Babich Valerii
"""


"""Handlers description"""
from .x86 import *
from .helpers import LabelManager, CONST
from ast import Subscript

class Handler():
    def __init__(self, dispatcher, mem, instrWriter):
        self.mem = mem
        self.instrWriter = instrWriter
        self.dispatcher = dispatcher

    def doAdd(self, ast):
        label_type = LabelManager.newLabel("type_set_same")
        label_list = LabelManager.newLabel("list_addition")
        label_end = LabelManager.newLabel("end_addition")

        left = self.dispatcher.dispatch(ast.left)
        right = self.dispatcher.dispatch(ast.right)
        
        jump_type = OpJumpOnSame(self.mem, left, right, label_type)
        self.instrWriter.write(jump_type)

        self.instrWriter.write(OpLabel(label_type))

        jump_list = OpJumpOnTag(self.mem, left, label_list, 'big', isTag=True)
        self.instrWriter.write(jump_list)

        op_add = OpAdd(self.mem, left, right, is_int=True)
        self.instrWriter.write(op_add)
        self.instrWriter.write(OpJump(label_end))

        self.instrWriter.write(OpLabel(label_list))

        op = OpAdd(self.mem, left, right,
                is_int=False, output_key=op_add.output_key)
        self.instrWriter.write(op)

        self.instrWriter.write(OpLabel(label_end))

        return op_add.output_key
        
    def doModule(self, ast):
        op = OpModule(self.mem)
        self.instrWriter.write(op)
        _ = self.dispatcher.dispatch(ast.node)
        return None

    def doStmt(self, ast):
        op = OpStmt(self.mem)
        self.instrWriter.write(op)
        _ = self.dispatcher.dispatch_many(ast)
        ret = OpReturn(self.mem)
        self.mem.finalize()
        self.instrWriter.write(ret)
        return None

    def doPrintnl(self, ast):
        items = self.dispatcher.dispatch_many(ast)
        for node in items:
            op = OpPrintnl(self.mem, node)
            self.instrWriter.write(op)
        return None
    
    def doCallFunc(self, ast):
        name = self.dispatcher.dispatch(ast.node)
        op = OpCallFunc(self.mem, name)
        self.instrWriter.write(op)
        return op.output_key
                    
    def doAssign(self, ast):
        names, value_ref = ast.nodes, self.dispatcher.dispatch(ast.expr)
        for name in names:
            if isinstance(name, Subscript):
                pyobj = self.dispatcher.dispatch(name.expr)
                key = self.dispatcher.dispatch(name.subs[0])
                op = OpSetSubscript(self.mem, pyobj, key, value_ref)

            else:
                op = OpAssign(self.mem, name.name, value_ref)
            self.instrWriter.write(op)
        return None

    def doDiscard(self, ast):
        _ = self.dispatcher.dispatch(ast.expr)
        return None

    def doConst(self, ast):
        op = OpNewConst(self.mem, ast.value)
        self.instrWriter.write(op)
        return op.output_key

    def doName(self, ast):
        if ast.name == "True":
            op = OpNewConst(self.mem, 1, tag='BOOL')
            self.instrWriter.write(op)
            return op.output_key
        elif ast.name == "False":
            op = OpNewConst(self.mem, 0, tag='BOOL')
            self.instrWriter.write(op)
            return op.output_key

        return self.mem.getReference(ast.name)

    def doUnarySub(self, ast):
        node = self.dispatcher.dispatch(ast.expr)
        op = OpUnarySub(self.mem, node)
        self.instrWriter.write(op)
        return op.output_key

    def doList(self, ast):
        nodes = [self.dispatcher.dispatch(item) for item in ast.nodes]
        op = OpList(self.mem, nodes)
        self.instrWriter.write(op)
        return op.output_key 
    
    def doDict(self, ast):
        nodes = [(self.dispatcher.dispatch(item[0]),
            self.dispatcher.dispatch(item[1])) for item in ast.items]

        op = OpDict(self.mem, nodes)
        self.instrWriter.write(op)
        return op.output_key

    def doOr(self, ast):
        label_true = LabelManager.newLabel("or_set_true")
        label_end = LabelManager.newLabel("end")

        left = self.dispatcher.dispatch(ast.nodes[0])

        jump_true = OpJumpOnBool(self.mem, left, label_true, boolean=True)
        self.instrWriter.write(jump_true)

        right = self.dispatcher.dispatch(ast.nodes[1])

        op = OpBoolSetCondition(self.mem,
                left, right,
                label_true, label_end)

        self.instrWriter.write(op)

        return op.output_key

    
    def doAnd(self, ast):
        label_false = LabelManager.newLabel("and_set_false")
        label_end = LabelManager.newLabel("and_end")

        left = self.dispatcher.dispatch(ast.nodes[0])

        jump_false = OpJumpOnBool(self.mem, left, label_false, boolean=False)
        self.instrWriter.write(jump_false)

        right = self.dispatcher.dispatch(ast.nodes[1])

        op = OpBoolSetCondition(self.mem,
                left, right,
                label_false, label_end)
        self.instrWriter.write(op)

        return op.output_key

    def doCompare(self, ast):
        left = self.dispatcher.dispatch(ast.expr)
        ops = ast.ops[0]
        val = self.dispatcher.dispatch(ops[1])

        if ops[0] == 'is':
            op = OpIs(self.mem, left, val)
        elif ops[0] == '==' or ops[0] == "!=":
            shouldInvert = '!' in ops[0]

            dobig_label = LabelManager.newLabel('op_eq_bothbig')
            false_label = LabelManager.newLabel('op_eq_false')
            true_label = LabelManager.newLabel('op_eq_true')
            end_label = LabelManager.newLabel('op_eq_end')
            
            left_big = OpJumpOnTag(self.mem, left, dobig_label, 'BIG')
            self.instrWriter.write(left_big)

            right_big = OpJumpOnTag(self.mem, val, false_label, 'BIG')
            self.instrWriter.write(right_big)

            op = OpPrimEquals(self.mem, left, val, invert=shouldInvert)
            self.instrWriter.write(op)
            self.instrWriter.write(OpJump(end_label))

            self.instrWriter.write(OpLabel(dobig_label))

            both_objs = OpJumpOnTag(self.mem, val, false_label, 'BIG', isTag=False)
            self.instrWriter.write(both_objs)

            op2 = OpBigEquals(self.mem, left, val, invert=shouldInvert, output_key=op.output_key)
            self.instrWriter.write(op2)
            self.instrWriter.write(OpJump(end_label))

            self.instrWriter.write(OpLabel(false_label))
            opFalse = OpDirectAssign(self.mem, op.output_key, CONST(shouldInvert, tag="BOOL"))
            self.instrWriter.write(opFalse)

            self.instrWriter.write(OpJump(end_label))

            self.instrWriter.write(OpLabel(true_label))
            opTrue = OpDirectAssign(self.mem, op.output_key, CONST(not shouldInvert, tag="BOOL"))
            self.instrWriter.write(opTrue)

            self.instrWriter.write(OpLabel(end_label))

            return op.output_key
            pass
        elif ops[0] == '!=':
            pass

        self.instrWriter.write(op)
        return op.output_key


    def doNot(self, ast):
        node = self.dispatcher.dispatch(ast.expr)

        op = OpNot(self.mem, node)
        self.instrWriter.write(op)

        return op.output_key

    def doSubscript(self, ast):
        key, pyobj = self.dispatcher.dispatch(ast.subs[0]), self.dispatcher.dispatch(ast.expr)

        op = OpSubscript(self.mem, pyobj, key)
        self.instrWriter.write(op)

        return op.output_key

    def doIfExp(self, ast):
        test = self.dispatcher.dispatch(ast.test)
        then = LabelManager.newLabel('ifexp_then')
        end = LabelManager.newLabel('ifexp_end')

        op = OpIfExpr(self.mem, test)
        self.instrWriter.write(op)
        out_var = op.output_key

        branch = OpJumpOnBool(self.mem, test, then)
        self.instrWriter.write(branch)

        val1 = self.dispatcher.dispatch(ast.else_)
        copy1 = OpDirectAssign(self.mem, out_var, val1, value_is_const=False)
        self.instrWriter.write(copy1)

        self.instrWriter.write(OpJump(end))

        self.instrWriter.write(OpLabel(then))
        val2 = self.dispatcher.dispatch(ast.then)
        copy2 = OpDirectAssign(self.mem, out_var, val2, value_is_const=False)
        self.instrWriter.write(copy2)

        self.instrWriter.write(OpLabel(end))

        return out_var
