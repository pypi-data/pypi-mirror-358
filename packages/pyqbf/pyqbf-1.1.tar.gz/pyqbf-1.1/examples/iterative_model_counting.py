from argparse import ArgumentParser
import os
import itertools

from pyqbf.formula import PCNF, OUTERMOST_BLOCK, QUANTIFIER_EXISTS
from pyqbf.solvers import DepQBF

# In this example, we will count models of true QBFs with an existentially quantifier at the outermost block
# This is done, by iteratively adding the negated models to the formula
#
# Assume the formula Ea Eb Ec Ed Ve: (a \/ c \/ e) /\ (b \/ d \/ e)
# First, we evaluate the truth value and extract a model from the formula
# The QBF-solver will fetch us the following model: a, b, c, d
#
# Now, we prevent the solver from choosing this model by adding it as a countermodel to the clauses, i.e. negate it
# After that, the formula looks the following:
# Ea Eb Ec Ed Ve: (a \/ c \/ e) /\ (b \/ d \/ e) /\ (-a \/ -b \/ -c \/ -d)
#                                                    -------------------- negated assignment
#
# After that step, we solve again and repeat this steps, until the formula becomes false

if __name__ == "__main__":
    cli = ArgumentParser()
    cli.add_argument("--path", help="path to the qdimacs-formula to be solved.", default="formula2.qdimacs")

    args = cli.parse_args()
    if not os.path.exists(args.path):
        print("Path does not exist!")
        exit(-1)

    # Load formula and setup solver
    formula = PCNF(from_file=args.path)
    solver = DepQBF(incr=True)

    # get first result
    result = solver.solve(formula)
    print(f"Solved base formula, result: {result}")

    if result and (formula.get_block_type(OUTERMOST_BLOCK) != QUANTIFIER_EXISTS):
        print("Can not compute models of this formula! The outermost quantifier block is universal")
        exit(0)

    iteration = 0
    while result:
        iteration += 1
        print(f"----------Starting Iteration {iteration:02d}----------")

        # Get the models of the outermost, existentially quantified block
        a = [solver.get_assignment(abs(var)) for var in itertools.takewhile(lambda x: x > 0, formula.prefix)]
        assert len(a) > 0, "No possible assignments"  #just to be sure we received something
        print(f"Assignment of the existential blocK: {a}")
        
        # negate the assignment and add it as a new clause to the solver
        clause = [-x for x in a]
        solver.add(clause)
        formula.append(clause)
        print(f"Added {clause} to solver!")

        result = solver.solve()
        print(f"Solver resulted in {result}")
    print(f"-----------------------------------------")
    print(f"Found {iteration} model(s)!")
    print(f"-----------------------------------------")
    print(formula.to_qdimacs())
