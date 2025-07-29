.. _multi_physics-biot_parallel_interactive:

multi_physics/biot_parallel_interactive.py
==========================================

**Description**


Parallel assembling and solving of a Biot problem (deformable porous medium),
using commands for interactive use.

Find :math:`\ul{u}`, :math:`p` such that:

.. math::
    \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
    - \int_{\Omega}  p\ \alpha_{ij} e_{ij}(\ul{v})
    = 0
    \;, \quad \forall \ul{v} \;,

    \int_{\Omega} q\ \alpha_{ij} e_{ij}(\ul{u})
    + \int_{\Omega} K_{ij} \nabla_i q \nabla_j p
    = 0
    \;, \quad \forall q \;,

where

.. math::
    D_{ijkl} = \mu (\delta_{ik} \delta_{jl}+\delta_{il} \delta_{jk}) +
    \lambda \ \delta_{ij} \delta_{kl}
    \;.

Important Notes
---------------

- This example requires petsc4py, mpi4py and (optionally) pymetis with their
  dependencies installed!
- This example generates a number of files - do not use an existing non-empty
  directory for the ``output_dir`` argument.
- Use the ``--clear`` option with care!

Notes
-----

- Each task is responsible for a subdomain consisting of a set of cells (a cell
  region).
- Each subdomain owns PETSc DOFs within a consecutive range.
- When both global and task-local variables exist, the task-local
  variables have ``_i`` suffix.
- This example shows how to use a nonlinear solver from PETSc.
- This example can serve as a template for solving a (non)linear multi-field
  problem - just replace the equations in :func:`create_local_problem()`.
- The material parameter :math:`\alpha_{ij}` is artificially high to be able to
  see the pressure influence on displacements.
- The command line options are saved into <output_dir>/options.txt file.

Usage Examples
--------------

See all options::

  python3 sfepy/examples/multi_physics/biot_parallel_interactive.py -h

See PETSc options::

  python3 sfepy/examples/multi_physics/biot_parallel_interactive.py -help

Single process run useful for debugging with :func:`debug()
<sfepy.base.base.debug>`::

  python3 sfepy/examples/multi_physics/biot_parallel_interactive.py output-parallel

Parallel runs::

  mpiexec -n 3 python3 sfepy/examples/multi_physics/biot_parallel_interactive.py output-parallel -2 --shape=101,101

  mpiexec -n 3 python3 sfepy/examples/multi_physics/biot_parallel_interactive.py output-parallel -2 --shape=101,101 --metis

  mpiexec -n 8 python3 sfepy/examples/multi_physics/biot_parallel_interactive.py output-parallel -2 --shape 101,101 --metis -snes_monitor -snes_view -snes_converged_reason -ksp_monitor

Using FieldSplit preconditioner::

  mpiexec -n 2 python3 sfepy/examples/multi_physics/biot_parallel_interactive.py output-parallel --shape=101,101 -snes_monitor -snes_converged_reason -ksp_monitor -pc_type fieldsplit

  mpiexec -n 8 python3 sfepy/examples/multi_physics/biot_parallel_interactive.py output-parallel --shape=1001,1001 --metis -snes_monitor -snes_converged_reason -ksp_monitor -pc_type fieldsplit -pc_fieldsplit_type additive

View the results using::

  sfepy-view output-parallel/sol.h5


.. image:: /../doc/images/gallery/multi_physics-biot_parallel_interactive.png


:download:`source code </../sfepy/examples/multi_physics/biot_parallel_interactive.py>`

.. literalinclude:: /../sfepy/examples/multi_physics/biot_parallel_interactive.py

