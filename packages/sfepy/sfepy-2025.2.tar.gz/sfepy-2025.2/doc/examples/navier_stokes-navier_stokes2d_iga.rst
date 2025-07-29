.. _navier_stokes-navier_stokes2d_iga:

navier_stokes/navier_stokes2d_iga.py
====================================

**Description**


Navier-Stokes equations for incompressible fluid flow in 2D solved in a single
patch NURBS domain using the isogeometric analysis (IGA) approach.

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

The domain geometry was created by::

  sfepy-mesh iga-patch -2 -d 0.1,0.1 -s 10,10 -o meshes/iga/block2d.iga

View the results using::

  sfepy-view block2d.vtk -2


.. image:: /../doc/images/gallery/navier_stokes-navier_stokes2d_iga.png


:download:`source code </../sfepy/examples/navier_stokes/navier_stokes2d_iga.py>`

.. literalinclude:: /../sfepy/examples/navier_stokes/navier_stokes2d_iga.py

