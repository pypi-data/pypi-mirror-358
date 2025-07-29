.. _diffusion-poisson_neumann:

diffusion/poisson_neumann.py
============================

**Description**


The Poisson equation with Neumann boundary conditions on a part of the
boundary.

Find :math:`T` such that:

.. math::
    \int_{\Omega} K_{ij} \nabla_i s \nabla_j p T
    = \int_{\Gamma_N} s g
    \;, \quad \forall s \;,

where :math:`g` is the given flux, :math:`g = \ul{n} \cdot K_{ij} \nabla_j
\bar{T}`, and :math:`K_{ij} = c \delta_{ij}` (an isotropic medium). See the
tutorial section :ref:`poisson-weak-form-tutorial` for a detailed explanation.

The diffusion velocity and fluxes through various parts of the boundary are
computed in the :func:`post_process()` function. On 'Gamma_N' (the Neumann
condition boundary part), the flux/length should correspond to the given value
:math:`g = -50`, while on 'Gamma_N0' the flux should be zero. Use the
'refinement_level' option (see the usage examples below) to check the
convergence of the numerical solution to those values. The total flux and the
flux through 'Gamma_D' (the Dirichlet condition boundary part) are shown as
well.

Usage Examples
--------------

Run with the default settings (no refinement)::

  sfepy-run sfepy/examples/diffusion/poisson_neumann.py

Refine the mesh twice::

  sfepy-run sfepy/examples/diffusion/poisson_neumann.py -O "'refinement_level' : 2"


.. image:: /../doc/images/gallery/diffusion-poisson_neumann.png


:download:`source code </../sfepy/examples/diffusion/poisson_neumann.py>`

.. literalinclude:: /../sfepy/examples/diffusion/poisson_neumann.py

