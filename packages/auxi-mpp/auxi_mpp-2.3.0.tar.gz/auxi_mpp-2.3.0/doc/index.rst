.. auxi-mpp user manual documentation master file, created by
   sphinx-quickstart on Mon May 12 13:18:27 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. Reducing Electric Furnace Material Physical Property Infrastructure
.. ===================================================================

auxi-mpp: 
========

The pyrometallurgy industry plays an important role in the global economy but faces growing challenges that demand innovative solutions.
These challenges include stricter environmental regulations, such as the EU's target of a 30\% reduction in :math:`CO_2` emissions by 2030, alongside the rising global demand for high-grade steel and increased reliance on lower-quality ores due to the depletion of high-grade resources.
Consequently, traditional :term:`BOF` must be replaced with more efficient smelting technologies, such as the proposed :term:`REF` process unit, to help the industry adapt.

Innovation also requires advancements in existing tools, particularly in pyrometallurgy, there is a growing need to more fundamentally describe processes through improved material property models, process models, and multiphysics models.
These improved models can assist the industry in developing new :term:`REF` process units more quickly and cost-effectively.

This software manual supports the development of new :term:`REF` processes with improved material property models.
It provides the guidance necessary to understand and implement the material property models available in ``auxi-mpp``.

Theoretical background and information on the models' validation can be found in: :download:`auxi-mpp Theory Manual<_static/test.txt>`.

.. User Manual
.. +++++++++++

.. Add your content using ``reStructuredText`` syntax. See the
.. `reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_
.. documentation for details.

.. toctree::
   :maxdepth: 2
   :caption: Preliminaries:
   :hidden:

   20-front-matter/document-purpose
   20-front-matter/disclaimer


.. toctree::
   :maxdepth: 2
   :caption: Building
   :hidden:

   30-content/installation/index


.. toctree::
   :maxdepth: 2
   :caption: Software Tutorial
   :hidden:

   30-content/software-tutorial/introduction
   30-content/software-tutorial/material/slag-mpp-model-implementation/index
   30-content/software-tutorial/supplementary-examples/index
   50-back-matter/glossary

..    :caption: API Reference

.. .. toctree::
..    :maxdepth: 2
..    :caption: References
..    :hidden:

..    50-back-matter/glossary
..    50-back-matter/references


Installation
------------

.. tab-set::

   .. tab-item:: Linux

      The recommended installation is to:

      .. code::

         pip install auxi-mpp

   .. tab-item:: macOS

      The recommended installation is to:

      .. code::

         pip install auxi-mpp


   .. tab-item:: Windows

      .. code::

         pip install auxi-mpp
