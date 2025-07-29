"""
Unit tests for the pyqbf framework
"""

import unittest
import sys
import os
import pathlib

from pyqbf.formula import PCNF, to_pcnf, split_atoms_and_auxvars, QUANTIFIER_EXISTS, QUANTIFIER_FORALL, QUANTIFIER_NONE, OUTERMOST_BLOCK, INNERMOST_BLOCK
from pyqbf.solvers import Solver, DepQBF, Qute, RAReQS, QFun, QuAPI, Caqe, SolverNames, solve, solve_file, solve_all_files, any_incremental_solver, AssumingEnvironment
from pyqbf.process import Processor, Bloqqer
from pyqbf.proof import QratProof, QratLemma, QratType
import pyqbf_cpp
from pysat.card import CardEnc
from pysat.formula import CNF, Atom, Formula
from qbcircuit import QBCircuit, FormulaGenerator

SOLVERS = [pyqbf_cpp.SOLVER_DEPQBF, pyqbf_cpp.SOLVER_QUTE, pyqbf_cpp.SOLVER_RAREQS, pyqbf_cpp.SOLVER_QFUN]

def warn(msg):
    print('\033[93m' + msg + '\033[0m')


TESTDATA_FOLDER = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
TESTDATA_FORMULA1 = os.path.join(TESTDATA_FOLDER, "formula1.qdimacs")
TESTDATA_FORMULA1_DIMACS = os.path.join(TESTDATA_FOLDER, "formula1.dimacs")
TESTDATA_HALFADDER = os.path.join(TESTDATA_FOLDER, "half_adder.qdimacs")
TESTDATA_HALFADDER_AIG = os.path.join(TESTDATA_FOLDER, "half_adder.aag")

# Interface
class TestPyQbfInterface(unittest.TestCase):
    def test_python_structure(self):
        def check_formula(sut):            
            
            self.assertEqual(sut.nv, 5)
            self.assertEqual(sut.var_type(1), QUANTIFIER_EXISTS)
            self.assertEqual(sut.var_type(2), QUANTIFIER_EXISTS)
            self.assertEqual(sut.var_type(3), QUANTIFIER_FORALL)
            self.assertEqual(sut.var_type(4), QUANTIFIER_FORALL)
            self.assertEqual(sut.var_type(5), QUANTIFIER_FORALL)
            self.assertEqual(len(sut.clauses), 3) 
            self.assertEqual(sut[0], [-1, 2])
            self.assertEqual(sut[1], [2, -3, -4])
            self.assertEqual(sut[2], [1, -5])

        # From code
        sut = PCNF(from_clauses=[[-1, 2], [2, -3, -4], [1,-5]])
        sut.exists(1,2)
        sut.forall(3,4,5)
        check_formula(sut)
        
        # From file
        sut = PCNF(from_file=TESTDATA_FORMULA1)
        check_formula(sut)

        # From file pointer
        with open(TESTDATA_FORMULA1, "r") as fp:
            sut = PCNF(from_fp=fp)
            check_formula(sut)

        # From string    
        content = ""
        with open(TESTDATA_FORMULA1, "r") as fp:
            content = fp.read()    
        sut = PCNF(from_string=content)
        check_formula(sut)

        # copy
        sut2 = sut.copy()
        sut.prefix = []     # reset formula to check deepcopy
        sut.clauses = []
        check_formula(sut2)    
        sut = sut2

        # negate
        negated = sut.negate()                 #negation with tseitin transformation and negation of quantifier block
        self.assertEqual(negated.nv, 8)
        self.assertEqual(negated.var_type(1), -1)
        self.assertEqual(negated.var_type(2), -1)
        self.assertEqual(negated.var_type(3), 1)
        self.assertEqual(negated.var_type(4), 1)
        self.assertEqual(negated.var_type(5), 1)
        self.assertEqual(len(negated.clauses), 8) 
        self.assertEqual(negated[0], [1, -6])          # [-1, 2] => [1, -6] [-2, -6]
        self.assertEqual(negated[1], [-2, -6])         
        self.assertEqual(negated[2], [-2, -7])         # [2, -3, -4] => [-2, -7] [3, -7] [4, -7]
        self.assertEqual(negated[3], [3, -7])
        self.assertEqual(negated[4], [4, -7])
        self.assertEqual(negated[5], [-1, -8])         # [1, -5] => [-1, -8] [5, -8]
        self.assertEqual(negated[6], [5, -8])
        self.assertEqual(negated[7], [6,7,8])          # all equivalences have to hold

        # set quantifier
        sut2 = sut.copy()
        sut2.set_quantifier(1,QUANTIFIER_FORALL)
        self.assertEqual(sut2.nv, 5)
        self.assertEqual(sut2.var_type(1), QUANTIFIER_FORALL)
        self.assertEqual(sut2.var_type(2), QUANTIFIER_EXISTS)
        self.assertEqual(sut2.var_type(3), QUANTIFIER_FORALL)
        self.assertEqual(sut2.var_type(4), QUANTIFIER_FORALL)
        self.assertEqual(sut2.var_type(5), QUANTIFIER_FORALL)

        # flip_quantifier
        sut3 = sut.copy()
        sut3.flip_quantifier(1)
        self.assertEqual(sut3.nv, 5)
        self.assertEqual(sut3.var_type(1), QUANTIFIER_FORALL)
        self.assertEqual(sut3.var_type(2), QUANTIFIER_EXISTS)
        self.assertEqual(sut3.var_type(3), QUANTIFIER_FORALL)
        self.assertEqual(sut3.var_type(4), QUANTIFIER_FORALL)
        self.assertEqual(sut3.var_type(5), QUANTIFIER_FORALL)
        sut3.flip_quantifier(2, 3, 4)
        self.assertEqual(sut3.nv, 5)
        self.assertEqual(sut3.var_type(1), QUANTIFIER_FORALL)
        self.assertEqual(sut3.var_type(2), QUANTIFIER_FORALL)
        self.assertEqual(sut3.var_type(3), QUANTIFIER_EXISTS)
        self.assertEqual(sut3.var_type(4), QUANTIFIER_EXISTS)
        self.assertEqual(sut3.var_type(5), QUANTIFIER_FORALL)
        sut3.flip_quantifier(4, 5)
        self.assertEqual(sut3.nv, 5)
        self.assertEqual(sut3.var_type(1), QUANTIFIER_FORALL)
        self.assertEqual(sut3.var_type(2), QUANTIFIER_FORALL)
        self.assertEqual(sut3.var_type(3), QUANTIFIER_EXISTS)
        self.assertEqual(sut3.var_type(4), QUANTIFIER_FORALL)
        self.assertEqual(sut3.var_type(5), QUANTIFIER_EXISTS)


    def test_to_pcnf_call(self):
        import pysat.formula as pyf
        cnf = pyf.CNF(from_clauses=[[1,2,3], [-1, 2], [-2, 3]])
        pcnf = to_pcnf(cnf)
        self.assertEqual(len(pcnf.prefix), 3)
        self.assertEqual(pcnf.clauses[0], [1,2,3])
        self.assertEqual(pcnf.clauses[1], [-1,2])
        self.assertEqual(pcnf.clauses[2], [-2,3])
        self.assertEqual(pcnf.nv, 3)

    def test_cpp_pcnf_to_lit_list(self):
        sut = PCNF(from_clauses=[[1,2], [3,4], [5,6]])
        lit_list = pyqbf_cpp.pcnf_to_lit_list(sut)
        self.assertListEqual(lit_list, [1,2,0,3,4,0,5,6,0])

    def test_cpp_solve_default(self):
        sut = PCNF(from_file=TESTDATA_FORMULA1)
        self.assertTrue(pyqbf_cpp.solve(sut))

        sut = PCNF(from_clauses=[[1], [-1]])
        sut.forall(1)
        self.assertFalse(pyqbf_cpp.solve(sut))

    def test_cpp_solve_formula1(self):
        for solver in SOLVERS:
            sut = PCNF(from_file=TESTDATA_FORMULA1)
            s = pyqbf_cpp.init_solver(solver)
            self.assertTrue(pyqbf_cpp.solve(sut,s))
            pyqbf_cpp.release_solver(s)    

    def test_cpp_solve_simple_refutable(self):
        for solver in SOLVERS:
            sut = PCNF(from_clauses=[[1], [-1]])
            sut.forall(1)            
            s = pyqbf_cpp.init_solver(solver)
            self.assertFalse(pyqbf_cpp.solve(sut,s))
            pyqbf_cpp.release_solver(s)            


