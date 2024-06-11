from setuptools import setup, find_packages
from multilevelgraphs import __version__

setup(
    name="multilevelgraphs",
    version=__version__,
    author="M. Caputo, L. Lupi",
    description="A simple library for creating and managing hierarchical structures of graphs obtained by gradual contractions of nodes and edges.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/Caputommy/multilevel_graphs",
    packages=find_packages(include=['multilevelgraphs', 'multilevelgraphs.*']),
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
