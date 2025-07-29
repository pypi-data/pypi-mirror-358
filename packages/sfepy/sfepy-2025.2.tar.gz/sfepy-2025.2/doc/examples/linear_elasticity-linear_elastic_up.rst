.. _linear_elasticity-linear_elastic_up:

linear_elasticity/linear_elastic_up.py
======================================

**Description**


Nearly incompressible linear elasticity in mixed displacement-pressure
formulation with comments.

Find :math:`\ul{u}`, :math:`p` such that:

.. math::
    \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
    - \int_{\Omega} p\ \nabla \cdot \ul{v}
    = 0
    \;, \quad \forall \ul{v} \;,

    - \int_{\Omega} q\ \nabla \cdot \ul{u}
    - \int_{\Omega} \gamma q p
    = 0
    \;, \quad \forall q \;.


.. image:: /../doc/images/gallery/linear_elasticity-linear_elastic_up.png


:download:`source code </../sfepy/examples/linear_elasticity/linear_elastic_up.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/linear_elastic_up.py

