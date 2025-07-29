.. _multi_physics-biot_npbc_lagrange:

multi_physics/biot_npbc_lagrange.py
===================================

**Description**


Biot problem - deformable porous medium with the no-penetration boundary
condition on a boundary region enforced using Lagrange multipliers.

The non-penetration condition is enforced weakly using the Lagrange
multiplier :math:`\lambda`. There is also a rigid body movement
constraint imposed on the :math:`\Gamma_{outlet}` region using the
linear combination boundary conditions.

Find :math:`\ul{u}`, :math:`p` and :math:`\lambda` such that:

.. math::
    \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
    - \int_{\Omega}  p\ \alpha_{ij} e_{ij}(\ul{v})
    + \int_{\Gamma_{walls}} \lambda \ul{n} \cdot \ul{v}
    = 0
    \;, \quad \forall \ul{v} \;,

    \int_{\Omega} q\ \alpha_{ij} e_{ij}(\ul{u})
    + \int_{\Omega} K_{ij} \nabla_i q \nabla_j p
    = 0
    \;, \quad \forall q \;,

    \int_{\Gamma_{walls}} \hat\lambda \ul{n} \cdot \ul{u}
    = 0
    \;, \quad \forall \hat\lambda \;,

    \ul{u} \cdot \ul{n} = 0 \mbox{ on } \Gamma_{walls} \;,

where

.. math::
    D_{ijkl} = \mu (\delta_{ik} \delta_{jl}+\delta_{il} \delta_{jk}) +
    \lambda \ \delta_{ij} \delta_{kl}
    \;.


.. image:: /../doc/images/gallery/multi_physics-biot_npbc_lagrange.png


:download:`source code </../sfepy/examples/multi_physics/biot_npbc_lagrange.py>`

.. literalinclude:: /../sfepy/examples/multi_physics/biot_npbc_lagrange.py