class TestFormulaClass(unittest.TestCase):
    def test_unusual_formulas(self):
        pcnf = PCNF(from_clauses=[])
        self.assertEqual(pcnf.nv, 0)
        self.assertEqual(len(pcnf.clauses), 0)

        pcnf = PCNF(from_string="p cnf 0 0\n")
        self.assertEqual(pcnf.nv, 0)
        self.assertEqual(len(pcnf.clauses), 0)
        
        pcnf = PCNF(from_clauses=[[]])
        self.assertEqual(pcnf.nv, 0)
        self.assertEqual(len(pcnf.clauses), 1)
        self.assertEqual(len(pcnf.clauses[0]), 0)

        pcnf = PCNF(from_string="p cnf 0 1\n0\n")
        self.assertEqual(pcnf.nv, 0)
        self.assertEqual(len(pcnf.clauses), 1)
        self.assertEqual(len(pcnf.clauses[0]), 0)
        
        pcnf = PCNF(from_string="p cnf 2 3\na 1 0\ne 2 0\n1 -2 0\n0\n-1 2 0\n")
        self.assertEqual(pcnf.nv, 2)
        self.assertEqual(len(pcnf.clauses), 3)


    def test_forall_exists(self):
        pcnf = PCNF(from_clauses=[[1, 2, 3, 4, 5, 6, 7, 8]])
        pcnf.forall(1).exists(2).forall(3)
        self.assertEqual(pcnf.prefix, [-1, 2, -3])
        pcnf.exists(4, block=OUTERMOST_BLOCK)
        self.assertEqual(pcnf.prefix, [4, -1, 2, -3])
        pcnf.forall(5, block=1)
        self.assertEqual(pcnf.prefix, [4, -5, -1, 2, -3])
        pcnf.exists(5, block=2)
        self.assertEqual(pcnf.prefix, [4, -1, 5, 2, -3])
        pcnf.exists(6, block=INNERMOST_BLOCK)
        self.assertEqual(pcnf.prefix, [4, -1, 5, 2, -3, 6])
        pcnf.exists(7, block=4)
        self.assertEqual(pcnf.prefix, [4, -1, 5, 2, -3, 7, 6])
        pcnf.forall(8, block=10)
        self.assertEqual(pcnf.prefix, [4, -1, 5, 2, -3, 7, 6, -8])

    def test_block_edgecases(self):
        pcnf = PCNF(from_clauses=[[1, 2, 3, 4, 5]])
        # empty prefix
        self.assertEqual(pcnf.count_quantifier_alternations(), 0)
        self.assertEqual(pcnf.innermost_block(), [])
        self.assertEqual(pcnf.innermost_block(QUANTIFIER_EXISTS), [])
        self.assertEqual(pcnf.innermost_block(QUANTIFIER_FORALL), [])
        self.assertEqual(pcnf.outermost_block(), [])
        self.assertEqual(pcnf.outermost_block(QUANTIFIER_EXISTS), [])
        self.assertEqual(pcnf.outermost_block(QUANTIFIER_FORALL), [])
        self.assertEqual(pcnf.get_block(OUTERMOST_BLOCK), [])
        self.assertEqual(pcnf.get_block(INNERMOST_BLOCK), [])
        self.assertEqual(pcnf.get_block(0), [])
        self.assertEqual(pcnf.get_block(100), [])
        self.assertEqual(pcnf.get_block_type(OUTERMOST_BLOCK), QUANTIFIER_NONE)
        self.assertEqual(pcnf.get_block_type(INNERMOST_BLOCK), QUANTIFIER_NONE)
        self.assertEqual(pcnf.get_block_type(0), QUANTIFIER_NONE)
        self.assertEqual(pcnf.get_block_type(100), QUANTIFIER_NONE)       

        # existential prefix
        pcnf.exists(1, 2)
        self.assertEqual(pcnf.count_quantifier_alternations(), 0)
        self.assertEqual(pcnf.innermost_block(), [1,2])
        self.assertEqual(pcnf.innermost_block(QUANTIFIER_EXISTS), [1,2])
        self.assertEqual(pcnf.innermost_block(QUANTIFIER_FORALL), [])
        self.assertEqual(pcnf.outermost_block(), [1,2])
        self.assertEqual(pcnf.outermost_block(QUANTIFIER_EXISTS), [1,2])
        self.assertEqual(pcnf.outermost_block(QUANTIFIER_FORALL), [])
        self.assertEqual(pcnf.get_block(OUTERMOST_BLOCK), [1,2])
        self.assertEqual(pcnf.get_block(INNERMOST_BLOCK), [1,2])
        self.assertEqual(pcnf.get_block(0), [1,2])
        self.assertEqual(pcnf.get_block(1), [])
        self.assertEqual(pcnf.get_block(100), [])
        self.assertEqual(pcnf.get_block_type(OUTERMOST_BLOCK), QUANTIFIER_EXISTS)
        self.assertEqual(pcnf.get_block_type(INNERMOST_BLOCK), QUANTIFIER_EXISTS)
        self.assertEqual(pcnf.get_block_type(0), QUANTIFIER_EXISTS)
        self.assertEqual(pcnf.get_block_type(1), QUANTIFIER_NONE)
        self.assertEqual(pcnf.get_block_type(100), QUANTIFIER_NONE)       

        # universal prefix
        pcnf.flip_quantifier(1, 2)
        self.assertEqual(pcnf.prefix, [-1, -2])
        self.assertEqual(pcnf.count_quantifier_alternations(), 0)
        self.assertEqual(pcnf.innermost_block(), [-1,-2])
        self.assertEqual(pcnf.innermost_block(QUANTIFIER_EXISTS), [])
        self.assertEqual(pcnf.innermost_block(QUANTIFIER_FORALL), [-1,-2])
        self.assertEqual(pcnf.outermost_block(), [-1,-2])
        self.assertEqual(pcnf.outermost_block(QUANTIFIER_EXISTS), [])
        self.assertEqual(pcnf.outermost_block(QUANTIFIER_FORALL), [-1,-2])
        self.assertEqual(pcnf.get_block(OUTERMOST_BLOCK), [-1,-2])
        self.assertEqual(pcnf.get_block(INNERMOST_BLOCK), [-1,-2])
        self.assertEqual(pcnf.get_block(0), [-1,-2])
        self.assertEqual(pcnf.get_block(1), [])
        self.assertEqual(pcnf.get_block(100), [])
        self.assertEqual(pcnf.get_block_type(OUTERMOST_BLOCK), QUANTIFIER_FORALL)
        self.assertEqual(pcnf.get_block_type(INNERMOST_BLOCK), QUANTIFIER_FORALL)
        self.assertEqual(pcnf.get_block_type(0), QUANTIFIER_FORALL)
        self.assertEqual(pcnf.get_block_type(1), QUANTIFIER_NONE)
        self.assertEqual(pcnf.get_block_type(100), QUANTIFIER_NONE)     


    def test_normalization(self):
        f = PCNF(from_clauses=[[-1, 2], [-2, 3], [-3, 1]])
        self.assertFalse(f.is_normalized)
        f.prefix_from_clauses()
        self.assertTrue(f.is_normalized)

        f = PCNF(from_clauses=[[-2, 4], [-4, 6], [-6, 2]])
        self.assertFalse(f.is_normalized)
        f.prefix_from_clauses()
        self.assertFalse(f.is_normalized)
        f.normalize()
        self.assertTrue(f.is_normalized)

    def test_negation(self):
        f = PCNF(from_clauses=[[1, 2], [3]], auto_generate_prefix=True)
        neg = f.negate()
        self.assertEqual(neg.clauses, [[-1, -4], [-2, -4], [4, -3]])
        self.assertEqual(neg.prefix, [-1, -2, -3, 4])
        self.assertEqual(neg.enclits, [4, -3])
        self.assertEqual(neg.auxvars, [4])

        f2 = neg.negate()
        self.assertEqual(f2.clauses, [[1, 2], [3]])
        self.assertEqual(f2.prefix, [1, 2, 3])
        self.assertEqual(f2.nv, 3)
        self.assertFalse(hasattr(f2, "enclits"))
        self.assertFalse(hasattr(f2, "auxvars"))

        neg.clauses.append([1,2,3])
        f3 = neg.negate()
        self.assertEqual(f3.clauses, [[1, -5], [4, -5], \
                                      [2, -6], [4, -6], \
                                      [-4, -7], [3, -7], \
                                      [-1, -8], [-2, -8], [-3, -8], \
                                      [5, 6, 7, 8]])
        self.assertEqual(f3.prefix, [1, 2, 3, -4, 5, 6, 7, 8])
        self.assertEqual(f3.nv, 8)
        self.assertEqual(f3.enclits, [5, 6, 7, 8])
        self.assertEqual(f3.auxvars, [5, 6, 7, 8])
        
    def test_sorting(self):
        pcnf = PCNF(from_clauses=[[1, 2], [-3, 4], [1, -3], [2, 4]])
        pcnf.forall(4).exists(3).forall(2, 1)
        self.assertEqual(pcnf.var_order_relation(), [None, 4, 3, 2, 1])
        pcnf.sort_clauses()
        self.assertEqual(pcnf.clauses, [[2, 1], [4, -3], [-3, 1], [4, 2]])

        pcnf = PCNF(from_clauses=[[1, 2], [-3, 4], [1, -3], [2, 4]])
        self.assertEqual(pcnf.var_order_relation(), [None, None, None, None, None])
        pcnf.sort_clauses()
        self.assertEqual(pcnf.clauses, [[1, 2], [-3, 4], [1, -3], [2, 4]])


