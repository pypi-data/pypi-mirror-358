Modifying the Matrix
====================

The :class:`pyqbf.formula.PCNF`-class provides a lot of different functionalities to get information about as well as modify the propositional formula.
Note that most of these methods are derived by the :class:`pysat.formula.CNF` and can also be used in this framework.

In general, the ``pyqbf.formula.PCNF.clauses``-field of the formula can be used as a list of list in order to access/add/remove/modify/... clauses.

Access Clauses
~~~~~~~~~~~~~~
There are two methods of accessing a clause on a certain index

1. Using the indexer of the :class:`pyqbf.formula.PCNF`-class.
.. code-block:: python

    >>> from pyqbf.formula import PCNF
    >>> pcnf = PCNF(from_clauses=[[-1, 2], [3]])
    >>> print(pcnf[0])
    [-1, 2]

3. Directly access the ``pyqbf.formula.PCNF.clauses``-field.

.. code-block:: python

    >>> from pyqbf.formula import PCNF
    >>> pcnf = PCNF(from_clauses=[[-1, 2], [3]])
    >>> print(pcnf.clauses[0])
    [-1, 2]


Adding Clauses
~~~~~~~~~~~~~~
There are three methods of adding clauses. 

1. Using the :func:`pyqbf.formula.PCNF.append`-function, in order to add a single clauses to the formula.

.. code-block:: python

    >>> from pyqbf.formula import PCNF
    >>> pcnf = PCNF(from_clauses=[[-1, 2], [3]])
    >>> pcnf.append([-3, 4])
    >>> print(pcnf.clauses)
    [[-1, 2], [3], [-3, 4]]

2. Using the :func:`pyqbf.formula.PCNF.extend`-function, in order to add multiple clauses to the formula.

.. code-block:: python

    >>> from pyqbf.formula import PCNF
    >>> pcnf = PCNF(from_clauses=[[-1, 2], [3]])
    >>> pcnf.extend([[-3, 4], [5, 6]])
    >>> print(pcnf.clauses)
    [[-1, 2], [3], [-3, 4], [5, 6]]

3. Directly access the ``pyqbf.formula.PCNF.clauses``-field.
Modifying the list of clauses directly by list-operations can be also used to delete or insert clauses.

.. code-block:: python

    >>> from pyqbf.formula import PCNF
    >>> pcnf = PCNF(from_clauses=[[-1, 2]])
    >>> pcnf.clauses.append([3])
    >>> pcnf.clauses.extend([[-3, 4], [5, 6]])
    >>> print(pcnf.clauses)
    [[-1, 2], [3], [-3, 4], [5, 6]]
    >>> pcnf.clauses.remove([3])
    >>> print(pcnf.clauses)
    [[-1, 2], [-3, 4], [5, 6]]