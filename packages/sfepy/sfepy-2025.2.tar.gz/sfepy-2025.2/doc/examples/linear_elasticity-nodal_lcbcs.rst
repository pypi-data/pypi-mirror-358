.. _linear_elasticity-nodal_lcbcs:

linear_elasticity/nodal_lcbcs.py
================================

**Description**


Linear elasticity with nodal linear combination constraints.

Find :math:`\ul{u}` such that:

.. math::
    \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
    = - \int_{\Gamma_{right}} \ul{v} \cdot \ull{\sigma} \cdot \ul{n}
    \;, \quad \forall \ul{v} \;,

where

.. math::
    D_{ijkl} = \mu (\delta_{ik} \delta_{jl}+\delta_{il} \delta_{jk}) +
    \lambda \ \delta_{ij} \delta_{kl}
    \;.

and :math:`\ull{\sigma} \cdot \ul{n} = \bar{p} \ull{I} \cdot \ul{n}` with given
traction pressure :math:`\bar{p}`. The constraints are given in terms of
coefficient matrices and right-hand sides, see the ``lcbcs`` keyword below. For
instance, ``'nlcbc1'`` in the 3D mesh case corresponds to

.. math::
    u_0 - u_1 + u_2 = 0 \\
    u_0 + 0.5 u_1 + 0.1 u_2 = 0.05

that should hold in the ``'Top'`` region.

This example demonstrates how to pass command line options to a problem
description file using ``--define`` option of ``sfepy-run``. Try::

  sfepy-run sfepy/examples/linear_elasticity/nodal_lcbcs.py --define='dim: 3'

to use a 3D mesh, instead of the default 2D mesh. The example also shows that
the nodal constraints can be used in place of the Dirichlet boundary
conditions. Try::

  sfepy-run sfepy/examples/linear_elasticity/nodal_lcbcs.py --define='use_ebcs: False'

to replace ``ebcs`` with the ``'nlcbc4'`` constraints. The results should be
the same for the two cases. Both options can be combined::

  sfepy-run sfepy/examples/linear_elasticity/nodal_lcbcs.py --define='dim: 3, use_ebcs: False'

The :func:`post_process()` function is used both to compute the von Mises
stress and to verify the linear combination constraints.

View the 2D results using::

  sfepy-view square_quad.vtk -2

View the 3D results using::

  sfepy-view cube_medium_tetra.vtk


.. image:: /../doc/images/gallery/linear_elasticity-nodal_lcbcs.png


:download:`source code </../sfepy/examples/linear_elasticity/nodal_lcbcs.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/nodal_lcbcs.py

