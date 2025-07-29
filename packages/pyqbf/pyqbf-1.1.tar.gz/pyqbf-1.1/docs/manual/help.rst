===============
Common Problems
===============

On this page you will find answers and fixes to commonly known problems when dealing with our framework.

.. contents::
    :depth: 3
    :local:


Installation
============
Externally-managed-environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Error-Message
"""""""""""""

.. code-block::

    error: externally-managed-environment                                                                                                                                        
    × This environment is externally managed
    ....

Prerequisites
"""""""""""""
Running ``pip install .``

Solution
""""""""
This error happens on new python versions.
In order to fix this, create a new virtual environment, activate it and re-run the command.
Details about this topic can be found under the name `PEP 668 <https://peps.python.org/pep-0668/>`_.
The following is an example of initializing a simple venv:

.. code-block:: bash

    python -m venv .venv
    source .venv/bin/activate
    pip install .


Another solution (which we do not recommend but will work) is adding the ``--break-system-packages``-flag and running again:

.. code-block:: bash

    pip install . --break-system-packages

.. warning::

    If you choose to break the system packages and enforce the installation, you might break your python-environment!
    Please only consider this option if you know what you are doing!

Runtime
=======

ModuleNotFoundError: PySAT
~~~~~~~~~~~~~~~~~~~~~~~~~~
Error-Message
"""""""""""""
``ModuleNotFoundError: No module named 'pysat'``

Prerequisites
"""""""""""""
Running any python-side PyQBF.

Solution
""""""""
The ``pysat``-package is not installed or was not found. 
If you use a virtual environment, please check if it is active and the package is installed.
You can install all python-packages required for PyQBF using the ``./requirements.txt`` file as shown in the :doc:`installation guide <../manual/install>`.

.. note::

    This package can **not** be installed using ``pip install pysat`` as this is a different package.
    The unique package name of PySAT is ``pip install python-sat``


Permission denied when executing execvpe
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Error-Message
"""""""""""""

``[QuAPI] [ERROR] [<id>] Could not execvpe! Killing this process. Error: Permission denied``

Prerequisites
"""""""""""""

* using :class:`pyqbf.solvers.QuAPI` with a custom path
* using :class:`pyqbf.solvers.Caqe`
* using :class:`pyqbf.solvers.Solver` with ``use_quapi=true``
* any other usage of QuAPI in the Backend

Solution
""""""""
This error occurs when the executable targeted by QuAPI does not have permission to be executed.
If a custom path is used, please check again if the file specified by the path can be run by the program.
If this occurs within the PyQBF-framework, navigate to the ``./executables`` folder from the repository's root 
and manually add the corresponding permission using e.g. ``chmod +x <file>``


Deadlock when using Qute and QuAPI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Error-Message
"""""""""""""
No error message, the solver stays idle and does not return.

Prerequisites
"""""""""""""

* using :class:`pyqbf.solvers.Solver` with ``use_quapi=true`` and ``SolverNames.Qute`` as backend
* using :class:`pyqbf.solvers.QuAPI` with a custom path to a Qute solver
* any other usage of QuAPI with Qute

Furthermore, no assumptions were provided.

Solution
""""""""
Currently, there is no known solution for this problem. 
As it only occurs when using QuAPI without assumptions, we suggest only use this combination when working with assumptions and else use the basic version of Qute.
