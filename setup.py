#!/usr/bin/env python
"""
Setup package.
"""
from setuptools import setup
import io

# Get long description from readme
with io.open("README.md", "rt", encoding="utf8") as readmefile:
    readme = readmefile.read()


setup(
    name="nest-graph",
    version="0.1.1",
    description="Utility to graph a nest's thermostat's data",
    author="Alan Rosenthal",
    author_email="1288897+AlanRosenthal@users.noreply.github.com",
    url="https://github.com/AlanRosenthal/nest-graph",
    project_urls={
        "Code": "https://github.com/noahp/py-commit-checker",
        "Issues": "https://github.com/AlanRosenthal/nest-graph/issues",
    },
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=["nest_graph"],
    install_requires=["click", "plotly", "numpy", "pandas"],
    license="MIT",
    long_description=open("README.txt").read(),
    entry_points={"console_scripts": ["nest-graph=nest_graph.nest_graph:main"]},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
    ],
)
