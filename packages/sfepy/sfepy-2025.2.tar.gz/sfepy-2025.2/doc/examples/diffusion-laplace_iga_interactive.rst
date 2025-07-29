.. _diffusion-laplace_iga_interactive:

diffusion/laplace_iga_interactive.py
====================================

**Description**


Laplace equation with Dirichlet boundary conditions solved in a single patch
NURBS domain using the isogeometric analysis (IGA) approach, using commands
for interactive use.

This script allows the creation of a customisable NURBS surface using igakit
built-in CAD routines, which is then saved in custom HDF5-based files with
.iga extension.

Notes
-----

The ``create_patch`` function creates a NURBS-patch of the area between two
coplanar nested circles using igakit CAD built-in routines. The created patch
is not connected in the orthoradial direction. This is a problem when the
disconnected boundary is not perpendicular to the line connecting the two
centres of the circles, as the solution then exhibits a discontinuity along
this line. A workaround for this issue is to enforce perpendicularity by
changing the start angle in function ``igakit.cad.circle`` (see the code down
below for the actual trick). The discontinuity disappears.

Usage Examples
--------------

Default options, storing results in this file's parent directory::

  python3 sfepy/examples/diffusion/laplace_iga_interactive.py

Command line options for tweaking the geometry of the NURBS-patch & more::

  python3 sfepy/examples/diffusion/laplace_iga_interactive.py --R1=0.7 --C2=0.1,0.1 --viewpatch

View the results using::

  sfepy-view concentric_circles.vtk


.. image:: /../doc/images/gallery/diffusion-laplace_iga_interactive.png


:download:`source code </../sfepy/examples/diffusion/laplace_iga_interactive.py>`

.. literalinclude:: /../sfepy/examples/diffusion/laplace_iga_interactive.py

