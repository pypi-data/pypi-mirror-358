Loading and Saving Formulas
===========================

For loading and saving formulas, the :doc:`formula-module <../api/formula>` can be used. In particular, the class :class:`pyqbf.formula.PCNF` represents a QBF.

.. code-block:: python
    
    >>> from pyqbf.formula import PCNF

Loading and saving as QDIMACS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Assume have the file ``input.qdimacs`` containing a QBF in the `QDIMACS <https://www.qbflib.org/qdimacs.html>`__-format.
In order to load it, you can use the constructor provided by the class.

.. code-block:: python

    >>> formula = PCNF(from_file='/path/to/input.qdimacs')

Similarily, the loading can be done using either a file-pointer or the string-representation of the formula.

.. code-block:: python

    >>> fp = open('/path/to/input.qdimacs', 'r')
    >>> formula2 = PCNF(from_fp=fp)
    >>> formula3 = PCNF(from_string="p cnf 1 1\ne 1 0\n1 -1 0\n")

The same three methods are available for saving a formula.

.. code-block:: python

    >>> formula.to_file("/path/to/output.qdimacs")
    >>> formula2.to_fp(fp)
    >>> print(formula3.to_qdimacs())
    p cnf 1 1 
    e 1 0
    1 -1 0


Loading DIMACS
~~~~~~~~~~~~~~~
Assume the file ``cnf.dimacs`` containing a propositional formula in the DIMACS-format.
As this format is compatible with QDIMACS, it can still be loaded the same three ways as already described.
In order to simplify things, we will continue with the file-option, but all approaches also work with file-pointers and strings.

.. code-block:: python

    >>> formula = PCNF(from_file='/path/to/cnf.dimacs')

The loaded formula has an empty prefix.

.. code-block:: python

    >>> print(formula.prefix)
    []

In order to generate a prefix, there are four options:

1. Use the constructor-parameter ``auto_generate_prefix``. This will existentially quantify the variables in the order of occurrence.

.. code-block:: python

    >>> formula = PCNF(from_file='/path/to/cnf.dimacs', auto_generate_prefix=True)
    >>> print(formula.prefix)
    [1, 2, 3, 4, 5]
    

2. Use the :func:`pyqbf.formula.to_pcnf`-function. This call will also existentially quantify the variables in the order of occurrence.

.. code-block:: python

    >>> from pyqbf.formula import to_pcnf
    >>> cnf = PCNF(from_file='/path/to/cnf.dimacs')
    >>> formula = to_pcnf(cnf)
    >>> print(formula.prefix)
    [1, 2, 3, 4, 5]

.. note::

    This function can be used for all possible inputs which can be transformed to a :class:`pyqbf.formula.PCNF` by the framework.


3. Use the class-method :func:`pyqbf.formula.PCNF.prefix_from_clauses`. This even allows to choose, which quantifier is used for the quantification.

.. code-block:: python
    
    >>> formula = PCNF(from_file='/path/to/cnf.dimacs')
    >>> formula.prefix_from_clauses()
    >>> print(formula.prefix)
    [1, 2, 3, 4, 5]
    >>> formula.prefix_from_clauses(QUANTIFIER_FORALL)
    >>> print(formula.prefix)
    [-1, -2, -3, -4, -5]

4. Manually define the prefix with the :func:`pyqbf.formula.PCNF.forall`- and :func:`pyqbf.formula.PCNF.exists` methods.

.. code-block:: python
    
    >>> formula = PCNF(from_file='/path/to/cnf.dimacs')
    >>> formula.forall(1).exists(2,3).forall(4).exists(5)
    >>> print(formula.prefix)
    [-1, 2, 3, -4, 5]

Furthermore, you can also modify the prefix afterwards, as shown in the :doc:`formula-module <../tutorial/modify_prefix>`-chapter.


Loading AIGER
~~~~~~~~~~~~~~~
If provided a formula ``formula.aig`` or ``formula.aag``, the framework will use the `py-aiger-cnf <https://github.com/mvcisback/py-aiger-cnf>`__-project.
In particular, the :func:`aig2cnf`-function. 
This can be used by either passing a circuit suitable with the package (i.e. having a ``aig``-attribute encoding a circuit) or a string in the AIGER format.

.. code-block:: python
    
    >>> aig = open("/path/to/circuit.aig", "r").read()
    >>> formula = PCNF(from_aiger=aig)
    >>> import aiger
    >>> expr = aiger.atom('x') | aiger.atom('y')
    >>> formula2 = PCNF(from_aiger=expr)

After that, the formula in CNF format was loaded, thus like with DIMACS the prefix still has to be initialized after.