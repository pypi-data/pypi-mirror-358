.. _linear_elasticity-shell10x_cantilever_interactive:

linear_elasticity/shell10x_cantilever_interactive.py
====================================================

**Description**


Bending of a long thin cantilever beam, imperative problem description.

The example demonstrates use of the
:class:`dw_shell10x <sfepy.terms.terms_shells.Shell10XTerm>` term.

Find displacements of the central plane :math:`\ul{u}`, and rotations
:math:`\ul{\alpha}` such that:

.. math::
    \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}, \ul{\beta})
    e_{kl}(\ul{u}, \ul{\alpha})
    = - \int_{\Gamma_{right}} \ul{v} \cdot \ul{f}
    \;, \quad \forall \ul{v} \;,

where :math:`D_{ijkl}` is the isotropic elastic tensor, given using the Young's
modulus :math:`E` and the Poisson's ratio :math:`\nu`.

The variable ``u`` below holds both :math:`\ul{u}` and :math:`\ul{\alpha}`
DOFs. For visualization, it is saved as two fields ``u_disp`` and ``u_rot``,
corresponding to :math:`\ul{u}` and :math:`\ul{\alpha}`, respectively.

The material, loading and discretization parameters can be given using command
line options.

Besides the default straight beam, two coordinate transformations can be applied
(see the ``--transform`` option):

- bend: the beam is bent
- twist: the beam is twisted

For the straight and bent beam a comparison with the analytical solution
coming from the Euler-Bernoulli theory is shown.

See also :ref:`linear_elasticity-shell10x_cantilever` example.

Usage Examples
--------------

See all options::

  python3 sfepy/examples/linear_elasticity/shell10x_cantilever_interactive.py -h

Apply the bending transformation to the beam domain coordinates, plot
convergence curves w.r.t. number of elements::

  python3 sfepy/examples/linear_elasticity/shell10x_cantilever_interactive.py output -t bend -p

Apply the twisting transformation to the beam domain coordinates, change number of cells::

  python3 sfepy/examples/linear_elasticity/shell10x_cantilever_interactive.py output -t twist -n 2,51,3


.. image:: /../doc/images/gallery/linear_elasticity-shell10x_cantilever_interactive-shell10x_cantilever_convergence_bent.png
.. image:: /../doc/images/gallery/linear_elasticity-shell10x_cantilever_interactive.png


:download:`source code </../sfepy/examples/linear_elasticity/shell10x_cantilever_interactive.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/shell10x_cantilever_interactive.py

