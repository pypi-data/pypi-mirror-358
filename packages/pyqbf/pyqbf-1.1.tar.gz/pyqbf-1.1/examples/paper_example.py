import itertools
from pyqbf.solvers import DepQBF
from pyqbf.formula import PCNF

# The example given in the PyQBF paper (https://doi.org/10.1007/978-3-031-76554-4_16).
# A more compact version of the counting outer-models like done in iterative_counter_model_counting

pcnf = PCNF(from_file="unsat.qdimacs")
ts = pcnf.nv + 1; pcnf.set_quantifier(ts)
for c in pcnf.clauses:
    c.append(-ts)

solver = DepQBF(incr=True); solver.load(pcnf); solver.push()
root_clause = [ts]; solver.add(root_clause)
result = solver.solve()
count = 1
while not result:
    a = [solver.get_assignment(abs(v)) \
    	 for v in itertools.takewhile   
         (lambda x: x < 0, pcnf.prefix)]
    solver.pop()
    ts = pcnf.nv + 1; pcnf.set_quantifier(ts); solver.add_var(ts)
    root_clause.append(ts)
    for var in a:
        solver.add([-ts, var])
    solver.push(); solver.add(root_clause)
    result = solver.solve()
    if not result: count += 1
print(count)	