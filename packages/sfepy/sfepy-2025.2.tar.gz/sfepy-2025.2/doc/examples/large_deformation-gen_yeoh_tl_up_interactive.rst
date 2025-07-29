.. _large_deformation-gen_yeoh_tl_up_interactive:

large_deformation/gen_yeoh_tl_up_interactive.py
===============================================

**Description**


Incompressible generalized Yeoh hyperelastic material model.

In this model, the deformation energy density per unit reference volume is
given by

.. math::
    W =
      K_1 \, \left( \overline I_1 - 3 \right)^{m}
      +K_2 \, \left( \overline I_1 - 3 \right)^{p}
      +K_3 \, \left( \overline I_1 - 3 \right)^{q}

where :math:`\overline I_1` is the first main invariant of the deviatoric part
of the right Cauchy-Green deformation tensor :math:`\ull{C}`, the coefficients
:math:`K_1, K_2, K_3` and exponents :math:`m, p, q` are material parameters.
Only a single term (:class:`dw_tl_he_genyeoh
<sfepy.terms.terms_hyperelastic_tl.GenYeohTLTerm>`) is used in this example for
the sake of simplicity.

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
        \frac{2}{3} \, m \, K_1 \,
        \left( \lambda^2 + \frac{2}{\lambda} - 3 \right)^{m-1} \,
        \left( \lambda - \frac{1}{\lambda^2} \right) \;,

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

The three-term generalized Yeoh model is meant to be used for modelling of
filled rubbers. The following choice of parameters is suggested [1] based on
experimental data and stability considerations:

  :math:`K_1 > 0`,

  :math:`K_2 < 0`,

  :math:`K_3 > 0`,

  :math:`0.7 < m < 1`,

  :math:`m < p < q`.

Usage Examples
--------------

Default options::

  python3 sfepy/examples/large_deformation/gen_yeoh_tl_up_interactive.py

To show a comparison of stress against the analytic formula::

  python3 sfepy/examples/large_deformation/gen_yeoh_tl_up_interactive.py -p

Using different mesh fineness::

  python3 sfepy/examples/large_deformation/gen_yeoh_tl_up_interactive.py \
    --shape "5, 5, 5"

Different dimensions of the computational domain::

  python3 sfepy/examples/large_deformation/gen_yeoh_tl_up_interactive.py \
    --dims "2, 1, 3"

Different length of time interval and/or number of time steps::

  python3 sfepy/examples/large_deformation/gen_yeoh_tl_up_interactive.py \
    -t 0,15,21

Use higher approximation order (the ``-t`` option to decrease the time step is
required for convergence here)::

  python3 sfepy/examples/large_deformation/gen_yeoh_tl_up_interactive.py \
    --order 2 -t 0,2,21

Change material parameters::

  python3 sfepy/examples/large_deformation/gen_yeoh_tl_up_interactive.py -m 2,1

View the results using ``sfepy-view``
-------------------------------------

Show pressure on deformed mesh (use PgDn/PgUp to jump forward/back)::

  sfepy-view --fields=p:f1:wu:p1 domain.??.vtk

Show the axial component of stress (second Piola-Kirchhoff)::

  sfepy-view --fields=stress:c0 domain.??.vtk

[1] Travis W. Hohenberger, Richard J. Windslow, Nicola M. Pugno, James J. C.
Busfield. Aconstitutive Model For Both Lowand High Strain Nonlinearities In
Highly Filled Elastomers And Implementation With User-Defined Material
Subroutines In Abaqus. Rubber Chemistry And Technology, Vol. 92, No. 4, Pp.
653-686 (2019)


.. image:: /../doc/images/gallery/large_deformation-gen_yeoh_tl_up_interactive-gen_yeoh_tl_up_comparison.png
.. image:: /../doc/images/gallery/large_deformation-gen_yeoh_tl_up_interactive.png


:download:`source code </../sfepy/examples/large_deformation/gen_yeoh_tl_up_interactive.py>`

.. literalinclude:: /../sfepy/examples/large_deformation/gen_yeoh_tl_up_interactive.py

