.. _linear_elasticity-its2D_interactive:

linear_elasticity/its2D_interactive.py
======================================

**Description**


Diametrically point loaded 2-D disk, using commands for interactive use. See
:ref:`sec-primer`.

The script combines the functionality of all the ``its2D_?.py`` examples and
allows setting various simulation parameters, namely:

- material parameters
- displacement field approximation order
- uniform mesh refinement level

The example shows also how to probe the results as in
:ref:`linear_elasticity-its2D_4`. Using :mod:`sfepy.discrete.probes` allows
correct probing of fields with the approximation order greater than one.

In the SfePy top-level directory the following command can be used to get usage
information::

  python sfepy/examples/linear_elasticity/its2D_interactive.py -h


.. image:: /../doc/images/gallery/linear_elasticity-its2D_interactive-its2D_interactive_probe_0.png
.. image:: /../doc/images/gallery/linear_elasticity-its2D_interactive-its2D_interactive_probe_1.png
.. image:: /../doc/images/gallery/linear_elasticity-its2D_interactive.png


:download:`source code </../sfepy/examples/linear_elasticity/its2D_interactive.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/its2D_interactive.py

