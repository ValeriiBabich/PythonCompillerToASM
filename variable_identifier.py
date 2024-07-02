"""
Author: IO-02 Babich Valerii
"""


"""Identify variables as such ways: abstract, anonymous"""
import inspect

class AbstractIdentifier(object):
    def __init__(self, spillable=True):
        self.allocated_at = inspect.stack()
        self.allocated_at.reverse()
        self.anonId = AnonymousIdentifier.ANON_ID
        self.spillable = spillable

    def setSpillable(self, canSpill):
        self.spillable = canSpill

    def canSpill(self):
        return self.spillable

    def shouldAllocate(self):
        return True

    def printAllocation(self):
        for frame in self.allocated_at:
            code = "\n".join([line.strip() for line in frame[4]])
            print('File "{fname}", line {line}, in {module}\n\t{code}'.format(
                    fname=frame[1],
                    line=frame[2],
                    module=frame[3],
                    code=code))

class AnonymousIdentifier(AbstractIdentifier):
    ANON_ID = 0
    def __init__(self, **kwargs):
        super(AnonymousIdentifier, self).__init__(**kwargs)
        AnonymousIdentifier.ANON_ID += 1

    def __repr__(self):
        return "<AnonVariable_{num}>".format(num=self.anonId)

class NamedIdentifier(AbstractIdentifier):
    def __init__(self, name, **kwargs):
        super(NamedIdentifier, self).__init__(**kwargs)
        self.name = name

    def __repr__(self):
        return "<NamedVariable_[{name}]>".format(name=self.name)

class PassThroughIdentifier(AbstractIdentifier):
    def __init__(self, name, **kwargs):
        super(PassThroughIdentifier, self).__init__(**kwargs)
        self.name = name

    def __repr__(self):
        return "<PassThroughVariable_[{name}]>".format(name=self.name)
    
    def shouldAllocate(self):
        return False
