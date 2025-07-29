.. _dg-laplace_2D:

dg/laplace_2D.py
================

**Description**


Laplace equation solved in 2d by discontinous Galerkin method

.. math:: - div(grad\,p) = 0

on rectangle
                    p = 0
                    p_y = 0
    [0,b]-----------------------------[a, b]
         |                           |
         |                           |
p_x = -a |         p(x,y)            | p_x = 0
p = 0    |                           | p = 0
         |                           |
    [0,0]-----------------------------[a, 0]
                    p_y = b
                    p = 0

solution to this is
   .. math:: p(x,y) = 1/2*x**2 - 1/2*y**2 - a*x + b*y


Usage Examples
--------------

Run::

  sfepy-run sfepy/examples/dg/laplace_2D.py

Results are saved to output/dg/laplace_2D folder by default as ``.msh`` files,
the best way to view them is through GMSH (http://gmsh.info/) version 4.6 or
newer. Start GMSH and use ``File | Open`` menu or Crtl + O shortcut, navigate to
the output folder, select all ``.msh`` files and hit Open, all files should load
as one item in Post-processing named p_cell_nodes.

GMSH is capable of rendering high order approximations in individual elements,
to modify fidelity of rendering, double click the displayed mesh, quick options
menu should pop up, click on ``All view options...``. This brings up the Options
window with ``View [0]`` selected in left column. Under the tab ``General``
ensure that ``Adapt visualization grid`` is ticked, then you can adjust
``Maximum recursion depth`` and ```Target visualization error`` to tune
the visualization. To see visualization elements (as opposed to mesh elements)
go to ``Visibility`` tab and tick ``Draw element outlines``, this option is also
available from quick options menu as ``View element outlines`` or under shortcut
``Alt+E``. In the quick options menu, you can also modify normal raise by
clicking ``View Normal Raise`` to see solution rendered as surface above the
mesh. Note that for triangular meshes normal raise -1 produces expected raise
above the mesh. This is due to the opposite orientation of the reference
elements in GMSH and Sfepy and might get patched in the future.




:download:`source code </../sfepy/examples/dg/laplace_2D.py>`

.. literalinclude:: /../sfepy/examples/dg/laplace_2D.py

