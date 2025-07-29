"""
    ===============
    List of classes
    ===============

    .. autosummary::
        :nosignatures:

        PCNF

    ===============
    List of methods
    ===============

    .. autosummary::
        :nosignatures:

        split_atoms_and_auxvars
        to_pcnf

    =================
    List of constants
    =================

    .. autosummary::
        :nosignatures:

        QUANTIFIER_FORALL
        QUANTIFIER_EXISTS 
        QUANTIFIER_NONE
        OUTERMOST_BLOCK
        INNERMOST_BLOCK

        

    ==================
    Module description
    ==================

    This module provides classes and methods for simple manipulation of quantified boolean 
    formulas in `prenex normal form <https://en.wikipedia.org/wiki/Prenex_normal_form>`__, 
    where the propositional part of the formula is in `conjunctive normal form (CNF) <https://en.wikipedia.org/wiki/Conjunctive_normal_form>`__,
    i.e. PCNF.

    We can see PCNF as an extension of CNF with the addition of a quantifier-prefix.
    Therefore, the :class:`PCNF`-class inherits all the properties provided by :class:`pysat.formula.CNF`
    with the additional ``prefix``-attribute. The prefix can be set using the :meth:`forall` and :meth:`exists` functions

    The propositional part can be seen as a set of clauses, where each clause is a set of literals.
    Literals are represented using the ``int`` type, where a negative value indicates the negation of the variable
    referenced.

    The prefix can be seen as an ordered tuple of `quantifiers <https://en.wikipedia.org/wiki/Quantifier_(logic)>`__. 
    The order-relation applied to the quantifier is expressed by the order of where the variable occur in the prefix.
    A negative value indicates *forall*-quantification whereas a postive value indicates *exists*.

    .. code-block:: python

        >>> from pyqbf.formula import PCNF
        >>> pcnf = PCNF()
        >>> pcnf.append([-1, 2])
        >>> pcnf.append([-2, 3])
        >>> pcnf.forall(1).exists(2, 3)
        >>> print(pcnf.clauses)
        [[-1, 2], [-2, 3]]
        >>> print(pcnf.prefix)
        [-1, 2, 3]
        >>> print(pcnf.nv)
        3

    The default input-format is `QDIMACS <https://www.qbflib.org/qdimacs.html>`__. Very similar to DIMACS for PySAT, reading and writing can be done the following way:

    .. code-block:: python

    
        >>> from pyqbf.formula import PCNF
        >>> f1 = PCNF(from_file="some-file-name.qdimacs") 
        >>> f1.to_file("another-file-name.qdimacs")
        >>>
        >>> with open('some-file-name.qdimacs', 'r+') as fp:
        ...     f2 = PCNF(from_fp=fp)
        ...
        ...     fp.seek(0)
        ...     f2.to_fp(fp)
        >>>
        >>> f3 = PCNF(from_string="p cnf 3 3\\na 1 0\\ne 2 3 0\\n-1 2 0\\n-2 3 0\\n-3 0\\n")
        >>> print(f3.clauses)
        [[-1, 2], [-2, 3], [-3]]
        >>> print(f3.prefix)
        [-1, 2, 3]
        >>> print(f3.nv)
        3
        
    PyQBF furthermore allows easy extensions from the domain of Propositional Logic into QBF. 
    In the following are a few examples.

    .. code-block:: python

        >>> from pyqbf.formula import PCNF, to_pcnf
        >>> f1 = PCNF(from_file="cnf.dimacs")   #DIMACS is compatible with QDIMACS
        >>> print(f1.prefix)                    #but the prefix is empty
        []
        >>> f1.forall(1).exists(2,3,4).forall(5,6)
        >>> print(f1.prefix)
        [-1, 2, 3, 4, -5, -6]
        >>>
        >>> f2 = PCNF(from_file="cnf.dimacs", auto_generate_prefix=True)
        >>> print(f2.prefix)                    #now everything is automatically existentially quantified
        [1, 2, 3, 4, 5, 6]
        >>> f2.set_quantifier(1, QUANTIFIER_FORALL)
        >>> print(f2.prefix)
        [-1, 2, 3, 4, 5, 6]

    .. note::
        Currently only the :class:`pysat.formula.CNF` class is supported.
        More complex structures like :class:`pysat.formula.WCNF` or :class:`pysat.formula.CNFPlus`
        can not be expressed using quantification at the moment.

    ==============
    Module details
    ==============
"""

import copy
from pysat import formula

#: Indicator for an universial quantifier
QUANTIFIER_FORALL = -1
#: Indicator for an existential quantifier
QUANTIFIER_EXISTS = 1
#: Indicator for a free variable
QUANTIFIER_NONE = 0

#: Indicator for the outermost quantifier block
OUTERMOST_BLOCK = 0
#: Indicator for the innermost quantifier block
INNERMOST_BLOCK = None

