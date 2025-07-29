"""
    ===============
    List of classes
    ===============

    .. autosummary::
        :nosignatures:

        Solver
        Caqe
        DepQBF
        QFun
        QuAPI
        Qute
        RAReQS
        SolverNames
        pyqbf_incremental_solver
        pyqbf_solver
        AssumingEnvironment

    ===============
    List of methods
    ===============

    .. autosummary::
        :nosignatures:

        any_incremental_solver
        solve
        solve_all_files
        solve_file

    =================
    List of constants
    =================

    .. autosummary::
        :nosignatures:

        DISABLE_WARNING_NON_ASSUMING

        

    ==================
    Module description
    ==================
    This module provides access to a few modern QBF solvers. Currently supported are

    * `DepQBF (Version 6.03) <https://github.com/lonsing/depqbf>`__
    * `QFun (Version 1.0) <https://sat.inesc-id.pt/~mikolas/sw/qfun/>`__
    * `Qute (1.1) <https://github.com/fslivovsky/qute>`__
    * `RAReQS (1.1) <https://sat.inesc-id.pt/~mikolas/sw/areqs/>`__
    * `Caqe (4.0.1) <https://github.com/ltentrup/caqe>`__ (integration via QuAPI)
    
    Additionally, for making assumptions with non-assuming solvers, the `QuAPI <https://github.com/maximaximal/QuAPI>`__ 
    interface can be used by providing a path to a solver-executable.
    
    The Backend-API of the solver is exposed in the classes having the same name as the solvers
    (:class:`DepQBF`, :class:`QFun`, :class:`Qute`, :class:`RAReQS`, :class:`Caqe`, :class:`QuAPI`)
    In contrast to the :class:`pysat.solvers`-module there is no necessity to use a ``with``-block or
    manual :func:`delete`, as ``weakref`` will take care of the cleanup when the objects run out of scope.
    
    Similar to the :class:`pysat.solvers.Solver`-class, the :class:`Solver` will provide a higher
    API-level for those solvers. 

    .. note::
        All functions from :class:`pysat.solvers.Solver` are also availabe in the QBF-counterpart, 
        but not every functionality is implement

    Thus, a solver can be used the following ways:
    
    .. code-block:: python

        >>> s = DepQBF()
        >>>
        >>> s = Solver(name='depqbf')

    .. note::
        We still recommend using the ``with``-block when working with solvers as this causes the
        object to go out of scope faster and allows cleanup. All solvers will support being used 
        in such a way.
    
    As for its CNF-counterpart, the :mod:`pyqbf.solvers` module is designed to provide
    QBF solvers as *oracles* without exposing internal states. The following functionalities are 
    currently supported

    * creating and deleting solver objects
    * adding clauses and formulas to the solvers
    * use different configurations-values
    * checking satisfiability with and without assumptions
    * extracting a (partial) model from a satisfiable formula 
    * enumerating models of an input formula

    PyQBF supports non-incremental and incremental solving, where `QuAPI <https://github.com/maximaximal/QuAPI>`__
    is used for allowing non-assuming solvers to make assumptions and solve incrementally.


    For those who just need a fast interface for QBF utilities, we provide the
    very basic use-cases in form of pre-configuration. 
    
    * Function :func:`solve` for fast oracle-calls without instantiation of a solver
    * Function :func:`solve_file` and :func:`solve_all_files` for fast oracle-calls for QDIMACS-file(s)
    * Function :func:`any_incremental_solver` for providing a preconfigured :class:`Solver`-object fit for incremental solving
    * Class :class:`AssumingEnvironment` for incremental solving with assumptions

    .. code-block:: python

        >>> pcnf = ...
        >>> solve(pcnf)
        True
        >>> solve_file("my_formula.qdimacs")
        False
        >>> solve_all_files(["f1.qdimacs", "f2.qdimacs"])
        {"f1.qdimacs": True, "f2.qdimacs": False}
        >>> with any_incremental_solver(bootstrap_with=pcnf) as solver:
        ...     solver.solve()
        ...     solver.add_clause([1, 2, 3])
        ...     solver.solve(assumptions=[3, 4])                
        >>> with AssumingEnvironment(pcnf) as solver:
        >>>     solver.solve([1, 2, 3])
        >>>     solver.solve([1, -2, -3])
        >>>     solver.solve([-1, -2, 3])
    

    ==============
    Module details
    ==============
"""

import abc
import enum
import weakref
import time
import sys
from pysat.solvers import NoSuchSolverError

from pyqbf.formula import to_pcnf, PCNF
from pyqbf.process import Bloqqer
import pyqbf_cpp

#: If set to true, this variable will supress warnings about using assumptions with a non-assuming solver
DISABLE_WARNING_NON_ASSUMING = False


