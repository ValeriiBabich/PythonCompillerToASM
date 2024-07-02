"""
Author: IO-02 Babich Valerii
"""


"""ASM structure"""
def CONST(val, tag=None):
    tag_value = 0
    if tag == None:
        return "$" + str(val)
    elif tag == "INT":
        tag_value = 0
    elif tag == "BOOL":
        tag_value = 1
    elif tag == "FLOAT":
        tag_value = 2
    elif tag == "BIG":
        tag_value = 3
        
    return "$" + str( (val << 2) | tag_value )

def call_func_asm(funcname, arguments=None, output=None):
    if arguments == None:
        arguments = []
    if output != None:
        write_output = "movl %eax, {output}\n".format(output=output)
    else:
        write_output = ""

    assert isinstance(arguments, list), "Arguments must be lists, not " + str(type(arguments))

    arguments.reverse()

    argtext = "\n".join(['pushl ' + str(arg) for arg in arguments or []])
    popargs = "addl ${num}, %esp".format(num=len(arguments)*4)

    return """
    pushl %ebx 
    pushl %ecx
    pushl %edx
    {argtext}
    call {funcname}
    {popargs}
    popl %edx 
    popl %ecx
    popl %ebx
    {write_output}
    """.format(
            funcname=funcname,
            argtext=argtext,
            popargs=popargs,
            write_output=write_output
            )

class __LabelManager__(object):
    def __init__(self):
        self.labels = {}

    def newLabel(self, name):
        if name not in self.labels:
            self.labels[name] = 0

        next_label = name + "_" + str(self.labels[name])
        self.labels[name] += 1

        return next_label

LabelManager = __LabelManager__()
