"""
    ===============
    List of classes
    ===============

    .. autosummary::
        :nosignatures:

        Bloqqer
        Processor

    ==================
    Module description
    ==================

    This module provides access to the `Bloqqer <https://fmv.jku.at/bloqqer/>`__-preprocessor.
    It implements the following techniques:

    - Quantified Literal Elimination
    - Quantified Blocked Clause Elimination
    - Quantified Covered Blocked Clause Elimination
    - Quantified Covered Tautology Elimination
    - Subsumption
    - Variable Expansion
    - Equivalence Detection

    Besides the class :class:`Bloqqer` which is a direct implementation of the interface,
    there is also the class :class:`Processor` implementing the exact same interface as
    :class:`pysat.process.Processor`.

    At the moment, no configuration is possible using the interface.

    ==============
    Module details
    ==============
"""

import os
import sys
import enum
import pyqbf_cpp
from pyqbf.formula import PCNF, to_pcnf

class Bloqqer:
    """
    Direct usage of the backend-interface of Bloqqer

    .. code-block:: python

        >>> from pyqbf.formula import PCNF
        >>> from pyqbf.process import Processor
        >>> from pyqbf.solvers import Solver
        >>> 
        >>> pcnf = PCNF(from_clauses=[[1, 2], [3, 2], [-1, 4, -2], [3, -2], [3, 4]], auto_generate_prefix=True)
        >>> processor = Bloqqer()
        >>> processed = processor.preprocess(pcnf)
        >>> print(processed)
        True        
        >>> pcnf = PCNF(from_file="formula_not_being_solved_directly.qdimacs")
        >>> processed = processor.preprocess(pcnf)
        >>> type(processed)
        <class 'pyqbf.formula.PCNF'>
    """
    def preprocess(self, formula):
        """
        Processes the provided formula using Bloqqer

        :param formula: the target to preprocess            
        :type formula: :class:`pyqbf.formula.PCNF`
        
        :return: ``True`` or ``False`` if the preprocessor was able to solve the formula. Else a formula describing the state after preprocessing
        :rtype: :class:`bool` or :class:`pyqbf.formula.PCNF`

        .. code-block:: python

            >>> processor = Bloqqer()
            >>> processor.preprocess()
        """
        output = PCNF()
        if hasattr(self,"qrat_trace"):
            result = pyqbf_cpp.preprocess_with_trace(formula, output, self.qrat_trace)
        else:
            result = pyqbf_cpp.preprocess(formula, output)
        if result != 0:
            return result == 10
        else:
            return output
        
    def set_qrat_file(self, file):
        """
        Sets the provided file path as output for the QRAT-trace

        :param file: target path for the trace
        :type file: :class:`str` 

        .. code-block:: python

            >>> processor = Bloqqer()
            >>> processor.set_qrat_file("./trace.qrat")
            >>> processor.preprocess()
        """
        self.qrat_trace = file


class TraceType(enum.Enum):
    """
    Contains all available tracing types
    """
    qrat = "qrat"