SOLVER_FACTORIES = [(lambda: DepQBF()), (lambda: Qute()), (lambda: RAReQS()), (lambda: QFun()), (lambda: Caqe())]
class TestSolverClasses(unittest.TestCase):
    def test_solve_formula1(self):
        for sf in SOLVER_FACTORIES:
            solver = sf()
            sut = PCNF(from_file=TESTDATA_FORMULA1)
            self.assertTrue(solver.solve(sut))       

    def test_multiple_solve_call_depqbf(self):
        solver = DepQBF()
        sut = PCNF(from_clauses=[[-1, 2], [2, -3, -4], [1,-5]])
        sut.exists(1,2)
        sut.forall(3,4,5)
        self.assertTrue(solver.solve(sut))
        sut2 = PCNF(from_clauses=[[1,2], [1,-2], [-1]], auto_generate_prefix=True)
        try:
            solver.solve(sut2)
            self.assertTrue(False, "DepQBF should raise an error if load is called multiple times!")
        except RuntimeError:            
            pass

    def test_multiple_solve_call_qute(self):
        solver = Qute()
        sut = PCNF(from_clauses=[[-1, 2], [2, -3, -4], [1,-5]])
        sut.exists(1,2)
        sut.forall(3,4,5)
        self.assertTrue(solver.solve(sut))
        sut2 = PCNF(from_clauses=[[1,2], [1,-2], [-1]], auto_generate_prefix=True)
        self.assertFalse(solver.solve(sut2))

    def test_multiple_solve_call_rareqs(self):
        solver = RAReQS()
        sut = PCNF(from_clauses=[[-1, 2], [2, -3, -4], [1,-5]])
        sut.exists(1,2)
        sut.forall(3,4,5)
        self.assertTrue(solver.solve(sut))
        sut2 = PCNF(from_clauses=[[1,2], [1,-2], [-1]], auto_generate_prefix=True)
        self.assertFalse(solver.solve(sut2))

    def test_multiple_solve_call_qfun(self):
        solver = QFun()
        sut = PCNF(from_clauses=[[-1, 2], [2, -3, -4], [1,-5]])
        sut.exists(1,2)
        sut.forall(3,4,5)
        self.assertTrue(solver.solve(sut))
        sut2 = PCNF(from_clauses=[[1,2], [1,-2], [-1]], auto_generate_prefix=True)
        self.assertFalse(solver.solve(sut2))

    def test_multiple_solve_call_caqe(self):
        solver = Caqe()
        sut = PCNF(from_clauses=[[-1, 2], [2, -3, -4], [1,-5]])
        sut.exists(1,2)
        sut.forall(3,4,5)
        self.assertTrue(solver.solve(sut))
        sut2 = PCNF(from_clauses=[[1,2], [1,-2], [-1]], auto_generate_prefix=True)
        try:
            self.assertFalse(solver.solve(sut2))
            self.assertTrue(False, "Caqe should raise an error if load is called multiple times!")
        except RuntimeError:
            pass


class TestSolverConfigurations(unittest.TestCase):
    def test_solver_config_qute(self):
        solver = Qute()
        solver.configure(Qute.Configuration.phase_heuristic_qtype)
        solver.configure(Qute.Configuration.initial_clause_DB_size(2000))
        solver.configure(Qute.Configuration.restarts_ema)
        solver.configure(Qute.Configuration.alpha("4e-5"))
        solver.configure(Qute.Configuration.minimum_distance(40))
        solver.configure(Qute.Configuration.threshold_factor(1.5))
        solver.configure(Qute.Configuration.decision_heuristic_VSIDS)
        solver.configure(Qute.Configuration.tiebreak_more_secondary)
        solver.configure(Qute.Configuration.no_phase_saving)
        solver.configure(Qute.Configuration.var_activity_decay(0.85))
        solver.configure(Qute.Configuration.var_activity_inc(2))
        sut = PCNF(from_clauses=[[-1, 2], [2, -3, -4], [1,-5]])
        sut.exists(1,2)
        sut.forall(3,4,5)
        self.assertTrue(solver.solve(sut))

        solver = Qute()
        exception_thrown = False
        try:
            solver.configure("Not a configuration")
        except RuntimeError:
            exception_thrown = True
        self.assertTrue(exception_thrown, "No exception was thrown when using an invalid configuration")            


