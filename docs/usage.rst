Usage
=====


Installation
------------

.. code-block:: shell

   pip install dreambank


The |dreambank| package version corresponds to versions of the datasets. To get a specific version of the datasets, install a specific version of |dreambank|. For example:

.. code-block:: shell

   pip install --force-reinstall dreambank==1.0


Check your current version of |dreambank| in a Python session with ``print(dreambank.__version__)``.


Quick start
-----------

.. code-block:: python

   import dreambank
   dreams = dreambank.read_dreams("izzy22_25")
   info = dreambank.read_info("izzy22_25")
