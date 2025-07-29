.. _diffusion-sinbc:

diffusion/sinbc.py
==================

**Description**


Laplace equation with Dirichlet boundary conditions given by a sine function
and constants.

Find :math:`t` such that:

.. math::
    \int_{\Omega} c \nabla s \cdot \nabla t
    = 0
    \;, \quad \forall s \;.

The :class:`sfepy.discrete.fem.meshio.UserMeshIO` class is used to refine the
original two-element mesh before the actual solution.

The FE polynomial basis and the approximation order can be chosen on the
command-line. By default, the fifth order Lagrange polynomial space is used,
see ``define()`` arguments.

This example demonstrates how to visualize higher order approximations of the
continuous solution. The adaptive linearization is applied in order to save
viewable results, see both the options keyword and the ``post_process()``
function that computes the solution gradient. The linearization parameters can
also be specified on the command line.

The Lagrange or Bernstein polynomial bases support higher order
DOFs in the Dirichlet boundary conditions, unlike the hierarchical Lobatto
basis implementation, compare the results of::

  sfepy-run sfepy/examples/diffusion/sinbc.py -d basis=lagrange
  sfepy-run sfepy/examples/diffusion/sinbc.py -d basis=bernstein
  sfepy-run sfepy/examples/diffusion/sinbc.py -d basis=lobatto

Use the following commands to view each of the results of the above commands
(assuming default output directory and names)::

  sfepy-view 2_4_2_refined_t.vtk -2 -f t:wt
  sfepy-view 2_4_2_refined_grad.vtk -2


.. image:: /../doc/images/gallery/diffusion-sinbc_grad.png
.. image:: /../doc/images/gallery/diffusion-sinbc_t.png


:download:`source code </../sfepy/examples/diffusion/sinbc.py>`

.. literalinclude:: /../sfepy/examples/diffusion/sinbc.py

