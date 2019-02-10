#!/usr/bin/env python
"""
Setup package.
"""
from setuptools import setup

setup(
    name="nest-graph",
    version="0.1",
    packages=["nest_graph"],
    license="MIT",
    long_description=open("README.txt").read(),
    install_requires=["click", "matplotlib", "numpy"],
    entry_points={"console_scripts": ["nest-graph=nest_graph.nest_graph:main"]},
)
