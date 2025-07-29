.. _multi_physics-thermo_elasticity:

multi_physics/thermo_elasticity.py
==================================

**Description**


Thermo-elasticity with a given temperature distribution.

Uses `dw_biot` term with an isotropic coefficient for thermo-elastic coupling.

For given body temperature :math:`T` and background temperature
:math:`T_0` find :math:`\ul{u}` such that:

.. math::
    \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
    - \int_{\Omega}  (T - T_0)\ \alpha_{ij} e_{ij}(\ul{v})
    = 0
    \;, \quad \forall \ul{v} \;,

where

.. math::
    D_{ijkl} = \mu (\delta_{ik} \delta_{jl}+\delta_{il} \delta_{jk}) +
    \lambda \ \delta_{ij} \delta_{kl}
    \;, \\

    \alpha_{ij} = (3 \lambda + 2 \mu) \alpha \delta_{ij}

and :math:`\alpha` is the thermal expansion coefficient.


.. image:: /../doc/images/gallery/multi_physics-thermo_elasticity.png


:download:`source code </../sfepy/examples/multi_physics/thermo_elasticity.py>`

.. literalinclude:: /../sfepy/examples/multi_physics/thermo_elasticity.py

