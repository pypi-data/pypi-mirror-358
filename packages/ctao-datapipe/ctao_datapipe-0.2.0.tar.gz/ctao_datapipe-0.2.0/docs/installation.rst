Installation
============

User Installation
-----------------

As a user, install from pypi:

.. code-block:: shell

    $ pip install ctao-datapipe

Or using Docker:

.. code-block:: shell

    $ docker pull harbor.cta-observatory.org/dpps/datapipe:v0.1.0-rc1

The tag after the colon (``:``) should be the release you want to use.

Developer Setup
---------------

As a developer, clone the repository, create a virtual environment
and then install the package in development mode:

.. code-block:: shell

   $ git clone git@gitlab.cta-observatory.org:cta-computing/dpps/datapipe/datapipe.git
   $ cd datapipe
   $ python -m venv venv
   $ source venv/bin/activate
   $ pip install -e .[test,doc,dev]

The same also works with conda, create a conda env instead of a venv above.
