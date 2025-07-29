.. _diffusion-poisson_parallel_interactive:

diffusion/poisson_parallel_interactive.py
=========================================

**Description**


Parallel assembling and solving of a Poisson's equation, using commands for
interactive use.

Find :math:`u` such that:

.. math::
    \int_{\Omega} \nabla v \cdot \nabla u
    = \int_{\Omega} v f
    \;, \quad \forall s \;.

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
- This example does not use a nonlinear solver.
- This example can serve as a template for solving a linear single-field scalar
  problem - just replace the equations in :func:`create_local_problem()`.
- The command line options are saved into <output_dir>/options.txt file.

Usage Examples
--------------

See all options::

  python3 sfepy/examples/diffusion/poisson_parallel_interactive.py -h

See PETSc options::

  python3 sfepy/examples/diffusion/poisson_parallel_interactive.py -help

Single process run useful for debugging with :func:`debug()
<sfepy.base.base.debug>`::

  python3 sfepy/examples/diffusion/poisson_parallel_interactive.py output-parallel

Parallel runs::

  mpiexec -n 3 python3 sfepy/examples/diffusion/poisson_parallel_interactive.py output-parallel -2 --shape=101,101

  mpiexec -n 3 python3 sfepy/examples/diffusion/poisson_parallel_interactive.py output-parallel -2 --shape=101,101 --metis

  mpiexec -n 5 python3 sfepy/examples/diffusion/poisson_parallel_interactive.py output-parallel -2 --shape=101,101 --verify --metis -ksp_monitor -ksp_converged_reason

View the results using::

  sfepy-view output-parallel/sol.h5 -f u:wu 1:vw


.. image:: /../doc/images/gallery/diffusion-poisson_parallel_interactive.png


:download:`source code </../sfepy/examples/diffusion/poisson_parallel_interactive.py>`

.. literalinclude:: /../sfepy/examples/diffusion/poisson_parallel_interactive.py