class Processor:
    """
    API for compatibility with :class:`pysat.process.Processor`

    :param bootstrap_with: Formula to be preprocessed
    :type bootstrap_with: :class:`pyqbf.formula.PCNF`

    .. code-block:: python

        >>> from pyqbf.formula import PCNF
        >>> from pyqbf.process import Processor
        >>> from pyqbf.solver import Solver
        >>> 
        >>> pcnf = PCNF(from_clauses=[[1, 2], [3, 2], [-1, 4, -2], [3, -2], [3, 4]], auto_generate_prefix=True)
        >>> processor = Processor(bootstrap_with=pcnf)
        >>> processed = processor.process()
        >>> print(processed.clauses)
        []
        >>> print(processor.status)
        True

        >>> with Solver(bootstrap_with=processed) as solver:
        >>>     solver.solve()
        True
        ...     print('proc model:', solver.get_model())
        >>> proc model: []
    """
    def __init__(self, bootstrap_with=None):
        """
        Standard Constructor
        """
        self.status = True

        if bootstrap_with is None:
            bootstrap_with = PCNF()  #empty        
        elif not isinstance(bootstrap_with, PCNF):            
            bootstrap_with = to_pcnf(bootstrap_with)

        self.formula = bootstrap_with
        self.preprocessor = Bloqqer()
        self.status = None

    def __enter__(self):
        """
        'with' constructor.
        """

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        'with' destructor.
        """
        pass

    def add_clause(self, clause):
        """
        Add a single clause to the processor.

        :param clause: a clause to add
        :type clause: :class:`list[int]` or any iterable of type :class:`int`

        .. code-block:: python

            >>> processor = Processor()
            >>> processor.add_clause([-1, 2, 3])
        """
        self.formula.append(clause)

    def append_formula(self, formula, no_return=True):
        """
            Add a given formula into the preprocessor.

            For a list of clauses (:class:`list[list[int]]`), they will be added to the clause-part of the internal :class:`pyqbf.formula.PCNF`.
            For a (transformed) :class:`pyqbf.formula.PCNF`, the non-occurring variables will be added at the end of the prefix existentially quantified.

            :param formula: a list of clauses or another formula convertable to PCNF
            :param no_return: check processors's internal formula and return the result, if set to ``False``. Default ``True``
            
            :type formula: e.g. :class:`pyqbf.formula.PCNF`
            :type no_return: :class:`bool`

            :rtype: bool if ``no_return`` is set to ``False``.

            .. code-block:: python

                >>> pcnf = PCNF(from_file="formula.qdimacs")
                >>> processor = Processor()
                >>> processor.append_formula(pcnf)
        """
        if self.formula:
            clauses = []
            if isinstance(formula, list):
                clauses = formula
            elif isinstance(formula, PCNF):
                clauses = formula.clauses   
                self.formula.prefix.extend([x for x in formula.prefix if x not in self.formula.prefix and -x not in self.formula.prefix])
            else:
                pcnf = to_pcnf(formula)
                clauses = pcnf.clauses
                self.formula.prefix.extend([x for x in pcnf.prefix if x not in self.formula.prefix and -x not in self.formula.prefix])

            for clause in clauses:
                self.add_clause(clause)

    def process(self, rounds=1, block=False, cover=False, condition=False,
                decompose=True, elim=True, probe=True, probehbr=True,
                subsume=True, vivify=True):
        """
        Run the preprocessor on the specified formula

        .. warning::

            All parameters are specified due to compatibility-reasons with :class:`pysat.process.Processor` and will be ignored

        .. code-block:: python

            >>> processor = Processor(bootstrap_with=[[-1, 2], [-2, 3], [-1, -3]])
            >>> processor.add_clause([1])
            >>> processed = processor.process()
            >>> print(processed.clauses)
            [[]]
            >>> print(processor.status)
            False
        """
        if self.preprocessor:
            result = self.preprocessor.preprocess(self.formula)
            if isinstance(result, bool):
                self.status = result
                return PCNF(from_clauses=[]) if result else PCNF(from_clauses=[[]])
            else:
                self.status = None
                return result

    def get_status(self):
        """
        Preprocessor's status as the result of the previous call to :func:`process`.
        If the preprocessor was not able to solve the formula or the function was not called yet,
        the status is ``None``.
        
        :returns: The result of the last call of :meth:`process()`
        :rtype: :class:`bool` or ``None``

        .. code-block:: python

            >>> processor = Processor(bootstrap_with=[[-1, 2], [-2, 3], [-1, -3]])
            >>> processed = processor.process()
            >>> print(processor.get_status())
            True
        """
        return self.status

    def restore(self, model):
        """
        Compatibility method for :class:`pysat.process.Processor`. 
        
        .. warning::
            Not implemented for QBFs
        """
        raise NotImplementedError("Model-restauration is not possible using Bloqqer")

    def add_tracing(self, file, traceType = TraceType.qrat):
        """
        Adds a new tracing file of the specified tracing type. 
        If the type is not supported, a :class:`NotImplementedError` is thrown

        :param file: The file-path to the tracing file
        :param traceType: Specification of the tracing output

        :type file: :class:`str`
        :type traceType: :class:`TraceType`
           
        .. code-block:: python

                >>> pcnf = PCNF(from_file="formula.qdimacs")
                >>> processor = Processor()
                >>> processor.set_qrat_file("trace.qrat")
                >>> processor.process()
        """
        if traceType == TraceType.qrat:
            self.preprocessor.set_qrat_file(file)
        else:
            raise NotImplementedError("This tracing type is currently not supported")

