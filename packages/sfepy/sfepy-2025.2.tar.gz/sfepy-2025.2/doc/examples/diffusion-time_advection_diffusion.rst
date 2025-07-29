.. _diffusion-time_advection_diffusion:

diffusion/time_advection_diffusion.py
=====================================

**Description**


The transient advection-diffusion equation with a given divergence-free
advection velocity.

Find :math:`u` such that:

.. math::
    \int_{\Omega} s \pdiff{u}{t}
    + \int_{\Omega} s \nabla \cdot \left(\ul{v} u \right)
    + \int_{\Omega} D \nabla s \cdot \nabla u
    = 0
    \;, \quad \forall s \;.

View the results using::

  sfepy-view square_tri2.*.vtk -f u:wu 1:vw


.. image:: /../doc/images/gallery/diffusion-time_advection_diffusion.png


:download:`source code </../sfepy/examples/diffusion/time_advection_diffusion.py>`

.. literalinclude:: /../sfepy/examples/diffusion/time_advection_diffusion.py

