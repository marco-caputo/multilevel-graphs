Installation Guide
===================================

This guide will help you to install the MultiLevelGraphs library.

Requirements
------------

Before installing MultiLevelGraphs, ensure that you have the following prerequisites:

- Python 3.10 or higher
- pip (Python package installer)

Installation
------------

You can install MultiLevelGraphs using pip. Open your terminal or command prompt and run the following command:

.. code-block:: bash

    pip install --index-url https://test.pypi.org/simple/ multilevelgraphs

Verifying Installation
----------------------

To verify that the library has been installed correctly, you can try importing it in a Python shell or script.
Open your terminal or command prompt and enter:

.. code-block:: python

    import multilevelgraphs

    print(multilevelgraphs.__version__)

This should print the version number of MultiLevelGraphs if the installation was successful.

Dependencies
------------

MultiLevelGraphs has a few dependencies which should be installed automatically when you install the library.
However, for reference, here are the main dependencies:

- NetworkX
- typing
- abc

If you encounter any issues during installation, make sure these libraries are installed and updated to
compatible versions.

Uninstallation
--------------

To uninstall MultiLevelGraphs, you can use pip:

.. code-block:: bash

    pip uninstall MultiLevelGraphs

Support
-------

If you encounter any issues or have questions, please check the documentation or raise an issue on our GitHub page:
https://github.com/lorenzo-lupi/multilevel_graphs.git

License
-------

This project is licensed under the MIT License. See the LICENSE file for more details.