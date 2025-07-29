import abc
from pyqbf.formula import PCNF

class IdPoolProvider(object):
    def __init__(self):
        self.next_id = 1
        self.references = [0]
    
    def next(self, entry):
        current = self.next_id
        self.next_id += 1
        self.references.append(entry)
        return current
    
    def resolve(self, id):
        if id < 0 or id >= len(self.references):
            raise RuntimeError(f"Requesting {id}, which was not registered by the Id Pool!")
        return self.references[id]

    def cleanup(self):
        self.references.clear()
        self.references.append(0)
        self.next_id = 1


class CircuitElement(abc.ABC):
    def __init__(self, idpool):
        self.id = idpool.next(self)

    def qdimacs(self, formula):
        raise NotImplementedError("No qdimacs-format for abstract CircuitElement!")

    def __and__(self, other):
        if not isinstance(other, CircuitElement):
            raise TypeError(f"Cannot generate And-Gate for non-circuit elements!")
        return AndGate(self.id, other.id)

    def __or__(self, other):
        if not isinstance(other, CircuitElement):
            raise TypeError(f"Cannot generate Or-Gate for non-circuit elements!")
        return OrGate(self.id, other.id)            
    
    def __neg__(self):
        return _Negation(self)

    def __str__(self) -> str:
        return self.__repr__()


class Input(CircuitElement):
    def __init__(self, idpool):
        super().__init__(idpool)

    def qdimacs(self, formula):
        formula.exists(self.id)

    def __repr__(self) -> str:
        return f"Input[{self.id}]"


class Output(CircuitElement):
    def __init__(self, idpool):
        super().__init__(idpool)

    def qdimacs(self, formula):
        formula.exists(self.id)

    def __repr__(self) -> str:
        return f"Output[{self.id}]"


class _Negation(CircuitElement):
    def __init__(self, child):
        self.id = -child.id

    def qdimacs(self, formula):
        pass

    def __repr__(self) -> str:
        return f"Not({self.id})"


class BinaryGate(CircuitElement):
    def __init__(self, idpool, inp1, inp2, repr_op = "<Binary>"):
        super().__init__(idpool)
        self.inp1 = inp1
        self.inp2 = inp2
        self.__repr_op = repr_op

    def qdimacs(self, formula):
        raise NotImplementedError("Abstract Binary Gate class does not support qdimacs!")
        

    def __repr__(self) -> str:
        return f"{self.__repr_op}[{self.id}]({self.inp1},{self.inp2})"


class AndGate(BinaryGate):
    def __init__(self, idpool, inp1, inp2):
        super().__init__(idpool, inp1, inp2, "And")

    def qdimacs(self, formula):
        formula.exists(self.id)
        formula.append([-self.id, self.inp1])
        formula.append([-self.id, self.inp2])
        formula.append([self.id, -self.inp1, -self.inp2])


class OrGate(BinaryGate):
    def __init__(self, idpool, inp1, inp2):
        super().__init__(idpool, inp1, inp2, "Or")

    def qdimacs(self, formula):
        formula.exists(self.id)
        formula.append([self.id, -self.inp1])
        formula.append([self.id, -self.inp2])
        formula.append([-self.id, self.inp1, self.inp2])


class XorGate(BinaryGate):
    def __init__(self, idpool, inp1, inp2):
        self.left_gate = OrGate(idpool, inp1, inp2)
        self.right_gate = OrGate(idpool, -inp1, -inp2)
        super().__init__(idpool, inp1, inp2, "Xor")

    def qdimacs(self, formula):
        self.left_gate.qdimacs(formula)
        self.right_gate.qdimacs(formula)
        formula.exists(self.id)
        formula.append([-self.id, self.left_gate.id])
        formula.append([-self.id, self.right_gate.id])
        formula.append([self.id, -self.left_gate.id, -self.right_gate.id])


class HalfAdderGate(BinaryGate):
    def __init__(self, idpool, inp1, inp2):
        self.sum = XorGate(idpool, inp1, inp2)
        self.carry = AndGate(idpool, inp1, inp2)
        super().__init__(idpool, inp1, inp2)

    def qdimacs(self, formula):
        self.sum.qdimacs(formula)
        self.carry.qdimacs(formula)

    def __repr__(self) -> str:
        return f"HalfAdder[{self.sum.id}, {self.carry.id}]({self.inp1}, {self.inp2})"


