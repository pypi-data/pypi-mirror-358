.. _navier_stokes-navier_stokes2d:

navier_stokes/navier_stokes2d.py
================================

**Description**


Navier-Stokes equations for incompressible fluid flow in 2D.

Find :math:`\ul{u}`, :math:`p` such that:

.. math::
    \int_{\Omega} \nu\ \nabla \ul{v} : \nabla \ul{u}
    + \int_{\Omega} ((\ul{u} \cdot \nabla) \ul{u}) \cdot \ul{v}
    - \int_{\Omega} p\ \nabla \cdot \ul{v}
    = 0
    \;, \quad \forall \ul{v} \;,

    \int_{\Omega} q\ \nabla \cdot \ul{u}
    = 0
    \;, \quad \forall q \;.

The mesh is created by ``gen_block_mesh()`` function.

View the results using::

  sfepy-view user_block.vtk -2


.. image:: /../doc/images/gallery/navier_stokes-navier_stokes2d.png


:download:`source code </../sfepy/examples/navier_stokes/navier_stokes2d.py>`

.. literalinclude:: /../sfepy/examples/navier_stokes/navier_stokes2d.py

