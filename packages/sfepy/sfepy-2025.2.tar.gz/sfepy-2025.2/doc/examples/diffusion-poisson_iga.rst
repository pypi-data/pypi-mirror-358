.. _diffusion-poisson_iga:

diffusion/poisson_iga.py
========================

**Description**


Poisson equation solved in a single patch NURBS domain using the isogeometric
analysis (IGA) approach.

Find :math:`t` such that:

.. math::
    \int_{\Omega} c \nabla s \cdot \nabla t
    =  \int_{\Omega_0} f s
    \;, \quad \forall s \;.

Try setting the Dirichlet boundary condition (ebcs) on various sides of the
domain (``'Gamma1'``, ..., ``'Gamma4'``).

View the results using::

  sfepy-view patch2d.vtk -f t:wt:f0.4 1:vw


.. image:: /../doc/images/gallery/diffusion-poisson_iga.png


:download:`source code </../sfepy/examples/diffusion/poisson_iga.py>`

.. literalinclude:: /../sfepy/examples/diffusion/poisson_iga.py

