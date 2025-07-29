.. _diffusion-laplace_fluid_2d:

diffusion/laplace_fluid_2d.py
=============================

**Description**


A Laplace equation that models the flow of "dry water" around an obstacle
shaped like a Citroen CX.


Description
-----------

As discussed e.g. in the Feynman lectures Section 12-5 of Volume 2
(https://www.feynmanlectures.caltech.edu/II_12.html#Ch12-S5),
the flow of an irrotational and incompressible fluid can be modelled with a
potential :math:`\ul{v} = \ul{grad}(\phi)` that obeys

.. math::
    \nabla \cdot \ul{\nabla}\,\phi = \Delta\,\phi = 0

The weak formulation for this problem is to find :math:`\phi` such that:

.. math::
    \int_{\Omega} \nabla \psi \cdot \nabla \phi
    = \int_{\Gamma_{left}} \ul{v}_0 \cdot n  \, \psi
    + \int_{\Gamma_{right}} \ul{v}_0 \cdot n  \, \psi
    + \int_{\Gamma_{top}} \ul{v}_0 \cdot n \,\psi
    + \int_{\Gamma_{bottom}} \ul{v}_0 \cdot n \, \psi
    \;, \quad \forall \psi \;,

where :math:`\ul{v}_0` is the 2D vector defining the far field velocity that
generates the incompressible flow.

Since the value of the potential is defined up to a constant value, a Dirichlet
boundary condition is set at a single vertex to avoid having a singular matrix.

Usage examples
--------------

This example can be run with the following::

  sfepy-run sfepy/examples/diffusion/laplace_fluid_2d.py
  sfepy-view citroen.vtk -f phi:p0 phi:t50:p0 --2d-view

Generating the mesh
-------------------

The mesh can be generated with::

  gmsh -2 -f msh22 meshes/2d/citroen.geo -o meshes/2d/citroen.msh
  sfepy-convert --2d meshes/2d/citroen.msh meshes/2d/citroen.h5


.. image:: /../doc/images/gallery/diffusion-laplace_fluid_2d.png


:download:`source code </../sfepy/examples/diffusion/laplace_fluid_2d.py>`

.. literalinclude:: /../sfepy/examples/diffusion/laplace_fluid_2d.py

