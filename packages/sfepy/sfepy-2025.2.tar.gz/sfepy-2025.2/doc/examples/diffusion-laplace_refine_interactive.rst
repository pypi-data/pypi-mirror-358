.. _diffusion-laplace_refine_interactive:

diffusion/laplace_refine_interactive.py
=======================================

**Description**


Example of solving Laplace's equation on a block domain refined with level 1
hanging nodes.

The domain is progressively refined towards the edge/face of the block, where
Dirichlet boundary conditions are prescribed by an oscillating function.

Find :math:`u` such that:

.. math::
    \int_{\Omega} \nabla v \cdot \nabla u = 0
    \;, \quad \forall s \;.

Notes
-----
The implementation of the mesh refinement with level 1 hanging nodes is a
proof-of-concept code with many unresolved issues. The main problem is the fact
that a user needs to input the cells to refine at each level, while taking care
of the following constraints:

- the level 1 hanging nodes constraint: a cell that has a less-refined
  neighbour cannot be refined;
- the implementation constraint: a cell with a refined neighbour cannot be
  refined.

The hanging nodes are treated by a basis transformation/DOF substitution, which
has to be applied explicitly by the user:

- call ``field.substitute_dofs(subs)`` before assembling and solving;
- then call ``field.restore_dofs()`` before saving results.

Usage Examples
--------------

Default options, 2D, storing results in 'output' directory::

  python3 sfepy/examples/diffusion/laplace_refine_interactive.py output
  sfepy-view output/hanging.vtk -2 -f u:wu 1:vw

Default options, 3D, storing results in 'output' directory::

  python3 sfepy/examples/diffusion/laplace_refine_interactive.py -3 output
  sfepy-view output/hanging.vtk -f u:wu:f0.1 1:vw


Finer initial domain, 2D, storing results in 'output' directory::

  python3 sfepy/examples/diffusion/laplace_refine_interactive.py --shape=11,11 output
  sfepy-view output/hanging.vtk -2 -f u:wu 1:vw

Bi-quadratic approximation, 2D, storing results in 'output' directory::

  python3 sfepy/examples/diffusion/laplace_refine_interactive.py --order=2 output

  # View solution with higher order DOFs removed.
  sfepy-view output/hanging.vtk -2 -f u:wu 1:vw

  # View full solution on a mesh adapted for visualization.
  sfepy-view output/hanging_u.vtk -2 -f u:wu 1:vw


.. image:: /../doc/images/gallery/diffusion-laplace_refine_interactive.png


:download:`source code </../sfepy/examples/diffusion/laplace_refine_interactive.py>`

.. literalinclude:: /../sfepy/examples/diffusion/laplace_refine_interactive.py

