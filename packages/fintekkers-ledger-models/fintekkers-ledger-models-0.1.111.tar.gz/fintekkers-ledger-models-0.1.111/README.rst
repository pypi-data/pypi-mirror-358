Overview
============

This project contains protobuf models of financial objects & request/response formats for APIs; as well as Python specific bindings and 
wrappers to make Python development more streamlined.

See the Readme.md on https://github.com/FinTekkers/ledger-models/ for general information

Installing from pypi
============

.. code-block:: bash

    pip3 install fintekkers_ledger_models

Installing locally
============

This will build and install the package locally. Note the version is set to 0.0.0. If you have the production installation already installed 
you can use a virtualenv or uninstall before installing this

.. code-block:: bash

    ./build_pip_package.sh

Testing
=====

.. code-block:: bash

    >>> pytest

Testing in VSCode. In your .vscode folder open the launch.json and add the below. Note the intellisense may say request="test" is not valid, but it is!

Install the python extension and set pytest as your test runner.

.. code-block:: json

{
    "version": "0.2.0",
    "configurations": [
        
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "test",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}

Developer Notes
=====

*build_generate_init_files.py* is used to generate __init__.py files. The python auto-generated code for protobufs
do not do this, and not all versions of Python support implicit modules.

*build_pip_package.sh* will build and install ledger_models_python to your local machine with version 0.0.0. Use this 
for local testing.

*fintekkers/py.typed* this is added to the distribution as an indicator that the pyi files exist and can be used to provide type hints

*MANIFEST.in* used by the sdist build to include files. (This was easier than using the setup.py)

*requirements.txt* Dependent packages (not guaranteed to be up to date at the moment)

*setup.py* The configuration to build. Run as `python setup.py sdist bdist_wheel`

*setup.cfg* Might be worth getting rid of this?

*clean_pycache.sh* Removes all __pycache__ entries. Occasionally you'll hit some error where a file is cached and out of date. 

*pyproject.toml* This was added so that running pytest without any parameters or PYTHONPATH arguments would work

*pvenv.cfg* Configuration for venv