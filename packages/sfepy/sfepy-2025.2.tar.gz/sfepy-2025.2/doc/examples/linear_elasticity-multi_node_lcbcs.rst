.. _linear_elasticity-multi_node_lcbcs:

linear_elasticity/multi_node_lcbcs.py
=====================================

**Description**


Linear elasticity with multi node linear combination constraints.

Find :math:`\ul{u}` such that:

.. math::
    \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
    = 0
    \;, \quad \forall \ul{v} \;,

where

.. math::
    D_{ijkl} = \mu (\delta_{ik} \delta_{jl}+\delta_{il} \delta_{jk}) +
    \lambda \ \delta_{ij} \delta_{kl}
    \;.

The hanging nodes in ``'Dependent_nodes'`` region are bounded
to the nodes in ``'Independent_nodes'`` region using the ``lcbcs`
(``multi_node_combination``) conditions

View the results using::

  sfepy-view hanging_nodes.vtk -f u:wu:e -2


.. image:: /../doc/images/gallery/linear_elasticity-multi_node_lcbcs.png


:download:`source code </../sfepy/examples/linear_elasticity/multi_node_lcbcs.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/multi_node_lcbcs.py

