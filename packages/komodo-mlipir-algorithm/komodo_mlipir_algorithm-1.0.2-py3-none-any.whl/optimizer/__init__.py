"""
Komodo Mlipir Algorithm (KMA) - A Nature-Inspired Optimization Algorithm.

This package provides a Python implementation of the Komodo Mlipir Algorithm,
a metaheuristic optimization algorithm inspired by the behavior of Komodo dragons.

Basic usage:
    >>> from komodo_mlipir import KomodoMlipirAlgorithm
    >>> 
    >>> def objective_function(x):
    ...     return -sum(xi**2 for xi in x)
    >>> 
    >>> kma = KomodoMlipirAlgorithm(
    ...     fitness_function=objective_function,
    ...     search_space=[(-5, 5), (-5, 5)]
    ... )
    >>> kma.fit()
    >>> results = kma.get_results()

For more examples, see the documentation at:
https://komodo-mlipir-algorithm.readthedocs.io/
"""

from optimizer.algorithm.komodo_mlipir_algorithm import KomodoMlipirAlgorithm, KMA
from optimizer.__version__ import __version__

__all__ = [
    "KomodoMlipirAlgorithm",
    "KMA",
    "__version__",
]

# Package metadata
__author__ = "Pejalan Sunyi"
__email__ = "khalifardy.miqdarsah@example.com"
__license__ = "MIT"