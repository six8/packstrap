=========
Packstrap
=========

Bootstrap new Python packages with one simple command::

    packstrap create my_package
    
When starting a Python package a lot of boilerplate is involved. You
have to make several files and directories. When you decide to distribute
your package you have to write a setup.py and reference docs for even the
basics. Packstrap aims to make starting a Python package simpler.    

Install
-------

    pip install packstrap
    packstrap --help

Creating a Package
------------------

With Packstrap, creating a package is a simple as one command::

    packstrap create my_package /path/to/code --author "My Name" --plugin git --plugin fabfile --plugin pytest

This will create a `my_package` directory in `/path/to/code` with a structure similar to::

    /path/to/code/my_package/
        .gitignore
        LICENSE
        MANIFEST.in
        README.rst
        VERSION.txt
        fabfile.py
        setup.py
        src/
            my_package/
                __init__.py
            tests/
                conftest.py
                runtests.py

Packstrap creates the base files for a python project and fills in the basics for setup.py, README.rst, etc.
The git plugin creates `.gitignore`, the fabfile plugin creates `fabfile.py`, and the pytest plugin creates the
`src/tests` directory and files.

So now all you have to do is write your module in `my_package`, expand on your docs in README.rst, and commit
your package.

Set Defaults
------------

`packstrap create` has several options to help generate your package. A lot of the options like `author`, `author_email`, and even `plugins` are going to be the same for all your projects. To save you some keystrokes you can use `packstrap defaults`::


    packstrap defaults --author "My Name"
    {
      "author": "My Name", 
      "skeleton": "default"
    }

You can also use `packstrap defaults` without options to list the current defaults.