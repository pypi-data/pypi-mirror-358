.. _multi_physics-biot_short_syntax:

multi_physics/biot_short_syntax.py
==================================

**Description**


Biot problem - deformable porous medium with a no-penetration boundary
condition imposed in the weak sense on a boundary region, using the short
syntax of keywords.

The Biot coefficient tensor :math:`\alpha_{ij}` is non-symmetric. The mesh
resolution can be changed by editing the `shape` variable.

This example demonstrates how to set up various linear solvers and
preconditioners (see `solvers` dict):

- `'direct'` (a direct solver from SciPy), `'iterative-s'` (an iterative solver
  from SciPy), `'iterative-p'` (an iterative solver from PETSc) solvers can be
  used as the main linear solver.
- `'direct'`, `'cg-s'` (several iterations of CG from SciPy), `'cg-p'` (several
  iterations of CG from PETSc), `'pyamg'` (an algebraic multigrid solver)
  solvers can be used as preconditioners for the matrix blocks on the diagonal.

See :func:`setup_precond()` and try to modify it.

The PETSc solvers can be configured also using command line options. For
example, set ``'ls' : 'iterative-p'`` in `options`, and run::

  sfepy-run sfepy/examples/multi_physics/biot_short_syntax.py -ksp_monitor

or simply run::

  sfepy-run sfepy/examples/multi_physics/biot_short_syntax.py -O "ls='iterative-p'"

to monitor the PETSc iterative solver convergence. It will diverge without
preconditioning, see :func:`matvec_bj()`, :func:`matvec_j()` for further
details.

The PETSc options can also be set in the solver configuration - try
uncommenting the ``'ksp_*'`` or ``'pc_*'`` parameters in ``'iterative-p'``.
Uncommenting all the lines leads to, among other things, using the GMRES method
with no preconditioning and the condition number estimate computation. Compare
the condition number estimates with and without a preconditioning (try, for
example, using ``'precond' : 'mg'`` or ``'pc_type' : 'mg'``).

Find :math:`\ul{u}`, :math:`p` such that:

.. math::
    \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
    - \int_{\Omega}  p\ \alpha_{ij} e_{ij}(\ul{v})
    + \int_{\Gamma_{TB}} \varepsilon (\ul{n} \cdot \ul{v}) (\ul{n} \cdot \ul{u})
    = 0
    \;, \quad \forall \ul{v} \;,

    - \int_{\Omega} q\ \alpha_{ij} e_{ij}(\ul{u})
    - \int_{\Omega} K_{ij} \nabla_i q \nabla_j p
    = 0
    \;, \quad \forall q \;,

where

.. math::
    D_{ijkl} = \mu (\delta_{ik} \delta_{jl}+\delta_{il} \delta_{jk}) +
    \lambda \ \delta_{ij} \delta_{kl}
    \;.


.. image:: /../doc/images/gallery/multi_physics-biot_short_syntax.png


:download:`source code </../sfepy/examples/multi_physics/biot_short_syntax.py>`

.. literalinclude:: /../sfepy/examples/multi_physics/biot_short_syntax.py

