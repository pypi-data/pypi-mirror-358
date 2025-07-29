.. _linear_elasticity-seismic_load:

linear_elasticity/seismic_load.py
=================================

**Description**


The linear elastodynamics of an elastic body loaded by a given base motion.

Find :math:`\ul{u}` such that:

.. math::
    \int_{\Omega} \rho \ul{v} \pddiff{\ul{u}}{t}
    + \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
    = 0
    \;, \quad \forall \ul{v} \;, \\
    u_1(t) =  10^{-5} \sin(\omega t) \sin(k x_2)
    \mbox{ on } \Gamma_\mathrm{Seismic} \;, \\
    \omega = c_L k \;,

where :math:`c_L` is the longitudinal wave propagation speed, :math:`k = 2 \pi
/ L`,` :math:`L` is the length of the domain and

.. math::
    D_{ijkl} = \mu (\delta_{ik} \delta_{jl}+\delta_{il} \delta_{jk}) +
    \lambda \ \delta_{ij} \delta_{kl}
    \;.

See :ref:`linear_elasticity-elastodynamic` example for notes on elastodynamics
solvers.

Usage Examples
--------------

Run with the default settings (the Newmark method, 2D problem, results stored
in ``output/seismic/``)::

  sfepy-run sfepy/examples/linear_elasticity/seismic_load.py -o tsn

View the resulting displacements on the deforming mesh (10x magnified)::

  sfepy-view output/seismic/tsn.h5 -2 -f u:wu:f10:p0 1:vw:p0

Use the central difference explicit method with the reciprocal mass matrix
algorithm [1]_ and view the resulting stress waves::

  sfepy-run sfepy/examples/linear_elasticity/seismic_load.py  -d "dims=(5e-3, 5e-3), shape=(51, 51), tss_name=tscd, ls_name=lsrmm, mass_beta=0.5, mass_lumping=row_sum, fast_rmm=True, save_times=all" -o tscd

  sfepy-view output/seismic/tscd.h5 -2 -f cauchy_stress:wu:f10:p0 1:vw:p0

.. [1] González, J.A., Kolman, R., Cho, S.S., Felippa, C.A., Park, K.C., 2018.
       Inverse mass matrix via the method of localized Lagrange multipliers.
       International Journal for Numerical Methods in Engineering 113, 277–295.
       https://doi.org/10.1002/nme.5613


.. image:: /../doc/images/gallery/linear_elasticity-seismic_load.png


:download:`source code </../sfepy/examples/linear_elasticity/seismic_load.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/seismic_load.py

