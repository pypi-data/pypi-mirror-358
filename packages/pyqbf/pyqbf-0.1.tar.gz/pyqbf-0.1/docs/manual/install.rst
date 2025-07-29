Installation Guide for PyQBF
============================

Installation
------------
.. code-block::

    pip install --user git+https://gitlab.sai.jku.at/qbf/pyqbf.git


.. note::

    Git has to be available for this command to work


Install from Git Repository
---------------------------
PyQBF can be cloned the following way.

.. code-block::

    git clone git@gitlab.sai.jku.at:qbf/pyqbf.git --recursive 

Or, if you already cloned the project

.. code-block::

    git submodule update --init --recursive


Then the project can be installed by navigating to the directory and executing the following command
.. code-block::
    
    pip install .

.. warning::

    PyQBF is not supported on Windows-systems!

.. warning::

    Currently, MacOS is not fully supported by PyQBF due to problems in the building pipeline.

List of Requirements
--------------------
**NOTE**: these requirements (usually) do not have to be installed manually.
Pip will take care of them during the installation. 
If problems occur, here are the system-dependencies needed for running PyQBF.
In the following subsections you will furthermore find the commands to install the dependencies on your operating system.

* CMake version >= 3.13
* Python >= 3.8
* g++ Compiler
* ZeroMQ (dev)
* ZLib (dev)

Ubuntu
~~~~~~
Python should already be pre-installed.

.. code-block::

    apt-get -y install cmake g++ libzmq3-dev zlib1g-dev


Fedora
~~~~~~

.. code-block::

    dnf install cmake python3-devel python3-pip g++ zeromq-devel zlib-devel  -y