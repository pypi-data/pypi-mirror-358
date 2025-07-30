.. _viscosity:

Viscosity
=========

These are viscosity models that take temperature and composition as input and return dynamic viscosity in Pa s.

To use the viscosity models they should be imported first:

``from auxi.mpp.slag.μ import ExampleModel``

Suppose ``ExampleModel`` is an instance of one of the viscosity models. 
``ExampleModel`` will then have the following attributes:

property
--------

.. code-block::

   print(ExampleModel.property)

**Output**

.. code-block::

   Dynamic Viscosity

symbol
--------

.. code-block::

   print(ExampleModel.symbol)

**Output**

.. code-block::

   μ

display_symbol
--------------

.. code-block::

   print(ExampleModel.display_symbol)

**Output**

.. code-block::

   \mu

Allows for direct use in :math:`\LaTeX` to display :math:`\mu`.

units
-----

.. code-block::

   print(ExampleModel.units)

**Output**

.. code-block::

   \pascal\second

Allows for direct use in :math:`\LaTeX` to display Pa s.
