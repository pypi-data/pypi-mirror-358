from pysat.formula import Atom
from pyqbf.formula import to_pcnf, OUTERMOST_BLOCK
from pyqbf.solvers import solve
import itertools


# In this example, we will check the output of a 2-bit full adder
# First, encode it using Atoms
#  s0        s1    c
#  |          |    |
#------    ------  |
#| HA |----| FA |--
#------ c0 ------
# |  |      |  |
# a0 a1     b0 b1



# define inputs
a0, a1, b0, b1 = Atom("a0"), Atom("a1"), Atom("b0"), Atom("b1")

s0 = a0 ^ a1    #s0 = a xor b
c0 = a0 & a1  

s1 = c0 ^ b0 ^ b1 
c = (c0 & (b0 ^ b1)) | (b0 & b1)

# encode all possibilities
access = [a0, a1, b0, b1]
out = (Atom("s0") @ s0) & (Atom("s1") @ s1) & (Atom("c") @ c)   #manually tseitin encode

print("==========Circuit encoding==========")
print(out)

s0 = Atom("s0")
s1 = Atom("s1")
c = Atom("c")

print("==========Assignments==========")
for assignment in itertools.product([True, False], repeat=4):
    cnt = sum(1 if idx < 2 else 2 for idx, x in enumerate(assignment) if x)    #count of the bits (second position is 2)
    case = None
    for idx, value in enumerate(assignment):
        node = access[idx] if value else ~access[idx]
        if case is None:
            case = node
        else:
            case &= node
    
    res = s0 if cnt & 1 else ~s0
    res &= s1 if cnt & 2  else ~s1
    res &= c if cnt & 4 else ~c

    print(case >> res)

    out &= case >> res

pcnf = to_pcnf(out)
pcnf.forall(a0.name, a1.name, b0.name, b1.name, block=OUTERMOST_BLOCK)  #universially quantify input variables

print("==========Result==========")
print("Solver resulted in", solve(pcnf), "(expected True)")