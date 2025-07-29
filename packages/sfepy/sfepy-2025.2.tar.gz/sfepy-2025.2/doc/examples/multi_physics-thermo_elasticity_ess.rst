.. _multi_physics-thermo_elasticity_ess:

multi_physics/thermo_elasticity_ess.py
======================================

**Description**


Thermo-elasticity with a computed temperature demonstrating equation sequence
solver.

Uses `dw_biot` term with an isotropic coefficient for thermo-elastic coupling.

The equation sequence solver (``'ess'`` in ``solvers``) automatically solves
first the temperature distribution and then the elasticity problem with the
already computed temperature.

Find :math:`\ul{u}`, :math:`T` such that:

.. math::
    \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
    - \int_{\Omega}  (T - T_0)\ \alpha_{ij} e_{ij}(\ul{v})
    = 0
    \;, \quad \forall \ul{v} \;,

    \int_{\Omega} \nabla s \cdot \nabla T
    = 0
    \;, \quad \forall s \;.

where

.. math::
    D_{ijkl} = \mu (\delta_{ik} \delta_{jl}+\delta_{il} \delta_{jk}) +
    \lambda \ \delta_{ij} \delta_{kl}
    \;, \\

    \alpha_{ij} = (3 \lambda + 2 \mu) \alpha \delta_{ij} \;,

:math:`T_0` is the background temperature and :math:`\alpha` is the thermal
expansion coefficient.

Notes
-----
The gallery image was produced by (plus proper view settings)::

  sfepy-view block.vtk -f T:p1 u:wu:f1000:p0 u:vw:p0


.. image:: /../doc/images/gallery/multi_physics-thermo_elasticity_ess.png


:download:`source code </../sfepy/examples/multi_physics/thermo_elasticity_ess.py>`

.. literalinclude:: /../sfepy/examples/multi_physics/thermo_elasticity_ess.py

