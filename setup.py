from setuptools import setup, find_packages
import os
import re

def get_version():
    version_file = os.path.join("src", "multilevelgraphs", "version.py")
    with open(version_file) as f:
        match = re.search(r'^__version__ = ["\']([^"\']*)["\']', f.read())
        if match:
            return match.group(1)
        raise RuntimeError("Unable to find version string.")

setup(
    name="multilevelgraphs",
    version=get_version(),
    author="M. Caputo, L. Lupi",
    description="A simple library for creating and managing hierarchical structures of graphs obtained by gradual contractions of nodes and edges.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/marco-caputo/multilevel-graphs",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    install_requires=[
        'networkx>=3.3'
    ],
)
