import itertools
from pyqbf.solvers import DepQBF
from pyqbf.formula import PCNF

# This example is the pyqbf-version of the outer-counter tool (https://github.com/marseidl/outer-count)
# For a detailed explanation of the function please read the corresponding paper (https://doi.org/10.1007/978-3-031-16681-5_19)
# For an explanation of the implementation please read the PyQBF paper (https://doi.org/10.1007/978-3-031-76554-4_16)

pcnf = PCNF(from_file="unsat.qdimacs")
ts = pcnf.nv + 1
pcnf.set_quantifier(ts)
for c in pcnf.clauses:
    c.insert(0, -ts)
solver = DepQBF(incr=True)
solver.load(pcnf)
solver.assume([ts])
result = solver.solve()
root_clause = [ts]

if (result and pcnf.prefix[0] < 0) or (not result and pcnf.prefix[0] > 0):
    raise RuntimeError("Cannot only compute countermodels for first universal or models for first existential!")

relevant_prefix = list(itertools.takewhile(lambda x: (x > 0) == result, pcnf.prefix))

phase = result
count = 0
pushed = False
MAX_COUNT = 18446744073709551615
while result == phase:
    a = [solver.get_assignment(abs(v)) for v in relevant_prefix]
    d = 1
    dont_cares = 0
    for value in a:
        if value == 0:
            d *= 2
            dont_cares += 1
    if dont_cares >= 64:
        print("More than 2^64 models")
        exit()      

    if pushed:
        solver.pop()
        pushed = False

    if count + d > MAX_COUNT:
        print("Overflow during iterating!")
        print(f"More than {count + d} models")
        exit()
    count += d    

    if not phase:
        ts = pcnf.nv + 1
        pcnf.set_quantifier(ts); 
        solver.add_var(ts)
        root_clause.append(ts)
        for var in a:
            if var != 0:
                solver.add([-ts, var])
        solver.push()
        solver.add(root_clause)
        pushed = True
    else:
       solver.add([-x for x in a if x != 0])
       solver.assume([ts])
    result = solver.solve()
print(f"{'Counter' if not phase else ''}models: {count}")
