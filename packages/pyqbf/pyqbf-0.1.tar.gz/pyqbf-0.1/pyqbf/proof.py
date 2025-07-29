"""
    ===============
    List of classes
    ===============

    .. autosummary::
        :nosignatures:

        QratType
        QratLemma
        QratProof


    ==================
    Module description
    ==================

    This module provides classes and methods for manipulation and handling of proofs for QBFs 

   

    At the moment, we only support QRAT [1]_.


    .. [1] Heule, Marijn JH, Martina Seidl, and Armin Biere. "A unified proof system for QBF preprocessing." International Joint Conference on Automated Reasoning. Cham: Springer International Publishing, 2014.

    ==============
    Module details
    ==============
"""
import enum
import dataclasses
from io import StringIO

class QratType(enum.Enum):
    """
    Contains all available types for the QRAT lemmas
    """
    QRATA = "a"
    QRATE = "d"
    QRATU = "u"


@dataclasses.dataclass
class QratLemma:
    """
    Class for storing a QRAT-Lemma

    :ivar types: type of the lemma
    :ivar clause: clause information of the lemma

    :vartype types: :class:`QratType`
    :vartype clause: :class:`list[int]`
    """
    type: QratType = QratType.QRATA
    clause: list[int] = dataclasses.field(default_factory=list)
    pivot: int = 0

    def __str__(self):
        type_str = ""
        if self.type != QratType.QRATA:
            type_str = str(self.type.value) + " "
        clause_str = ""
        if self.pivot != 0:
            clause_str = str(self.pivot) + " "
        for x in self.clause:
            if x != self.pivot:
                clause_str += str(x) + " "
        clause_str += "0"
        return type_str + clause_str 
    

class QratProof:

    """
        Class for manipulating QRAT-proofs. It can be used for creating
        formulas, reading them from a file+, or writing them to a file.

        
        :param from_file: a QRAT filename to read from
        :param from_fp: a file pointer to read from
        :param from_string: a string storing a PCNF formula in QDIMACS format

        :type from_file: :class:`str`
        :type from_fp: :class:`SupportsRead[str]`
        :type from_string: :class:`str`

        :ivar lemmas: list of proof-lemmas
        :ivar comments: Comments encountered during parsing

        :vartype lemmas: :class:`list[int]`
        :vartype comments: :class:`list[str]`

    """
    def __init__(self, from_file=None, from_fp=None, from_string=None):
        """
        Default constructor
        """
        self.lemmas = []
        self.comments = []

        if from_file:
            self.from_file(from_file)
        elif from_fp:
            self.from_fp(from_fp)
        elif from_string:
            self.from_string(from_string)

    def __len__(self):
        return len(self.lemmas)
    
    def __getitem__(self, c):
        return self.lemmas[c]

    def from_file(self, fname):
        """
        Read a QRAT-proof from a file

        :param fname: file path to the file
        :type fname: :class:`str`

        .. code-block:: python

            >>> proof = QratProof()
            >>> proof.from_file("/path/to/proof.qrat")

        """
        with open(fname, "r") as fp:
            self.from_fp(fp)

    def from_string(self, text):
        """
        Read a QRAT-proof from a string

        :param text: string containing the proof 
        :type text: :class:`str`

        .. code-block:: python

            >>> proof = QratProof()
            >>> proof.from_string("1 2 0\\nd 3 4 0\\nu 6 2 0")

        """
        self.from_fp(StringIO(text))

    def from_fp(self, fp):
        """
        Read a QRAT-proof from a file pointer

        :param fp: file pointer to file containing the proof 
        :type fp: :class:`SupportsRead[str]`

        .. code-block:: python

            >>> proof = QratProof()
            >>> with open("/path/to/proof.qrat", "r") as fp:
            ...     proof.from_fp(fp)

        """
        self.comments.clear()
        self.lemmas.clear()
        
        for line in fp:
            if line.strip() == "":
                continue
            lemma = QratLemma()
            comment = ""
            splitter = line.strip().split(" ")
            idx = 0
            if splitter[idx] == 'd':
                lemma.type = QratType.QRATE
                idx += 1
            elif splitter[idx] == 'u':
                lemma.type = QratType.QRATU
                idx += 1
            else:
                lemma.type = QratType.QRATA
            
            inComment = False
            while idx < len(splitter):
                if inComment:
                    if len(comment) > 0:
                        comment += " "
                    comment += splitter[idx]
                else:
                    if splitter[idx].lstrip("-").isdigit():
                        digit = int(splitter[idx])
                        if digit != 0:
                            lemma.clause.append(digit)
                        else:
                            inComment = True
                    else:
                        inComment = True
                idx += 1

            if len(lemma.clause) > 0:
                lemma.pivot = lemma.clause[0]
            self.lemmas.append(lemma)
            self.comments.append(comment)

    def to_string(self, with_comments=False):
        """
            Return the current state of the object in QRAT encoding.

            :returns: a QRAT representation of the formula
            :rtype: :class:`str`

            Usage example:

            .. code-block:: python

                >>> proof = QratProof(from_file="/path/to/proof.qrat")
                >>> print(proof.comments)
                ["clause addition", "universal reduction"]
                >>> print(proof.to_string())
                1 2 0
                u 2 1 0
                >>> print(proof.to_string(with_comments=True))
                1 2 0 clause addition
                u 2 1 0 universal reduction

        """
        if not with_comments:
            return "\n".join([str(lem) for lem in self.lemmas])
        else:
            lines = []
            for idx, lem in enumerate(self.lemmas):
                lines.append(str(lem))
                if idx < len(self.comments):
                    lines[idx] += " " + self.comments[idx]
            return "\n".join(lines)
            
    def to_file(self, fname, with_comments=False):
        """
            Writes the current state of the object in QRAT encoding to a file.

            :param fname: file path to the file
            :type fname: :class:`str`

            Usage example:

            .. code-block:: python

                >>> proof = QratProof(from_file="/path/to/proof.qrat")
                >>> proof.to_file("/path/to/target1.qrat")
                >>> proof.to_file("/path/to/target2.qrat", with_comments=True)

        """    
        with open(fname, "w") as fp:
            self.to_fp(fp, with_comments)
    
    def to_fp(self, fp, with_comments=False):
        """
            Writes the current state of the object in QRAT encoding to a filepointer.

                :param fp: file pointer to target
                :type fp: :class:`SupportsRead[str]`

            Usage example:

            .. code-block:: python

                >>> proof = QratProof(from_file="/path/to/proof.qrat")
                >>> with open("/path/to/target1.qrat", "w") as fp:
                ...     proof.to_fp(fp)
                >>> with open("/path/to/target2.qrat", "w") as fp:
                ...     proof.to_fp(fp, with_comments=True)

        """
        for idx, lem in enumerate(self.lemmas):
            if not with_comments or idx >= len(self.comments):
                print(lem, file=fp)
            else:
                print(lem, self.comments[idx], file=fp)

    def add(self, lemma_type, clause):
        """
            Adds a lemma of the specified type to the proof.

            :param lemma_type: type of the lemma
            :param clause: clause learnt by the lemma

            :type lemma_type: :class:`QratType`
            :type clause: :class:`list[int]`

            .. code-block:: python

                >>> proof = QratProof(from_file="/path/to/proof.qrat")
                >>> proof.add(QratType.QRATA, [1, 2])
                >>> proof.add(QratType.QRATE, [1, 2])
                >>> proof.add(QratType.QRATU, [2, 1])
        """
        self.lemmas.append(QratLemma(lemma_type, clause, clause[0] if len(clause) > 0 else 0))
