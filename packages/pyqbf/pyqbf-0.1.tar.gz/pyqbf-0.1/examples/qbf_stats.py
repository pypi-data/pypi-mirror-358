from argparse import ArgumentParser
import os
import sys
import time
from enum import Enum

from pyqbf.formula import PCNF, OUTERMOST_BLOCK, INNERMOST_BLOCK, QUANTIFIER_FORALL

# This example is a small tool to print out a table containing information about qbf-formulas.

COL_FILE_TEXT = "File"
COL_CLAUSES_TEXT = "Clauses"
COL_CLAUSES_WIDTH = 10
COL_VARS_TEXT = "Vars"
COL_VARS_WIDTH = 10
COL_QUANT_ALT_TEXT = "Quant. Alt."
COL_QUANT_ALT_WIDTH = 13
COL_OUTERMOST_QUANT_TEXT = "Outer Quant."
COL_OUTERMOST_QUANT_WIDTH = 14
COL_INNERMOST_QUANT_TEXT = "Inner Quant."
COL_INNERMOST_QUANT_WIDTH = 14
COL_BLOCK_SIZES_TEXT = "Block Sizes"
COL_BLOCK_SIZES_WIDTH = 40


COLUMN_TEXTS = [COL_FILE_TEXT, COL_VARS_TEXT, COL_CLAUSES_TEXT, COL_QUANT_ALT_TEXT, COL_OUTERMOST_QUANT_TEXT, COL_INNERMOST_QUANT_TEXT, COL_BLOCK_SIZES_TEXT]
COLUMN_WIDTHS = [0, COL_VARS_WIDTH, COL_CLAUSES_WIDTH, COL_QUANT_ALT_WIDTH, COL_OUTERMOST_QUANT_WIDTH, COL_INNERMOST_QUANT_WIDTH, COL_BLOCK_SIZES_WIDTH]  #file is variable size
COLUMN_ALIGNMENTS = ['l', 'c', 'c', 'c', 'c', 'c', 'l']

OUT_FILE = sys.stdout
SEP = "|"
CSV_SEP = ";"
TAB = "  "

LATEX_ESCAPES = ["^", "_", "&", "%", "$", "#", "{", "}", "~"]

width = 0
padding = ""

class WriteMode(Enum):
    text = 0
    html = 1
    latex = 2
    csv = 3

def out(*args):
    print(*args, file=OUT_FILE)

def write_preamble(mode = WriteMode.text): 
    if mode == WriteMode.text:
        global width
        out("-" * width)
        out(SEP + SEP.join(text.center(COLUMN_WIDTHS[idx]) for idx, text in enumerate(COLUMN_TEXTS)) + SEP)
        out("-" * width)

    elif mode == WriteMode.html:
        global padding
        out(f"<html>")
        out(TAB + "<style> table, th, td {border: 1px solid black; border-collapse: collapse;padding: 10px}</style")
        out(f"{TAB}<body>\n{2*TAB}<table>")
        padding = 3*TAB
        out(padding + "<tr>")
        padding += TAB
        for text in COLUMN_TEXTS:
            out(padding + "<th>" + text + "</th>")
        padding = padding[len(TAB):]
        out(padding + "</tr>")

    elif mode == WriteMode.latex:
        out("\\documentclass[12pt]{standalone}")
        out("\\usepackage{array}")
        out("\\begin{document}")
        out(TAB + "\\begin{tabular} {|" + '|'.join(COLUMN_ALIGNMENTS) + "|}")
        out(2*TAB + "\\hline")
        out(2*TAB + " & ".join(["\\textbf{" + text + "}" for text in COLUMN_TEXTS]) + "\\\\")
        out(2*TAB + "\\hline")

    elif mode == WriteMode.csv:
        out(CSV_SEP.join(text for text in COLUMN_TEXTS))

def latex_correct_escapes(value):
    for rep in LATEX_ESCAPES:
        value = str(value).replace(rep, "\\"+rep)
    return value

def write_data_line(values, mode = WriteMode.text):
    if mode == WriteMode.text:
        def format_value(value, idx):
            if COLUMN_ALIGNMENTS[idx] == 'c':
                return str(value).center(COLUMN_WIDTHS[idx])
            else:
                return str(value).ljust(COLUMN_WIDTHS[idx])

        out(SEP + SEP.join(format_value(value, idx) for idx, value in enumerate(values)) + SEP)
        out("-" * width)
    
    elif mode == WriteMode.html:
        global padding
        out(padding + "<tr>")
        padding += TAB
        for value in values:
            out(padding + "<td>" + str(value) + "</td>")
        padding = padding[len(TAB):]
        out(padding + "</tr>")

    elif mode == WriteMode.latex:
        out(2*TAB + " & ".join([str(value) for value in values]) + "\\\\")
        out(2*TAB + "\\hline")

    elif mode == WriteMode.csv:
        out(CSV_SEP.join([str(value) for value in values]))

