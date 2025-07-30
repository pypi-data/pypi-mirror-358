Essentials
==========

Slag Physical Properties
------------------------

The instructions that are given applies to the properties listed below.

#. Density

#. Molar Volume

#. Electrical Conductivity

#. Diffusivity

#. Viscosity

Core Attributes
---------------

The basic attributes describing the essence of the model are the
following.

#. property

#. symbol

#. displaysymbol (for use in :math:`\LaTeX`)

#. units - for use in :math:`\LaTeX` (all model outputs are in SI units)

#. references - gives the source from which the model was taken

These attributes are callable. For example, if ``ExampleModel`` is an
instance of a molar volume model;

.. code-block::

   print(ExampleModel.property)

**Output**

.. code-block::

   Molar Volume
