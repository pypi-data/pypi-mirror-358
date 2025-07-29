from argparse import ArgumentParser
import os

from pyqbf.formula import PCNF
from pyqbf.solvers import Solver, SolverNames

# This example is a testcase, how different solvers can be compared to each other
# It takes an argument (a formula), otherwise it will use a simple default formula

if __name__ == "__main__":
    cli = ArgumentParser()
    cli.add_argument("--path", help="path to the qdimacs-formula to be solved.", default="formula2.qdimacs")

    args = cli.parse_args()
    if args.path is None or not os.path.exists(args.path):
        print("Path does not exist!")
        exit(-1)

    # Loading formula
    formula = PCNF(from_file=args.path)

    # Iterate over all available solvers
    for name in SolverNames:
        with Solver(name, bootstrap_with=formula, use_timer=True) as solver:
            result = solver.solve()
            print(f"{name.value.center(8)} took {solver.time():.6f}s and resulted in {result}")
