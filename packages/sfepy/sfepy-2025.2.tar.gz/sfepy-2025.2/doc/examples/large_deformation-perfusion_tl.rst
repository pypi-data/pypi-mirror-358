.. _large_deformation-perfusion_tl:

large_deformation/perfusion_tl.py
=================================

**Description**


Porous nearly incompressible hyperelastic material with fluid perfusion.

Large deformation is described using the total Lagrangian formulation.
Models of this kind can be used in biomechanics to model biological
tissues, e.g. muscles.

Find :math:`\ul{u}` such that:

(equilibrium equation with boundary tractions)

.. math::
    \intl{\Omega\suz}{} \left( \ull{S}\eff - p J \ull{C}^{-1}
    \right) : \delta \ull{E}(\ul{v}) \difd{V}
    + \intl{\Gamma_0\suz}{} \ul{\nu} \cdot \ull{F}^{-1} \cdot \ull{\sigma}
    \cdot  \ul{v} J \difd{S}
    = 0
    \;, \quad \forall \ul{v} \;,

(mass balance equation (perfusion))

.. math::
    \intl{\Omega\suz}{} q J(\ul{u})
    + \intl{\Omega\suz}{} \ull{K}(\ul{u}\sunm) : \pdiff{q}{X} \pdiff{p}{X}
    = \intl{\Omega\suz}{} q J(\ul{u}\sunm)
    \;, \quad \forall q \;,


where

.. list-table::
   :widths: 20 80

   * - :math:`\ull{F}`
     - deformation gradient :math:`F_{ij} = \pdiff{x_i}{X_j}`
   * - :math:`J`
     - :math:`\det(F)`
   * - :math:`\ull{C}`
     -  right Cauchy-Green deformation tensor :math:`C = F^T F`
   * - :math:`\ull{E}(\ul{u})`
     - Green strain tensor :math:`E_{ij} = \frac{1}{2}(\pdiff{u_i}{X_j} +
       \pdiff{u_j}{X_i} + \pdiff{u_m}{X_i}\pdiff{u_m}{X_j})`
   * - :math:`\ull{S}\eff(\ul{u})`
     - effective second Piola-Kirchhoff stress tensor

The effective (neo-Hookean) stress :math:`\ull{S}\eff(\ul{u})` is given
by:

.. math::
    \ull{S}\eff(\ul{u}) = \mu J^{-\frac{2}{3}}(\ull{I}
    - \frac{1}{3}\tr(\ull{C}) \ull{C}^{-1})
    \;.

The linearized deformation-dependent permeability is defined as
:math:`\ull{K}(\ul{u}) = J \ull{F}^{-1} \ull{k} f(J) \ull{F}^{-T}`,
where :math:`\ul{u}` relates to the previous time step :math:`(n-1)` and
:math:`f(J) = \max\left(0, \left(1 + \frac{(J -
1)}{N_f}\right)\right)^2` expresses the dependence on volume
compression/expansion.


.. image:: /../doc/images/gallery/large_deformation-perfusion_tl.png


:download:`source code </../sfepy/examples/large_deformation/perfusion_tl.py>`

.. literalinclude:: /../sfepy/examples/large_deformation/perfusion_tl.py

