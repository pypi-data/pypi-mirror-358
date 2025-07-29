Incremental Solving
===================

Incremental solving is a useful tool for many applications. 
While most incremental solvers allow individual assumptions of variables only, others allow extending the formula on the fly by additional clauses and variables. 
We will show methods to use the incremental capability of the framework for each of those two variants.

Incremental Solving with Assumptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We assume to have our formula ``/path/to/formula.qdimacs`` and want to solve it under assumptions :math:`(1 \wedge \neg 2)` and accordingly :math:`(3 \wedge \neg 6 \wedge 9)`.
In the following, we show ways to achieve this goal.

1. PyQBF provides the class :class:`pyqbf.solvers.AssumingEnvironment`, which allows solving formulas under assumptions on a high API level. The backend can not be chosen or configured.

.. code-block:: python

    >>> from pyqbf.sovers import AssumingEnvironment
    >>> from pyqbf.formula import PCNF
    >>> formula = PCNF(from_file="/path/to/formula.qdimacs") 
    >>> with AssumingEnvironment(formula) as solver:
    ...     print(solver.solve())                   #solve without assumptions
    ...     print(solver.solve([1, -2]))            #solve with specified assumptions
    ...     print(solver.solve([3, -6, 9]))         #solve with specified assumptions
    True
    False
    True


2. The class :class:`pyqbf.solvers.Solver` can be parameterized with ``incr=True`` to be configured for incremental solving. Note that this only works for a subset of solvers.
We recommend DepQBF as this solver provides the most functionalities for incremental solving. 
This approach has the advantage, that it still allows to configure the solver and even modify the formula with certain restrictions. 
Furthermore, if supported also more powerful incremental solving can be done, but more of that later.

.. code-block:: python

    >>> from pyqbf.solvers import Solver, SolverNames
    >>> from pyqbf.formula import PCNF
    >>> formula = PCNF(from_file="/path/to/formula.qdimacs") 
    >>> with Solver(name=SolverNames.depqbf, bootstrap_with=formula, incr=True) as solver:    
    ...     print(solver.solve())
    ...     print(solver.solve([1,-2]))             #solve under assumptions [1,-2]
    ...     solver.assume(3)
    ...     solver.assume([-6, 9])                 
    ...     print(solver.solve())                   #solve under assumptions [3, -6, 9]; assumptions are collected
    True
    False
    True

3. Of course, one can also directly use the solver classes without the API. This approach allows the most configurabilty and directly provides all available functions.
Using the derived :py:attr:`pyqbf.solvers.pyqbf_solver.assuming`-property, it is possible to check if the solver allows assumptions.

.. code-block:: python
    
    >>> from pyqbf.solvers import DepQBF, Qute
    >>> from pyqbf.formula import PCNF
    >>> formula = PCNF(from_file="/path/to/formula.qdimacs") 
    >>> with Qute() as solver:
    ...     print(solver.assuming)
    False       #can not be used as assuming solver
    >>> with DepQBF(incr=True) as solver:
    ...     print(solver.assuming)
    True
    >>> with DepQBF(incr=True) as solver:
    ...      print(solver.solve(formula))   # load and solve the formula in one go
    ...      solver.assume([1, -2])
    ...      print(solver.solve())          # formula is already loaded, do not try to load again
    ...      solver.assume(3)
    ...      solver.assume([-6, 9])
    ...      print(solver.solve())
    True
    False
    True


Advanced Incremental Solving
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In this section we want to solve the formula ``/path/to/formula.qdimacs`` and afterwards add the clause ``[1, 2, 3]`` and solve it again. 
In the following we describe ways to do that in the framework.

1. Using the function :func:`pyqbf.solvers.any_incremental_solver` directly provides a :class:`pyqbf.solvers.Solver` configured for incremental solving without the need for the user to configure it.
In order to use the incremental functionality, the :func:`pyqbf.solvers.Solver.add_clause`-function can be used, which is derived for every solver.
Note that adding clauses after the solver was called is only possible for this special kind of incremental solvers, otherwise an error will be thrown.

.. code-block:: python
    
    >>> from pyqbf.solvers import any_incremental_solver
    >>> from pyqbf.formula import PCNF
    >>> formula = PCNF(from_file="/path/to/formula.qdimacs") 
    >>> with any_incremental_solver(bootstrap_with=formula) as solver:
    ...     print(solver.solve())
    ...     solver.add_clause([1, 2, 3])
    ...     print(solver.solve())
    True
    False

2. The solver :class:`pyqbf.solvers.DepQBF` provides the same functionalities and more. 
It even allows to push and pop pages, allowing to efficiently add and remove clauses from the formula.


.. code-block:: python
    
    >>> from pyqbf.solvers import DepQBF
    >>> from pyqbf.formula import PCNF
    >>> formula = PCNF(from_file="/path/to/formula.qdimacs") 
    >>> with DepQBF(incr=True) as solver:
    ...      print(solver.solve(formula))   # load and solve the formula in one go
    ...      solver.add([2, 3])             # add clause
    ...      print(solver.solve())          # formula is already loaded, do not try to load again
    ...      solver.push()                  # new frame
    ...      solver.add([1, 2, 3])
    ...      print(solver.solve()) 
    ...      solver.pop()                   # remove frame
    ...      print(solver.solve()) 
    True    # original formula is true
    True    # adding [2,3] => still true
    False   # adding [1,2,3] => false
    True    # remove [1,2,3] by popping the frame => true