.. _navier_stokes-stokes_slip_bc:

navier_stokes/stokes_slip_bc.py
===============================

**Description**


Incompressible Stokes flow with Navier (slip) boundary conditions, flow driven
by a moving wall and a small diffusion for stabilization.

This example demonstrates the use of `no-penetration` and `edge direction`
boundary conditions together with Navier or slip boundary conditions.
Alternatively the `no-penetration` boundary conditions can be applied in a weak
sense using the penalty term ``dw_non_penetration_p``.

Find :math:`\ul{u}`, :math:`p` such that:

.. math::
    \int_{\Omega} \nu\ \nabla \ul{v} : \nabla \ul{u}
    - \int_{\Omega} p\ \nabla \cdot \ul{v}
    + \int_{\Gamma_1} \beta \ul{v} \cdot (\ul{u} - \ul{u}_d)
    + \int_{\Gamma_2} \beta \ul{v} \cdot \ul{u}
    = 0
    \;, \quad \forall \ul{v} \;,

    \int_{\Omega} \mu \nabla q \cdot \nabla p
    + \int_{\Omega} q\ \nabla \cdot \ul{u}
    = 0
    \;, \quad \forall q \;,

where :math:`\nu` is the fluid viscosity, :math:`\beta` is the slip
coefficient, :math:`\mu` is the (small) numerical diffusion coefficient,
:math:`\Gamma_1` is the top wall that moves with the given driving velocity
:math:`\ul{u}_d` and :math:`\Gamma_2` are the remaining walls. The Navier
conditions are in effect on both :math:`\Gamma_1`, :math:`\Gamma_2` and are
expressed by the corresponding integrals in the equations above.

The `no-penetration` boundary conditions are applied on :math:`\Gamma_1`,
:math:`\Gamma_2`, except the vertices of the block edges, where the `edge
direction` boundary conditions are applied.

The penalty term formulation is given by the following equations.

Find :math:`\ul{u}`, :math:`p` such that:

.. math::
    \int_{\Omega} \nu\ \nabla \ul{v} : \nabla \ul{u}
    - \int_{\Omega} p\ \nabla \cdot \ul{v}
    + \int_{\Gamma_1} \beta \ul{v} \cdot (\ul{u} - \ul{u}_d)
    + \int_{\Gamma_2} \beta \ul{v} \cdot \ul{u}
    + \int_{\Gamma_1 \cup \Gamma_2} \epsilon (\ul{n} \cdot \ul{v})
      (\ul{n} \cdot \ul{u})
    = 0
    \;, \quad \forall \ul{v} \;,

    \int_{\Omega} \mu \nabla q \cdot \nabla p
    + \int_{\Omega} q\ \nabla \cdot \ul{u}
    = 0
    \;, \quad \forall q \;,

where :math:`\epsilon` is the penalty coefficient (sufficiently large). The
`no-penetration` boundary conditions are applied on :math:`\Gamma_1`,
:math:`\Gamma_2`.

Optionally, Dirichlet boundary conditions can be applied on
the inlet in the both cases, see below.

For large meshes use the ``'ls_i'`` linear solver - PETSc + petsc4py are needed
in that case.

Several parameters can be set using the ``--define`` option of ``sfepy-run``,
see :func:`define()` and the examples below.

Examples
--------

Specify the inlet velocity and a finer mesh::

  sfepy-run sfepy/examples/navier_stokes/stokes_slip_bc -d shape="(11,31,31),u_inlet=0.5"
  sfepy-view -f p:p0 u:o.4:p1 u:g:f0.2:p1 -- user_block.vtk

Use the penalty term formulation and einsum-based terms with the default
(numpy) backend::

  sfepy-run sfepy/examples/navier_stokes/stokes_slip_bc -d "mode=penalty,term_mode=einsum"
  sfepy-view -f p:p0 u:o.4:p1 u:g:f0.2:p1 -- user_block.vtk

Change backend to opt_einsum (needs to be installed) and use the quadratic velocity approximation order::

  sfepy-run sfepy/examples/navier_stokes/stokes_slip_bc -d "u_order=2,mode=penalty,term_mode=einsum,backend=opt_einsum,optimize=auto"
  sfepy-view -f p:p0 u:o.4:p1 u:g:f0.2:p1 -- user_block.vtk

Note the pressure field distribution improvement w.r.t. the previous examples. IfPETSc + petsc4py are installed, try using the iterative solver to speed up the solution::

  sfepy-run sfepy/examples/navier_stokes/stokes_slip_bc -d "u_order=2,ls=ls_i,mode=penalty,term_mode=einsum,backend=opt_einsum,optimize=auto"
  sfepy-view -f p:p0 u:o.4:p1 u:g:f0.2:p1 -- user_block.vtk


.. image:: /../doc/images/gallery/navier_stokes-stokes_slip_bc.png


:download:`source code </../sfepy/examples/navier_stokes/stokes_slip_bc.py>`

.. literalinclude:: /../sfepy/examples/navier_stokes/stokes_slip_bc.py