class TestincrementalSolverClasses(unittest.TestCase):
    def test_solve_incremental(self):
        solver = DepQBF()
        solver.configure("--incremental-use")
        solver.configure("--dep-man=simple")
        self.assertTrue(solver.alive)
        sut = PCNF(from_clauses=[[1,2], [-1,2],[1,-2]])
        sut.exists(1,2)
        self.assertTrue(solver.solve(sut))
        solver.add([-1,-2])
        self.assertFalse(solver.solve())

    def test_push_pop_incremental(self):
        solver = DepQBF()
        solver.configure("--incremental-use")
        solver.configure("--dep-man=simple")
        self.assertTrue(solver.alive)
        sut = PCNF(from_clauses=[[1,2]])        
        sut.exists(1,2)       
        self.assertTrue(solver.solve(sut))
        solver.push()
        solver.add([-1,2])
        solver.add([1,-2])
        self.assertTrue(solver.solve())
        solver.push()
        solver.add([-1,-2])
        self.assertFalse(solver.solve())
        solver.pop()
        self.assertTrue(solver.solve())

    def test_assume_incremental(self):
        solver = DepQBF()
        solver.configure("--incremental-use")
        solver.configure("--dep-man=simple")
        self.assertTrue(solver.alive)
        sut = PCNF(from_clauses=[[1,2], [1,-2]])
        sut.exists(1)
        sut.forall(2)
        solver.assume(-1)
        self.assertFalse(solver.solve(sut))
        self.assertTrue(solver.solve())


class TestQuAPI(unittest.TestCase):
    def test_solve_formula1_caqe(self):
        sut = PCNF(from_file=TESTDATA_FORMULA1)
        solver = QuAPI(None, pyqbf_cpp.SOLVER_CAQE)
        self.assertTrue(solver.solve(sut))

        solver = Caqe()
        self.assertEqual(solver.solve(sut), True)

    def test_solve_formula1_depqbf(self):
        sut = PCNF(from_file=TESTDATA_FORMULA1)
        solver = QuAPI(None, pyqbf_cpp.SOLVER_DEPQBF)
        self.assertTrue(solver.solve(sut))

    def test_solve_formula1_rareqs(self):
        sut = PCNF(from_file=TESTDATA_FORMULA1)
        solver = QuAPI(None, pyqbf_cpp.SOLVER_RAREQS)
        self.assertTrue(solver.solve(sut))   
        
    def test_solve_formula1_qute(self):
        sut = PCNF(from_file=TESTDATA_FORMULA1)
        solver = QuAPI(None, pyqbf_cpp.SOLVER_QUTE)
        solver.create_internal_solver(1, sut)
        solver.assume([1])
        self.assertTrue(solver.solve())   

    def test_solve_formula1_qfun(self):
        sut = PCNF(from_file=TESTDATA_FORMULA1)
        solver = QuAPI(None, pyqbf_cpp.SOLVER_QFUN)
        self.assertTrue(solver.solve(sut))   

    def test_assumptions(self):
        sut = PCNF(from_file=TESTDATA_FORMULA1)
        solver = Caqe()
        solver.create_internal_solver(5, sut)
        solver.assume([-1,2,3,4,5])
        self.assertFalse(solver.solve())
        solver.assume([1,2,-3,-4,-5])
        self.assertTrue(solver.solve())

    def test_configuration_caqe(self):
        sut = PCNF(from_file=TESTDATA_FORMULA1)
        solver = Caqe()
        solver.configure(Caqe.Configuration.miniscoping)
        solver.configure(Caqe.Configuration.conflict_clause_expansion)
        solver.create_internal_solver(5, sut)
        solver.assume([-1,2,3,4,5])
        self.assertFalse(solver.solve())
        solver.assume([1,2,-3,-4,-5])
        self.assertTrue(solver.solve())

    def test_configuration_depqbf(self):
        sut = PCNF(from_file=TESTDATA_FORMULA1)
        solver = QuAPI(None, pyqbf_cpp.SOLVER_DEPQBF)
        solver.configure(DepQBF.Configuration.dep_man_simple)
        solver.configure(DepQBF.Configuration.incremental_use)            
        self.assertEqual(solver.solve(sut), True)       

    def test_with_universial_variables(self):
        sut = PCNF(from_clauses=[[-1, 2], [2, 3], [3, -1]])
        sut.prefix_from_clauses(QUANTIFIER_FORALL)
        with Caqe() as solver:
            solver.create_internal_solver(2, sut)        
            solver.assume([-1, 2])
            self.assertTrue(solver.solve())
            solver.assume([1])
            self.assertFalse(solver.solve())
            # with 0 this would cause an error as QUAPI_ALLOW_MISSING_UNIVERSAL_ASSUMPTIONS is not set
            
        with Caqe() as solver:
            solver.create_internal_solver(2, sut, True)        
            self.assertTrue(solver.solve())

        sut.prefix_from_clauses()  #existentially quantified they are always ok
        with Caqe() as solver:
            solver.create_internal_solver(2, sut)        
            self.assertTrue(solver.solve())


class TestKISS(unittest.TestCase):
    def test_solve(self):
        formula = PCNF(from_clauses=[[1,2,3], [-1,2,3]], auto_generate_prefix=True)
        self.assertTrue(solve(formula))
        self.assertTrue(solve_file(TESTDATA_FORMULA1))

        result = solve_all_files([TESTDATA_FORMULA1, TESTDATA_HALFADDER])
        self.assertTrue(result[TESTDATA_FORMULA1])
        self.assertTrue(result[TESTDATA_HALFADDER])

    def test_incremental_solver(self):
        formula = PCNF(from_clauses=[[1,2], [-1,-2]], auto_generate_prefix=True)
        with any_incremental_solver(formula) as solver:
            self.assertTrue(solver.solve())
            solver.add_clause([-1,2])
            self.assertTrue(solver.solve())
            solver.append_formula(PCNF(from_clauses=[[1,-2]]))
            self.assertFalse(solver.solve())

    def test_assumption_environment(self):
        formula = PCNF(from_file=TESTDATA_FORMULA1) 
        with AssumingEnvironment(formula) as solver:
            self.assertTrue(solver.solve())
            self.assertFalse(solver.solve([-1,2,3,4,5]))
            self.assertTrue(solver.solve([1,2,-3,-4,-5]))


class TestPreprocessorClasses(unittest.TestCase):
    def test_preprocess_formula1(self):
        proc = Bloqqer()
        sut = PCNF(from_file=TESTDATA_FORMULA1)       
        self.assertTrue(proc.preprocess(sut))


