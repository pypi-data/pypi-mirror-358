from pysat.formula import Atom
from pyqbf.formula import PCNF, to_pcnf, QUANTIFIER_FORALL, OUTERMOST_BLOCK
from pyqbf.solvers import solve, Solver


# We are looking at the following Bounded Model Checking problem:
# (B) <-> (A) <-> (C)
#  |      ^
#  v   /
# (D)  
#
# Or, in Graph Representation: G = ({A, B, C, D}, {(A, B), (A, C), (B, A), (B, D), (C, A), (D, A)})
#
# We use two variables to encode the states such that
# A = !p /\ !q
# B =  p /\ !q
# C = !p /\  q
# D =  p /\  q
#
# Assume initial State A, we want to see if we can reach D in one step

print("==========BMC with 1 Step==========")

p0 = Atom('p0')
q0 = Atom('q0')
p1 = Atom('p1')
q1 = Atom('q1')
init_state = ~p0 & ~q0  # Start at !p, !q
goal_state = p1 & q1    # Goal at p1, q1

# By using placeholders in the transition function (universally quantified), we can bind each step to the transition function
cur_p = Atom("cur-p")
cur_q = Atom("cur-q")
next_p = Atom("next-p")
next_q = Atom("next-q")

trans_func_a = ((~cur_p & ~cur_q) >> ((next_p & ~next_q) | (~next_p & next_q))) # A => B | C
trans_func_b = (( cur_p & ~cur_q) >> ((~next_p & ~next_q) | (next_p & next_q)))  # B => A | D
trans_func_c = ((~cur_p &  cur_q) >> (~next_p & ~next_q))  # C => A
trans_func_d = (( cur_p &  cur_q) >> (~next_p & ~next_q))  # D => A

trans_func = trans_func_a & trans_func_b & trans_func_c & trans_func_d

# Alternatively, this is the short version of the transition function after applying some simplification
# trans_func = (((next_p @ (~cur_p & ~cur_p)) & (~next_q)) | ((next_p @ (cur_p & ~cur_q)) & (next_q @ ~cur_q))) 

# For one step, we can only bind p0, q0, p1, p2
steps_bound = ((cur_p @ p0) & (cur_q @ q0) & (next_p @ p1) & (next_q @ q1))

#finally, we have our formula
formula = init_state & goal_state & (steps_bound >> trans_func)

#transform to PCNF
pcnf = to_pcnf(formula)
print("Name of p0    :", p0.name)
print("Name of q0    :", q0.name)
print("Name of p1    :", p1.name)
print("Name of q1    :", q1.name)
print("Name of cur_p :", cur_p.name)
print("Name of cur_q :", cur_q.name)
print("Name of next_p:", next_p.name)
print("Name of next_q:", next_q.name)

#correct the quantifier of the placeholders
pcnf.flip_quantifier(cur_p.name, cur_q.name, next_p.name, next_q.name)

print("Solver resulted in", solve(pcnf), "(expected False)")

print("==========BMC with 2 Step==========")

# Now extend the formula to two steps and look if a result can be found
p2 = Atom("p2")
q2 = Atom("q2")
goal_state = p2 & q2

steps_bound = steps_bound | ((cur_p @ p1) & (cur_q @ q1) & (next_p @ p2) & (next_q @ q2))   #step from 1 to 2

formula = init_state & goal_state & (steps_bound >> trans_func)

pcnf = to_pcnf(formula)
print("Name of p0    :", p0.name)
print("Name of q0    :", q0.name)
print("Name of p1    :", p1.name)
print("Name of q1    :", q1.name)
print("Name of p2    :", p2.name)
print("Name of q2    :", q2.name)
print("Name of cur_p :", cur_p.name)
print("Name of cur_q :", cur_q.name)
print("Name of next_p:", next_p.name)
print("Name of next_q:", next_q.name)

pcnf.flip_quantifier(cur_p.name, cur_q.name, next_p.name, next_q.name)

pcnf.exists(p2.name, q2.name, block=OUTERMOST_BLOCK)    #set p2 and q2 to the outermost block, they are not dependent of the universal quantified variables

print("Solver resulted in", solve(pcnf), "(expected True)")

#Now get the model
print("Model:")
with Solver(bootstrap_with=pcnf) as solver:
    solver.solve()
    model_lookup = {abs(var): var for var in solver.get_model()}
    print("p0:", model_lookup[p0.name])
    print("q0:", model_lookup[q0.name])
    print("p1:", model_lookup[p1.name])
    print("q1:", model_lookup[q1.name])
    print("p2:", model_lookup[p2.name])
    print("q2:", model_lookup[q2.name])
    print("Expected path: A -> B -> D ((!p0, !q0) -> (p1, !q1) -> (p1, q1))")