.. _multi-class:

Multi Class
===========

Multicomponent liquid oxide physical property models for systems
containing three or more components. 
Let ``ModelMulti`` represent an abstract multicomponent class.

Creating an Instance
--------------------

To create an instance of a ``ModelMulti`` model, a :term:`BFF` has to be provided.

Example: ``ExampleModel = ModelMulti(bff=my_bff)``

The provided :term:`BFF` should be set up by the user to take temperature, pressure, composition and phase constituent activities and return a dictionary containing the bond fractions. 
The returned dictionary should be of type ``dict[str: floatFraction]`` where the keys follow the naming convention of, for example, ``"Si-Al"`` to mark the bond fractions. 
See the :ref:`supplementary-examples` section for a guide on setting up a :term:`BFF`.

Calculating the Physical Property
---------------------------------

Call 

.. code-block::

    ExampleModel.calculate(T=temperature, p=pressure, x=composition, a=activities)

where

| ``T: floatPositive``
| ``p: floatPositive``
| ``x: dict[str, floatFraction]``
| ``a: dict[str, dict[str, floatFraction]]``

If a temperature or pressure is not provided, standard temperature and pressure will be assumed.

Usage example:

.. code-block::

    ExampleModel.calculate(T=1773, x={"SiO2": 0.5, "Al2O3": 0.25, "FeO: 0.25"}, a={"gas_ideal": {"O2": 0.21}})

where temperature (and pressure) are in SI units, composition fractions
are in mole fractions and activity is unitless. This example is for a
system in equilibrium with air.

For ease of use,
``ExampleModel(T=temperature, p=pressure, x=composition, a=activities)``
can also be used.
