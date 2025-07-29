.. _linear_elasticity-prestress_fibres:

linear_elasticity/prestress_fibres.py
=====================================

**Description**


Linear elasticity with a given prestress in one subdomain and a (pre)strain
fibre reinforcement in the other.

Find :math:`\ul{u}` such that:

.. math::
    \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
    + \int_{\Omega_1} \sigma_{ij} e_{ij}(\ul{v})
    + \int_{\Omega_2} D^f_{ijkl} e_{ij}(\ul{v}) \left(d_k d_l\right)
    = 0
    \;, \quad \forall \ul{v} \;,

where

.. math::
    D_{ijkl} = \mu (\delta_{ik} \delta_{jl}+\delta_{il} \delta_{jk}) +
    \lambda \ \delta_{ij} \delta_{kl}
    \;.

The stiffness of fibres :math:`D^f_{ijkl}` is defined analogously,
:math:`\ul{d}` is the unit fibre direction vector and :math:`\sigma_{ij}` is
the prestress.

Visualization
-------------

Use the following to see the deformed structure with 10x magnified
displacements::

  sfepy-view block.vtk -f u:wu:f5 1:vw


.. image:: /../doc/images/gallery/linear_elasticity-prestress_fibres.png


:download:`source code </../sfepy/examples/linear_elasticity/prestress_fibres.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/prestress_fibres.py

