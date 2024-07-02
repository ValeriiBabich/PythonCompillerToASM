"""
Author: IO-02 Babich Valerii
"""

"""Manage memmory addresses & registers"""


from .dbg import dbg
from .memory import OpMovl, OpStackAllocate, OpStackDeallocate, OpNoop
from .variable_identifier import AnonymousIdentifier, NamedIdentifier, PassThroughIdentifier
import itertools
from .allocation_identifier import RegisterAllocation, StackAllocation

class MemoryManager:
    def __init__(self, instrWriter):
        self.registers = ['ebx', 'ecx', 'edx']
        self.allocations = {}
        self.named_vars = {}
        self.anon_vars = []
        self.instrWriter = instrWriter
        self.stack_alloc = OpStackAllocate(0)
        self.builtins = ['input']

        for builtin in self.builtins:
            bvar = PassThroughIdentifier(builtin)
            self.named_vars[builtin] = bvar
            self.allocations[bvar] = 'input'


    def getStackAllocation(self):
        return self.stack_alloc
       
    def get(self, key):
        dbg.log("Retrieving:", key)
        try:
            return self.allocations[key]
        except KeyError, e:
            print(self.allocations)
            print("Failed get key: %s" % str(key))
            print(key.printAllocation())
            raise e

    def allocate(self, name=None, spillable=True):
        if name == None:
            newVar = AnonymousIdentifier(spillable=spillable)
            self.anon_vars.append(newVar)
        else:
            if name in self.named_vars:
                return self.named_vars[name]
            newVar = NamedIdentifier(name, spillable=spillable)
            self.named_vars[name] = newVar

        return newVar

    def doLoad(self, left, right):
        if left != right:
            load = OpMovl(left, right)
        else:
            load = OpNoop()

        return load

    def finalize(self):
        op = OpStackDeallocate(self.stack_alloc.size)
        self.instrWriter.write(op)

    def getReference(self, name):
        return self.named_vars[name]

    def getAccesses(self):
        memoryAccesses = []
        for instr in self.instrWriter.instructions:
            memoryAccesses += instr.get_memory_operands()
        return memoryAccesses

    def liveness(self):
        def is_alive(tmp, rest_of_accesses):
            for reads, writes in rest_of_accesses:
                if tmp in reads:
                    return True
                elif tmp in writes:
                    return False
            return False
        
        liveness = []
        currentVars = []
        memoryAccesses = self.getAccesses()
        for idx, (_, writes) in enumerate(memoryAccesses):
            candidates = writes + currentVars
            currentVars = []
            for term in candidates:
                if is_alive(term, memoryAccesses[idx+1:]):
                    currentVars.append(term)

            liveness.append(currentVars)
        edges = {alloc:[] for alloc in self.named_vars.values() + self.anon_vars if alloc.shouldAllocate()}
        for iteration in liveness:
            perms = itertools.permutations(iteration, 2)
            for (l, r) in perms:
                if l not in edges:
                    edges[l] = []
                if r not in edges[l]:
                    edges[l].append(r)

        c = DSATUR(edges, len(self.registers))
        c.run()
        allocs = c.getColor()
        for alloc_var in allocs:
            color_id = allocs[alloc_var]
            if color_id < len(self.registers):
                self.allocations[alloc_var] = RegisterAllocation(self.registers[color_id])
            else:
                self.stack_alloc.size += 4
                self.allocations[alloc_var] = StackAllocation(self.stack_alloc.size)
