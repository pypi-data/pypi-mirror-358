.. _extracting-bond-fractions:

Extracting Bond Fractions
=========================

The bond fractions can be obtained from a pair fraction calculation
between the first (cationic) and the second (anionic) sublattice. To
specifically calculate the interactions, only oxygen should be specified
for the second lattice.

Pair Fraction Calculation
-------------------------

To perform this calculation we use the chemapp.basic function
``tqbond(ph, slc1, slc2, slc3, slc4)``, where the parameters are:

- ``ph`` (``int``): Zero-based index of phase of interest.

- ``slc1`` (``int``): Zero-based index of constituent one.

- ``slc2`` (``int``): Zero-based index of constituent two.

- ``slc3`` (``int``): Zero-based index of constituent three.

- ``slc4`` (``int``): Zero-based index of constituent four.

This function returns the pair fraction (``float``).

The function requires that two of the constituent indeces should be for
the first sublattice and two for the second. The order in which they are
provided does not matter. It is also important to note that the second
sublattice constituent index = (total number of constituents of the
first sublattice + the second sublattice constituent index). In
practical terms, the second sublattice constituents should therefore be
added to the back of the first sublattice constituent list. This will be
demonstrated in :ref:`building-the-function` section.

Get Sublattice Constituent List
-------------------------------

To be able to reference the indeces in the ``tqbond()`` function, we
need a ``list[str]`` containing the symbols of the cations and anions,
sorted according to index. To build this list we need to know the number
of constituents (ions) there is in every sublattice. For this we use the
chemapp.basic function ``tqnolc(ph, sl)``, where the parameters are:

- ``ph`` (``int``): Zero-based index of phase of interest.

- ``sl`` (``int``): Zero-based index of sublattice.

This function returns the number of sublattice constituents (``int``).
The cationic and anionic sublattices have indeces 0 and 1, respectively.

To get the constituent names, we use the chemapp.basic function
``tqgnlc(ph, sl, slc)``, where the parameters are:

- ``ph`` (``int``): Zero-based index of phase of interest.

- ``sl`` (``int``): Zero-based index of sublattice.

- ``slc`` (``int``): Zero-based index of constituent.

This function returns the sublattice constituent symbol (``str``).
