"""
Setup configuration for Komodo Mlipir Algorithm package.

This file is used to build and distribute the package via pip.
"""

from setuptools import setup, find_packages
import os
import codecs
import re

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from README
with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = fh.read()

# Get version from __version__ file
with codecs.open(os.path.join(here, "optimizer", "__version__.py"), encoding="utf-8") as fh:
    version_file = fh.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    name="komodo-mlipir-algorithm",
    version=version,
    author="Pejalan Sunyi",
    author_email="khalifardy.miqdarsah@example.com",
    description="A Python implementation of Komodo Mlipir Algorithm (KMA) for optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/khalifardy/komodo_mlipir_algorithm",
    project_urls={
        "Bug Tracker": "https://github.com/khalifardy/komodo_mlipir_algorithm/issues",
        "Documentation": "https://komodo-mlipir-algorithm.readthedocs.io/",
        "Source Code": "https://github.com/khalifardy/komodo_mlipir_algorithm/",
    },
    # Explicitly specify packages from optimizer folder
    packages=[
        "optimizer",
        "optimizer.algorithm",
        "optimizer.utils"
    ],
    # Alternative: use find_packages with where parameter
    # packages=find_packages(where=".", include=["optimizer", "optimizer.*"]),
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="optimization metaheuristic komodo-mlipir evolutionary-algorithm swarm-intelligence",
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "pytest-mock>=3.6.0",
            "black>=21.6b0",
            "flake8>=3.9.0",
            "mypy>=0.910",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
        ],
        "viz": [
            "matplotlib>=3.3.0",
            "seaborn>=0.11.0",
        ],
        "examples": [
            "jupyter>=1.0.0",
            "notebook>=6.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            # Update entry points to use optimizer instead of komodo_mlipir
            "kma-benchmark=optimizer.cli:benchmark_cli",
            "kma-optimize=optimizer.cli:optimize_cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)