.. _linear_elasticity-truss_bridge:

linear_elasticity/truss_bridge.py
=================================

**Description**


An example demonstrating the usage of the truss elements in 2D.
The bridge structure is fixed on the left and supported on the right.

Running the simulation::

  sfepy-run sfepy/examples/linear_elasticity/truss_bridge.py

Viewing the results::

  sfepy-view bridge.vtk -f u:wu:p0 1:vw:p0 S:e:p1 --2d-view


.. image:: /../doc/images/gallery/linear_elasticity-truss_bridge.png


:download:`source code </../sfepy/examples/linear_elasticity/truss_bridge.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/truss_bridge.py

