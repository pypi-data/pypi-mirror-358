.. _molar-volume:

Molar Volume
============

These are models that take temperature and composition as input and return molar volume in m\ :sup:`3` mol\ :sup:`-1`.

To use the molar volume models they should be imported first:

``from auxi.mpp.slag.Vm import ExampleModel``

Suppose ``ExampleModel`` is an instance of one of the molar volume models. 
``ExampleModel`` will then have the following attributes:

property
--------

.. code-block::

   print(ExampleModel.property)

**Output**
    
.. code-block::
    
   Molar Volume

symbol
------

.. code-block::

   print(ExampleModel.symbol)

**Output**

.. code-block::

   Vm


display_symbol
--------------

.. code-block::

   print(ExampleModel.display_symbol)

**Output**

.. code-block::

   \barV

Allows for direct use in :math:`\LaTeX` to display  :math:`\bar{V}`.

units
-----

.. code-block::

   print(ExampleModel.units)


**Output**

.. code-block::

   \cubic\meter\per\mol


Allows for direct use in :math:`\LaTeX` to display m\ :sup:`3` mol\ :sup:`-1`.
