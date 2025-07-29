import pyqbf_cpp
import pathlib

VERSION = (1, 1)

__version__ = "%d.%d" % VERSION

__all__ = ['formula', 'solvers', 'process', 'proof']

pyqbf_cpp.init_module(str(pathlib.Path(__file__).parent.resolve()))