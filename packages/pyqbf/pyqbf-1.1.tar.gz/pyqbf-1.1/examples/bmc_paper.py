from pysat.formula import Atom
from pyqbf.formula import to_pcnf, OUTERMOST_BLOCK
from pyqbf.solvers import solve, Solver

# The BMC problem as described in the paper. This is the same as "bmc.py" just in a more compact form and simplified transition function

from pysat.formula import Atom
from pyqbf.formula import to_pcnf
from pyqbf.solvers import solve

p0 = Atom("s0"); q0 = Atom("q0"); p1 = Atom("p1"); q1 = Atom("q1")
px = Atom("px"); qx = Atom("qx"); px1 = Atom("px1"); qx1 = Atom("qx1")

# p0 <=> px, p1 <=> px1, ...
bind = (p0 @ px) & (q0 @ qx) & (p1 @ px1) & (q1 @ qx1)	  
# transition
t = (((px1 @ (~px & ~qx)) & (~qx1)) | ((px1 @ (px & ~qx)) & (qx1 @ ~qx)))

formula = (~p0) & (~q0) & (p1) & (q1) & (bind >> t) 

pcnf = to_pcnf(formula)
pcnf.flip_quantifier(px.name, qx.name, px1.name, qx1.name)

print(solve(pcnf)) # False	

p2 = Atom("p2"); q2 = Atom("q2")

bind = bind | ((p1 @ px) & (q1 @ qx) & (p2 @ px1) & (q2 @ qx1))
formula = (~p0) & (~q0) & (p2) & (q2) & (bind >> t) 

pcnf = to_pcnf(formula)
pcnf.flip_quantifier(px.name, qx.name, px1.name, qx1.name)
pcnf.exists(p2.name, q2.name, block=OUTERMOST_BLOCK) # move to front

print(solve(pcnf)) # True	