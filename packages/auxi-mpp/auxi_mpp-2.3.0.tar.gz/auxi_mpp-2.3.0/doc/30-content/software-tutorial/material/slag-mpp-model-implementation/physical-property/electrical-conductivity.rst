.. _electrical-conductivity:

Electrical Conductivity
=======================

These are electrical conductivity models that take temperature and composition as input and return electrical conductivity in S m\ :sup:`-1`.

To use the electrical conductivity models they should be imported first:

``from auxi.mpp.slag.σ import ExampleModel``

Suppose ``ExampleModel`` is an instance of one of the electrical conductivity models. ``ExampleModel`` will then have the following attributes:

property
--------

.. code-block::

   print(ExampleModel.property)

**Output**

.. code-block::

   Electrical Conductivity


symbol
------

.. code-block::

   print(ExampleModel.symbol)

**Output**

.. code-block::

   σ

display_symbol
--------------

.. code-block::

   print(ExampleModel.display_symbol)

**Output**

.. code-block::

   \sigma

Allows for direct use in :math:`\LaTeX` to display :math:`\sigma`.

units
-----

.. code-block::

   print(ExampleModel.units)

**Output**

.. code-block::

   \siemens\per\meter

Allows for direct use in :math:`\LaTeX` to display S m\ :sup:`-1`.