class pyqbf_solver(abc.ABC):
    """
    Base class for all solvers of the pyqbf module

    :param sid: solver-id for the backend
    :type sid: :class:`int`
    """
    def __init__(self, sid):
        """
        Constructor
        """
        self.backend_id = pyqbf_cpp.init_solver(sid)
        self.__finalizer = weakref.finalize(self, pyqbf_cpp.release_solver, self.backend_id)

    @property
    def assuming(self):
        """
        Indicates whether the solver supports assumptions

        Usage example:

        .. code-block:: python

            >>> s = Qute()
            >>> print(s.assuming)
            False
            >>> s = DepQBF()
            >>> print(s.assuming)
            True
        """
        return False

    @property
    def alive(self):
        """
        Indicates if the finalizer of the object is active. This should always be :class:`True`.

        Usage example:

        .. code-block:: python

            >>> s = QFun()
            >>> print(s.alive)
            True
        """
        return self.__finalizer.alive

    def configure(self, option):
        """
        Configures the solver with the specified option

        :param option: configuration-string to be applied
        :type option: :class:`str`
        """
        if isinstance(option, enum.Enum):
            option = option.value
        pyqbf_cpp.configure(self.backend_id, option)

    def get_stats(self):
        """
        Get accumulated low-level stats from the solver. Currently, the statistics includes the number of restarts, conflicts, decisions, and propagations

        Usage example:

        .. code-block:: 

            >>> formula = PCNF(from_file="some-file.qdimacs")
            >>> solver = DepQBF()
            >>> solver.solve()
            >>> print(solver.get_stats())
            {'restarts': 2, 'conflicts': 0, 'decisions': 254, 'propagations': 2321}        
        """
        target = {}
        return pyqbf_cpp.get_stats(self.backend_id, target)
    
    def get_assignment(self, var):
        """
        Interface method for retrieving the assignment value of the specified variable
        
        :param var: variable to retrieve the assignment for
        :type var: :class:`int`
        
        :returns: The assignment of the specified variable if a model was previously computed                                
        :rtype: :class:`int`
        """
        return pyqbf_cpp.get_assignment(self.backend_id, var)

    def solve(self, formula):
        """
        Interface method for solving a PCNF-formula with the solver

        :param formula: a formula to be solved
        :type formula: :class:`pyqbf.formula.PCNF`

        :returns: ``True``, if the formula is SAT, else ``False``
        :rtype: :class:`bool`

        Usage example:

        .. code-block:: python

            >>> pcnf = PCNF(from_file="some-file.qdimacs")
            >>> solver = QFun()
            >>> print(solver.solve(pcnf))
            True            
        """
        return pyqbf_cpp.solve(formula, self.backend_id)
          
    def __enter__(self):
        """
        'with' constructor
        """
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        'with' destructor
        """
        pass    #weakref will take care of this    


class pyqbf_incremental_solver(pyqbf_solver):
    """
    Base class for all solvers with incremental abilities

    :param sid: solver-id for the backend
    :type sid: :class:`int`
    """
    def __init__(self, sid):
        """
        Constructor
        """
        super().__init__(sid)
        self.__loaded = False             #load may only occur once but clauses can be added
        self.__solution_ready = False     #after solving, a reset has to be done when adding variables

    @property
    def assuming(self):
         return True

    def __check_alive(self):
        if not self.alive:
            print(f"Internal error: solver is already deleted at this point!", file=sys.stderr)
            return False
        else:
            return True

    def solve(self, formula = None):
        """
        Interface method for solving a PCNF-formula with the incremental solver

        :param formula: a PCNF-formula to be solved. Note that this may only be specified once per solver, as incremental solving does not support the loading of multiple formulas
        :type formula: :class:`pyqbf.formula.PCNF`

        :returns: ``True``, if the formula is SAT, else ``False``
        :rtype: :class:`bool`

        Usage example:

        .. code-block:: python
            
            >>> pcnf = PCNF(from_clauses=[[1, 2], [-1, -2]], auto_generate_prefix=True)
            >>> solver = DepQBF()
            >>> print(solver.solve(pcnf))
            True
            >>> solver.add([-1, 2]) 
            >>> print(solver.solve())
            True
            >>> solver.assume([1, 2])
            >>> print(solver.solve())
            False
        """
        if self.__check_alive():
            if self.__solution_ready:
                self.reset()
            if formula is not None:
               self.load(formula) 
            self.__solution_ready = True
            return pyqbf_cpp.solve_incremental(self.backend_id)            
        return None
        
    def load(self, formula):
        """
        Interface method for loading a formula into the solver.
        This method may only be called once for loading the formula into the solver.
        For incremental solving the :func:`add`-function may be used
                
        :param formula: a PCNF formula
        :type formula: :class:`pyqbf.formula.PCNF`

        :raises: :class:`RuntimeError` if there already was a formula loaded into the solver.

        Usage example:

        .. code-block:: python

            >>> pcnf = PCNF(from_clauses=[[1, 2], [-1, -2]], auto_generate_prefix=True)
            >>> solver = DepQBF()
            >>> solver.load(pcnf)
            >>> solver.solve()
            True
            >>> # Equivalent to
            >>> solver = DepQBF()
            >>> solver.solve(pcnf)
        """
        if self.__check_alive():
            if self.__loaded:
                raise RuntimeError(f"Cannot load two formulas! If you want to add more clauses, use the add-function!")           
            else:
                if formula is not None:
                    pyqbf_cpp.load_incremental(formula, self.backend_id)
                    self.__loaded = True

    def add_var(self, var):
        """
        Interface method for adding a variable to the current frame of the incremental solver. 
        Note: Resetting the solver after calling add_var after solving is done automatically

        :param var: variable to be added
        :type var: :class:`int`

        Usage example:

        .. code-block:: python
            
            >>> pcnf = PCNF(from_clauses=[[1, 2], [-1, -2]], auto_generate_prefix=True)
            >>> solver = DepQBF()
            >>> solver.load(pcnf)
            >>> solver.add_var(3)
        """
        if self.__check_alive():
            if self.__solution_ready:
                self.reset()
                self.__solution_ready = False                        
            pyqbf_cpp.quant_incremental(var, self.backend_id)


    def add(self, clause):
        """
        Interface method for adding a clause to the current frame of the incremental solver. 
        Note: Resetting the solver after calling add after solving is done automatically
        
        :param clause: a list of literals to be added to the solver
        :type clause: :class:`list[int]`

        Usage example:

        .. code-block:: python
            
            >>> pcnf = PCNF(from_clauses=[[1, 2], [-1, -2]], auto_generate_prefix=True)
            >>> solver = DepQBF()
            >>> solver.load(pcnf)
            >>> solver.add([-1, 2])            
        """
        if self.__check_alive():
            if self.__solution_ready:     # reset required
                self.reset()
                self.__solution_ready = False
            if type(clause) is list:
                pyqbf_cpp.add_incremental(clause, self.backend_id)
            elif type(clause) is int:
                pyqbf_cpp.add_incremental([clause], self.backend_id)
            else:
                raise TypeError(f"Expected int or list but got {type(clause)}")

    def reset(self):
        """
        Resets the internal solver states, keeps prefix and clauses.
        A reset is necessary after calls of the :func:`solve`-function.

        .. note::
            Resets are normally done automatically by the solver, such that this function rarely has to be called explicitely

        .. code-block:: python

            >>> solver = DepQBF()
            >>> sut = PCNF(from_clauses=[[1,2], [1,-2]])
            >>> sut.exists(1).forall(2)
            >>> solver.assume(-1)
            >>> print(solver.solve(sut))
            False
            >>> solver.reset()    #would be done automatically
            >>> print(solver.solve())
            True

        """
        if self.__check_alive():
            pyqbf_cpp.reset_incremental(self.backend_id)


    def push(self):
        """
        Interface method for pushing a new frame. All clauses added after calling this function are added to the new frame.

        Usage example: 

        .. code-block:: python

            >>> solver = DepQBF()
            >>> sut = PCNF(from_clauses=[[1,2]])        
            >>> sut.exists(1,2)       
            >>> print(solver.solve(sut))
            True
            >>> solver.push()   # new frame
            >>> solver.add([-1,2])
            >>> solver.push()   # new frame
            >>> solver.add([1,-2])
            >>> solver.push()   # new frame
            >>> solver.add([-1, -2])
            >>> print(solver.solve())
            False
        """
        if self.__check_alive():
            if self.__solution_ready:     # reset required
                self.reset()
                self.__solution_ready = False
            pyqbf_cpp.push_incremental(self.backend_id)

    def pop(self):
        """
        Interface method for popping the current frame. All clauses added after calling this function are added to the previous frame.
        
        Usage example: 

        .. code-block:: python

            >>> solver = DepQBF()
            >>> sut = PCNF(from_clauses=[[1,2]])        
            >>> sut.exists(1,2)       
            >>> print(solver.solve(sut))
            True
            >>> solver.push()   # new frame
            >>> solver.add([-1,2])
            >>> solver.add([1,-2])
            >>> solver.add([-1,-2])
            >>> print(solver.solve())
            False
            >>> solver.pop()   # remove last frame
            >>> print(solver.solve())        
            True
        """
        if self.__check_alive():
            if self.__solution_ready:     # reset required
                self.reset()
                self.__solution_ready = False
            pyqbf_cpp.pop_incremental(self.backend_id)

    def assume(self, clause_or_lit):
        """
        Interface method for assuming the value of a variable
            
        :param clause_or_lit: a clause of assumptions or a single assumption to be added to the solver
        :type clause_or_lit: :class:`int` or :class:`list[int]`

        :raises: :class:`TypeError` if the provided parameter is neither :class:`int` or :class:`list[int]`

        Usage example:

        .. code-block:: python

            >>> solver = DepQBF()
            >>> sut = PCNF(from_clauses=[[1,2], [1,-2]])
            >>> sut.exists(1).forall(2)
            >>> solver.assume(-1)
            >>> print(solver.solve(sut))
            False
            >>> print(solver.solve())   # assumptions are resetted with the next call of solve()
            True
        """
        if self.__check_alive():           
            if self.__solution_ready:
                self.reset()
                self.__solution_ready = False
            if type(clause_or_lit) is list:
                for lit in clause_or_lit:
                    pyqbf_cpp.assume_incremental(self.backend_id, lit)
            elif type(clause_or_lit) is int:
                pyqbf_cpp.assume_incremental(self.backend_id, clause_or_lit)
            else:
                raise TypeError(f"Expected int or list but got {type(clause_or_lit)}")


class DepQBF(pyqbf_incremental_solver):
    """
    Interface class for the DepQBF-Solver
    """
    def __init__(self, dynamic_nenofex = False, incr=False):
        super().__init__(pyqbf_cpp.SOLVER_DEPQBF)
        if not dynamic_nenofex:
            self.configure(DepQBF.Configuration.no_dynamic_nenofex) #in order to gather assignments
        if incr:
            self.configure(DepQBF.Configuration.dep_man_simple)
            self.configure(DepQBF.Configuration.incremental_use)

    def configure(self, option):
        """
            Allows the configuration of the solver using either a string or the 
            :class:`DepQBF.Configuration`-Enum

            :param option: the option to configure
            :type option: :class:`DepQBF.Configuration` or :class:`str`

            Usage example:

            .. code-block:: python

                >>> s = DepQBF()
                >>> s.configure(DepQBF.Configuration.qdo)
                >>> s.configure(DepQBF.Configuration.max_dec(100))
                >>> s.configure("--lclauses-init-size=4")
        """
        if isinstance(option, DepQBF.Configuration):
            option = option.value
        return super().configure(option)

    class Configuration(enum.Enum):
        """
            Enum providing a variety of configuration option for the DepQBF-solver
        """
        pretty_print =              "--pretty-print"        
        incremental_use =           "--incremental-use"
        qdo =                       "--qdo"
        traditional_qcdcl =         "--traditional-qcdcl"
        long_dist_res =             "--long-dist-res"
        no_lazy_qpup =              "--no-lazy-qpup"
        no_qpup_cdcl =              "--no-qpup-cdcl"
        no_qpup_sdcl =              "--no-qpup-sdcl"
        trace_bqrp =                "--trace=bqrp"
        dep_man_simple =            "--dep-man=simple" 
        no_cdcl =                   "--no-cdcl" 
        no_sdcl =                   "--no-sdcl" 
        no_pure_literals  =         "--no-pure-literals" 
        no_spure_literals  =        "--no-spure-literals" 
        no_unit_mtf  =              "--no-unit-mtf" 
        no_res_mtf  =               "--no-res-mtf" 
        @staticmethod
        def lclause_init_size(count): 
            return                 f"--lclauses-init-size={int(count)}"
        @staticmethod
        def lcubes_init_size(count): 
            return                 f"--lcubes-init-size={int(count)}"
        @staticmethod
        def lclauses_resize_value(count): 
            return                 f"--lclauses-resize-value={int(count)}"
        @staticmethod
        def lcubes_resize_value(count): 
            return                 f"--lcubes-resize-value={int(count)}"
        @staticmethod
        def orestart_dist_init(count): 
            return                 f"--orestart-dist-init={int(count)}"
        @staticmethod
        def orestart_dist_inc(count): 
            return                 f"--orestart-dist-inc={int(count)}"        
        @staticmethod
        def irestart_dist_init(count): 
            return                 f"--irestart-dist-init={int(count)}"
        @staticmethod
        def irestart_dist_inc(count): 
            return                 f"--irestart-dist-inc={int(count)}"        
        @staticmethod
        def max_dec(count): 
            return                 f"--max-dec={int(count)}"
        @staticmethod
        def max_btracks(count): 
            return                 f"--max-btracks={int(count)}"
        @staticmethod
        def max_secs(count): 
            return                 f"--max-secs={int(count)}"    
        no_qbce_dynamic =           "--no-qbce-dynamic"
        qbce_preprocessing =        "--qbce-preprocessing"
        qbce_inprocessing =         "--qbce-inprocessing"
        @staticmethod
        def qbce_witness_max_occs(count): 
            return                 f"--qbce-witness-max-occs={int(count)}"    
        @staticmethod
        def qbce_max_clause_size(count): 
            return                 f"--qbce-max-clause-size={int(count)}"    
        no_empty_formula_watching="--no-empty-formula-watching"
        no_dynamic_nenofex =        "--no-dynamic-nenofex"
        dyn_nenofex_ignore_unsat =  "--dyn-nenofex-ignore-unsat"
        dyn_nenofex_ignore_sat =    "--dyn-nenofex-ignore-sat"
        no_trivial_falsity =        "--no-trivial-falsity"
        no_trivial_truth =          "--no-trivial-truth"               


class Qute(pyqbf_solver):
    """
    Interface for the Qute-Solver
    """
    def __init__(self):
        super().__init__(pyqbf_cpp.SOLVER_QUTE)

    class Configuration(enum.Enum):
        """
            Enum providing a variety of configuration option for the Qute-solver
        """
        @staticmethod
        def initial_clause_DB_size(count):
            return f"--initial-clause-DB-size={int(count)}"
        @staticmethod
        def initial_term_DB_size(count):
            return f"--initial-term-DB-size={int(count)}"
        decision_heuristic_VSIDS =      "--decision-heuristic=VSIDS"
        decision_heuristic_VMTF  =      "--decision-heuristic=VMTF"
        decision_heuristic_SGDB  =      "--decision-heuristic=SGDB"        
        dependency_learning_off  =      "--dependency-learning=off"
        dependency_learning_outermost = "--dependency-learning=outermost"
        dependency_learning_fewest =    "--dependency-learning=fewest"
        dependency_learning_all    =    "--dependency-learning=all"
        no_phase_saving =               "--no-phase-saving"
        phase_heuristic_invJW =         "--phase-heuristic=invJW"
        phase_heuristic_qtype =         "--phase-heuristic=qtype"
        phase_heuristic_watcher =       "--phase-heuristic=watcher"
        phase_heuristic_random =        "--phase-heuristic=random"
        phase_heuristic_false =         "--phase-heuristic=false"
        phase_heuristic_true =          "--phase-heuristic=true"
        restarts_off =                  "--restarts=off"
        restarts_luby =                 "--restarts=luby"
        restarts_inner_outer =          "--restarts=inner-outer"
        restarts_ema =                  "--restarts=EMA"
        trace =                         "--trace"
        #VSIDS Options
        tiebreak_arbitrary =            "--tiebreak=arbitrary"
        tiebreak_more_primary =         "--tiebreak=more-primary"
        tiebreak_fewer_primary =        "--tiebreak=fewer-primary"        
        tiebreak_more_secondary =       "--tiebreak=more-secondary"
        tiebreak_fewer_secondary =      "--tiebreak=fewer-secondary"
        @staticmethod
        def var_activity_inc(value):
            return f"--var-activity-inc={float(value)}"
        @staticmethod
        def var_activity_decay(value):
            return f"--var-activity-decay={float(value)}"
        #SGDB Options
        @staticmethod
        def initial_learning_rate(value):
            return f"--initial-learning-rate={float(value)}"
        @staticmethod
        def learning_rate_decay(value):
            return f"--learning-rate-decay={float(value)}"        
        @staticmethod
        def learning_rate_minimum(value):
            return f"--learning-rate-minimum={float(value)}"                
        @staticmethod
        def lambda_factor(value):
            return f"--lambda-factor={float(value)}"
        #Restart Options
        @staticmethod
        def luby_restart_multiplier(count):
            return f"--luby-restart-multiplier={int(count)}"
        @staticmethod
        def alpha(value):
            return f"--alpha={float(value)}"        
        @staticmethod
        def minimum_distance(count):
            return f"--minimum-distance={int(count)}"            
        @staticmethod
        def threshold_factor(value):
            return f"--threshold-factor={float(value)}"           
        @staticmethod
        def inner_restart_distance(count):
            return f"--inner-restart-distance={int(count)}"            
        @staticmethod
        def outer_restart_distance(count):
            return f"--outer-restart-distance={int(count)}"            
        @staticmethod
        def restart_multiplier(value):
            return f"--restart_multiplier={float(value)}"           
        
        

    __supported__variants__ = ["--initial-term-DB-size=","--initial-clause-DB-size=", "--luby-restart-multiplier=", "--alpha=", "--minimum-distance=", "--threshold-factor=", "--inner-restart-distance=", "--outer-restart-distance=", "--restart_multiplier",\
                               "--var-activity-inc=","--var-activity-decay=", "--initial-learning-rate=","--learning-rate-decay=","--learning-rate-minimum=", "--lambda-factor=" \
                              ]
    __supported_options__ = [e.value for e in Configuration]

    def configure(self, option):
        """
        Allows the configuration of the solver using either a string or the 
        :class:`Qute.Configuration`-Enum

        :param option: the option to configure
        :type option: :class:`Qute.Configuration` or :class:`str`
        
        Usage example:

        .. code-block:: python

            >>> s = Qute()
            >>> s.configure(Qute.Configuration.no_phase_saving)
            >>> s.configure(Qute.Configuration.var_activity_inc(4))
            >>> s.configure("--restarts=EMA")

        .. note::
            Not all configuration options of the Qute-Solver are available at the moment. 
            A :class:`RuntimeError` will be raised if such an option is specified.

        """
        if isinstance(option, Qute.Configuration):
            option = option.value
        if option not in Qute.__supported_options__ and not any([option.startswith(x) for x in self.__supported__variants__]):
            raise RuntimeError(f"Option {option} is currently not supported for Qute with pyQBF!")
        return super().configure(option)
    
    def solve(self, formula):    
        if not formula.is_normalized:
            formula.normalize() #Qute needs a normalized formula (this is normally done by its parser)
        return super().solve(formula)
    

class RAReQS(pyqbf_solver):
    """
    Interface class for the RAReQS-Solver
    """
    def __init__(self):
        super().__init__(pyqbf_cpp.SOLVER_RAREQS)


class QFun(pyqbf_solver):
    """
    Interface class for the QFun-Solver
    """
    def __init__(self):
        super().__init__(pyqbf_cpp.SOLVER_QFUN)

    def solve(self, formula):        
        formula.quantify_free_variables()
        return super().solve(formula)


class QuAPI(pyqbf_solver):
    """
    Base class for usage of the QuAPI-Interface for assumptions with non-assuming solvers.
    It can either be initialized with an executable-path or by using the preset by specifying the solver-id

    :param solver_path: path to the executable QuAPI should be used with
    :param solver_id: if specified, a the preset of the solver with this id is used as executable

    :type solver_path: :class:`str`
    :type solver_id: :class:`int`

    .. note::
        Using a preset should be done via the ``use_quapi``-parameter of the :class:`Solver` class 
        rather than by instantiating this class directly.
        
    The object can be used the following:
    if you want to solve a formula ``pcnf``:
    
    .. code-block:: python

        >>> solver = QuAPI("/path/to/solver")
        >>> print(solver.solve(pcnf))
        True

    For configuration or assuming calls, the internal solver has to be bootstrapped with the formula.
    Thus :func:`create_internal_solver` has to be called once configuration is finished

    .. code-block:: python

        >>> solver = QuAPI("/path/to/solver")
        >>> solver.configure("conf1")
        >>> solver.configure("conf2")
        >>> ...
        >>> solver.create_internal_solver(max_assumptions=5, formula=pcnf)
        >>> #Now you can assume and solve as much as you want

    A more advanced example:

    .. code-block:: python    

        >>> solver = QuAPI("/path/to/solver")
        >>> solver.configure("--solverargument")
        >>> solver.create_internal_solver(max_assumptions=5, formula=pcnf)
        >>> solver.assume([1, 2])
        >>> print(solver.solve())
        True
        >>> solver.assume([4, 5])
        >>> print(solver.solve())
        False

    In order to use QuAPI safely, there are some things that have to be considered. 
    For example, assumptions should only be done on variables with id less or equal than ``max_assumptions``. 
    Otherwise, if the assumed variable is universial, this is trivially false. 
    Also, QuAPI might change quantifiers of the formula during initialization, making an unsound result possible if used incorrectly.
    
    PyQBF already does some usability-checks in order to avoid misleading results. 
    If you know what you are doing and actually want to use QuAPI this way, you can deactivate this checks by calling :func:`allow_unsafe`.
    Here is an example:

    .. code-block:: python

        >>> pcnf = PCNF(from_clauses=[[-4, 1, 2, 3], [-5, -1], [4, 5]])
        >>> pcnf.exists(1, 2).forall(3).exists(4, 5)
        >>> # We know that 4 and 5 are Tseitin variables simplified with Plaisted-Greenbaum
        >>> solver = QuAPI("/path/to/solver")
        >>> solver.create_internal_solver(max_assumptions=2)
        >>> solver.assume([-4])
        Traceback (most recent call last):
        ...
        RuntimeError: Trying to assume variable 4, which is out of range for max-assumption count of 2!
        >>> solver.allow_unsafe()
        >>> solver.assume([-4])
        >>> solver.assume([-5])
        >>> print(solver.solve())
        False

    """
    def __init__(self, solver_path, solver_id=None):
        self.last_result = []
        if solver_id is None:
            self.backend_id = pyqbf_cpp.init_quapi(solver_path)
        else:
            self.backend_id = pyqbf_cpp.init_quapi_with_preset(solver_id)
        self.__finalizer = weakref.finalize(self, pyqbf_cpp.release_quapi, self.backend_id)
        self.__solver_instantiated = False
        self.__max_assumptions = None
        self.__unsafe = False

    @property
    def assuming(self):
         return True
    
    def __check_alive(self):
        if not self.alive:
            print(f"Internal error: solver is already deleted at this point!", file=sys.stderr)
            return False
        else:
            return True
        
    @staticmethod
    def __formula_check_partial_normalized(formula, max_id):
        for idx, elem in enumerate(formula.prefix):
            if idx >= max_id:
                return True
            if abs(elem) != (idx + 1):
                return False
        return True
        
    def create_internal_solver(self, max_assumptions, formula, allow_missing_universal_assumptions=False):
        """
        Instantiates the internal solver with the configuration set so far

        :param max_assumptions: maximal count of assumptions allowed
        :param formula: The formula to instantiate the solver with
        :param allow_missing_universal_assumptions: if set to true, QuAPI will not terminate if universal assumptions are missing.

        :type max_assumptions: :class:`int`
        :type formula: :class:`PCNF`
        :type allow_missing_universal_assumptions: :class:`bool`
        """
        if not self.__solver_instantiated:
            if not QuAPI.__formula_check_partial_normalized(formula, max_assumptions) and not self.__unsafe:
                raise RuntimeError(f"QuAPI is not able to process non-normalized formulas when assuming (this may lead to unsafe behaviour)!")

            pyqbf_cpp.instantiate_quapi(self.backend_id, max_assumptions, formula, allow_missing_universal_assumptions)
            self.__solver_instantiated = True
            self.__max_assumptions = max_assumptions
        
    def configure(self, option):
        if not self.__solver_instantiated:
            return super().configure(option)
        else:
            raise RuntimeError("Cannot configure QuAPI after instantiation!")

    def __assume_single(self, assumption:int):
        if (abs(assumption) > self.__max_assumptions) and not self.__unsafe:
            raise RuntimeError(f"Trying to assume variable {abs(assumption)}, which is out of range for max-assumption count of {self.__max_assumptions}!")
        pyqbf_cpp.assume_quapi(self.backend_id, assumption)

    def assume(self, clause_or_lit):
        """
        Adds an assumption to the solver. This is only possible if the solver is already instantiated

        :param clause_or_lit: the literal or list of literals containing the assumption(s)
        :type clause_or_lit: :class:`int` or :class:`list[int]`        

        Usage example:

        .. code-block:: python

            >>> solver = QuAPI("/path/to/solver")
            >>> formula = PCNF(from_file="some-formula.qdimacs")
            >>> solver.create_internal_solver(5, formula)
            >>> solver.assume([1, -2, 3, -4, 5])
            >>> print(solver.solve())
            False
            >>> print(solver.solve([1, 2]))
            True
        """
        if not self.__solver_instantiated:
            raise RuntimeError("Cannot make assumptions without the internal solver being instantiated first!")
        if type(clause_or_lit) is list:
            for lit in clause_or_lit:
                self.__assume_single(lit)
        elif type(clause_or_lit) is int:
            self.__assume_single(clause_or_lit)
        else:
            raise TypeError(f"Expected int or list but got {type(clause_or_lit)}")
        self.__assume_single(0)      # close assumption

    def solve(self, formula=None, max_assumptions=0):
        """
        Interface function for the QuAPI solving

        :param formula: the formula to be solve. Only necessary if the solver was not already instantiated
        :param max_assumptions: the maximal amount of assumptions. Only necessary if the solver was not already instantiated and assumptions should be added
        :type formula: :class:`pyqbf.formula.PCNF`
        :type max_assumptions: :class:`int`

        :returns: True, if the formula is satisfiable
        :rtype: :class:`bool`

        Usage example:

        .. code-block:: python

            >>> solver = QuAPI("/path/to/solver")
            >>> formula = PCNF(from_file="some-formula.qdimacs")
            >>> solver.create_internal_solver(5, formula)
            >>> print(solver.solve())
            True
            >>> solver = QuAPI("/path/to/solver2")
            >>> print(solver.solve(formula))
            True
            >>> solver = QuAPI("/path/to/solver3")
            >>> print(solver.solve(formula, max_assumptions=2))
            True
            >>> solver.assume([1, -2])
            >>> print(solver.solve())
            False
        """
        if not self.__solver_instantiated:
            if formula is None:
                raise RuntimeError("Cannot instantiate internal solver with no provided formula!")
            self.create_internal_solver(max_assumptions, formula)
        elif formula is not None:
            raise RuntimeError("Cannot load formula after instantiating internal solver using QuAPI!")
        self.last_result =  pyqbf_cpp.solve_quapi(self.backend_id)
        return self.last_result
    

    def add_var(self, var):
       raise RuntimeError("Adding variables during runtime is not supported by QuAPI!")


    def add(self, clause):
        raise RuntimeError("Adding clauses during runtime is not supported by QuAPI!")
    
    def allow_unsafe(self):
        """
        When calling this method, all usability-checks will be disabled.

        .. warning::
            It is advised to only do this, when you know what you are doing. 
            This may allow the formula to be changed by QuAPI in an unsound way if used incorrectly!

        :returns: The current :class:`QuAPI`-class for chaining
        :rtype: :class:`QuAPI`
        """
        self.__unsafe = True
        return self


class Caqe(QuAPI):
    """
    Interface class for the usage of the Caqe-solver.
    As the original source code is Rust, the integration is done by
    using the executable with the :class:`QuAPI`-Interface
    """
    def __init__(self):
        super().__init__(None, pyqbf_cpp.SOLVER_CAQE)

    def configure(self, option):
        """
        Allows the configuration of the solver using either a string or the 
        :class:`Caqe.Configuration`-Enum

        :param option: the option to configure
        :type option: :class:`Caqe.Configuration` or :class:`str`

        Usage example:

        .. code-block:: python

            >>> s = Caqe()
            >>> s.configure(Caqe.Configuration.no_abstraction_equivalence)
            >>> s.configure("--expansion_refinement=light")
        """
        if isinstance(option, Caqe.Configuration):
            option = option.value
        super().configure(option)

    class Configuration(enum.Enum):
        """
        Enum providing a variety of configuration option for the Caqe-solver
        """
        no_abstraction_equivalence = "--abstraction-equivalence=0"
        build_conflict_clauses = "--build-conflict-clauses=1"
        def config(path):
            return f"--config={path}"
        conflict_clause_expansion = "--conflict-clause-expansion=1"
        dependency_schemes = "--dependency-schemes=1"
        expansion_refinement_none = "--expansion-refinement=none"
        expansion_refinement_light = "--expansion-refinement=light"
        expansion_refinement_0 = "--expansion-refinement=0"
        expansion_refinement_1 = "--expansion-refinement=1"
        miniscoping = "--miniscoping=1"
        strong_unsat_refinement="--strong-unsat-refinement=1"


class SolverNames(enum.Enum):
    """
    Contains all available solvers that can be instantiated by the :class:`Solver`-class
    """
    depqbf = "depqbf"
    qute = "qute"
    rareqs = "rareqs"
    qfun = "qfun"
    caqe = "caqe"


class Solver:
    """
    High-Level API for compatibility with :class:`pysat.Solver`

    :raises ReferenceError: if there is no solver matching the given name
    :raises TypeError: if one of the arguments in kwargs is not valid      
        
    :param name: The name or :class:``SolverNames``-enum of the solver to choose. Default ``"depqbf"``
    :param bootstrap_with: The formula the solver should be initialized. if None, an empty PCNF is created. Default ``None``
    :param use_timer: If true, the solver will measure how long the solving takes. Default ``False``
    :param incr: If true, the solver will be configured to allow incremental solving if possible. Default ``False``                    

    :type name: :class:`str` or :class:`SolverNames`
    :type bootstrap_with: :class:`pyqbf.formula.PCNF` or anything a PCNF can be constructed from with the ``pyqbf.formula.to_pcnf``-method
    :type use_timer: :class:`bool`
    :type incr: :class:`bool`

    Allowed kwargs:
    
    :param use_quapi: If true, the QuAPI will be used for the solver
    :param quapi_custom_path: Path to an executable for a custom QuAPI solver
    :param quapi_max_assumption_size: The maximal number of assumptions in a run. Has to be set when using quapi. Default will be the size of the prefix
    :param quapi_solver_configurations: An array of additional configuration-strings passed to the solver-backend of QuAPI
    :param quapi_allow_missing_universials: Indicates whether the usage of missing universial assumptions is permitted
    
    :type use_quapi: :class:`bool`
    :type quapi_custom_path: :class:`str`
    :type quapi_max_assumption_size: :class:`int`
    :type quapi_solver_configurations: :class:`list[str]`
    :type quapi_allow_missing_universials: :class:`bool`

    Usage example:

    .. code-block:: python

        >>> s = Solver()
        >>> s.add_clause([1, 2])
        >>> s.add_clause([-1, -2])
        >>> s.formula.forall(1).exists(2)
        >>> print(s.solve())
        True
        >>> print(s.get_model()) #no model as first block is universially quantified
        []
        >>>
        >>> f = PCNF(from_file="some-file.qdimacs")
        >>> s = Solver(name=SolverNames.qfun, bootstrap_with=f)
        >>> print(s.solve())
        False
        >>>
        >>> s = Solver(quapi_custom_path="/path/to/depqbf", use_quapi=True, quapi_max_assumption_size=5,
        ...            bootstrap_with=f, quapi_solver_configurations=[DepQBF.Configuration.qdo])
        >>>print(s.solve())
        False
        >>>
        >>> s = Solver(name=SolverNames.depqbf, use_quapi=True, bootstrap_with=f)
        ...    s.assume([1, 2])
        >>> print(s.solve())
        False
        >>>
        >>> with Solver(name=SolverNames.depqbf, incr=True) as solver:
        ...     solver.append_formula(PCNF(from_file="some-other-file.qdimacs"))
        ...     print(solver.solve())
        ...     solver.add_clause([1, 2, 3])
        ...     print(solver.solve())
        ...
        True
        False
    """
    def __init__(self, name="depqbf", bootstrap_with=None, use_timer=False, incr=False, **kwargs):
        """
        Constructor of the API. 
        """
        self.solver = None

        if bootstrap_with is None:
            bootstrap_with = PCNF()  #empty        
        elif not isinstance(bootstrap_with, PCNF):  
            bootstrap_with = to_pcnf(bootstrap_with)

        self.formula = bootstrap_with
        self.use_timer = use_timer

        self.__last = None
        self.__loaded = False
        self.calltime = 0
        self.accu_time = 0.0

        kwallowed = set(['use_quapi', 'quapi_custom_path', 'quapi_max_assumption_size', 'quapi_solver_configurations', "quapi_allow_missing_universials"])
        for arg in kwargs:
            if not arg in kwallowed:
                raise TypeError(f"Unexpected keyword argument '{arg}'")

        if isinstance(name, SolverNames):
            name = name.value

        self.name = name.lower()
        if 'use_quapi' in kwargs and kwargs['use_quapi']:
            if self.name == SolverNames.caqe.value:
                self.solver = Caqe()
            elif self.name == SolverNames.depqbf.value:
                self.solver = QuAPI(None, pyqbf_cpp.SOLVER_DEPQBF)
                self.solver.configure(DepQBF.Configuration.no_dynamic_nenofex)  #for extracting models
            elif self.name == SolverNames.qute.value:
                self.solver = QuAPI(None, pyqbf_cpp.SOLVER_QUTE)
            elif self.name == SolverNames.rareqs.value:
                self.solver = QuAPI(None, pyqbf_cpp.SOLVER_RAREQS)
            elif self.name == SolverNames.qfun.value:
                self.solver = QuAPI(None, pyqbf_cpp.SOLVER_QFUN)
            elif 'quapi_custom_path' in kwargs:
                self.solver = QuAPI(kwargs['quapi_custom_path'])
            else:
                raise RuntimeError(f"Solver {self.name} is currently not supported with QuAPIs presets! Please choose another or provide a custom path.")

            if 'quapi_solver_configurations' in kwargs:
                for arg in kwargs["quapi_solver_configurations"]:
                    self.solver.configure(arg)

            if len(self.formula.prefix) > 0 and self.formula.prefix[0] < 0:
                raise RuntimeError("QuAPI does not work with formulas, where the first quantifier block is universial!")

            allow_missing_universials = ("quapi_allow_missing_universials" in kwargs) and (kwargs["quapi_allow_missing_universials"])    
            max_assumption_size = 0
            if 'quapi_max_assumption_size' in kwargs:                
                max_assumption_size = int(kwargs['quapi_max_assumption_size'])
                
            self.solver.create_internal_solver(max_assumption_size, self.formula, allow_missing_universials)            
            self.__loaded = True

        else:
            if self.name == SolverNames.depqbf.value:
                self.solver = DepQBF()            
            elif self.name == SolverNames.qute.value:
                self.solver = Qute()
            elif name == SolverNames.rareqs.value:
                self.solver = RAReQS()
            elif name == SolverNames.qfun.value:
                self.solver = QFun()
            elif name == SolverNames.caqe.value:
                self.solver = Caqe()
            else:
                raise NoSuchSolverError(f"No solver with name {name} found!")

        if incr:
            if self.name == SolverNames.depqbf.value:
                self.solver.configure(DepQBF.Configuration.incremental_use)
                self.solver.configure(DepQBF.Configuration.dep_man_simple)                 
            else:
                raise NotImplementedError(f'Incremental mode is not supported by {self.name}.')
        
    def __del__(self):
        """
        Destructor of the API
        """
        self.delete()

    def __enter__(self):
        """
        'with' constructor
        """
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        'with' destructor
        """
        self.delete()

    def delete(self):
        """
        Manual destruction of the solver.
        Can be used for clean-up.

        .. note::

            This is not necessary if used in a ``with``-block. 
            In general, cleanup is also automatically done after the solver-variable goes out of scope.
        """
        if self.solver:
            del self.solver 
            self.solver = None
                
    def start_mode(self, warm=False):
        """
        .. warning::

            Warm-starts are not supported by QBFs
        
        :raises: :class:`NotImplementedError`
        """
        raise NotImplementedError("Warm-start mode is not implemented for QBF-solvers")

    def configure(self, *options):
        """
        Set further configuration values of the chosen solver. 
        For the available options, use the <Solver-Class>.Configuration enum to set the configuration values
    
        :param options: a vararg-list of configurations (either an element of one of the ``Configuration``-enums or :class:`str`)
        :type options: :class:`str` or :class:`enum.Enum`

        Usage example:

        .. code-block:: python

            >>> s = Solver(name=SolverNames.depqbf)
            >>> s.configure(DepQBF.Configuration.qbo)
            >>>
            >>> s = Solver(name=SolverNames.qute)
            >>> s.configure(Qute.Configuration.no_phase_saving)
            >>>
            >>> s = Solver(quapi_custom_path="/path/to/solver", use_quapi=True)
            >>> s.configure("--custom-flag")
        """
        for param in options:
            self.solver.configure(param)

    def accum_stats(self):
        """
        Get accumulated low-level stats from the solver. Currently, the statistics includes the number of restarts, conflicts, decisions, and propagations

        :returns: a dictionary containing the accumulated stats
        :rtype: :class:`dict`

        Usage example:

        .. code-block:: 

            >>> formula = PCNF(from_file="some-file.qdimacs")
            >>> with Solver(name=SolverNames.depqbf,bootstrap_with=formula) as solver:
            ...    solver.solve()
            ...    print(solver.accum_stats()) #note that depqbf does not provide conflicts
            ...
            {'restarts': 2, 'conflicts': 0, 'decisions': 254, 'propagations': 2321}
        """
        return self.solver.get_stats()
        

    def solve(self, assumptions=[]):
        """
        This method is used to check satisfiability of the internal formula

        :param assumptions: A list of literals to be assumed for this run
        :type assumptions: :class:`list[int]`

        .. note::

            If the solver does not support assumptions, it will add unit-clauses directly to the formula.
            In this case a warning will be printed, which can be disabled by setting :class:`DISABLE_WARNING_NON_ASSUMING` to ``True``

        :rtype: :class:`bool` or ``None``    

        Usage example:

        .. code-block:: python

            >>> formula = PCNF(from_file="some-file.qdimacs")
            >>> s = Solver(bootstrap_with=formula)
            >>> s.solve()
            True
            >>> s.solve([1, 2])
            False
        """
        if self.solver:
            if self.use_timer:
                start_time = time.process_time()

            if len(assumptions) > 0:
                if self.solver.assuming:
                    self.assume(assumptions)                    
                else:
                    if not DISABLE_WARNING_NON_ASSUMING:
                        print(f"WARNING, trying to use assumptions with non-assuming solver {self.name}! Assumptions are added as units instead!")
                        print(f"If you want to disable this warning, set the global 'pyqbf.solvers.DISABLE_WARNING_NON_ASSUMING'-variable to True")
                    [self.add_clause([x]) for x in assumptions]

            if self.__loaded:
                self.__last = self.solver.solve()
            else:
                self.__last = self.solver.solve(self.formula)
                self.__loaded = True

            if self.use_timer:
                self.calltime = time.process_time() - start_time
                self.accu_time += self.calltime

            return self.__last
        return None
    
    def solve_limited(self, assumptions=[], expect_interrupt=False):
        """
        .. warning::

            This function is currently unsupported

        :raises: :class:`NotImplementedError`
        """
        #TODO Implement API
        raise NotImplementedError("Currently not supported!")

    def conf_budget(self, budget=-1):
        """
        Set limit on the number of conflicts.

        :param budget: the upper bound on the number of conflicts
        :type budget: :class:`int`

        :raises: :class:`NotImplementedError`, if the solver does not support limitation of conflicts

        .. warning::
            Currently not supported by our framework
        """
        # Definetly not supported by depqbf, qute
        #TODO check other solvers
        raise NotImplementedError(f"{self.name} does not support limiting conflicts!")

    def prop_budget(self, budget):
        """
        Set limit on the number of propagations.

        :param budget: the upper bound on the number of propagatoins
        :type budget: :class:`int`

        :raises: :class:`NotImplementedError`, if the solver does not support limitation of propagations

        .. warning::

            Currently not supported by our framework
        """
        # Definetly not supported by depqbf   
        raise NotImplementedError(f"{self.name} does not support limiting propagations!")

    def dec_budget(self, budget):
        """
        Set limit on the number of decisions.

        :param budget: the upper bound on the number of decisions
        :type budget: :class:`int`

        :raises: :class:`NotImplementedError`, if the solver does not support limitation of decisions

        .. note::

            In contrast to :func:`pysat.solvers.Solver.dec_budget`, this is equivalent to setting a configuration value

        Usage example:

        .. code-block:: python

            >>> pcnf = PCNF(from_file="some-file.qdimacs")
            >>> s = Solver(name=SolverNames.depqbf, bootstrap_with=pcnf)
            >>> s.dec_budget(500)
            >>> s.solve()
            False

        """
        if self.name == SolverNames.depqbf:
            self.solver.configure(DepQBF.Configuration.max_dec(budget))        
        #TODO check other solvers
        else:
            # Definetly not supported by qute   
            raise NotImplementedError(f"{self.name} does not support limiting decisions!")

    def interrupt(self):
        """
        .. warning::

            This function is currently unsupported

        :raises: :class:`NotImplementedError`
        """
        #TODO Implement API
        raise NotImplementedError("Currently, interrupts are not supported")

    def clear_interrupt(self):
        """
        .. warning::

            This function is currently unsupported

        :raises: :class:`NotImplementedError`
        """
        #TODO Implement API
        raise NotImplementedError("Currently, interrupts are not supported")

    def propagate(self, assumptions=[], phase_saving=0):
        """
        .. warning::

            This function is currently unsupported

        :raises: :class:`NotImplementedError`
        """
        #TODO Implement API
        raise NotImplementedError(f"{self.name} does not support propgation!")

    def set_phases(self, literals=[]):
        """
        .. warning::

            This function is currently unsupported

        :raises: :class:`NotImplementedError`
        """
        #TODO check other solvers
        # Definetly not supported by depqbf
        raise NotImplementedError(f"{self.name} does not support phases")

    def process(self, **kwargs):
        """
        Preprocesses the formula. This is done by Bloqqer using the :mod:`pyqbf.process`-module

        :returns: The result if the formula was solved. Else ``None`` - in this case the internal formula is the formula retrieved from the preprocessor
        :rtype: :class:`bool` or ``None``


        Usage example:

        .. code-block:: python

            >>> pcnf = PCNF(from_clauses=[[-1, 2], [1, -2]])
            >>> pcnf.forall(1).exists(2)
            >>> s = Solver(bootstrap_with=pcnf)
            >>> print(s.process())
            True
            >>> pcnf = PCNF(from_file="formula_not_being_solved_directly.qdimacs")
            >>> s = Solver(bootstrap_with=pcnf)
            >>> print(s.process())
            None
            >>> print(s.formula)
            <Preprocessed formula>
        """
        proc = Bloqqer()
        result = proc.preprocess(self.formula)
        if isinstance(result, bool):
            return result
        else:
            self.formula = result
            return None

    def get_status(self):
        """
            Obtains the result of the previous SAT call.

            :rtype: :class:`bool` or ``None``.

            Usage example:

            .. code-block:: python

                >>> pcnf = PCNF(from_file="some-file.qdimacs")
                >>> solver = Solver(bootstrap_with=pcnf):
                >>> print(solver.solve())
                True
                >>> print(solver.get_status())
                True
        """         
        return self.__last


    def get_model(self):
        """
        Retrieves the model of the **outermost existential quantifier block**            

        :rtype: :class:`list[int]`

        Usage example:

        .. code-block:: python

            >>> pcnf = PCNF(from_clauses=[[-1, 2, 3], [1, -2, -3]])
            >>> pcnf.exists(1, 2).forall(3)
            >>> with Solver(bootstrap_with=pcnf) as solver:
            ...     solver.solve()
            ...     print(solver.get_model())
            ...
            [-1, -2]
        """
        model = []
        for var in self.formula.prefix:
            if var < 0: 
                break
            else:
                model.append(self.solver.get_assignment(var))
        return model

    def get_core(self):
        """
        Extract the unsatisfiable core of the formula

        :raises: :class:`NotImplementedError`

        .. warning::
            This is currently not supported
        """
        #TODO Implement API
        #Depqbf is able to do this with the clause group API
        raise NotImplementedError("Currently, unsat-cores are not supported")

    def get_proof(self):
        """
        Returns a proof certificate

        :raises: :class:`NotImplementedError`

        .. warning::
        
            At the moment, no included solver supports the QRAT format

        :raises: :class:`NotImplementedError`
        """
        raise NotImplementedError(f"{self.name} does not support QRAT proofs!")

    def time(self):
        """
            Get the time spent when doing the last QBF call. **Note** that the
            time is measured only if the ``use_timer`` argument was previously
            set to ``True`` when creating the solver (see :class:`Solver` for
            details).

            :returns: the time the solver took in seconds
            :rtype: float.

            Example usage:

            .. code-block:: python

                >>> pcnf = PCNF(from_file="/path/to/formula.qdimacs")
                >>> with Solver(bootstrap_with=pcnf, use_timer=True) as s:
                ...     print(s.solve())
                False
                ...     print('{0:.2f}s'.format(s.time()))
                150.16s
        """
        return self.calltime

    def time_accum(self):
        """
            Get the time spent for doing all QBF calls accumulated. **Note**
            that the time is measured only if the ``use_timer`` argument was
            previously set to ``True`` when creating the solver (see
            :class:`Solver` for details).

            :returns: the accumulated time in seconds
            :rtype: float.

            Example usage:

            .. code-block:: python

                >>> pcnf = PCNF(from_file="/path/to/formula.qdimacs")
                >>> with Solver(bootstrap_with=pcnf, use_timer=True) as s:
                ...     print(s.solve(assumptions=[1]))
                False
                ...     print('{0:.2f}s'.format(s.time()))
                1.76s
                ...     print(s.solve(assumptions=[-1]))
                False
                ...     print('{0:.2f}s'.format(s.time()))
                113.58s
                ...     print('{0:.2f}s'.format(s.time_accum()))
                115.34s
        """

        return self.accu_time

    def nof_vars(self):
        """
        Returns the number of quantified variables currently occurring in the prefix

        :rtype: :class:`int`
        """
        if self.formula:
            return len(self.formula.prefix)
        
    def nof_clauses(self):
        """
        Returns the number of clauses currently occurring in the formula

        :rtype: :class:`int`

        Usage example:

        .. code-block:: python

            >>> s = Solver(bootstrap_with=[[-1, 2], [1, -2], [1, 2]])
            >>> s.nof_clauses()
            3
        """
        if self.formula:
            return len(self.formula.clauses)
        
    def enum_models(self, assumptions=[]):  
        """
        Enumerates the models of the outermost existential quantifier block.

        .. note::
            
            This function is only supported if the solver-backend supports and is configured for incremental solving!

        Usage example:

        .. code-block:: python
        
            >>> pcnf = PCNF(from_clauses=[[-1, 2, 3], [1, -2, -3]])
            >>> pcnf.exists(1, 2).forall(3)
            >>> with Solver(incr=True, bootstrap_with=pcnf) as solver:
            ...     print(list(solver.enum_models))
            [[1, 2], [-1, -2]]
        """      
        if not self.supports_incremental():
            raise RuntimeError(f"Unable to enumerate models using a non-incremental solver!")
        done = False            
        while not done:
            self.__last = self.solve(assumptions)

            if self.__last:                                   
                model = self.get_model()
                self.add_clause([-lit for lit in model])
                yield model
            else:
                done = True                


    def add_clause(self, clause, no_return=True):
        """
            Adds a single clause to the solver.
            The optional argument ``no_return`` controls whether or not to check the formula's satisfiability after adding the new clause.

            :param clause: an iterable over literals.
            :param no_return: check solver's internal formula and return the result, if set to ``False``.

            :type clause: :class:`iterable(int)`
            :type no_return: :class:`bool`

            :rtype: bool if ``no_return`` is set to ``False``.

            Usage example:

            .. code-block:: python

                >>> pcnf = PCNF(from_file="some-file.qdimacs")
                >>> solver = Solver(bootstrap_with=pcnf)
                >>> solver.add_clause([-1, 2])
                >>> solver.add_clause([-3, 4], no_return=False)
                True

        """
        if self.solver:
            if not self.__loaded:
                self.formula.clauses.append(clause)
            elif self.supports_incremental():
                self.solver.add(clause)
            else:
                raise RuntimeError("Cannot add clauses after solving for non-incremental solvers!")
            if not no_return:
                return self.solve()
            
    def add_atmost(self, lits, k, no_return=True):
        """
        .. warning::
            This function is not supported by QBFs!

        :raises: :class:`NotImplementedError`
        """
        raise NotImplementedError("Atmost constraints are currently supported by no implemented QBF solver")    

    def add_xor_clause(self, lits, value=True):
        """
        .. warning::
            This function is not supported by QBFs!

        :raises: :class:`NotImplementedError`
        """
        raise NotImplementedError("Xor clauses are currently supported by no implemented QBF solver")    

    def append_formula(self, formula, no_return=True):
        """
            This method can be used to add a given formula into the
            solver.

            For a list of clauses, this will be added to the clause-part of the internal PCNF.
            For a PCNF or object transformed from a PCNF, the non-occurring variables will be added at the end of the prefix

            :param formula: a list of clauses or another formula convertable to :class:`pyqbf.formula.PCNF`
            :param no_return: check solver's internal formula and return the
                result, if set to ``False``. Default ``True``

            :type formula: e.g. :class:`pyqbf.formula.PCNF`
            :type no_return: :class:`bool`
            
            :rtype: :class:`bool` if ``no_return`` is set to ``False``

            Usage example:

            .. code-block:: python

                >>> pcnf = PCNF(from_file="some-file.qdimacs")
                >>> s = Solver()
                >>> s.append_formula(pcnf)
                >>> s.solve()
                True
                >>>
                >>> s = Solver()
                >>> s.append_formula(pcnf, no_return=False)
                True
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
            if not no_return:
                return self.solve()
        
    def assume(self, clause_or_lit):
        """
        Adds an assumption to the next solver-run. Only available with incremental solvers or QuAPI.        

        :param clause_or_lit: a clause of assumptions or a single assumption to be added to the solver
        :type clause_or_lit: :class:`int` or :class:`list[int]`

        :raises: :class:`RuntimeError`, if the solver does not support assumptions

        Usage example:

        .. code-block:: python

            >>> pcnf = PCNF(from_file="some-file.qdimacs")
            >>> with Solver(name=SolverNames.depqbf, bootstrap_with=pcnf) as solver:
            ...     solver.assume([1, 2])
            ...     solver.assume(3)
            ...     print(solver.solve())
            ...
            True
        """
        if not self.supports_assumptions():
            raise RuntimeError(f"{self.name} does not support assumptions!")
        self.solver.assume(clause_or_lit)

    def supports_atmost(self):
        """
        .. note::
            
            Currently, no implemented solver supports atmost-encodings

        :returns: ``False``
        :rtype: :class:`bool`
        """
        return False

    def supports_incremental(self):
        """
        Indicates whether the solver supports incremental solving

        :returns: ``True`` if incremental solving is supported
        :rtype: :class:`bool`
        """
        return isinstance(self.solver, pyqbf_incremental_solver)
    
    def supports_assumptions(self):
        """
        Indicates whether the solver supports assumptions

        :returns: ``True`` if assumptions are supported
        :rtype: :class:`bool`
        """
        return self.solver.assuming
    

#------------------------------------------------------
#-----------------------KISS-API-----------------------
#------------------------------------------------------
def solve(formula):
    """
    Providing the most basic functionality one would expect: solving the given formula.
    If the only goal is solving a provided formula without thinking about which solver or configuration, this function may be used.

    :param formula: the formula to be solve
    :type formula: :class:`pyqbf.formula.PCNF`

    :returns: ``True`` if the formula is satisfiable
    :rtype: :class:`bool`

    Usage example:

    .. code-block:: python

        >>> pcnf = PCNF(from_file="some-file.qdimacs")
        >>> print(solve(pcnf))
        True            
    """
    return pyqbf_cpp.solve(formula)

def solve_file(target):
    """
    Loads the formula from a given target and solves it.

    :param target: a path to the formula
    :type target: :class:`str`

    :returns: ``True`` if the formula provided in the file is satisfiable
    :rtype: :class:`bool`

    Usage example:

    .. code-block:: python

        >>> print(solve_file("some-file.qdimacs"))
        True      
    """
    formula = PCNF(from_file=target)
    return solve(formula)

def solve_all_files(targets):
    """
    Loads the formulas from a given list of targets and solves them.
    
    :param target: a list of paths to the formulas
    :type target: :class:`list[str]`

    :returns: A dictionary containing the corresponding result from solving
    :rtype: :class:`dict[str,bool]`


    Usage example:

    .. code-block:: python

        >>> targets = ["some-file.qdimacs", "some-other-file.qdimacs", "another-file.qdimacs"]
        >>> print(solve_all_files(targets))
        {"some-file.qdimacs": True, "some-other-file.qdimacs": False, "another-file.qdimacs": True}
    """
    results = {}
    for target in targets:
        results[target] = solve_file(target)
    return results


def any_incremental_solver(bootstrap_with=None):
    """
    Provides a pre-configured solver for incremental solving.    
    If the only goal is getting an incremental solver without thinking about which solver or configuration, this function may be used.

    :param bootstrap_with: The formula to be solved. If none is provided, an empty formula is used.
    
    :returns: The preconfigured solver
    :rtype: :class:`Solver`

    Usage example:
    
    .. code-block:: python

        >>> formula = PCNF(from_file="some-file.qdimacs")
        >>> solver = any_incremental_solver(formula)
        >>> print(solver.solve())
        True
        >>> solver.add_clause([-1,2])
        >>> print(solver.solve())
        True
        >>> solver.append_formula(PCNF(from_clauses=[[1,-2]]))
        >>> print(solver.solve())
        False
    """
    return Solver(SolverNames.depqbf, bootstrap_with=bootstrap_with, incr=True)


class AssumingEnvironment:
    """
        An simple, high-level API for solving with assumptions

        :param formula: the target-formula to be solved with assumptions
        :type formula: :class:`pyqbf.formula.PCNF`

        Usage example:

        .. code-block:: python

            >>> formula = PCNF(from_file="formula.qdimacs") 
            >>> with AssumingEnvironment(formula) as solver:
            ...     print(solver.solve())                   #solve without assumptions
            ...     print(solver.solve([-1, 2, 3, 4, 5]))   #solve with specified assumptions
            ...     print(solver.solve([1, 2, -3]))         #solve with specified assumptions
            True
            False
            True
    """
    def __init__(self, formula):
        """
        Constructor for Assuming Environment
        """
        self.solver = DepQBF()
        self.solver.load(formula)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        'with' destructor
        """
        if self.solver:
            del self.solver
        self.solver = None

    def solve(self, assumptions = []):
        """
        Solves the formula with the provided assumptions.
        If no assumptions are provided, the original formula is solved

        :param assumptions: a list of assumptions
        :type assumptions: :class:`list[int]`

        :returns: ``True``, if the formula is satisfiable under these assumptions
        :rtype: :class:`bool`

        Usage example:

        .. code-block:: python

            >>> formula = PCNF(from_file="formula.qdimacs", auto_generate_prefix=True) 
            >>> with AssumingEnvironment(formula) as solver:
            ...     print(solver.solve())                   #solve without assumptions
            ...     print(solver.solve([-1, 2, 3, 4, 5]))   #solve with specified assumptions
            ...     print(solver.solve([1, 2, -3]))         #solve with specified assumptions
            True
            False
            True
        """
        if len(assumptions) > 0:
            self.solver.assume(assumptions)
        return self.solver.solve()    
