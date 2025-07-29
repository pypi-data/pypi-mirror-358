.. _linear_elasticity-material_nonlinearity:

linear_elasticity/material_nonlinearity.py
==========================================

**Description**


Example demonstrating how a linear elastic term can be used to solve an
elasticity problem with a material nonlinearity.

.. math::
    \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
    = 0
    \;, \quad \forall \ul{v} \;,

where

.. math::
    D_{ijkl} = \mu (\delta_{ik} \delta_{jl}+\delta_{il} \delta_{jk}) +
    \lambda \ \delta_{ij} \delta_{kl}
    \;.


.. image:: /../doc/images/gallery/linear_elasticity-material_nonlinearity.png


:download:`source code </../sfepy/examples/linear_elasticity/material_nonlinearity.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/material_nonlinearity.py

