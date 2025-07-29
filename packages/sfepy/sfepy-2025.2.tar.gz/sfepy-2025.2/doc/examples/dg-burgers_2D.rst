.. _dg-burgers_2D:

dg/burgers_2D.py
================

**Description**


Burgers equation in 2D solved using discontinous Galerkin method

.. math:: \frac{dp}{dt} + div\,f(p) - div(grad\,p) = 0

Based on

Kučera, V. (n.d.). Higher order methods for the solution of compressible flows.
Charles University. p. 21 eq. (1.39)


Usage Examples
--------------

Run::

  sfepy-run sfepy/examples/dg/burgers_2D.py

Results are saved to output/dg/burgers_2D folder by default as ``.msh`` files,
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




:download:`source code </../sfepy/examples/dg/burgers_2D.py>`

.. literalinclude:: /../sfepy/examples/dg/burgers_2D.py

