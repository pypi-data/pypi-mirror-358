.. _large_deformation-hyperelastic_tl_up_interactive:

large_deformation/hyperelastic_tl_up_interactive.py
===================================================

**Description**


Incompressible Mooney-Rivlin hyperelastic material model.

In this model, the deformation energy density per unit reference volume is
given by

.. math::
    W = C_{(10)} \, \left( \overline I_1 - 3 \right)
        + C_{(01)} \, \left( \overline I_2 - 3 \right) \;,

where :math:`\overline I_1` and :math:`\overline I_2` are the first
and second main invariants of the deviatoric part of the right
Cauchy-Green deformation tensor :math:`\ull{C}`. The coefficients
:math:`C_{(10)}` and :math:`C_{(01)}` are material parameters.

Components of the second Piola-Kirchhoff stress are in the case of an
incompressible material

.. math::
    S_{ij} = 2 \, \pdiff{W}{C_{ij}} - p \, F^{-1}_{ik} \, F^{-T}_{kj} \;,

where :math:`p` is the hydrostatic pressure.

The large deformation is described using the total Lagrangian formulation in
this example. The incompressibility is treated by mixed displacement-pressure
formulation. The weak formulation is:
Find the displacement field :math:`\ul{u}` and pressure field :math:`p`
such that:

.. math::
    \intl{\Omega\suz}{} \ull{S}\eff(\ul{u}, p) : \ull{E}(\ul{v})
    \difd{V} = 0
    \;, \quad \forall \ul{v} \;,

    \intl{\Omega\suz}{} q\, (J(\ul{u})-1) \difd{V} = 0
    \;, \quad \forall q \;.

The following formula holds for the axial true (Cauchy) stress in the case of
uniaxial stress:

.. math::
    \sigma(\lambda) =
        2\, \left( C_{(10)} + \frac{C_{(01)}}{\lambda} \right) \,
        \left( \lambda^2 - \frac{1}{\lambda} \right) \;,

where :math:`\lambda = l/l_0` is the prescribed stretch (:math:`l_0` and
:math:`l` being the original and deformed specimen length respectively).

The boundary conditions are set so that a state of uniaxial stress is achieved,
i.e. appropriate components of displacement are fixed on the "Left", "Bottom",
and "Near" faces and a monotonously increasing displacement is prescribed on
the "Right" face. This prescribed displacement is then used to calculate
:math:`\lambda` and to convert the second Piola-Kirchhoff stress to the true
(Cauchy) stress.

Note on material parameters
---------------------------

The relationship between material parameters used in the *SfePy* hyperelastic
terms (:class:`NeoHookeanTLTerm
<sfepy.terms.terms_hyperelastic_tl.NeoHookeanTLTerm>`,
:class:`MooneyRivlinTLTerm
<sfepy.terms.terms_hyperelastic_tl.MooneyRivlinTLTerm>`)
and the ones used in this example is:

.. math::
    \mu = 2\, C_{(10)} \;,

    \kappa = 2\, C_{(01)} \;.

Usage Examples
--------------

Default options::

  $ python sfepy/examples/large_deformation/hyperelastic_tl_up_interactive.py

To show a comparison of stress against the analytic formula::

  $ python sfepy/examples/large_deformation/hyperelastic_tl_up_interactive.py -p

Using different mesh fineness::

  $ python sfepy/examples/large_deformation/hyperelastic_tl_up_interactive.py \
    --shape "5, 5, 5"

Different dimensions of the computational domain::

  $ python sfepy/examples/large_deformation/hyperelastic_tl_up_interactive.py \
    --dims "2, 1, 3"

Different length of time interval and/or number of time steps::

  $ python sfepy/examples/large_deformation/hyperelastic_tl_up_interactive.py \
    -t 0,15,21

Use higher approximation order (the ``-t`` option to decrease the time step is
required for convergence here)::

  $ python sfepy/examples/large_deformation/hyperelastic_tl_up_interactive.py \
    --order 2 -t 0,2,21

Change material parameters::

  $ python sfepy/examples/large_deformation/hyperelastic_tl_up_interactive.py -m 2,1


.. image:: /../doc/images/gallery/large_deformation-hyperelastic_tl_up_interactive-hyperelastic_tl_up_comparison.png
.. image:: /../doc/images/gallery/large_deformation-hyperelastic_tl_up_interactive.png


:download:`source code </../sfepy/examples/large_deformation/hyperelastic_tl_up_interactive.py>`

.. literalinclude:: /../sfepy/examples/large_deformation/hyperelastic_tl_up_interactive.py

