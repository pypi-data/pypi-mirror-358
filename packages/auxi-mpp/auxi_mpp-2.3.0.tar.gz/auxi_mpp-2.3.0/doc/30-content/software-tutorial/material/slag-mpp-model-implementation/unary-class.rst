.. _unary-class:

Unary Class
===========

Unary liquid oxide physical property models for single component
systems. Let ``ModelUnary`` represent an abstract unary class.

Creating an Instance
--------------------

Unary classes does not need an input to have an instance created.

.. code-block:: python

   ExampleModel = ModelUnary()

Calculating the Physical Property
---------------------------------

Call

.. code-block:: python
   
   ExampleModel.calculate(T=temperature, p=pressure, x=composition)

where

| ``T: floatPositive``
| ``p: floatPositive``
| ``x: dict[str, floatFraction]``

If a temperature or pressure is not provided, standard temperature and
pressure will be assumed.

Usage example: 

.. code-block:: python

   ExampleModel.calculate(T=1773, x={"SiO2": 1.0})

where temperature (and pressure) are in SI units.

For ease of use,
``ExampleModel(T=temperature, p=pressure, x=composition)`` can also be
used to achieve the same result.
