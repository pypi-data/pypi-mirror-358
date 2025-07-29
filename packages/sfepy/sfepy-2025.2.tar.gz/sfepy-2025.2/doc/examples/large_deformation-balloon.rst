.. _large_deformation-balloon:

large_deformation/balloon.py
============================

**Description**


Inflation of a Mooney-Rivlin hyperelastic balloon.

This example serves as a verification of the membrane term (``dw_tl_membrane``,
:class:`TLMembraneTerm <sfepy.terms.terms_membrane.TLMembraneTerm>`)
implementation.

Following Rivlin 1952 and Dumais, the analytical relation between a
relative stretch :math:`L = r / r_0` of a thin (membrane) sphere made of the
Mooney-Rivlin material of the undeformed radius :math:`r_0`, membrane
thickness :math:`h_0` and the inner pressure :math:`p` is

.. math::

   p = 4 \frac{h_0}{r_0} (\frac{1}{L} - \frac{1}{L^7}) (c_1 + c_2 L^2) \;,

where :math:`c_1`, :math:`c_2` are the Mooney-Rivlin material parameters.

In the equations below, only the surface of the domain is mechanically
important - a stiff 2D membrane is embedded in the 3D space and coincides with
the balloon surface. The volume is very soft, to simulate a fluid-filled
cavity. A similar model could be used to model e.g. plant cells. The balloon
surface is loaded by prescribing the inner volume change :math:`\omega(t)`.
The fluid pressure in the cavity is a single scalar value, enforced either by
the ``'integral_mean_value'`` linear combination condition, when ``use_lcbcs``
argument of :func:`define()` is set to ``True`` (default), or by the
:math:`L^2` constant approximation.

Find :math:`\ul{u}(\ul{X})` and a constant :math:`p` such that:

- balance of forces:

  .. math::
     \intl{\Omega\suz}{} \left( \ull{S}\eff(\ul{u})
     - p\; J \ull{C}^{-1} \right) : \delta \ull{E}(\ul{v}; \ul{v}) \difd{V}
     + \intl{\Gamma\suz}{} \ull{S}\eff(\tilde{\ul{u}}) \delta
     \ull{E}(\tilde{\ul{u}}; \tilde{\ul{v}}) h_0 \difd{S}
     = 0 \;, \quad \forall \ul{v} \in [H^1_0(\Omega)]^3 \;,

- volume conservation:

  .. math::
     \int\limits_{\Omega_0} \left[\omega(t)-J(u)\right] q\, dx = 0
     \qquad \forall q \in L^2(\Omega) \;,

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

The :math:`\tilde{\ul{u}}` and :math:`\tilde{\ul{v}}` variables correspond to
:math:`\ul{u}`, :math:`\ul{v}`, respectively, transformed to the membrane
coordinate frame.

Use the following command to show a comparison of the FEM solution with the
above analytical relation (notice the nonlinearity of the dependence)::

  sfepy-run sfepy/examples/large_deformation/balloon.py -d 'plot=True'

or::

  sfepy-run sfepy/examples/large_deformation/balloon.py -d 'plot=True, use_lcbcs=False'

The agreement should be very good, even though the mesh is coarse.

View the results using::

  sfepy-view unit_ball.h5 -f u:wu:s12:p0 p:s12:p1

This example uses the adaptive time-stepping solver (``'ts.adaptive'``) with
the default adaptivity function :func:`adapt_time_step()
<sfepy.solvers.ts_solvers.adapt_time_step>`. Plot the used time steps by::

  python3 sfepy/scripts/plot_times.py unit_ball.h5


.. image:: /../doc/images/gallery/large_deformation-balloon.png


:download:`source code </../sfepy/examples/large_deformation/balloon.py>`

.. literalinclude:: /../sfepy/examples/large_deformation/balloon.py

