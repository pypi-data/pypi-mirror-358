.. _linear_elasticity-multi_point_constraints:

linear_elasticity/multi_point_constraints.py
============================================

**Description**


The linear elasticity of two discs connected using multi-point constraints.

Find :math:`\ul{u}`, :math:`\ul{u_c}` such that:

.. math::
    \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
    + \sum_{i,j \in \Omega_c} K_{kl}\ ((u_c)^{(j)}_l - (u_c)^{(i)}_l)
    = 0
    \;, \quad \forall \ul{v} \;,

where

.. math::
    D_{ijkl} = \mu (\delta_{ik} \delta_{jl}+\delta_{il} \delta_{jk}) +
    \lambda \ \delta_{ij} \delta_{kl} \;,

    K_{kl} = K_{kl}(\ul{d}, \ul{k}) \;,

:math:`u_c^{(j)}` are the DOFs - two displacements and one rotation in 2D -
of the node :math:`j` in :math:`\Omega_c`, which is a subdomain composed of two
1D spring terms with the generalized stiffness matrix :math:`K_{kl}` depending
on the directions :math:`\ul{d}` of the springs and the stiffness vector
:math:`\ul{k}`.

The deformation is governed by the Dirichlet conditions applied to one of the
spring end points, see the `dofs` argument of :func:`define()` below.

Usage Examples
--------------

- Save and display boundary regions::

    sfepy-run sfepy/examples/linear_elasticity/multi_point_constraints.py --save-regions-as-groups --solve-not

    sfepy-view annulus-c_regions.vtk -2e -f Gamma1:p0 Gamma2:p1 Gamma3:p3 Gamma4:p4 --max-plots=4 --color-map=summer

- Run::

    sfepy-run sfepy/examples/linear_elasticity/multi_point_constraints.py
    sfepy-run sfepy/examples/linear_elasticity/multi_point_constraints.py -d "dofs=(0,1)"
    sfepy-run sfepy/examples/linear_elasticity/multi_point_constraints.py -d "dofs=(0,1), is_rot=False"
    sfepy-run sfepy/examples/linear_elasticity/multi_point_constraints.py -d "dofs=2"

- Display results::

    sfepy-view annulus-c.vtk -2e
    sfepy-view annulus-c.vtk -2e -f u:wu:f1:p0 1:vw:p0 u:gu:p0


.. image:: /../doc/images/gallery/linear_elasticity-multi_point_constraints.png


:download:`source code </../sfepy/examples/linear_elasticity/multi_point_constraints.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/multi_point_constraints.py

