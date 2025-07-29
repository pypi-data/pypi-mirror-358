from argparse import ArgumentParser
import os

from pyqbf.formula import PCNF
from pyqbf.solvers import Qute

# Shows an example for the usage of configurations by using the solver Qute in order to print out a trace

if __name__ == "__main__":
    cli = ArgumentParser()
    cli.add_argument("--path", help="path to the qdimacs-formula to be solved.", default="formula.qdimacs")

    args = cli.parse_args()
    if not os.path.exists(args.path):
        print("Path does not exist!")
        exit(-1)

    formula = PCNF(from_file=args.path)
    solver = Qute()
    solver.configure(Qute.Configuration.trace)

    result = solver.solve(formula)