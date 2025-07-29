.. _linear_elasticity-linear_elastic_damping:

linear_elasticity/linear_elastic_damping.py
===========================================

**Description**


Time-dependent linear elasticity with a simple damping.

Find :math:`\ul{u}` such that:

.. math::
    \int_{\Omega} c\ \ul{v} \cdot \pdiff{\ul{u}}{t}
    + \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
    = 0
    \;, \quad \forall \ul{v} \;,

where

.. math::
    D_{ijkl} = \mu (\delta_{ik} \delta_{jl}+\delta_{il} \delta_{jk}) +
    \lambda \ \delta_{ij} \delta_{kl}
    \;.


.. image:: /../doc/images/gallery/linear_elasticity-linear_elastic_damping.png


:download:`source code </../sfepy/examples/linear_elasticity/linear_elastic_damping.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/linear_elastic_damping.py

