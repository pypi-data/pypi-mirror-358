.. _linear_elasticity-elastodynamic_identification:

linear_elasticity/elastodynamic_identification.py
=================================================

**Description**


The linear elastodynamics solution of an iron plate impact problem with
identification of material parameters from simulated measurement data.

Find :math:`\ul{u}` such that:

.. math::
    \int_{\Omega} \rho \ul{v} \pddiff{\ul{u}}{t}
    + \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
    = 0
    \;, \quad \forall \ul{v} \;,

where

.. math::
    D_{ijkl} = \mu (\delta_{ik} \delta_{jl}+\delta_{il} \delta_{jk}) +
    \lambda \ \delta_{ij} \delta_{kl} \;,

    \lambda = E \nu / ((1 + \nu)(1 - 2\nu)), \\ \mu = E / 2(1 + \nu)
    \;.

Usage Examples
--------------

- Run without the identification::

    sfepy-run sfepy/examples/linear_elasticity/elastodynamic_identification.py
    sfepy-view output/edi/user_block.h5 -f u:wu:f1e3:p0 1:vw:p0

- Get help::

    python3 sfepy/examples/linear_elasticity/elastodynamic_identification.py -h

- Run the identification with default parameters, show live plot of
  convergence and launch ipython shell after the computation::

    python3 sfepy/examples/linear_elasticity/elastodynamic_identification.py --plot-log --shell

  Result figures are in output/edi, if not changed using --output-dir option.

- Check the Jacobian matrix by finite differences::

    python3 sfepy/examples/linear_elasticity/elastodynamic_identification.py --opt-conf=max_nfev=1 --check-jac --shell

- Identify also the damping parameters (zero by default)::

    python3 sfepy/examples/linear_elasticity/elastodynamic_identification.py --par-names=young,poisson,density,alpha,beta --plot-log --shell

See also :ref:`linear_elasticity-elastodynamic`.


.. image:: /../doc/images/gallery/linear_elasticity-elastodynamic_identification-res00004.png
.. image:: /../doc/images/gallery/linear_elasticity-elastodynamic_identification-pars.png


:download:`source code </../sfepy/examples/linear_elasticity/elastodynamic_identification.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/elastodynamic_identification.py