class PCNF(formula.CNF):
    # Existential is +, Universal is -

    """
        Class for manipulating PCNF formulas. It can be used for creating
        formulas, reading them from a file, or writing them to a file.

        
        :param from_file: a QDIMACS filename to read from
        :param from_fp: a file pointer to read from
        :param from_string: a string storing a PCNF formula in QDIMACS format
        :param from_clauses: a list of clauses to bootstrap the formula with. Variables are free by default
        :param from_aiger: an AIGER circuit to bootstrap the formula with. Variables are free by default
        :param from_cnf: a CNF-formula. Variables are free by default
        :param auto_generate_prefix: if true, a prefix is automatically generated from the propositional part.

        :type from_file: :class:`str`
        :type from_fp: :class:`SupportsRead[str]`
        :type from_string: :class:`str`
        :type from_clauses: :class:`list[list[int]]`
        :type from_aiger: :class:`aiger.AIG` (see `py-aiger package <https://github.com/mvcisback/py-aiger>`__)
        :type from_cnf: :class:`pysat.formula.CNF`
        :type auto_generate_prefix: :class:`bool`

        :ivar prefix: Prefix of the formula containing the quantifications
        :ivar clauses: Propositional part of the formula containing the clauses
        :ivar comments: Comments encountered during parsing
        :ivar nv: Total count of variables

        :vartype prefix: :class:`list[int]`
        :vartype clauses: :class:`list[list[int]]`
        :vartype comments: :class:`list[str]`
        :vartype nv: :class:`int`

    """
    def __init__(self, from_file=None, from_fp=None, from_string=None,
                from_clauses=[], from_aiger=None, from_cnf=None, auto_generate_prefix=False):
        """
        Default constructor
        """
        self.prefix = []   

        super().__init__(from_file=from_file, from_fp=from_fp, from_string=from_string, from_clauses=from_clauses, from_aiger=from_aiger,comment_lead=['c'])

        if from_cnf:
            if not isinstance(from_cnf, formula.CNF):
                raise TypeError(f"Parameter of 'from_cnf' is not of type {type(formula.CNF)}!")
            self.clauses = copy.deepcopy(from_cnf.clauses)
            self.comments = copy.deepcopy(from_cnf.comments)
            self.nv = from_cnf.nv

        if auto_generate_prefix:
            self.prefix_from_clauses()        

    def __repr__(self):
        """
        State reproducible string representaion of object.
        """
        s = self.to_qdimacs().replace('\n', '\\n')
        return f"PCNF(from_string=\"{s}\")"

    def __getitem__(self, c):
        """
        Indexer of the object, for easily access clauses

        Parameters:
            :param c: index of the clause

            :type c: int
        """
        return self.clauses[c]
    
    def __check_variable_count(self):
        if len(self.prefix) > self.nv:
            print("WARNING: The number of variables specified in the preamble is less then the amount of variables declared in the prefix! This is a violation of the QDIMACS format!")
            self.nv = len(self.prefix)

    def from_fp(self, file_pointer, comment_lead=[]):
        """
            Read a PCNF formula in `QDIMACS <https://www.qbflib.org/qdimacs.html>`__ format from a file pointer.

            .. note::
                The parameter ``comment_lead`` exists due to compatibility with
                :func:`pysat.formula.CNF.from_fp` but does not serve a purpose here

            :param file_pointer: a file pointer to read the formula from.
            :param comment_lead: a list of characters leading comment lines (for compatibility reason)

            :type file_pointer: :class:`SupportsRead[str]`
            :type comment_lead: :class:`list[str]`

            Usage example:

            .. code-block:: python

                >>> with open('some-file.qdimacs', 'r') as fp:
                ...     pcnf1 = PCNF()
                ...     pcnf1.from_fp(fp)
                >>>
                >>> with open('another-file.qdimacs', 'r') as fp:
                ...     pcnf2 = PCNF(from_fp=fp)
        """

        self.nv = 0
        self.prefix = []
        self.clauses = []
        self.comments = []        
        max_id = 0

        for line in file_pointer:            
            line = line.rstrip()
            if len(line) < 1:
                continue            
            if line[0] == "c":
                self.comments.append(line)
            elif line[0] == "p":
                self.nv = int(line.split(' ')[-2])
            elif line[0] == "a":
               self.prefix.extend([-int(x) for x in line.split(' ') [1:-1]])            
            elif line[0] == "e":
               self.prefix.extend(list(map(int, line.split()[1:-1])))
            else:
                clause = list(map(int, line.split()[:-1]))
                self.clauses.append(clause)
                max_id = max(max([abs(x) for x in clause] if len(clause) > 0 else [0]), max_id)
        
        if max_id > self.nv:
            self.nv = max_id
        self.__check_variable_count()

    def _add_at_block(self, vars, block):
        if len(self.prefix) == 0:            
            self.prefix.extend(vars)
            return
        
        lookup = set([abs(x) for x in vars])

        if block is None:
            self.prefix = [x for x in self.prefix if abs(x) not in lookup]
            self.prefix.extend(vars)
            return

        new_prefix = []

        bidx = 0
        if block == 0:
            new_prefix.extend(vars)
            bidx = 1
            
        curq = QUANTIFIER_FORALL if self.prefix[0] < 0 else QUANTIFIER_EXISTS
        for var in self.prefix:
            q = QUANTIFIER_FORALL if var < 0 else QUANTIFIER_EXISTS
            if curq != q:
                bidx += 1
                curq = q
            if bidx == block:
                new_prefix.extend(vars)
                bidx += 1
            if abs(var) not in lookup:
                new_prefix.append(var)
            
        if bidx < block:    #outside
            new_prefix.extend(vars)

        self.prefix = new_prefix

    def forall(self, *vars, block=None):
        """
        Adds variables bound by an universial quantifier to the formula's prefix. 
        Optionally, specify the ``block``-parameter to add it to the front of the block at the specified index.
        You can also use the special indicess :class:``OUTERMOST_BLOCK`` and :class:``INNERMOST_BLOCK``
        If the variable already exists in the prefix, it is removed at the old position

        :param vars: identifiers of the variables
        :param block: index of the block to be added to.

        :type vars: :class:`int`

        :returns: The current :class:`PCNF` for chaining
        :rtype: :class:`PCNF`

        Usage example:

        .. code-block:: python

            >>> pcnf = PCNF()
            >>> pcnf.forall(1, 2, "3", 4.0).forall(5)
            >>> qlist = [6, 7, 8, 9]
            >>> pcnf.forall(*qlist)
            >>> print(pcnf.prefix)
            [-1, -2, -3, -4, -5, -6, -7, -8, -9]
            >>> pcnf.forall(10, block=OUTERMOST_BLOCK)
            >>> print(pcnf.prefix)
            [-10, -1, -2, -3, -4, -5, -6, -7, -8, -9]
            >>> pcnf.forall(11, block=1)
            [-10, -1, -2, -3, -4, -5, -6, -7, -8, -9, -11]
        """
        self._add_at_block([-abs(int(x)) for x in vars], block)
        self.nv = max(self.nv, max([abs(int(x)) for x in vars]))
        return self #builder pattern

    def exists(self, *vars, block=None):
        """
            Adds variables bound by an existential quantifier to the formula's prefix. 
            Optionally, specify the ``block``-parameter to add it to the front of the block at the specified index.
            You can also use the special indicess :class:``OUTERMOST_BLOCK`` and :class:``INNERMOST_BLOCK``
            If the variable already exists in the prefix, it is removed at the old position
        
            :param vars: identifiers of the variables
            :type vars: :class:`int`

            :returns: The current :class:`PCNF` for chaining
            :rtype: :class:`PCNF`

            Usage example:

            .. code-block:: python

                >>> pcnf = PCNF()
                >>> pcnf.exists(1, 2, "3", 4.0).exists(5)
                >>> qlist = [6, 7, 8, 9]
                >>> pcnf.exists(*qlist)
                >>> print(pcnf.prefix)
                [1, 2, 3, 4, 5, 6, 7, 8, 9]
                >>> pcnf.exists(10, block=OUTERMOST_BLOCK)
                >>> print(pcnf.prefix)
                [10, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                >>> pcnf.exists(11, block=1)
                [10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11]

        """
        self._add_at_block([abs(int(x)) for x in vars], block)
        self.nv = max(self.nv, max([abs(int(x)) for x in vars]))
        return self #builder pattern

    def var_type(self, var):
        """
            Provides quantifier information for the specified variable.

            :param var: identifier of the variable
            :type var: :class:`int`

            :returns: :class:`QUANTIFIER_EXISTS`, :class:`QUANTIFIER_FORALL` or :class:`QUANTIFIER_NONE`
            :rtype: :class:`int`

            Usage example:

            .. code-block:: python

                >>> pcnf = PCNF()
                >>> pcnf.exists(1).forall(2)
                >>> print(pcnf.var_type(1))
                1
                >>> print(pcnf.var_type(1) == QUANTIFIER_EXISTS)
                True
                >>> print(pcnf.var_type(2))
                -1
                >>> print(pcnf.var_type(2) == QUANTIFIER_FORALL)
                True
                >>> print(pcnf.var_type(3))
                0
                >>> print(pcnf.var_type(3) == QUANTIFIER_NONE)
                True

        """
        if abs(var) in self.prefix:
            return QUANTIFIER_EXISTS
        elif -abs(var) in self.prefix:
            return QUANTIFIER_FORALL
        else:
            return QUANTIFIER_NONE
        
    def set_quantifier(self, var, quantifier = QUANTIFIER_EXISTS):
        """
        Changes the quantifier of the specified variable to the value specified.
        If the target is not in the prefix yet, it is appended.

        :param var: identifier of the variable
        :param quantifier: type of the quantifier. :class:`QUANTIFIER_NONE` is **not** supported

        :type var: :class:`int`
        :type quantifier: :class:`int`

        Usage example:

        .. code-block:: python

            >>> pcnf = PCNF(...)
            >>> pcnf.set_quantifier(1, QUANTIFIER_EXISTS)
            >>> pcnf.set_quantifier(2, QUANTIFIER_FORALL)
            >>> pcnf.set_quantifier(3)  
            >>> print(pcnf.prefix)
            [1, -2, 3, ...]
            >>> pcnf.set_quantifier(2, QUANTIFIER_EXISTS)
            [1, 2, 3, ...]
        """
        target_idx = -1
        for idx, elem in enumerate(self.prefix):
            if elem == var or elem == -var:
                target_idx = idx
                break
        if target_idx == -1:
            self.prefix.append(-var if quantifier == QUANTIFIER_FORALL else var)
            self.nv = max(self.nv, abs(var))
        else:
            self.prefix[target_idx] = -var if quantifier == QUANTIFIER_FORALL else var

    def flip_quantifier(self, *vars):
        """
        Flips the quantifier of the specified variables (:math:`\\exists \\Rightarrow \\forall`, :math:`\\forall \\Rightarrow \\exists`).
        If a variable is free, nothing changes.
         
        :param vars: identifiers of the variable
        :type var: :class:`list[int]`

        Usage example:

        .. code-block:: python

            >>> pcnf = PCNF(...)
            >>> print(pcnf.prefix)
            [1, -2, 3, ...]
            >>> pcnf.fip_quantifier(1)
            >>> print(pcnf.prefix)
            [-1, -2, 3, ...]
            >>> pcnf.fip_quantifier(1, 2, 3)
            >>> print(pcnf.prefix)
            [1, 2, -3, ...]        
        """
        lookup = set([abs(x) for x in vars])
        for idx, var in enumerate(self.prefix):
            if abs(var) in lookup:
                self.prefix[idx] = -var

    def introduce_var(self, quantifier = QUANTIFIER_EXISTS, block = INNERMOST_BLOCK):
        """
        Introduces a new variable on a unique id at the specified position

        :param quantifier: specifies the quantifier type of the variable (optional)
        :param block: specifies the block, the variable is instantiated into

        :type quantifier: :class:`int`
        :type block: :class:`int`

        Usage example:

        .. code-block:: python

            >>> pcnf = PCNF(from_clauses=[[1, 2], [-1, -2]], auto_generate_prefix=True)
            >>> print(pcnf.nv)
            2
            >>> var = pcnf.introduce_var()
            >>> print(var)
            3
            >>> var2 = pcnf.introduce_var(quantifier=QUANTIFIER_FORALL)
            >>> print(var2)
            4
            >>> var3 = pcnf.introduce_var(quantifier=QUANTIFIER_FORALL, block=OUTERMOST_BLOCK)
            >>> print(var3)
            5
            >>> print(pcnf.prefix)
            [-5, 1, 2, 3, -4]
            >>> print(pcnf.nv)
            5

        """
        id = self.nv + 1
        self.nv = id

        if quantifier == QUANTIFIER_FORALL:
            id = -id
        elif quantifier != QUANTIFIER_EXISTS:
            return 0    # not instantiated

        self._add_at_block([id], block)

        return abs(id)

    def copy(self):
        """
            This method can be used for creating a copy of a PCNF object. It
            creates another object of the :class:`PCNF` class and makes use of
            the :func:`deepcopy` functionality to copy the prefix and clauses.

            :returns: A copy of the current instance.
            :rtype: :class:`PCNF`

            Usage example:

            .. code-block:: python

                >>> pcnf1 = PCNF(from_clauses=[[-1, 2], [1]])
                >>> pcnf1.forall(1).exists(2)
                >>> pcnf2 = pcnf1.copy()
                >>> print(pcnf2.prefix)
                [-1, 2]
                >>> print(pcnf2.clauses)
                [[-1, 2], [1]]
                >>> print(pcnf2.nv)
                2
        """
        pcnf = PCNF()
        pcnf.nv = self.nv
        pcnf.prefix = copy.deepcopy(self.prefix)
        pcnf.clauses = copy.deepcopy(self.clauses)
        pcnf.comments = copy.deepcopy(self.comments)
        return pcnf
    
    def to_fp(self, file_pointer, comments=None):
        """
            The method can be used to save a PCNF formula into a file pointer using `QDIMACS <https://www.qbflib.org/qdimacs.html>`__ encoding.
            Additional comment lines can be specified with the ``comments`` parameter.

            :param file_pointer: a file pointer where to store the formula.
            :param comments: additional comments to put in the file.

            :type file_pointer: :class:`SupportsWrite[str]` (file pointer)
            :type comments: :class:`list[str]`

            Usage example:
            
            .. code-block:: python

                >>> pcnf = PCNF()
                >>> with open("file.qdimacs", "w") as fp:
                ...    pcnf.to_fp(fp)
        """
        if comments:
            self.comments.extend(comments)
        print(self.to_qdimacs(), file=file_pointer)

    def to_qdimacs(self):
        """
            Return the current state of the object in `QDIMACS <https://www.qbflib.org/qdimacs.html>`__ encoding.

            :returns: a QDIMACS representation of the formula
            :rtype: :class:`str`

            Usage example:

            .. code-block:: python

                >>> pcnf = PCNF(from_file="some-file.qdimacs")
                >>> print(pcnf.comments)
                ["c First Comment", "c Another Comment"]
                >>> print(pcnf.to_qdimacs())
                c First Comment
                c Another Comment
                p cnf 3 3 
                a 1 0
                e 2 3 0
                -1 2 0
                -2 3 0
                -3 0

        """
        comment_lines = [str(comment) for comment in self.comments]
        header_lines = [f"p cnf {self.nv} {len(self.clauses)}"]
        prefix_lines = []
        if len(self.prefix) > 0:
            curq = self.prefix[0] < 0
            curline = f"a {abs(self.prefix[0])}" if curq else f"e {abs(self.prefix[0])}"
            for var in self.prefix[1:]:
                if (var < 0) == curq:
                    curline += f" {abs(var)}"
                else:
                    curq = not curq
                    prefix_lines.append(curline + " 0")
                    curline = f"a {abs(var)}" if curq else f"e {abs(var)}"
            prefix_lines.append(curline + " 0")

        clause_lines = [" ".join(map(str,clause)) + " 0" for clause in self.clauses]
        lines = "\n".join(comment_lines + header_lines + prefix_lines + clause_lines) + "\n"
        return lines
    
    def _negate_formula(self):
        f = PCNF()
        f.nv = self.nv
        f.auxvars = []
        f.enclits = []
        
        for cl in self.clauses:
            if len(cl) == 1:
                # Add unit
                f.enclits.append(-cl[0])
            else:
                #we need a tseitin-variable
                f.nv += 1 
                t = f.nv
                f.auxvars.append(t)
                #CNF => Plaisted Greenbaum encoding. We only need the link in positive phase
                for l in cl:
                    f.clauses.append([-l, -t])                
                f.enclits.append(t)
        f.clauses.append(f.enclits)
        f.prefix = [-x for x in self.prefix]
        f.prefix.extend(f.auxvars)
        return f

    def _restore_negation(self):
        f = PCNF()       
        max_id = 0
        encoding = dict()
        for cl in self.clauses:            
            if cl == self.enclits:
                continue
            elif len(cl) == 2:
                l, t = cl
                if t > 0 or -t not in self.auxvars:
                    return None #not a tseitin encoding as used for generation, can not restore

                if -t not in encoding.keys():
                    encoding[-t] = []
                encoding[-t].append(-l)         
                max_id = max(max_id, abs(l))   
            else:
                return None     #Cannot restore
            
        for l in self.enclits:
            if l not in self.auxvars:
                #restore unit
                f.clauses.append([-l])
                max_id = max(max_id, abs(l))   

            elif l not in encoding.keys():
                return None
            
            else:
                f.clauses.append(encoding[l])
        f.nv = max_id
        f.prefix = [-x for x in self.prefix if abs(x) not in self.auxvars]
        return f

    def negate(self):
        """
            Given a PCNF formula :math:`\mathcal{F}`, this method creates a PCNF
            formula :math:`\\neg{\mathcal{F}}`.        

            The negation of the propositional part is encoded using additional Tseitin variables [1]_.
            Furthermore, the technique proposed by Plaisted and Greenbaum [2]_ is used to reduce the amount of clauses.
            For the prenex, the quantifiers are inversed, i.e. existential become universial and vice versa.
            A new PCNF formula is returned keeping all the newly introduced
            variables that can be accessed through the ``auxvars`` variable.
            All the literals used to encode the negation of the original
            clauses can be accessed through the ``enclits`` variable.

            If this function is called twice and the encoding can still be re-constructed, instead 
            of re-encoding with another set of tseitin variables it will reverse the encoding and restore the original formula.
           
            :returns: a formula describing the negated version of the input
            :rtype: :class:`PCNF`
            
            .. [1] G. S. Tseitin. *On the complexity of derivations in the
                propositional calculus*.  Studies in Mathematics and
                Mathematical Logic, Part II. pp.  115–125, 1968

            .. [2] Plaisted, D.A., Greenbaum, S. *A structure-preserving clause form translation.*
                Journal of Symbolic Computation  2(3),  293--304 (1986)


            .. code-block:: python

                >>> pos = PCNF(from_clauses=[[-1, 2], [3]])
                >>> pos.forall(1).exists(2,3)
                >>> neg = pos.negate()
                >>> print(neg.prefix)
                [1, -2, -3, 4]
                >>> print(neg.clauses)
                [[1, -4], [-2, -4], [4, -3]]
                >>> print(neg.auxvars)
                [4]
                >>> print(neg.enclits)
                [4, -3]
                >>> pos2 = neg.negate()
                >>> print(pos2.prefix)
                [-1, 2, 3]
                >>> print(pos2.clauses)
                [[-1, 2], [3]]
        """
        pcnf = None
        if hasattr(self, "auxvars") and hasattr(self, "enclits"):
            pcnf = self._restore_negation() #might yield None
        if pcnf is None:
            pcnf = self._negate_formula()
        return pcnf
    
    def to_alien(self, file_pointer, format='opb', comments=None):
        """
        .. warning::
            This method is currently not supported for PCNF-formulas

        :raises: :class:`NotImplementedError`
        """
        raise NotImplementedError("Currently only export to QDIMACS format is supported")
    
    def prefix_from_clauses(self, quantifier=QUANTIFIER_EXISTS):   
        """
        Generates the prefix from the clauses specified.
        The order is determined by the order they occur in the formula
        
        :param quantifier: the quantifier type the variables should be quantified with. Default :class:`QUANTIFIER_EXISTS`
        :type quantifier: :class:`int`

        .. code-block:: python

            >>> pcnf = PCNF(from_clauses=[[1, 2], [-4, 3]])
            >>> print(pcnf.prefix)
            []
            >>> pcnf.prefix_from_clauses()
            >>> print(pcnf.prefix)
            [1, 2, 3, 4]
            >>> pcnf.prefix_from_clauses(QUANTIFIER_FORALL)
            >>> print(pcnf.prefix)
            [-1, -2, -3, -4]
            >>> # Setting a flag can do this automatically during initialization
            >>> pcnf2 = PCNF(from_clauses=[[1, 2], [-4, 3]], auto_generate_prefix=True) 
            >>> print(pcnf2.prefix)  
            [1, 2, 3, 4]
        """     
        tmp_prefix = set()
        for clause in self.clauses:
            tmp_prefix.update([abs(x) for x in clause])
        if quantifier == QUANTIFIER_FORALL:
            self.prefix = [-x for x in tmp_prefix]
        elif quantifier == QUANTIFIER_EXISTS:
            self.prefix = list(tmp_prefix)  
        elif quantifier == QUANTIFIER_NONE:
            pass
        else:
            raise RuntimeError(f"Illegal quantifier specified: {quantifier}!")

    def quantify_free_variables(self, quantifier = QUANTIFIER_EXISTS):
        """
        Quantification of free variables by adding them to the prefix.     

        :param quantifier: the quantifier type the variables should be quantified with. Default :class:`QUANTIFIER_EXISTS`
        :type quantifier: :class:`int`

        Usage example:

        .. code-block:: python

            >>> pcnf = PCNF(from_clauses=[[1, 2, 3], [-1, 2, 3], [-1, -2, -3]])
            >>> pcnf.forall(1)
            >>> print(pcnf.prefix)
            [-1]
            >>> print(pcnf.nv)
            3
            >>> pcnf.quantify_free_variables()
            >>> print(pcnf.prefix)
            [2, 3, -1] 
            >>> # free variables are added at the front
            >>> print(pcnf.nv)
            3
            >>> pcnf = PCNF(from_clauses=[[1, 2, 3], [-1, 2, 3], [-1, -2, -3]])
            >>> pcnf.forall(1)
            >>> pcnf.quantify_free_variables(QUANTIFIER_FORALL)
            >>> print(pcnf.prefix)
            [-2, -3, -1] 
        """
        if quantifier != QUANTIFIER_EXISTS and quantifier != QUANTIFIER_FORALL:
            raise RuntimeError("Illegal quantifier specified! Only QUNATIFIER_EXISTS and QUNATIFIER_FORALL are allowed!")
                
        if self.nv > len(self.prefix):
            var_lookup = set()
            free_vars = set()
            for v in self.prefix:
                var_lookup.add(abs(v))

            for c in self.clauses:
                for lit in c:
                    v = abs(lit)
                    if v not in var_lookup:
                        if v not in free_vars:
                            free_vars.add(v)
            
            if len(free_vars) > 0:
                new_prefix = [None] * (len(self.prefix) + len(free_vars))
                idx = 0
                for x in free_vars: #insert at the beginning
                    new_prefix[idx] = x * quantifier
                    idx += 1
                for v in self.prefix:
                    new_prefix[idx] = v
                    idx += 1
                self.prefix = new_prefix

    def normalize(self):
        """
        Normalizes the current formula. Free variables are eliminated by adding them to the prefix.
        Variable-ids are assigned by the order they are defined such that there are no gaps.

        Usage example:

        .. code-block:: python

            >>> pcnf = PCNF(from_clauses=[[-2, 4], [-4, 6], [-6, 2]])
            >>> pcnf.forall(6)
            >>> print(pcnf.nv)
            6
            >>> pcnf.normalize()   # eliminate free variables and re-map ids
            >>> print(pcnf.prefix) # 2 => 1, 4 => 2, 6 => 3
            [1, 2, -3]
            >>> print(pcnf.clauses)
            [[-1, 2], [-2, 3], [-3, 1]]
            >>> print(pcnf.nv)
            3
        """
        self.quantify_free_variables()
        mapping = [None] * (self.nv + 1)  #pre-allocate
        next_id = 1
        for idx, var in enumerate(self.prefix):
            self.prefix[idx] = next_id * (-1 if var < 0 else 1)
            mapping[abs(var)] = next_id
            next_id += 1
        self.nv = next_id - 1

        for cidx, clause in enumerate(self.clauses):
            for lidx, lit in enumerate(clause):
                self.clauses[cidx][lidx] = mapping[abs(lit)] * (-1 if lit < 0 else 1)
        self.__normalized = True
    
    def __check_normalized(self):
        if self.nv > len(self.prefix):
            return False
        for idx, elem in enumerate(self.prefix):
            if abs(elem) != (idx + 1):
                return False
        return True
            
    @property
    def is_normalized(self):
        """
        Indicates whether the formula was normalized. This is needed for certain solvers like :class:`pyqbf.solvers.Qute`.

        Usage example:

        .. code-block:: python

            >>> pcnf = PCNF(from_clauses=[[1, 2, 3], [-1, 2, 3], [-1, -2, -3]])
            >>> print(pcnf.is_normalized)
            False
            >>> pcnf.normalize()
            >>> print(pcnf.is_normalized)
            True
        """
        return self.__check_normalized()
    
    def append(self, clause, update_vpool=False):
        """
        Add one more clauses to the PCNF formula. This method additionally
        updates the number of variables, i.e. variable ``self.nv``, used
        in the formula.

        The additional keyword argument ``update_vpool`` can be set to
        ``True`` if the user wants to update for default static pool of
        variable identifiers stored in class :class:`Formula`. In light of
        the fact that a user may encode their problem manually and add
        thousands to millions of clauses using this method, the value of
        ``update_vpool`` is set to ``False`` by default.

        .. note::

            Setting ``update_vpool=True`` is required if a user wants to
            combine this :class:`PCNF` formula with other (clausal or
            non-clausal) formulas followed by the clausification of the
            result combination. Alternatively, a user may resort to using
            the method :meth:`extend` instead.

        :param clause: a new clause to add
        :param update_vpool: update or not the static vpool

        :type clause: :class:`list[int]`
        :type update_vpool: bool

        .. code-block:: python

            >>> from pyqbf.formula import PCNF
            >>> pcnf = PCNF(from_clauses=[[-1, 2], [3]])
            >>> pcnf.append([-3, 4])
            >>> print(pcnf.clauses)
            [[-1, 2], [3], [-3, 4]]
        """
        super().append(clause, update_vpool)

    def extend(self, clauses):
        """
        Add several clauses to PCNF formula. The clauses should be given in
        the form of list. For every clause in the list, method
        :meth:`append` is invoked.

        :param clauses: a list of new clauses to add
        :type clauses: :class`list[list[int]]`

        Example:

        .. code-block:: python

            >>> from pyqbf.formula import PCNF
            >>> pcnf = PCNF(from_clauses=[[-1, 2], [3]])
            >>> pcnf.extend([[-3, 4], [5, 6]])
            >>> print(pcnf.clauses)
            [[-1, 2], [3], [-3, 4], [5, 6]]
        """
        super().extend(clauses)

    def generate_blocks(self):
        """
        Computes a representation of the quantifier blocks as generator

        :returns: a generator for a list of lists representing the quantifier blocks
        :rtype: :class:`list[list[int]]`

        Example: 
        
        .. code-block:: python

            >>> from pyqbf.formula import PCNF
            >>> p = PCNF(from_clauses=[[-1, 2], [3]])
            >>> p.forall(1).exists(2,3)
            >>> print(list(p.generate_blocks()))
            [[-1], [2, 3]]
        """
        if len(self.prefix) == 0:
            return

        res = []
        q = QUANTIFIER_FORALL if self.prefix[0] < 0 else QUANTIFIER_EXISTS
        for var in self.prefix:            
            curq = QUANTIFIER_FORALL if var < 0 else QUANTIFIER_EXISTS
            if q != curq :
                yield res
                res = []
                q = curq
            res.append(var)
        if len(res) > 0:
            yield res
    
    def get_block(self, b):
        """
        Returns the quantifier block in index b. If there is no block on this index, an empty list is returned
        You can also use the special indicess :class:``OUTERMOST_BLOCK`` and :class:``INNERMOST_BLOCK``

        :param b: index of the block to be computed
        :type b: :class:`int`
        
        :returns: a list representing the block at index b
        :rtype: :class:`list[int]`

        Example:

        .. code-block:: python

            >>> from pyqbf.formula import PCNF
            >>> p = PCNF(from_clauses=[[-1, 2], [3]])
            >>> p.forall(1).exists(2,3)
            >>> p.get_block(1)
            [2,3]
            >>> p.exists(4).forall(5,6)
            >>> p.get_block(2)
            [-5,-6]
            >>> p.get_block(3)
            []
        """    
        if len(self.prefix) == 0:
            return []

        if b == INNERMOST_BLOCK:
            *_, last = self.generate_blocks()
            return last
        
        for bidx, block in enumerate(self.generate_blocks()):
            if bidx == b:
                return block
        return [] #outside of blocks => empty
    

    def get_block_type(self, b):
        """
        Returns the type of the quantifier block on index b. If there is no block on this index or the block is empty, :class:`QUANTIFIER_NONE` is returned
        You can also use the special indicess :class:``OUTERMOST_BLOCK`` and :class:``INNERMOST_BLOCK``
        
        :param b: index of the block to be computed
        :type b: :class:`int`
        
        :returns: :returns: :class:`QUANTIFIER_EXISTS`, :class:`QUANTIFIER_FORALL` or :class:`QUANTIFIER_NONE`
        :rtype: :class:`int`

        Example:

        .. code-block:: python

            >>> from pyqbf.formula import PCNF
            >>> p = PCNF(from_clauses=[[-1, 2], [3]])
            >>> p.forall(1).exists(2,3)
            >>> print(pcnf.get_block_type(0) == QUANTIFIER_FORALL)
            True
            >>> print(pcnf.get_block_type(1) == QUANTIFIER_EXISTS)
            True
            >>> print(pcnf.get_block_type(2) == QUANTIFIER_NONE)
            True
        """
        block = self.get_block(b)
        if block is not None and len(block) > 0:
            return QUANTIFIER_FORALL if block[0] < 0 else QUANTIFIER_EXISTS
        return QUANTIFIER_NONE

    def innermost_block(self, qtype = QUANTIFIER_NONE):
        """
        Returns the innermost quantifier block of the specified type. 
        If :class:`QUANTIFIER_NONE` is specified as a type, the last block regardless of quantifier will be returned.

        :param qtype: :class:`QUANTIFIER_EXISTS`, :class:`QUANTIFIER_FORALL` or :class:`QUANTIFIER_NONE`
        :type qtype: :class:`int`
        
        :returns: a list representing the innermost block
        :rtype: :class:`list[int]`

        Example:

        .. code-block:: python

            >>> from pyqbf.formula import PCNF
            >>> p = PCNF(from_clauses=[[-1, 2], [3]])
            >>> p.forall(1).exists(2,3)
            >>> p.innermost_block()
            [2,3]
            >>> p.innermost_block(QUANTIFIER_EXISTS)
            [2,3]
            >>> p.innermost_block(QUANTIFIER_FORALL)
            [-1]
            >>> p.exists(4).forall(5,6)
            >>> p.innermost_block()
            [-5,-6]
            >>> p.innermost_block(QUANTIFIER_EXISTS)
            [2,3,4]
            >>> p.innermost_block(QUANTIFIER_FORALL)
            [-5,-6]
        """
        if len(self.prefix) == 0:
            return []

        last = []
        cur = []
        for block in self.generate_blocks():
            last = cur
            cur = block

        if len(cur) == 0 or qtype == QUANTIFIER_NONE:
            return cur
        
        q = QUANTIFIER_FORALL if cur[0] < 0 else QUANTIFIER_EXISTS
        if q == qtype:
            return cur
        else:
            return last
        
    def outermost_block(self, qtype = QUANTIFIER_NONE):
        """
        Returns the outermost quantifier block of the specified type. 
        If :class:`QUANTIFIER_NONE` is specified as a type, the first block regardless of quantifier will be returned.

        :param qtype: :class:`QUANTIFIER_EXISTS`, :class:`QUANTIFIER_FORALL` or :class:`QUANTIFIER_NONE`
        :type qtype: :class:`int`
        
        :returns: a list representing the outermost block
        :rtype: :class:`list[int]`

        Example:

        .. code-block:: python

            >>> from pyqbf.formula import PCNF
            >>> p = PCNF(from_clauses=[[-1, 2], [3]])
            >>> p.forall(1).exists(2,3)
            >>> p.outermost_block()
            [-1]
            >>> p.outermost_block(QUANTIFIER_EXISTS)
            [2,3]
            >>> p.outermost_block(QUANTIFIER_FORALL)
            [-1]
            >>> p.exists(4, block=OUTERMOST_BLOCK).forall(5,6, block=OUTERMOST_BLOCK)
            >>> p.outermost_block()
            [-5,-6]
            >>> p.outermost_block(QUANTIFIER_EXISTS)
            [4]
            >>> p.outermost_block(QUANTIFIER_FORALL)
            [-5,-6]
        """
        if len(self.prefix) == 0:
            return []
        
        gen = self.generate_blocks()
        first = next(gen, [])
        if len(first) == 0 or qtype == QUANTIFIER_NONE:
            return first
        
        q = QUANTIFIER_FORALL if first[0] < 0 else QUANTIFIER_EXISTS
        if q == qtype:
            return first
        else:
            return next(gen, [])

    def count_quantifier_alternations(self):
        """
        Computes the amount of quantifier alternations of the current prefix

        :returns: the number of quantifier alternations
        :rtype: :class:`int`

        Example:

        .. code-block:: python

            >>> from pyqbf.formula import PCNF
            >>> p = PCNF(from_clauses=[[-1, 2], [3]])
            >>> p.forall(1).exists(2,3)
            >>> p.count_quantifier_alternations()
            1
            >>> p.exists(4).forall(5,6)
            >>> p.count_quantifier_alternations()
            2
        """
        if len(self.prefix) == 0:
            return 0

        return sum(1 for _ in self.generate_blocks()) - 1

    def from_aiger(self, aig, vpool=False):
        """

        Create a PCNF formula by Tseitin-encoding an input AIGER circuit.

        The input circuit is expected to be an object of class
        :class:`aiger.AIG`. Alternatively, it can be specified as an
        :class:`aiger.BoolExpr`, an ``*.aag`` filename or an AIGER
        string to parse. (Classes :class:`aiger.AIG` and
        :class:`aiger.BoolExpr` are defined in the `py-aiger package
        <https://github.com/mvcisback/py-aiger>`__.)

        :param aig: an input AIGER circuit
        :param vpool: pool of variable identifiers (optional)

        :type aig: :class:`aiger.AIG` (see `py-aiger package <https://github.com/mvcisback/py-aiger>`__)
        :type vpool: :class:`.IDPool`

        Example:

        .. code-block:: python

            >>> import aiger
            >>> x, y, z = aiger.atom('x'), aiger.atom('y'), aiger.atom('z')
            >>> expr = ~(x | y) & z
            >>> print(expr.aig)
            aag 5 3 0 1 2
            2
            4
            8
            10
            6 3 5
            10 6 8
            i0 y
            i1 x
            i2 z
            o0 6c454aea-c9e1-11e9-bbe3-3af9d34370a9
            >>>
            >>> from pyqbf.formula import PCNF
            >>> pcnf = PCNF(from_aiger=expr.aig)
            >>> print(pcnf.nv)
            5
            >>> print(pcnf.clauses)
            [[3, 2, 4], [-3, -4], [-2, -4], [-4, -1, 5], [4, -5], [1, -5]]
            >>> print(['{0} <-> {1}'.format(v, pcnf.vpool.obj(v)) for v in pcnf.inps])
            ['3 <-> y', '2 <-> x', '1 <-> z']
            >>> print(['{0} <-> {1}'.format(v, pcnf.vpool.obj(v)) for v in pcnf.outs])
            ['5 <-> 6c454aea-c9e1-11e9-bbe3-3af9d34370a9']
        """
        super().from_aiger(aig, vpool)

    def from_clauses(self, clauses, by_ref=False):
        """
        This methods copies a list of clauses into a PCNF object. The
        optional keyword argument ``by_ref`` (``False`` by default) indicates whether the clauses should be deep-copied or
        copied by reference.

        :param clauses: a list of clauses
        :param by_ref: a flag to indicate whether to deep-copy the clauses or copy them by reference

        :type clauses: :class:`list(list(int))`
        :type by_ref: :class:`bool`

        Example:

        .. code-block:: python

            >>> from pyqbf.formula import PCNF
            >>> pcnf = PCNF(from_clauses=[[-1, 2], [1, -2], [5]])
            >>> print(pcnf.clauses)
            [[-1, 2], [1, -2], [5]]
            >>> print(pcnf.nv)
            5
        """
        super().from_clauses(clauses, by_ref)

    def from_file(self, fname, comment_lead=['c'], compressed_with='use_ext'):
        """
        Read a PCNF formula from a file in the `QDIMACS <https://www.qbflib.org/qdimacs.html>`__ format. A file name is
        expected as an argument. A given file can be compressed by either
        gzip, bzip2, or lzma.

        .. note::

            The parameter ``comment_lead`` exists due to compatibility with
            :func:`pysat.formula.CNF.from_file` but does not serve a purpose here

        :param fname: name of a file to parse.
        :param comment_lead: a list of characters leading comment lines
        :param compressed_with: file compression algorithm

        :type fname: str
        :type comment_lead: list(str)
        :type compressed_with: str

        Note that the ``compressed_with`` parameter can be ``None`` (i.e.
        the file is uncompressed), ``'gzip'``, ``'bzip2'``, ``'lzma'``, or
        ``'use_ext'``. The latter value indicates that compression type
        should be automatically determined based on the file extension.
        Using ``'lzma'`` in Python 2 requires the ``backports.lzma``
        package to be additionally installed.

        Usage example:

        .. code-block:: python

            >>> from pyqbf.formula import PCNF
            >>> pcnf1 = PCNF()
            >>> pcnf1.from_file('some-file.qcnf.gz', compressed_with='gzip')
            >>>
            >>> cnf2 = CNF(from_file='another-file.qcnf')
        """
        super().from_file(fname, comment_lead, compressed_with)

    def from_string(self, string, comment_lead=['c']):
        """
        Read a PCNF formula from a string. The string should be specified as
        an argument and should be in the `QDIMACS <https://www.qbflib.org/qdimacs.html>`__ PCNF format. The only
        default argument is ``comment_lead``, which can be used for parsing
        specific comment lines.

        :param string: a string containing the formula in QDIMACS.
        :param comment_lead: a list of characters leading comment lines

        :type string: str
        :type comment_lead: list(str)

        Example:

        .. code-block:: python

            >>> from pyqbf.formula import PCNF
            >>> pcnf1 = PCNF()
            >>> pcnf1.from_string('p cnf 2 2\\na 1 0\\ne 2 0\\n-1 2 0\\n1 -2 0')
            >>> print(pcnf1.clauses)
            [[-1, 2], [1, -2]]
            >>>
            >>> print(pcnf1.prefix)
            [-1, 2]
            >>> pcnf2 = PCNF(from_string='p cnf 3 3\\n-1 2 0\\n-2 3 0\\n-3 0\\n')
            >>> print(pcnf2.clauses)
            [[-1, 2], [-2, 3], [-3]]
            >>> print(pcnf2.nv)
            3)
            >>> print(pcnf2.prefix)
            []
        """
        super().from_string(string, comment_lead)

    def to_file(self, fname, comments=None, compress_with='use_ext'):
        """
        A method for saving a PCNF formula into a file in the `QDIMACS <https://www.qbflib.org/qdimacs.html>`__
        format. A file name is expected as an argument. Additionally,
        supplementary comment lines can be specified in the ``comments``
        parameter. Also, a file can be compressed using either gzip, bzip2,
        or lzma (xz).

        :param fname: a file name where to store the formula.
        :param comments: additional comments to put in the file.
        :param compress_with: file compression algorithm

        :type fname: :class:`str`
        :type comments: :class:`list[str]`
        :type compress_with: :class:`str`

        Note that the ``compress_with`` parameter can be ``None`` (i.e.
        the file is uncompressed), ``'gzip'``, ``'bzip2'``, ``'lzma'``, or
        ``'use_ext'``. The latter value indicates that compression type
        should be automatically determined based on the file extension.
        Using ``'lzma'`` in Python 2 requires the ``backports.lzma``
        package to be additionally installed.

        Example:

        .. code-block:: python

            >>> pcnf = PCNF()            ...
            >>> # the formula is filled with a bunch of clauses and a prefix
            >>> pcnf.to_file('some-file-name.qcnf')  # writing to a file
        """
        super().to_file(fname, comments, compress_with)


    def var_order_relation(self):
        """
        Returns an order relation with reference to the prefix, which can be used to order clauses

        :returns: a list containing the order
        :rtype: :class:`list[int]`

        Usage Exaple:

        .. code-block:: python

            >>> pcnf = PCNF(from_file="/path/to/formula.qdimacs")
            >>> print(pcnf.prefix)
            [2, 3, 1]
            >>> order = pcnf.var_order_relation()
            >>> print(order)
            [None, 3, 1, 2]
            >> print(order[1])
            3
            >> print(order[1] < order[2])
            False

        """
        order = [None] * (self.nv + 1)
        for idx, lit in enumerate(self.prefix):
            if idx >= len(order):
                #extend
                order = [order] * (idx - len(order) + 1)
            order[abs(lit)] = idx + 1
        return order

    def sort_clauses(self):
        """
        Sorts clauses according to the order relation given by the prefix (:func:`var_order_relation`).
        Literals which are not in the prefix (free variables) are inserted at the beginning

        Usage Exaple:

        .. code-block:: python

            >>> pcnf = PCNF(from_clauses=[[1, 2], [-1, -2]])
            >>> pcnf.forall(2).exists(1)
            >>> print(pcnf.prefix)
            [-2, -1]
            >>> pcnf.sort_clauses()
            >>> print(pcnf.clauses)
            [[2, 1], [-2, -1]]
        """
        order = self.var_order_relation()
        for clause in self.clauses:
            clause.sort(key=lambda x: order[abs(x)] if x < len(order) and order[abs(x)] is not None else 0)

    def minimize_prefix(self):
        """
        Removes all unnecessary variables from the prefix.

        Usage Exaple:

        .. code-block:: python

            >>> pcnf = PCNF(from_clauses=[[1, 2], [-1, -2]])
            >>> pcnf.forall(1,2,3).exists(4,5,6)
            >>> print(pcnf.prefix)
            [-1, -2, -3, 4, 5, 6]
            >>> pcnf.minimize_prefix()
            >>> print(pcnf.prefix)
            [-1, -2]
        """
        existing_vars = set()
        for clause in self.clauses:
            existing_vars = existing_vars.union([abs(x) for x in clause])
        
        new_prefix = []
        for var in self.prefix:
            if abs(var) in existing_vars:
                new_prefix.append(var)
        self.prefix = new_prefix


