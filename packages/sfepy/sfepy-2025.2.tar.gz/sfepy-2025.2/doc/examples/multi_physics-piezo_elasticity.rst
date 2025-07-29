.. _multi_physics-piezo_elasticity:

multi_physics/piezo_elasticity.py
=================================

**Description**


Piezo-elasticity problem - linear elastic material with piezoelectric
effects.

Find :math:`\ul{u}`, :math:`\phi` such that:

.. math::
    - \omega^2 \int_{Y} \rho\ \ul{v} \cdot \ul{u}
    + \int_{Y} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
    - \int_{Y_2} g_{kij}\ e_{ij}(\ul{v}) \nabla_k \phi
    = 0
    \;, \quad \forall \ul{v} \;,

    \int_{Y_2} g_{kij}\ e_{ij}(\ul{u}) \nabla_k \psi
    + \int_{Y} K_{ij} \nabla_i \psi \nabla_j \phi
    = 0
    \;, \quad \forall \psi \;,

where

.. math::
    D_{ijkl} = \mu (\delta_{ik} \delta_{jl}+\delta_{il} \delta_{jk}) +
    \lambda \ \delta_{ij} \delta_{kl}
    \;.


.. image:: /../doc/images/gallery/multi_physics-piezo_elasticity.png


:download:`source code </../sfepy/examples/multi_physics/piezo_elasticity.py>`

.. literalinclude:: /../sfepy/examples/multi_physics/piezo_elasticity.py