class FullAdderGate(CircuitElement):
    def __init__(self, idpool, a, b, carry):
        super().__init__(idpool)
        self.half_adder1 = HalfAdderGate(idpool, a, b)
        self.half_adder2 = HalfAdderGate(idpool, self.half_adder1.sum.id, carry)
        self.total_carry = OrGate(idpool, self.half_adder1.carry.id, self.half_adder2.carry.id)
        self.inp1 = a
        self.inp2 = b
        self.inp3 = carry

    def sum(self):
        return self.half_adder2.sum
    
    def carry(self):
        return self.total_carry

    def qdimacs(self, formula):
        self.half_adder1.qdimacs(formula)
        self.half_adder2.qdimacs(formula)
        self.total_carry.qdimacs(formula)

    def __repr__(self) -> str:
        return f"FullAdder[{self.half_adder1.sum.id}, {self.total_carry.id}]({self.inp1}, {self.inp2}, {self.inp3})"


class QBCircuit:
    def __init__(self):
        self.__idpool = IdPoolProvider()
        self.inputs = []
        self.elements = []
        self.outputs = []

    def __check_element(self, elem):
        if not isinstance(elem, CircuitElement):
            raise TypeError(f"{CircuitElement} expected!")        

    def input(self):
        inp = Input(self.__idpool)
        self.inputs.append(inp.id)
        return inp

    def output(self, out):
        self.__check_element(out)
        self.outputs.append(out.id)
        return out

    def or_gate(self, left, right):
        self.__check_element(left)
        self.__check_element(right)
        g = OrGate(self.__idpool, left.id, right.id)
        self.elements.append(g.id)
        return g
    
    def and_gate(self, left, right):
        self.__check_element(left)
        self.__check_element(right)
        g = AndGate(self.__idpool, left.id, right.id)
        self.elements.append(g.id)
        return g
    
    def xor_gate(self, left, right):
        self.__check_element(left)
        self.__check_element(right)
        g = XorGate(self.__idpool, left.id, right.id)
        self.elements.append(g.id)
        return g
    
    def half_adder(self, left, right):
        """
        Returns: Sum, Carry
        """
        self.__check_element(left)
        self.__check_element(right)
        g = HalfAdderGate(self.__idpool, left.id, right.id)
        self.elements.append(g.id)
        return g.sum, g.carry
    
    def full_adder(self, left, right, carry):
        """
        Return: Sum, Carry
        """
        self.__check_element(left)
        self.__check_element(right)
        self.__check_element(carry)        
        g = FullAdderGate(self.__idpool, left.id, right.id, carry.id)
        self.elements.append(g.id)
        return g.sum(), g.carry()

    def get_instance(self, id):
        return self.__idpool.resolve(id)

    def qdimacs(self):
        f = PCNF()
        for x in self.inputs:
            inp = self.__idpool.resolve(x)
            inp.qdimacs(f)
        for x in self.elements:
            gate = self.__idpool.resolve(x)
            gate.qdimacs(f)
        return f

    def __repr__(self) -> str:
        text = f"[{','.join([str(x) for x in self.inputs])}]=>CircuitBoard(\n  "
        elems = []
        for x in self.elements:
            gate = self.__idpool.resolve(x)
            elems.append(str(gate))        
        text += ",\n  ".join(elems)
        text += ")\n=>"
        text += f"[{','.join([str(x) for x in self.outputs])}]"
        return text


class FormulaGenerator:
    def __init__(self, circuit:QBCircuit):
        self.circuit = circuit
        self.formula = circuit.qdimacs()

    def forall(self, *args):
        for element in args:
            if not isinstance(element, CircuitElement):
                raise TypeError(f"Expected variable of type {CircuitElement}")
            if element.id in self.formula.prefix:
                idx = self.formula.prefix.index(element.id)
                self.formula.prefix[idx] = -element.id
            elif -element.id in self.formula.prefix:
                pass    #nothing to do
            else:
                self.formula.prefix.append(-element.id)
        return self

    def exists(self, *args):
        for element in args:
            if not isinstance(element, CircuitElement):
                raise TypeError(f"Expected variable of type {CircuitElement}")
            if -element.id in self.formula.prefix:
                idx = self.formula.prefix.index(element.id)
                self.formula.prefix[idx] = element.id
            elif element.id in self.formula.prefix:
                pass    #nothing to do
            else:
                self.formula.prefix.append(element)
        return self
        
    def requireTrue(self, *args):
        for element in args:
            if not isinstance(element, CircuitElement):
                raise TypeError(f"Expected variable of type {CircuitElement}")
            self.formula.append([element.id])
        return self
    
    def requireFalse(self, *args):
        for element in args:
            if not isinstance(element, CircuitElement):
                raise TypeError(f"Expected variable of type {CircuitElement}")
            self.formula.append([-element.id])
        return self
    
    def trivial_output(self, check_true = True):
        """
        Checks whether the outputs are trivially true
        """
        for inp in self.circuit.inputs:
            elem = self.circuit.get_instance(inp)
            self.forall(elem)
        for out in self.circuit.outputs:
            elem = self.circuit.get_instance(out)
            if check_true:
                self.requireTrue(elem)
            else:
                self.requireFalse(elem)
        return self

        
    def get_qdimacs(self):
        return self.formula