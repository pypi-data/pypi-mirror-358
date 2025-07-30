.. _density:

Density
=======

These are density models that take temperature and composition as input
and return density in kg m\ :sup:`-3`.

To use the density models they should be imported first:

``from auxi.mpp.slag.ρ import ExampleModel``

Suppose ``ExampleModel`` is an instance of one of the density models.
``ExampleModel`` will then have the following attributes:

property
--------

.. code-block::

   print(ExampleModel.property)

**Output**

.. code-block::

   Density

symbol
------

.. code-block::

   print(ExampleModel.symbol)

**Output**

.. code-block::

   ρ

display_symbol
--------------

.. code-block::

   print(ExampleModel.display_symbol)

**Output**

.. code-block::

   \rho

Allows for direct use in :math:`\LaTeX` to display :math:`\rho`.

units
-----

.. code-block::

   print(ExampleModel.units)
   

**Output**

.. code-block::

   \kilo\gram\per\cubic\meter


Allows for direct use in :math:`\LaTeX` to display kg m\ :sup:`-3`.
