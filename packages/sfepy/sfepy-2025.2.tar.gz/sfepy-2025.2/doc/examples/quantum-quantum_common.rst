.. _quantum-quantum_common:

quantum/quantum_common.py
=========================

**Description**


Common code for basic electronic structure examples.

It covers only simple single electron problems, e.g. well, oscillator, hydrogen
atom and boron atom with 1 electron - see the corresponding files in this
directory, where potentials (:func:`fun_v()`) as well as exact solutions
(:func:`get_exact()`) for those problems are defined.

Notes
-----

The same code should work also with a 3D (box) mesh, but a very fine mesh would
be required. Also in the 2D case, finer mesh and/or higher approximation order
means higher accuracy.

Try changing C, F and L parameters in ``meshes/quantum/square.geo`` and
regenerate the mesh using gmsh::

  gmsh -2 -format mesh meshes/quantum/square.geo -o meshes/quantum/square.mesh
  ./script/convert_mesh.py -2 meshes/quantum/square.mesh meshes/quantum/square.mesh

The ``script/convert_mesh.py`` call makes the mesh planar, as gmsh saves 2D
medit meshes including the zero z coordinates.

Also try changing approximation order ('approx_order') of the field below.

Usage Examples
--------------

The following examples are available and can be run using::

  sfepy-run sfepy/examples/quantum/boron.py
  sfepy-run sfepy/examples/quantum/hydrogen.py
  sfepy-run sfepy/examples/quantum/oscillator.py
  sfepy-run sfepy/examples/quantum/well.py




:download:`source code </../sfepy/examples/quantum/quantum_common.py>`

.. literalinclude:: /../sfepy/examples/quantum/quantum_common.py

