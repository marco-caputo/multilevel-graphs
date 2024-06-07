from setuptools import setup, find_packages

setup(
    name="multilevelgraphs",
    version="0.1.0-alpha.1",
    author="M. Caputo, L. Lupi",
    description="A simple library for creating and managing hierarchical structures of graphs obtained by gradual contractions of nodes and edges.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/yourusername/your-repo",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
