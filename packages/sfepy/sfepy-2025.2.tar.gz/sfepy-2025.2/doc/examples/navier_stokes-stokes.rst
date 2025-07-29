.. _navier_stokes-stokes:

navier_stokes/stokes.py
=======================

**Description**


Stokes equations for incompressible fluid flow.

This example demonstrates fields defined on subdomains as well as use of
periodic boundary conditions.

Find :math:`\ul{u}`, :math:`p` such that:

.. math::
    \int_{Y_1 \cup Y_2} \nu\ \nabla \ul{v} : \nabla \ul{u}
    - \int_{Y_1 \cup Y_2} p\ \nabla \cdot \ul{v}
    = 0
    \;, \quad \forall \ul{v} \;,

    \int_{Y_1 \cup Y_2} q\ \nabla \cdot \ul{u}
    = 0
    \;, \quad \forall q \;.


.. image:: /../doc/images/gallery/navier_stokes-stokes.png


:download:`source code </../sfepy/examples/navier_stokes/stokes.py>`

.. literalinclude:: /../sfepy/examples/navier_stokes/stokes.py

