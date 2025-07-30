.. _diffusivity:

Diffusivity
===========

These are ionic diffusivity models that take temperature and composition as input and return the diffusivity of each cation present in the form of a dictionary. The units are in m\ :sup:`2` s\ :sup:`-1`.

To use the diffusivity models they should be imported first:

``from auxi.mpp.slag.D import ExampleModel``

Suppose ``ExampleModel`` is an instance of one of the diffusivity models. 
``ExampleModel`` will then have the following attributes:

property
--------

.. code-block::

   print(ExampleModel.property)


**Output**

.. code-block::

   Diffusivity


symbol
------

.. code-block::

   print(ExampleModel.symbol)


**Output**
    
.. code-block::

   D


display_symbol
--------------

.. code-block::

   print(ExampleModel.display_symbol)

**Output**

.. code-block::

   D

units
-----

.. code-block::

   print(ExampleModel.units)

**Output**

.. code-block::

   \meter\squared\per\second


Allows for direct use in :math:`\LaTeX` to display  m\ :sup:`2` s\ :sup:`-1`.
