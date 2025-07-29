.. _linear_elasticity-truss_bridge3d:

linear_elasticity/truss_bridge3d.py
===================================

**Description**


An example demonstrating the usage of the truss structural elements in 3D.
The mixed (solid and structural elements) bridge structure is fixed
on the left and supported on the right.

Running the simulation::

  sfepy-run sfepy/examples/linear_elasticity/truss_bridge3d.py

Viewing the results::

  sfepy-view bridge3d_S*.vtk -f u_solid:s0:wu_solid:f1e3:p0 u_struct:s1:wu_struct:f1e3:p0


.. image:: /../doc/images/gallery/linear_elasticity-truss_bridge3d_Solid.png
.. image:: /../doc/images/gallery/linear_elasticity-truss_bridge3d_Struct.png


:download:`source code </../sfepy/examples/linear_elasticity/truss_bridge3d.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/truss_bridge3d.py

