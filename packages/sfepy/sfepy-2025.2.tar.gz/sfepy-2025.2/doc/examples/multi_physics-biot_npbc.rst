.. _multi_physics-biot_npbc:

multi_physics/biot_npbc.py
==========================

**Description**


Biot problem - deformable porous medium with the no-penetration boundary
condition on a boundary region.

Find :math:`\ul{u}`, :math:`p` such that:

.. math::
    \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
    - \int_{\Omega}  p\ \alpha_{ij} e_{ij}(\ul{v})
    = 0
    \;, \quad \forall \ul{v} \;,

    \int_{\Omega} q\ \alpha_{ij} e_{ij}(\ul{u})
    + \int_{\Omega} K_{ij} \nabla_i q \nabla_j p
    = 0
    \;, \quad \forall q \;,

    \ul{u} \cdot \ul{n} = 0 \mbox{ on } \Gamma_{walls} \;,

where

.. math::
    D_{ijkl} = \mu (\delta_{ik} \delta_{jl}+\delta_{il} \delta_{jk}) +
    \lambda \ \delta_{ij} \delta_{kl}
    \;.


.. image:: /../doc/images/gallery/multi_physics-biot_npbc.png


:download:`source code </../sfepy/examples/multi_physics/biot_npbc.py>`

.. literalinclude:: /../sfepy/examples/multi_physics/biot_npbc.py

