from argparse import ArgumentParser
import os
import sys
import itertools

from pyqbf.formula import PCNF, OUTERMOST_BLOCK, QUANTIFIER_FORALL
from pyqbf.solvers import DepQBF

# In this example, we will count countermodels of false QBFs with an universal quantifier at the outermost block
# This is done, by iteratively adding the countermodels to the formula using a disjunction.
#
# Assume the formula Vx Vy Ez: (x \/ -y) /\ (-x \/ y) /\ (x \/ z) /\ (y \/ -z)
# First, we modify the formula by adding a tseitin-variable t, the formula is bound to such that we can apply the disjunction later
# Vx Vy Ez Et: (-t \/ x \/ -y) /\ (-t \/ -x \/ y) /\ (-t \/ x \/ z) /\ (-t \/ y \/ -z)
#
# Now, the truth value of the formula is on t. Using the incremental functionalities of DepQBF, we can setup frames where sets of clauses can be pushed/popped
# This is relevant, as we want to exchange the uppermost clause (in the following target clause) whenever we add a countermodel
# Thus, we push a frame onto the solver, and start with the single tseitin-variable in our target clause
# Vx Vy Ez Et: (-t \/ x \/ -y) /\ (-t \/ -x \/ y) /\ (-t \/ x \/ z) /\ (-t \/ y \/ -z) /\ (t)
#                                                                                          ^ target Clause
#
# From a QBF-solver, we get the following countermodel of the outermost quantifier: -x, y
# In order to add it to the formula, we pop the target clause, add what we need and then push it again
#
# We can add -x, y by introducing a new tseitin variable (t2) and add the clauses (-t2 \/ -x) and (-t2 \/ y) 
# This simply encodes (-x /\ y)
#
# Now we modify the target clause by adding our countermodel as a disjunction, i.e. target clause = (t \/ t2)
#
# After this first iteration step, the formula looks the following:
# Vx Vy Ez Et Et2: (-t \/ x \/ -y) /\ (-t \/ -x \/ y) /\ (-t \/ x \/ z) /\ (-t \/ y \/ -z) /\ (-t2 \/ -x) /\ (-t2 \/ y) /\ (t \/ t2)
#                                                                               Counter-model -------------------------     ------- target clause
# Now again check the truth value. This is continued until the formula becomes true

def preprocess(formula:PCNF):
    # adds a new variable to the formula. This will represent the whole formula
    target = formula.introduce_var()    

    # adding the tseitin variable to each clause, such that it implies them
    for clause in formula.clauses:
        clause.append(-target)  
    return target

if __name__ == "__main__":
    cli = ArgumentParser()
    cli.add_argument("--path", help="path to the qdimacs-formula to be solved.", default="unsat.qdimacs")

    args = cli.parse_args()
    if not os.path.exists(args.path):
        print("Path does not exist!")
        exit(-1)

    formula = PCNF(from_file=args.path)    
    root = preprocess(formula)    

    # initialize solver with incremental capabilities
    solver = DepQBF(incr=True)

    solver.load(formula)        # load the formula
    solver.push()               # push a new frame for incremental solving (this can be popped later easily)
    target_clause = [root]      # at the moment, only the root of the formula is in this clause
    solver.add(target_clause)   
    result = solver.solve()     # get the base-truth value of the formula. We can only compute counter-models if there are any
    print(f"Solved base formula, result: {result}")    

    if not result and (formula.get_block_type(OUTERMOST_BLOCK) != QUANTIFIER_FORALL):
        print("Can not compute counter-models of this formula! The outermost quantifier block is existential")
        exit(0)

    iteration = 0
    while not result:
        iteration += 1
        print(f"----------Starting Iteration {iteration:02d}----------")
        # Get the countermodel of the outermost, universal quantifier block
        a = [solver.get_assignment(abs(var)) for var in itertools.takewhile(lambda x: x < 0, formula.prefix)]
        
        assert len(a) > 0, "No possible assignments"  #just to be sure we received something

        # Remove the frame, we will update the target_clause
        solver.pop()

        print(f"Assignment of the universial block: {a}")        
        
        # Introduce a new tseitin variable, in which we can encode the assignment into
        ts = formula.introduce_var()   
        solver.add_var(ts)
        target_clause.append(ts)
        
        # Simple AND-encoding: for each member of the AND add a clause where the tseitin variable implies this single memeber
        for var in a:
            clause = [-ts, var]
            solver.add(clause)        
            formula.append(clause)
            print(f"Added {clause} to solver!")
        
        # Add the updated clause (push before so we can pop it again if necessary)
        solver.push()
        solver.add(target_clause)        
        print(f"Added {target_clause} to solver!")
        
        # Compute the current truth value
        result = solver.solve()
        print(f"Solver resulted in {result}")

        # If all countermodels were found, we can add the final target_clause to the formula 
        if result:
            formula.append(target_clause)

    print(f"-----------------------------------------")
    print(f"Found {iteration} counter-model(s)!")
    print(f"-----------------------------------------")
    print(formula.to_qdimacs())