class TestProofClasses(unittest.TestCase):
    def test_qrat_proof(self):
        proof = QratProof(from_string="1 -2 0\nd 1 -2 0\nu -2 1 0\n")
        self.assertEqual(len(proof.lemmas), 3) 
        self.assertEqual(proof[0].type, QratType.QRATA)
        self.assertEqual(proof[0].clause, [1, -2])
        self.assertEqual(proof[0].pivot, 1)
        self.assertEqual(proof[1].type, QratType.QRATE)
        self.assertEqual(proof[1].clause, [1, -2])
        self.assertEqual(proof[1].pivot, 1)
        self.assertEqual(proof[2].type, QratType.QRATU)
        self.assertEqual(proof[2].clause, [-2, 1])
        self.assertEqual(proof[2].pivot, -2)

    def test_qrat_proof_with_comment(self):
        proof = QratProof(from_string="1 -2 0 added clause\nd 1 -2 0 deleted clause\nu -2 1 0 universal reduction\n")
        self.assertEqual(len(proof.lemmas), 3) 
        self.assertEqual(proof[0].type, QratType.QRATA)
        self.assertEqual(proof[0].clause, [1, -2])        
        self.assertEqual(proof[0].pivot, 1)
        self.assertEqual(proof[1].type, QratType.QRATE)
        self.assertEqual(proof[1].clause, [1, -2])
        self.assertEqual(proof[1].pivot, 1)
        self.assertEqual(proof[2].type, QratType.QRATU)
        self.assertEqual(proof[2].clause, [-2, 1])
        self.assertEqual(proof[2].pivot, -2)
        
        self.assertEqual(len(proof.comments), 3)
        self.assertEqual("added clause", proof.comments[0])
        self.assertEqual("deleted clause", proof.comments[1])
        self.assertEqual("universal reduction", proof.comments[2])

    def test_qrat_proof_add_lemmas(self):
        proof = QratProof(from_string="1 -2 0")
        self.assertEqual(len(proof), 1)
        self.assertEqual(proof[0].type, QratType.QRATA)
        self.assertEqual(proof[0].clause, [1, -2])
        self.assertEqual(proof[0].pivot, 1)
        proof.add(QratType.QRATE, [1, -2])
        self.assertEqual(len(proof), 2)
        self.assertEqual(proof[1].type, QratType.QRATE)
        self.assertEqual(proof[1].clause, [1, -2])
        self.assertEqual(proof[1].pivot, 1)
        proof.add(QratType.QRATU, [-2, 1])
        self.assertEqual(len(proof), 3)
        self.assertEqual(proof[2].type, QratType.QRATU)
        self.assertEqual(proof[2].clause, [-2, 1])
        self.assertEqual(proof[2].pivot, -2)


SOLVER_FOR_PYSAT = [SolverNames.depqbf]
SPEEDY = True

from tests_pysat import test_accum_stats
from tests_pysat import test_atmost
from tests_pysat import test_atmost1
from tests_pysat import test_atmostk
from tests_pysat import test_cnfplus
from tests_pysat import test_equals1
from tests_pysat import test_process
# from tests_pysat import test_propagate
from tests_pysat import test_unique_model
from tests_pysat import test_unique_mus
# from tests_pysat import test_warmstart
class TestPySat(unittest.TestCase):
    def test_pysat_accum_stats(self):
        test_accum_stats.solvers = SOLVER_FOR_PYSAT
        test_accum_stats.test_solvers()

    def test_pysat_atmost(self):
        test_atmost.test_atmost()

    def test_pysat_atmost1(self):
        test_atmost1.test_atmost1()

    def test_pysat_atmostk(self):
        if not SPEEDY:
            test_atmostk.test_atmostk() # takes approximately 30s

    def test_pysat_cnfplus(self):
        test_cnfplus.solvers = SOLVER_FOR_PYSAT
        test_cnfplus.test_cnfplus()
        test_cnfplus.test_cnf()

    def test_pysat_equals1(self):
        test_equals1.test_equals1()

    def test_pysat_process(self):
        test_process.test_processor()

    # # Propagate is currently not supported by any qbf solver
    # def test_pysat_propagate(self):
    #     test_propagate.solvers = SOLVER_FOR_PYSAT
    #     test_propagate.test_solvers()
        
    def test_unique_model(self):
        test_unique_model.solvers = SOLVER_FOR_PYSAT
        test_unique_model.test_solvers()

    def test_unique_mus(self):
        test_unique_mus.test_unique_mus()

    # # Warmstarts are not supported by any qbf solver
    # def test_pysat_warmstart(self):
    #     test_warmstart.test_warmstart()


SOLVER_FOR_INTEGRATION = [SolverNames.depqbf, SolverNames.qute]
class TestIntegration(unittest.TestCase):
    """
    Full pipeline and use-cases
    """
    def test_loading_formula_from_formats(self):
        qdimacs = (PCNF(from_file=TESTDATA_FORMULA1), True)        

        aig_str = None
        with open(TESTDATA_HALFADDER_AIG, "r") as fp:
            aig_str = fp.read() #from_aiger does not support reading from aag, only aig format
        aig = (PCNF(from_aiger=aig_str), True)
        aig[0].forall(1,2).exists(3,4,5)      #forall inputs exist a output assignment (root variable is not set by unit)

        clauses_src = [[-1,-2,-3], [-1,-2,3],[-1,2,-3], [-1,2,3],[1,-2,-3], [1,-2,3],[1,2,-3], [1,2,3]]
        clauses = (PCNF(from_clauses=clauses_src), False)
        clauses[0].forall(1).exists(2,3)

        dimacs = (PCNF(from_file=TESTDATA_FORMULA1), True)

        text_src = "p cnf 3 2\na 1 2 0\ne 3 0\n1 2 0\n1 2 -3 0\n"
        text = (PCNF(from_string=text_src), False)
        formulas = [qdimacs, aig, clauses, dimacs, text]

        for formula, expected in formulas:
            for sn in SOLVER_FOR_INTEGRATION:
                with Solver(sn, bootstrap_with=formula) as solver:
                    self.assertEqual(solver.solve(), expected)

    def test_get_all_models(self):
        formula = PCNF(from_clauses=[[1,2, 3], [-1,-2, 3], [1,-2,-3], [-1,2,-3]])
        formula.exists(3).forall(1).exists(2)

        expected_models = [[3],[-3]]
        for sn in SOLVER_FOR_INTEGRATION:   
            try:     
                with Solver(sn, bootstrap_with=formula, incr="True") as solver:
                    models = [x for x in solver.enum_models()]
                    self.assertCountEqual(models, expected_models)
                    expected_models_checked = [False for _ in expected_models]
                    for model in models:
                        self.assertTrue(model in expected_models)
                        idx = expected_models.index(model)
                        expected_models_checked[idx] = True
                    self.assertTrue(all(expected_models_checked))
            except NotImplementedError:
                with Solver(sn) as solver:
                    self.assertFalse(solver.supports_incremental())

    def test_preprocess(self):
        formula = to_pcnf([[1,2], [-1,-2], [1,-2], [-1,2]])
        proc = Bloqqer()
        self.assertFalse(proc.preprocess(formula))

        with Processor(bootstrap_with=formula) as proc:
            _ = proc.process()
            self.assertIsNotNone(proc.get_status())
            self.assertFalse(proc.get_status())

        with Solver(SolverNames.depqbf, bootstrap_with=formula) as solver:
            self.assertFalse(solver.process())

    def test_card_encodings(self):
        cnf = CardEnc.atmost([1,2,3,4,5,6,7], bound=4)
        cnf2 = CardEnc.atleast([1,2,3,4,5,6,7], bound=4)
        cnf3 = CardEnc.equals([1,2,3,4,5,6,7])
        formulas = [to_pcnf(cnf), to_pcnf(cnf2), to_pcnf(cnf3)]

        for formula in formulas:
            for sn in SOLVER_FOR_INTEGRATION:
                with Solver(sn, bootstrap_with=formula) as solver:
                    self.assertEqual(solver.solve(), True)
        
    def test_assumptions_with_quapi(self):
        circ = QBCircuit()
        x = circ.input()
        y = circ.input()
        s, c = circ.half_adder(x, y)
        out = circ.or_gate(s, c)
        circ.output(out)
        gen = FormulaGenerator(circ)
        formula = gen.forall(y).get_qdimacs()

        quapi_config = [Caqe.Configuration.build_conflict_clauses]
        with Solver(SolverNames.caqe, bootstrap_with=formula, use_quapi=True, quapi_max_assumption_size=1, quapi_solver_configurations=quapi_config) as solver:
            solver.solver.allow_unsafe()            #otherwise we can not check the output-id as this is out of scope for normal assuptions
            self.assertTrue(solver.solve([out.id]))
            self.assertFalse(solver.solve([-out.id]))

        formula = FormulaGenerator(circ).forall(x, y).get_qdimacs()

        try:
            with Solver(SolverNames.caqe, bootstrap_with=formula) as solver:
                solver.configure(Caqe.Configuration.build_conflict_clauses)
                solver.assume(out.id)
                solver.solve()
                self.assertTrue(False, msg="The solver should raise a runtime error as the formula starts with an universial quantifier block!")
        except RuntimeError:
            pass