def split_atoms_and_auxvars(f):
    """
    Computes the atoms (literals) and auxvars (tseitin-variables) from the given :class:`pysat.formula.Formula` using the internal :class:`pysat.formula.IDPool`.

    :param formula: an abstract formula representation 
    :type formula: :class:`pysat.formula.Formula`

    :returns: a list of atoms and auxvars read from the vpool of the formula
    :rtype: :class:`tuple[list[int], list[int]]`

    Usage example:

    .. code-block:: python

        >>> from pysat.formula import Atom
        >>> formula = (Atom('x') & Atom('y')) | Atom('z')
        >>> clauses = [c for c in formula]
        >>> print(clauses)
        [[1, -3], [2, -3], [3, -1, -2], [3, 4]]
        >>> atoms, auxvars = split_atoms_and_auxvars(formula)
        >>> print(atoms)
        [1, 2, 4]
        >>> print(auxvars)
        [3]
    """
    vpool = f._vpool[f._context]
    atoms = []
    auxvars = []
    for var, obj in vpool.id2obj.items():
        if isinstance(obj, formula.Atom):
            atoms.append(var)
        elif isinstance(obj, formula.Neg):
            continue    #skip negation, they are duplicated
        else:
            auxvars.append(var)
    return atoms, auxvars


def to_pcnf(cnf):
    """
    Safely transforms the input to a :class:`PCNF` class.
    The following inputs are currently supported for conversion:

    * :class:`PCNF`:              (no copy is made)
    * :class:`pysat.formula.CNF`: (variables are existentially quantified)
    * :class:`list[list[int]]`:   (variables are existentially quantified)
    * :class:`pysat.formula.Formula`: (variables are existentially quantified, tseitin variables occur at the end of the prefix)

    :param cnf: target of the domain expansion
    :type  cnf: e.g. :class:`pysat.formula.CNF`


    Usage example:

    .. code-block:: python

        >>> cnf = pysat.formula.CNF(from_clauses = [[-1, 2], [-2, 3], [-3, 1]])
        >>> pcnf = to_pcnf(cnf)
        >>> print(pcnf.prefix)
        [1, 2, 3]
        >>> print(pcnf.clauses)
        [[-1, 2], [-2, 3], [-3, 1]]
        >>> clauses = [[-1, 2], [-2, 3], [-3, 1]]
        >>> pcnf2 = to_pcnf(clauses)
        >>> print(pcnf2.prefix)
        [1, 2, 3]
        >>> print(pcnf2.clauses)
        [[-1, 2], [-2, 3], [-3, 1]]
        >>> f = (Atom('x') & Atom('y')) | Atom('z')
        >>> pcnf3 = to_pcnf(f)
        >>> print(pcnf3.prefix)
        [1, 2, 4, 3]
        >>> print("Clauses: ", pcnf3.clauses)
        [[1, -3], [2, -3], [3, -1, -2], [3, 4]]
        >>> print("Atoms:", pcnf3.atoms)
        [1, 2, 4]
        >>> print("Auxvars:", pcnf3.auxvars)
        [3]

    """
    if isinstance(cnf, PCNF):
        return cnf  #already a PCNF
    
    elif isinstance(cnf, formula.CNFPlus) and cnf.atmosts:
        raise NotImplementedError("Atmost-constraints have not yet a conversion to PCNF!")

    elif isinstance(cnf, formula.CNF):    
        pcnf = PCNF(from_cnf=cnf, auto_generate_prefix=True)
        return pcnf

    elif isinstance(cnf, list):
        pcnf = PCNF(from_clauses=cnf, auto_generate_prefix=True)
        return pcnf

    elif isinstance(cnf, formula.Formula):
        clauses = [c for c in cnf]
        pcnf = PCNF(from_clauses=clauses)
        pcnf.atoms, pcnf.auxvars = split_atoms_and_auxvars(cnf)
        pcnf.prefix.extend(pcnf.atoms)
        pcnf.prefix.extend(pcnf.auxvars)
        pcnf.minimize_prefix() #remove unnecessary variables
        return pcnf

    else:
        raise TypeError(f"An object of type {type(cnf)} has no known conversion to PCNF!")

