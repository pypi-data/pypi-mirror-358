.. _large_deformation-active_fibres:

large_deformation/active_fibres.py
==================================

**Description**


Nearly incompressible hyperelastic material model with active fibres.

Large deformation is described using the total Lagrangian formulation.
Models of this kind can be used in biomechanics to model biological
tissues, e.g. muscles.

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

The effective stress :math:`\ull{S}\eff(\ul{u})` incorporates also the
effects of the active fibres in two preferential directions:

.. math::
    \ull{S}\eff(\ul{u}) = \mu J^{-\frac{2}{3}}(\ull{I}
    - \frac{1}{3}\tr(\ull{C}) \ull{C}^{-1})
    + \sum_{k=1}^2 \tau^k \ull{\omega}^k
    \;.

The first term is the neo-Hookean term and the sum add contributions of
the two fibre systems. The tensors :math:`\ull{\omega}^k =
\ul{d}^k\ul{d}^k` are defined by the fibre system direction vectors
:math:`\ul{d}^k` (unit).

For the one-dimensional tensions :math:`\tau^k` holds simply (:math:`^k`
omitted):

.. math::
    \tau = A f_{\rm max} \exp{\left\{-(\frac{\epsilon - \varepsilon_{\rm
    opt}}{s})^2\right\}} \mbox{ , } \epsilon = \ull{E} : \ull{\omega}
    \;.

Usage Examples
--------------

- Run with the Newton solver::

    sfepy-run sfepy/examples/large_deformation/active_fibres.py

- Run with the matrix-free Newton-Krylov solver from SciPy::

    sfepy-run sfepy/examples/large_deformation/active_fibres.py -d solver=root

- Visualize the Green strain tensor magnitude on the deforming mesh::

    sfepy-view output/hsphere8.h5 -f green_strain:wu:f1:p0 1:vw:o0.3:p0 --color-limits=0.0,1.3

- Visualize the stresses in active fibres on the deforming mesh::

    sfepy-view output/hsphere8.h5 -f f1_stress:wu:f1:p0 1:vw:o0.3:p0 --color-limits=0,20
    sfepy-view output/hsphere8.h5 -f f2_stress:wu:f1:p0 1:vw:o0.3:p0 --color-limits=0,30

    sfepy-view output/hsphere8.h5 -f f1_stress:wu:f1:p0 1:vw:o0.3:p0 f2_stress:wu:f1:p1 1:vw:o0.3:p1 --grid-vector1="1.2,-1.2,0" --color-limits=0,30


.. image:: /../doc/images/gallery/large_deformation-active_fibres.png
.. image:: /../doc/images/gallery/large_deformation-active_fibres-hsphere8-fdir0.png
.. image:: /../doc/images/gallery/large_deformation-active_fibres-hsphere8-fdir1.png


:download:`source code </../sfepy/examples/large_deformation/active_fibres.py>`

.. literalinclude:: /../sfepy/examples/large_deformation/active_fibres.py