class TestInvalidUse(unittest.TestCase):
    def test_wrong_preamble_count(self):
        wrong = "p cnf 2 3\na 1 0\ne 2 3 0\n1 2 0\n1 3 0"
        tmp = sys.stdout
        sys.stdout = None
        formula = PCNF(from_string=wrong)
        sys.stdout = tmp
        self.assertEqual(formula.nv, 3)     

    def test_all_free_variables(self):
        only_free = "p cnf 3 3\n-1 2 0\n-2 3 0\n-3 1 0\n"
        formula = PCNF(from_string=only_free)
        for sf in SOLVER_FACTORIES:
            solver = sf()
            self.assertTrue(solver.solve(formula))              

    def test_partial_free_variables(self):
        partial_free = "p cnf 3 3\ne 1 0\n-1 2 0\n-2 3 0\n-3 1 0\n"
        formula = PCNF(from_string=partial_free)
        for sf in SOLVER_FACTORIES:
            solver = sf()
            self.assertTrue(solver.solve(formula))        

    def test_non_normalized_var_numbers(self):
        strange = "p cnf 3 3\na 2 0\ne 4 6 0\n2 4 0\n1 -6 0"
        formula = PCNF(from_string=strange)
        for sf in SOLVER_FACTORIES:
            solver = sf()
            self.assertTrue(solver.solve(formula))  

    def test_quapi_wrong_prefix(self):
        formula = PCNF(from_file=TESTDATA_FORMULA1) 
        x = Caqe()
        x.create_internal_solver(2, formula, True)  #check whether it still works if the env-var was set beforehand
        del x        

        try:
            warn("\nNote: The following message starting with '[QuAPI] [ERROR]' is part of the test case and does not mean something is wrong!")
            with Solver(SolverNames.depqbf, use_quapi=True, bootstrap_with=formula, quapi_max_assumption_size=5) as solver:
                solver.solve([1, 2])
            self.assertTrue(False, "QuAPI should raise an error at this point")
        except RuntimeError:
            pass
                
        try:
            with Solver(SolverNames.depqbf, use_quapi=True, bootstrap_with=formula, quapi_max_assumption_size=5, quapi_allow_missing_universials=True) as solver:
                solver.solve([1, 2])
        except RuntimeError as ex:
            self.assertTrue(False, "QuAPI should not raise an error at this point as missing universials are allowed. Message: " + str(ex))
            
    def test_quapi_wrong_assumption(self):
        formula = PCNF(from_file=TESTDATA_FORMULA1) 
        with Caqe() as solver:
            solver.create_internal_solver(2, formula)
            try:
                solver.assume([3])
                self.assertTrue(False, "QuAPI should raise an exception if a variable out of the scope of the max_assumptions is assumed in safe-mode!")
            except RuntimeError:
                pass

            solver.allow_unsafe().assume([3])   # bypass checks
            self.assertFalse(solver.solve())


