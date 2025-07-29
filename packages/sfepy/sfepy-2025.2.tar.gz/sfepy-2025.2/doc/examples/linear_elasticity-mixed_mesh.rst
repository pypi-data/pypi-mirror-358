.. _linear_elasticity-mixed_mesh:

linear_elasticity/mixed_mesh.py
===============================

**Description**


A linear elastic beam loaded with a continuous force. The FE mesh consists
of hexehedral and tetrahedral elements.

The displacement at the beam end is compared to the reference
solution calculated on the homogeneous hexahedral mesh.

Running the simulation::

    sfepy-run sfepy/examples/linear_elasticity/mixed_mesh.py

Viewing the results::

    sfepy-view beam_h* -f u:s0:wu:e:p0 u:s1:wu:e:p0 --camera-position="1.2,-0.6,0.1,0.4,0.1,-0.1,-0.2,0.1,1"


.. image:: /../doc/images/gallery/linear_elasticity-mixed_mesh.png


:download:`source code </../sfepy/examples/linear_elasticity/mixed_mesh.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/mixed_mesh.py

