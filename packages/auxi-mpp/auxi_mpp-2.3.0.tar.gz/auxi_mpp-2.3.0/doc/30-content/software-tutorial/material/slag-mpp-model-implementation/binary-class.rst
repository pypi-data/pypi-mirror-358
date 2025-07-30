.. _binary-class:

Binary Class
============

Binary liquid oxide physical property models for systems containing two components. Let ``ModelBinary`` represent an abstract binary class.

Creating an Instance
--------------------

To create an instance of a ``ModelBinary`` model, a :term:`BFF` has to be
provided.

.. code-block::

   ExampleModel = ModelBinary(bff=my_bff)

The provided :term:`BFF` should be set up by the user to take temperature, pressure, composition and phase constituent activities and return a dictionary containing the bond fractions. 
Note that the activities will only be used by multicomponent models.
This is simply to allow the same :term:`BFF` to be used by both the binary and multicomponent models.
The dictionary returned by the :term:`BFF` should be of type ``dict[str: floatFraction]`` where the keys follow the naming convention of, for example, ``"Si-Al"`` to mark the Si-O-Al bond fractions.
See the :ref:`supplementary-examples` section for a guide on setting up a :term:`BFF`.


Calculating the Physical Property
---------------------------------

Call

.. code-block::
   
   ExampleModel.calculate(T=temperature, p=pressure, x=composition)

where

| ``T: floatPositive``
| ``p: floatPositive``
| ``x: dict[str, floatFraction]``

If a temperature or pressure is not provided, standard temperature and pressure will be assumed.
Note that activities should not be provided for calculating binary system properties.

Usage example:

.. code-block::

   ExampleModel.calculate(T=1773, x={"SiO2": 0.5, "Al2O3": 0.5})

where temperature (and pressure) are in SI units. Composition fractions are in
mole fractions.

For ease of use,
``ExampleModel(T=temperature, p=pressure, x=composition)`` can also be
used to calculate the physical property.
