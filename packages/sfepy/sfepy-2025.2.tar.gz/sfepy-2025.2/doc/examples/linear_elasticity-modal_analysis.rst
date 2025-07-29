.. _linear_elasticity-modal_analysis:

linear_elasticity/modal_analysis.py
===================================

**Description**


Modal analysis of a linear elastic block in 2D or 3D.

The dimension of the problem is determined by the length of the vector
in ``--dims`` option.

Optionally, a mesh file name can be given as a positional argument. In that
case, the mesh generation options are ignored.

The default material properties correspond to aluminium in the following units:

- length: m
- mass: kg
- stiffness / stress: Pa
- density: kg / m^3

Examples
--------

- Run with the default arguments::

    python sfepy/examples/linear_elasticity/modal_analysis.py

- Fix bottom surface of the domain::

    python sfepy/examples/linear_elasticity/modal_analysis.py -b cantilever

- Increase mesh resolution::

    python sfepy/examples/linear_elasticity/modal_analysis.py -s 31,31

- Use 3D domain::

    python sfepy/examples/linear_elasticity/modal_analysis.py -d 1,1,1 -c 0,0,0 -s 8,8,8

- Change the eigenvalue problem solver to LOBPCG::

    python sfepy/examples/linear_elasticity/modal_analysis.py --solver="eig.scipy_lobpcg,i_max:100,largest:False"

  See :mod:`sfepy.solvers.eigen` for available solvers.


.. image:: /../doc/images/gallery/linear_elasticity-modal_analysis.png


:download:`source code </../sfepy/examples/linear_elasticity/modal_analysis.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/modal_analysis.py