class TestFromDocExamples(unittest.TestCase):
    def test_process_module(self):
        pcnf = PCNF(from_clauses=[[1, 2], [3, 2], [-1, 4, -2], [3, -2], [3, 4]], auto_generate_prefix=True)
        processor = Bloqqer()
        processed = processor.preprocess(pcnf)
        self.assertTrue(processed)

        pcnf = PCNF(from_clauses=[[1, 2], [3, 2], [-1, 4, -2], [3, -2], [3, 4]], auto_generate_prefix=True)
        processor = Processor(bootstrap_with=pcnf)
        processed = processor.process()
        self.assertEqual(processed.clauses, [])
        self.assertTrue(processor.status)

        with Solver(bootstrap_with=processed) as solver:
            self.assertTrue(solver.solve())
        
        self.assertEqual(solver.get_model(), [])

        processor.add_clause([-3,2])        
        processed = processor.process()
        self.assertEqual(processed.clauses, [])
        self.assertTrue(processor.status)

        f2 = PCNF(from_clauses=[[1,2,3,4], [-1,-2,-3,-4]], auto_generate_prefix=True)
        processor.append_formula(f2)
        processed = processor.process()
        self.assertEqual(processed.clauses, [])
        self.assertTrue(processor.status)

        processor = Processor(bootstrap_with=[[-1, 2], [-2, 3], [-1, -3]])
        processor.add_clause([1])
        processed = processor.process()
        self.assertEqual(processed.clauses, [[]])
        self.assertFalse(processor.status)

        processor = Processor(bootstrap_with=[[-1, 2], [-2, 3], [-1, -3]])
        processed = processor.process()
        self.assertTrue(processor.get_status())

    def test_formula_module(self):
        # Description
        pcnf = PCNF()
        pcnf.append([-1, 2])
        pcnf.append([-2, 3])
        pcnf.forall(1).exists(2, 3)
        self.assertEqual(pcnf.clauses, [[-1, 2], [-2, 3]])
        self.assertEqual(pcnf.prefix, [-1, 2, 3])
        self.assertEqual(pcnf.nv, 3)

        # copy
        pcnf1 = PCNF(from_clauses=[[-1, 2], [1]])
        pcnf1.forall(1).exists(2)
        pcnf2 = pcnf1.copy()
        pcnf1.prefix.clear; pcnf1.clauses.clear; pcnf1.nv = 0
        self.assertEqual(pcnf2.prefix, [-1, 2])
        self.assertEqual(pcnf2.clauses, [[-1, 2], [1]])
        self.assertEqual(pcnf2.nv, 2)

        #eliminate_free_variables
        pcnf = PCNF(from_clauses=[[1, 2, 3], [-1, 2, 3], [-1, -2, -3]])
        pcnf.forall(1)
        self.assertEqual(pcnf.prefix, [-1])
        self.assertEqual(pcnf.nv, 3)
        pcnf.quantify_free_variables()
        self.assertEqual(pcnf.prefix, [2, 3, -1])
        self.assertEqual(pcnf.nv, 3)
        pcnf = PCNF(from_clauses=[[1, 2, 3], [-1, 2, 3], [-1, -2, -3]])
        pcnf.forall(1)
        pcnf.quantify_free_variables(QUANTIFIER_FORALL)
        self.assertEqual(pcnf.prefix, [-2, -3, -1])

        #is_normalized
        pcnf = PCNF(from_clauses=[[1, 2, 3], [-1, 2, 3], [-1, -2, -3]])
        self.assertFalse(pcnf.is_normalized)
        pcnf.normalize()
        self.assertTrue(pcnf.is_normalized)

        #negate
        pos = PCNF(from_clauses=[[-1, 2], [3]])
        pos.forall(1).exists(2,3)
        neg = pos.negate()
        self.assertEqual(neg.prefix, [1, -2, -3, 4])
        self.assertEqual(neg.clauses, [[1, -4], [-2, -4], [4, -3]])
        self.assertEqual(neg.auxvars, [4])
        self.assertEqual(neg.enclits, [4, -3])
        pos2 = neg.negate()
        self.assertEqual(pos2.prefix, [-1, 2, 3])
        self.assertEqual(pos2.clauses, [[-1, 2], [3]])
        
        #normalize
        pcnf = PCNF(from_clauses=[[-2, 4], [-4, 6], [-6, 2]])
        pcnf.forall(6)
        self.assertEqual(pcnf.nv, 6)
        pcnf.normalize() 
        self.assertEqual(pcnf.prefix, [1, 2, -3])
        self.assertEqual(pcnf.clauses, [[-1, 2], [-2, 3], [-3, 1]])
        self.assertEqual(pcnf.nv, 3)

        #prefix_from_clauses
        pcnf = PCNF(from_clauses=[[1, 2], [-4, 3]])
        self.assertEqual(pcnf.prefix, [])
        pcnf.prefix_from_clauses()
        self.assertEqual(pcnf.prefix, [1, 2, 3, 4])
        pcnf2 = PCNF(from_clauses=[[1, 2], [-4, 3]], auto_generate_prefix=True)
        self.assertEqual(pcnf.prefix, pcnf2.prefix)
        pcnf.prefix_from_clauses(QUANTIFIER_FORALL)
        self.assertEqual(pcnf.prefix, [-1, -2, -3, -4])

        #to_qdimacs
        pcnf = PCNF(from_clauses=[[-1, 2], [-2, 3], [-3]])
        pcnf.forall(1).exists(2, 3)
        pcnf.comments = ["c First Comment", "c Another Comment"]        
        expected = "c First Comment\nc Another Comment\np cnf 3 3\na 1 0\ne 2 3 0\n-1 2 0\n-2 3 0\n-3 0\n"
        self.assertEqual(pcnf.to_qdimacs(), expected)

        #var_type
        pcnf = PCNF()
        pcnf.exists(1).forall(2)
        self.assertEqual(pcnf.var_type(1), QUANTIFIER_EXISTS)        
        self.assertEqual(pcnf.var_type(2), QUANTIFIER_FORALL)
        self.assertEqual(pcnf.var_type(3), QUANTIFIER_NONE)

        #generate_blocks
        pcnf = PCNF()
        pcnf.forall(1).exists(2,3)
        self.assertEqual(list(pcnf.generate_blocks()), [[-1], [2,3]])

        #count_quantifier_alternations
        self.assertEqual(pcnf.count_quantifier_alternations(), 1)
        pcnf.exists(4).forall(5,6)
        self.assertEqual(pcnf.count_quantifier_alternations(), 2)

        #get_block
        pcnf = PCNF()
        pcnf.forall(1).exists(2,3)
        self.assertEqual(pcnf.get_block(0), [-1])
        self.assertEqual(pcnf.get_block(1), [2,3])
        pcnf.exists(4).forall(5,6)
        self.assertEqual(pcnf.get_block(0), [-1])
        self.assertEqual(pcnf.get_block(1), [2,3,4])
        self.assertEqual(pcnf.get_block(2), [-5,-6])
        self.assertEqual(pcnf.get_block(3), [])
        self.assertEqual(pcnf.get_block(OUTERMOST_BLOCK), [-1])
        self.assertEqual(pcnf.get_block(INNERMOST_BLOCK), [-5, -6])

        #get_block_type
        pcnf = PCNF()
        pcnf.forall(1).exists(2,3)
        self.assertEqual(pcnf.get_block_type(0), QUANTIFIER_FORALL)
        self.assertEqual(pcnf.get_block_type(1), QUANTIFIER_EXISTS)
        self.assertEqual(pcnf.get_block_type(2), QUANTIFIER_NONE)
        self.assertEqual(pcnf.get_block_type(OUTERMOST_BLOCK), QUANTIFIER_FORALL)
        self.assertEqual(pcnf.get_block_type(INNERMOST_BLOCK), QUANTIFIER_EXISTS)

        #innermost_block
        pcnf = PCNF()
        pcnf.forall(1).exists(2,3)
        self.assertEqual(pcnf.innermost_block(), [2,3])
        self.assertEqual(pcnf.innermost_block(QUANTIFIER_EXISTS), [2,3])
        self.assertEqual(pcnf.innermost_block(QUANTIFIER_FORALL), [-1])
        pcnf.exists(4).forall(5,6)
        self.assertEqual(pcnf.innermost_block(), [-5,-6])
        self.assertEqual(pcnf.innermost_block(QUANTIFIER_EXISTS), [2,3,4])
        self.assertEqual(pcnf.innermost_block(QUANTIFIER_FORALL), [-5,-6])

        #outermost_block
        pcnf = PCNF()
        pcnf.forall(1).exists(2,3)
        self.assertEqual(pcnf.outermost_block(), [-1])
        self.assertEqual(pcnf.outermost_block(QUANTIFIER_EXISTS), [2,3])
        self.assertEqual(pcnf.outermost_block(QUANTIFIER_FORALL), [-1])
        pcnf.exists(4, block=OUTERMOST_BLOCK).forall(5,6, block=OUTERMOST_BLOCK)
        self.assertEqual(pcnf.outermost_block(), [-5,-6])
        self.assertEqual(pcnf.outermost_block(QUANTIFIER_EXISTS), [4])
        self.assertEqual(pcnf.outermost_block(QUANTIFIER_FORALL), [-5,-6])
            
        #introduce_variable
        pcnf = PCNF(from_clauses=[[1, 2], [-1, -2]], auto_generate_prefix=True)
        self.assertEqual(pcnf.nv, 2)
        var = pcnf.introduce_var()
        self.assertEqual(var, 3)
        var2 = pcnf.introduce_var(quantifier=QUANTIFIER_FORALL)
        self.assertEqual(var2, 4)
        var3 = pcnf.introduce_var(quantifier=QUANTIFIER_FORALL, block=OUTERMOST_BLOCK)
        self.assertEqual(var3, 5)
        self.assertEqual(pcnf.prefix, [-5, 1, 2, 3, -4])
        self.assertEqual(pcnf.nv, 5)

        #minimize_prefix
        pcnf = PCNF(from_clauses=[[1, 2], [-1, -2]])
        pcnf.forall(1,2,3).exists(4,5,6)
        self.assertEqual(pcnf.prefix, [-1, -2, -3, 4, 5, 6])
        pcnf.minimize_prefix()
        self.assertEqual(pcnf.prefix, [-1, -2])

        #split_atoms_and_auxvars
        Formula._vpool[Formula._context].restart()
        formula = (Atom('x') & Atom('y')) | Atom('z')
        clauses = [c for c in formula]
        self.assertEqual(clauses, [[1, -3], [2, -3], [3, -1, -2], [3, 4]])
        atoms, auxvars = split_atoms_and_auxvars(formula)
        self.assertEqual(atoms, [1, 2, 4])
        self.assertEqual(auxvars, [3])

        #to_pcnf
        cnf = CNF(from_clauses = [[-1, 2], [-2, 3], [-3, 1]])
        pcnf = to_pcnf(cnf)
        self.assertEqual(pcnf.prefix, [1, 2, 3])
        self.assertEqual(pcnf.clauses, [[-1, 2], [-2, 3], [-3, 1]])
        clauses = [[-1, 2], [-2, 3], [-3, 1]]
        pcnf2 = to_pcnf(clauses)
        self.assertEqual(pcnf2.prefix, [1, 2, 3])
        self.assertEqual(pcnf2.clauses, [[-1, 2], [-2, 3], [-3, 1]])
        
        f = (Atom('x') & Atom('y')) | Atom('z')
        pcnf = to_pcnf(f)
        self.assertEqual(pcnf.prefix, [1, 2, 4, 3])
        self.assertEqual(pcnf.clauses, [[1, -3], [2, -3], [3, -1, -2], [3, 4]])
        self.assertEqual(pcnf.atoms, [1, 2, 4])
        self.assertEqual(pcnf.auxvars, [3])

        pcnf = PCNF()
        qlist = [1, 2, 3, 4]
        pcnf.forall(*qlist)
        self.assertEqual(pcnf.prefix, [-1,-2,-3,-4])
        pcnf = PCNF()
        pcnf.exists(*qlist)
        self.assertEqual(pcnf.prefix, [1,2,3,4])

    def test_solvers_module(self):
        #AssumingEnvironment
        formula = PCNF(from_file=TESTDATA_FORMULA1) 
        with AssumingEnvironment(formula) as solver:
            self.assertTrue(solver.solve())
            self.assertFalse(solver.solve([-1,2,3,4,5]))
            self.assertTrue(solver.solve([1,2,-3]))

        #pyqbf_solver
        #assuming and alive
        with Qute() as s:
            self.assertFalse(s.assuming)
            self.assertTrue(s.alive)
        with DepQBF() as s:
            self.assertTrue(s.assuming)

        #QuAPI
        #general       
        pcnf = PCNF(from_clauses=[[-4, 1, 2, 3], [-5, -1, -2, -3], [4, 5]], auto_generate_prefix=True)
        solver = QuAPI(None, 1)
        solver.configure("--no-dynamic-nenofex")
        solver.create_internal_solver(max_assumptions=5, formula=pcnf)
        solver.assume([1, 2])
        self.assertTrue(solver.solve())
        solver.assume([-4, -5])
        self.assertFalse(solver.solve())

        pcnf = PCNF(from_clauses=[[-4, 1, 2, 3], [-5, -1], [4, 5]])
        pcnf.exists(1, 2).forall(3).exists(4, 5)
        # We know that 4 and 5 are Tseitin variables simplified with Plaisted-Greenbaum
        solver = Caqe()
        solver.create_internal_solver(2, pcnf)
        try:
            solver.assume([-4])
            self.assertTrue(False, "QuAPI should raise an error at this point")
        except RuntimeError:
            pass
        solver.allow_unsafe()
        solver.assume([-4])
        solver.assume([-5])
        self.assertFalse(solver.solve())

        #assume
        solver = QuAPI(None, pyqbf_cpp.SOLVER_DEPQBF)
        formula = PCNF(from_clauses=[[1, 2, 3], [-1, 4], [-2, 5]], auto_generate_prefix=True)
        solver.create_internal_solver(5, formula)
        self.assertTrue(solver.solve())
        solver.assume([1, 2, 3, 4, 5])    #these variables are existentially quantified!
        self.assertTrue(solver.solve())
        solver.assume([-3, -4, -5])
        self.assertFalse(solver.solve())

        #Solver
        s = Solver()
        s.add_clause([1, 2])
        s.add_clause([-1, -2])
        s.formula.forall(1).exists(2)
        self.assertTrue(s.solve())
        self.assertEqual(s.get_model(), [])

        f = PCNF(from_clauses=[[1, 2], [-1, -2]])
        f.prefix_from_clauses(QUANTIFIER_FORALL)
        s = Solver(name=SolverNames.qfun, bootstrap_with=f)
        self.assertFalse(s.solve())
                
        f = PCNF(from_clauses=[[1, 2], [-1, -2], [-1, 2], [1, -2]], auto_generate_prefix=True)
        s = Solver(name=SolverNames.depqbf, use_quapi=True, quapi_max_assumption_size=5,\
                   bootstrap_with=f, quapi_solver_configurations=[DepQBF.Configuration.qdo])
        self.assertFalse(s.solve())
        
        s = Solver(name=SolverNames.depqbf, use_quapi=True, bootstrap_with=f, quapi_max_assumption_size=2)
        s.assume([1, 2])
        self.assertFalse(s.solve())
        
        with Solver(name=SolverNames.depqbf, incr=True) as solver:
            solver.append_formula(PCNF(from_file=TESTDATA_FORMULA1))
            self.assertTrue(solver.solve())
            solver.add_clause([5])
            self.assertFalse(solver.solve())

        #add_clause
        pcnf = PCNF(from_clauses=[[1, 2], [-1, -2]], auto_generate_prefix=True)
        with Solver(bootstrap_with=pcnf) as solver:
            solver.add_clause([-1, 2])
            self.assertFalse(solver.add_clause([1, -2], no_return=False))

        #append_formula
        pcnf = PCNF(from_file=TESTDATA_FORMULA1)
        s = Solver()
        s.append_formula(pcnf)
        self.assertTrue(s.solve())
        s = Solver()
        self.assertTrue(s.append_formula(pcnf, no_return=False))

        #assume
        pcnf = PCNF(from_file=TESTDATA_FORMULA1)
        with Solver(name=SolverNames.depqbf, bootstrap_with=pcnf) as solver:
            solver.assume([1, 2])
            solver.assume(3)
            self.assertTrue(solver.solve())

        #configure
        with Solver(use_quapi=True, quapi_custom_path="ls"):
            pass

        #enum_models
        pcnf = PCNF(from_clauses=[[-1, 2, 3], [1, -2, -3]])
        pcnf.exists(1, 2).forall(3)
        with Solver(incr=True, bootstrap_with=pcnf) as solver:
            self.assertEqual(list(solver.enum_models()), [[1, 2], [-1, -2]])

        #get_model
        pcnf = PCNF(from_clauses=[[-1, 2, 3], [1, -2, -3]])
        pcnf.exists(1, 2).forall(3)
        with Solver(bootstrap_with=pcnf) as solver:
            solver.solve()
            self.assertEqual(solver.get_model(), [-1, -2])

        #get_status
        pcnf = PCNF(from_clauses=[[1, 2], [-1, -2]], auto_generate_prefix=True)
        with Solver(bootstrap_with=pcnf) as solver:
            self.assertIsNone(solver.get_status())
            self.assertTrue(solver.solve())
            self.assertTrue(solver.get_status())

        #nof_clauses
        s = Solver(bootstrap_with=[[-1, 2], [1, -2], [1, 2]])
        self.assertEqual(s.nof_clauses(), 3)

        #solve
        formula = PCNF(from_clauses=[[-1, -2], [1, -2], [-1, 2]], auto_generate_prefix=True)
        with Solver(bootstrap_with=formula) as s:
            self.assertTrue(s.solve())
            self.assertFalse(s.solve([1, 2]))

        #pyqbf_incremental_solver
        pcnf = PCNF(from_clauses=[[1, 2], [-1, -2]], auto_generate_prefix=True)
        solver = DepQBF()
        solver.configure(DepQBF.Configuration.dep_man_simple)
        solver.configure(DepQBF.Configuration.incremental_use)
        self.assertTrue(solver.solve(pcnf))
        solver.add([-1, 2]) 
        self.assertTrue(solver.solve())
        solver.assume([1, 2])
        self.assertFalse(solver.solve())
        
if __name__ == "__main__":
    unittest.main()
