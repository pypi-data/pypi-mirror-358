.. _multi_physics-piezo_elastodynamic:

multi_physics/piezo_elastodynamic.py
====================================

**Description**


The linear elastodynamics of a piezoelectric body loaded by a given base
motion.

The generated voltage between the bottom and top surface electrodes is recorded
and plotted. The scalar potential on the top surface electrode is modeled using
a constant L^2 field. The Nitsche's method is used to weakly apply the
(unknown) potential Dirichlet boundary condition on the top surface.

Find the displacements :math:`\ul{u}(t)`, the potential :math:`p(t)` and the
constant potential on the top electrode :math:`\bar p(t)` such that:

.. math::
    \int_\Omega \rho\ \ul{v} \cdot \ul{\ddot u}
    + \int_\Omega C_{ijkl}\ \veps_{ij}(\ul{v}) \veps_{kl}(\ul{u})
    - \int_\Omega e_{kij}\ \veps_{ij}(\ul{v}) \nabla_k p
    = 0
    \;, \quad \forall \ul{v} \;,

    \int_\Omega e_{kij}\ \veps_{ij}(\ul{u}) \nabla_k q
    + \int_\Omega \kappa_{ij} \nabla_i \psi \nabla_j p
    - \int_{\Gamma_{top}} \kappa_{ij} \nabla_j p n_i q
    + \int_{\Gamma_{top}} \kappa_{ij} \nabla_j q n_i (p - \bar p)
    + \int_{\Gamma_{top}} k q (p - \bar p)
    = 0
    \;, \quad \forall q \;,

    \int_{\Gamma_{top}} \kappa_{ij} \nabla_j \dot{p} n_i + \bar p / R = 0 \;,

where :math:`C_{ijkl}` is the matrix of elastic properties under constant
electric field intensity, :math:`e_{kij}` the piezoelectric modulus,
:math:`\kappa_{ij}` the permittivity under constant deformation, :math:`k` a
penalty parameter and :math:`R` the external circuit resistance (e.g. of an
oscilloscope used to measure the voltage between the electrodes).

Usage Examples
--------------

Run with the default settings, results stored in ``output/piezo-ed/``::

  sfepy-run sfepy/examples/multi_physics/piezo_elastodynamic.py

The :func:`define()` arguments, see below, can be set using the ``-d`` option::

  sfepy-run sfepy/examples/multi_physics/piezo_elastodynamic.py -d "order=2, ct1=2.5"

View the resulting potential :math:`p` on a deformed mesh (2000x magnified)::

  sfepy-view output/piezo-ed/user_block.h5 -f p:wu:f2000:p0 1:vw:wu:f2000:p0 --color-map=inferno


.. image:: /../doc/images/gallery/multi_physics-piezo_elastodynamic.png


:download:`source code </../sfepy/examples/multi_physics/piezo_elastodynamic.py>`

.. literalinclude:: /../sfepy/examples/multi_physics/piezo_elastodynamic.py

