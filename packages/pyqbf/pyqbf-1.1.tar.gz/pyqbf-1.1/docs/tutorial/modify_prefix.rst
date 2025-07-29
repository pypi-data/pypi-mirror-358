Modifying the Prefix
====================

The :class:`pyqbf.formula.PCNF`-class provides a lot of different functionalities to get information about as well as modify the prefix.

Get the quantifier type of a variable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In order to get the quantifier of a variable in the prefix, there are two different methods.

1. Using the :func:`pyqbf.formula.PCNF.var_type`-function. 
This will return one of the constants indicating the quantifier (:class:`pyqbf.formula.QUANTIFIER_EXISTS`, :class:`pyqbf.formula.QUANTIFIER_FORALL`, :class:`pyqbf.formula.QUANTIFIER_NONE`)

.. code-block:: python

    >>> pcnf = PCNF(from_clauses=[[1,2], [-1, -2]])
    >>> pcnf.exists(1).forall(2)
    >>> print(pcnf.var_type(1) == QUANTIFIER_EXISTS)
    True
    >>> print(pcnf.var_type(2) == QUANTIFIER_FORALL)
    True
    >>> print(pcnf.var_type(3) == QUANTIFIER_NONE) #variable not in prefix
    True

2. Directly access ``pyqbf.formula.PCNF.prefix``. This requires knowing on which position in the prefix the variable is, but also allows us to iterate.
   Existentially quantified variables are represented by natural numbers, universially quantified variables by their negation.

.. code-block:: python

    >>> pcnf = PCNF(from_clauses=[[1,2], [-1, -2]])
    >>> pcnf.exists(1).forall(2)
    >>> print(pcnf.prefix[0])
    1
    >>> print(pcnf.prefix[1])
    -2
    >>> for x in pcnf.prefix:
    ...    print(x)
    1
    -2

Set the quantifier type of a variable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Similar to getting the quantifier type, we can also set the quantifier of a variable. 
There also are five methods possible, where three can be used to manually set the quantifier and two of them automatically quantify the prefix according to the matrix.

1. Using the :func:`pyqbf.formula.PCNF.exists`- and :func:`pyqbf.formula.PCNF.forall`-functions.
They will simply add the specified variable(s) without further check to the end of the current prefix.
No checks will be carried out, whether this variable already exists.
Thus, we recommend using this method only for initialization of new variables.

.. code-block:: python

    >>> pcnf = PCNF(from_clauses=[[1,2], [-1, -2]])
    >>> pcnf.exists(1).forall(2)
    >>> print(pcnf.prefix)
    [1, -2]
    >>> pcnf.forall(1)
    >>> print(pcnf.prefix)
    [1, -2, -1]


2. Using the :func:`pyqbf.formula.PCNF.set_quantifier`-function
This allows us to directly set the quantifier type without worrying about the position in the prefix or the representation.
Furthermore, it will also handle the case that the variable is not yet in the prefix.
We highly recommend this method, as it will ensure the consistency of the formula's fields.

.. code-block:: python

    >>> pcnf = PCNF(from_clauses=[[1,2],[-1,-2]])
    >>> pcnf.forall(1)
    >>> print(pcnf.prefix)
    [-1]
    >>> pcnf.set_quantifier(1, QUANTIFIER_EXISTS)
    >>> pcnf.set_quantifier(2, QUANTIFIER_FORALL)
    >>> print(pcnf.prefix)
    [1, -2]
    >>> print(pcnf.nv)
    2


3. Directly setting the ``pyqbf.formula.PCNF.prefix``-list. 

.. code-block:: python
    
    >>> pcnf = PCNF(from_clauses=[[1,2], [-1,-2]])
    >>> pcnf.forall(1)
    >>> print(pcnf.prefix)
    [-1]
    >>> pcnf.prefix[0] = 1
    >>> pcnf.prefix[1] = -2
    >>> print(pcnf.prefix)
    [1, -2]

While possible, it is hard to keep the formula consistent. A good example is the ``pyqbf.formula.PCNF.prefix``-variable.

.. code-block:: python

    >>> print(pcnf.nv)
    1


Additionally, there are two methods automatically setting the quantifier prefix using information from the propositional formula.

4. Using the :func:`pyqbf.formula.PCNF.prefix_from_clauses`-function, the algorithm will automatically collect all occurring variables in the formula and order them by occurrence. 
The quantifier-type can be specified.

