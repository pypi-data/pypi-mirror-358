.. _installation:

Installation
============

The Kumo Python SDK is available for **Python 3.9** onwards, and has
a lightweight, minimal set of dependencies. It can be installed in any
environment with a supported Python version. Installation steps are identical
for a SaaS, Databricks, or Snowflake edition of the Kumo platform.

You can install the SDK with ``pip``, as follows:

.. code-block:: console

   pip install kumoai


Installation of this package requires `pip
<https://pip.pypa.io/en/stable/installation/>`_; please
ensure that it is present before proceeding.

You can verify that installation was successful by running:

.. code-block:: python

    >>> import kumoai as kumo
    >>> kumo.__version__
    '2.1.0'

If you run into any issues with package installation, please share the error
message and any environment information with your Kumo POC.
