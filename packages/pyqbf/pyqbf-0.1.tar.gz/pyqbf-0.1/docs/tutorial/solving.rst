Solving PCNF Formulas
=====================

In this section we will explore the different methods of solving a formula using the framework.

In the following, we will assume that there is a file ``/path/to/formula.qdimacs`` we want to solve and going to list different approaches.

1. Using the :func:`pyqbf.solvers.solve_file`, one does not even have to instantiate a formula. 
If there is a whole set of files, there is also the :func:`pyqbf.solvers.solve_all_files`-function, returning a dictionary with the result for each file.
Obviously, this appoach neither allows modfication of the formula nor configuration/choosing of the solver.

.. code-block:: python

    >>> from pyqbf.solvers import solve_file, solve_all_files
    >>> print(solve_file("/path/to/formula.qdimacs"))
    True
    >>> print(solve_all_files(["/path/to/formula.qdimacs", "/path/to/formula2.qdimacs"]))
    {"/path/to/formula.qdimacs": True, "/path/to/formula2.qdimacs": False}

2. If we want to simply solve a formula without caring for the solver, but still want to modify it or retreive information from it, there are also two approaches in doing so.
First, we can use the :func:`pyqbf.solvers.solve`-function, which will do the same as ``solve_file`` but taking a :class:`pyqbf.formula.PCNF` as an argument instead of a file.
Second, we can use the API-class :class:`pyqbf.solvers.Solver` with only the formula as a parameter.

.. code-block:: python

    >>> from pyqbf.solvers import solve, Solver
    >>> from pyqbf.formula import PCNF
    >>> formula = PCNF(from_file="/path/to/formula.qdimacs")
    >>> print(solve(formula))
    True
    >>> with Solver(bootstrap_with=formula) as solver:
    ...     print(solver.solve())
    True

3. For full configuration of the solver, either the :class:`pyqbf.solvers.Solver` may be used or the corresponding class of the solver. 
For the first approach, the enum-class :class:`pyqbf.solvers.SolverNames` can be used to select a backend.
For the letter, we recommend :class:`pyqbf.solvers.DepQBF` to start as it performed the best in our tests.
We now can for example configure, that there should be no Solution-Directed Cube Learning (SDCL) using the :class:`pyqbf.solvers.DepQBF.Configuration`-enum.
It is recommended but not necessary to use a ``with``-block for better readability (Cleanup is done via ``weakref``).

.. code-block:: python
    
    >>> from pyqbf.solvers import DepQBF, Solver, SolverNames
    >>> from pyqbf.formula import PCNF
    >>> formula = PCNF(from_file="/path/to/formula.qdimacs")
    >>> with Solver(name=SolverNames.depqbf, bootstrap_with=formula) as solver:
    ...     solver.configure(DepQBF.Configuration.no_sdcl)
    ...     print(solver.solve())
    True
    >>> with DepQBF() as solver:
    ...     solver.configure(DepQBF.Configuration.no_sdcl)
    ...     print(solver.solve())
    True   
