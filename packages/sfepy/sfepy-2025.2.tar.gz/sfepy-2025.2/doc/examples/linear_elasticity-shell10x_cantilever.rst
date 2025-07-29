.. _linear_elasticity-shell10x_cantilever:

linear_elasticity/shell10x_cantilever.py
========================================

**Description**


Bending of a long thin cantilever beam, declarative problem description.

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

See also :ref:`linear_elasticity-shell10x_cantilever_interactive` example.

View the results using::

  sfepy-view shell10x.vtk -f u_disp:wu_disp 1:vw


.. image:: /../doc/images/gallery/linear_elasticity-shell10x_cantilever.png


:download:`source code </../sfepy/examples/linear_elasticity/shell10x_cantilever.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/shell10x_cantilever.py

