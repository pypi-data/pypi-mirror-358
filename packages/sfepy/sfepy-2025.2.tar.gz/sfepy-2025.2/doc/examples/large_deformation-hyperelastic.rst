.. _large_deformation-hyperelastic:

large_deformation/hyperelastic.py
=================================

**Description**


Nearly incompressible Mooney-Rivlin hyperelastic material model.

Large deformation is described using the total Lagrangian formulation.
Models of this kind can be used to model e.g. rubber or some biological
materials.

Find :math:`\ul{u}` such that:

.. math::
    \intl{\Omega\suz}{} \left( \ull{S}\eff(\ul{u})
    + K(J-1)\; J \ull{C}^{-1} \right) : \delta \ull{E}(\ul{v}) \difd{V}
    = 0
    \;, \quad \forall \ul{v} \;,

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

The effective stress :math:`\ull{S}\eff(\ul{u})` is given by:

.. math::
    \ull{S}\eff(\ul{u}) = \mu J^{-\frac{2}{3}}(\ull{I}
    - \frac{1}{3}\tr(\ull{C}) \ull{C}^{-1})
    + \kappa J^{-\frac{4}{3}} (\tr(\ull{C}\ull{I} - \ull{C}
    - \frac{2}{6}((\tr{\ull{C}})^2 - \tr{(\ull{C}^2)})\ull{C}^{-1})
    \;.


.. image:: /../doc/images/gallery/large_deformation-hyperelastic.png


:download:`source code </../sfepy/examples/large_deformation/hyperelastic.py>`

.. literalinclude:: /../sfepy/examples/large_deformation/hyperelastic.py