.. code-block:: python
    
    >>> pcnf = PCNF(from_clauses=[[1,2], [-1,-2]])
    >>> pcnf.prefix_from_clauses()
    >>> print(pcnf.prefix)
    [1, 2]
    >>> pcnf.prefix_from_clauses(QUANTIFIER_FORALL)
    >>> print(pcnf.prefix)
    [-1, -2]

5. Using the :func:`pyqb.formula.PCNF.quantify_free_variables`-function, the algorithm will automatically quantify all free variables occurring in the propositional formula in a first block in the front of the prefix.
The quantifier-type can be specified.

.. code-block:: python

    >>> pcnf = PCNF(from_clauses=[[1, 2, 3], [-1, 2, 3], [-1, -2, -3]])
    >>> pcnf.forall(1)
    >>> print(pcnf.prefix)
    [-1]
    >>> pcnf.quantify_free_variables()
    >>> print(pcnf.prefix)
    [2, 3, -1] 
    >>> pcnf = PCNF(from_clauses=[[1, 2, 3], [-1, 2, 3], [-1, -2, -3]])
    >>> pcnf.forall(1)
    >>> pcnf.quantify_free_variables(QUANTIFIER_FORALL)
    >>> print(pcnf.prefix)
    [-2, -3, -1] 



Gain information about the quantifier blocks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
There is a list of information about quantifier blocks to be retrieved from the prefix.

1. The representation of the prefix as a 2D-array w.r.t. the quantifier blocks (function :func:`pyqbf.formula.PCNF.compute_blocks`)

.. code-block:: python

    >>> pcnf = PCNF(from_clauses=[[-4, 1, 2], [-5, -1, -2], [-6, 4], [-6, 5], [6]])
    >>> pcnf.forall(1).exists(2,3,4).forall(5,6)
    >>> print(pcnf.compute_blocks())
    [[-1], [2, 3, 4], [-5, -6]]

2. The amount of quantifier-alternations (function :func:`pyqbf.formula.PCNF.count_quantifier_alternations`)

.. code-block:: python

    >>> pcnf = PCNF(from_clauses=[[-4, 1, 2], [-5, -1, -2], [-6, 4], [-6, 5], [6]])
    >>> pcnf.forall(1).exists(2, 3)
    >>> print(pcnf.count_quantifier_alternations())
    1
    >>> pcnf.exists(4).forall(5,6)
    >>> print(pcnf.count_quantifier_alternations())
    2

3. The block at a specific index of the prefix (function :func:`pyqbf.formula.PCNF.get_block`)

.. code-block:: python
    
    >>> pcnf = PCNF(from_clauses=[[-4, 1, 2], [-5, -1, -2], [-6, 4], [-6, 5], [6]])
    >>> pcnf.forall(1).exists(2,3,4).forall(5,6)
    >>> print(pcnf.get_block(0))
    [-1]    
    >>> print(pcnf.get_block(2))
    [-5, -6]
    >>> print(pcnf.get_block(100))
    None

4. The quantifier type of a block at a specific index of the prefix (function :func:`pyqbf.formula.PCNF.get_block_type`)

.. code-block:: python
    
    >>> pcnf = PCNF(from_clauses=[[-4, 1, 2], [-5, -1, -2], [-6, 4], [-6, 5], [6]])
    >>> pcnf.forall(1).exists(2,3,4).forall(5,6)
    >>> print(pcnf.get_block_type(0) == QUANTIFIER_FORALL)
    True
    >>> print(pcnf.get_block_type(1) == QUANTIFIER_EXISTS)
    True
    >>> print(pcnf.get_block_type(100) == QUANTIFIER_NONE)
    True

5. The innermost block, optionally of a specific quantifier (function :func:`pyqbf.formula.PCNF.innermost_block`)

.. code-block:: python
    
    >>> pcnf = PCNF(from_clauses=[[-4, 1, 2], [-5, -1, -2], [-6, 4], [-6, 5], [6]])
    >>> pcnf.forall(1).exists(2,3,4).forall(5,6)
    >>> print(pcnf.innermost_block())
    [-5, -6]
    >>> print(pcnf.innermost_block(QUANTIFIER_FORALL))
    [-5, -6]
    >>> print(pcnf.innermost_block(QUANTIFIER_EXISTS))
    [2, 3, 4]
 