def write_postfix(mode = WriteMode.text):
    if mode == WriteMode.text:
        pass #done already

    elif mode == WriteMode.html:
        out(f"{2*TAB}</table>\n{TAB}</body>\n</html>")

    elif mode == WriteMode.latex:
        out(TAB + "\\end{tabular}\n\\end{document}")

    elif mode == WriteMode.csv:
        pass  #done already

def generate_data(file, mode = WriteMode.text, avg_blocks = False):
    def file_to_repr(f):
        if mode == WriteMode.latex:
            return latex_correct_escapes(f)
        elif mode == WriteMode.csv:
            return "\"" + file + "\""
        else:
            return file

    def quant_to_repr(q):
        #free variables => empty prefix => propositional which is existential
        if mode == WriteMode.latex:
            return "$\\forall$" if q == QUANTIFIER_FORALL else "$\\exists$" 
        elif mode == WriteMode.html:
            return "&#8704;" if q == QUANTIFIER_FORALL else "&#8707;" #html codes for the quantifier
        else:
            return "universal" if q == QUANTIFIER_FORALL else "existential"

    def count_block_sizes(pcnf):
        block_sizes = [len(block) for block in pcnf.generate_blocks()]
        if avg_blocks:
            return str(round(sum(block_sizes) / len(block_sizes), 4)) if len(block_sizes) > 0 else 0
        else:
            return "-".join([str(x) for x in block_sizes])

    pcnf = PCNF(from_file=file)
    return [
            file_to_repr(file),                                    # file
            pcnf.nv,                                               # vars
            len(pcnf.clauses),                                     # clauses
            pcnf.count_quantifier_alternations(),                  # quant. alt.
            quant_to_repr(pcnf.get_block_type(OUTERMOST_BLOCK)),   # outer quant.       
            quant_to_repr(pcnf.get_block_type(INNERMOST_BLOCK)),   # inner quant.       
            count_block_sizes(pcnf)                                # block sizes
           ]    


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--path", help="Target folder to be analyzed", default=".")
    parser.add_argument("--extension", help="The file extension to be analyzed", default="qdimacs")
    parser.add_argument("--abspath", help="If specified, the filename will be displayed with absolute path", action="store_true")
    parser.add_argument("--html", help="If specified, the output will be generated in HTML format", action="store_true")
    parser.add_argument("--latex", help="If specified, the output will be generated in latex format", action="store_true")
    parser.add_argument("--csv", help="If specified, the output will be generated in csv format", action="store_true")
    parser.add_argument("-o", "--output", help="Specifies the file the content is written to", default=None)
    parser.add_argument("--time", help="Displays the time needed for printing/computing the task", action="store_true")
    parser.add_argument("-n","--numbers", help="If specified, display line numbers", action="store_true")
    parser.add_argument("--block-avg", help="If specified, averages out the block size", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(args.path) or not os.path.isdir(args.path):
        print("Invalid folder path!")
        exit(-1)

    #check multiple modes
    checksum = sum([1 for x in [args.html, args.latex, args.csv] if x])

    if checksum > 1:
        print("Can not write more than one mode simultaneously!")
        exit(-1)

    mode = WriteMode.text
    if args.html:
        mode = WriteMode.html

    elif args.latex:
        mode = WriteMode.latex

    elif args.csv:
        mode = WriteMode.csv

    if args.output is not None:
        OUT_FILE = open(args.output, "w+")

    start = time.time()
    try:
        folder = []
        for root, _, files in os.walk(args.path):
            for file in files:
                folder.append(os.path.join(root, file))
        files = [os.path.abspath(f) if args.abspath else f for f in folder if f.endswith(args.extension)]
        
        if len(files) == 0:
            raise Exception("No relevant files found!")
            
        COLUMN_WIDTHS[0] = len(max(files, key=len)) + 5

        if args.numbers:
            COLUMN_TEXTS.insert(0, "Nr.")
            COLUMN_WIDTHS.insert(0, max(3, len(str(len(files))) + 2))
            COLUMN_ALIGNMENTS.insert(0, "c")
        
        if args.block_avg:
            idx = COLUMN_TEXTS.index(COL_BLOCK_SIZES_TEXT)
            COLUMN_TEXTS[idx] = "Avg. " + COLUMN_TEXTS[idx]
            COLUMN_WIDTHS[idx] = 16
            COLUMN_ALIGNMENTS[idx] = "c"

        width = len(SEP) + sum(COLUMN_WIDTHS) + len(COLUMN_WIDTHS) * len(SEP)

        write_preamble(mode)
        for idx, file in enumerate(files):
            values = generate_data(file, mode, args.block_avg)     
            if args.numbers:
                values.insert(0, idx + 1)
            write_data_line(values, mode)

        write_postfix(mode)
    except Exception as ex:
        if args.output is not None:
            OUT_FILE.close()
        raise ex

    end = time.time()

    if args.time:
        print(f"qbf_stats finished in {(end-start):.6f}s")

    if args.output is not None:
        OUT_FILE.close()
