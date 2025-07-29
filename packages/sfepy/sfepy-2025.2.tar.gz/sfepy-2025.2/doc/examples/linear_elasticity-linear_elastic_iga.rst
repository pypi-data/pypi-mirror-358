.. _linear_elasticity-linear_elastic_iga:

linear_elasticity/linear_elastic_iga.py
=======================================

**Description**


Linear elasticity solved in a single patch NURBS domain using the isogeometric
analysis (IGA) approach.

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

The domain geometry was created by::

  sfepy-mesh iga-patch -d [1,0.5,0.1] -s [11,5,3] --degrees [2,2,2] -o meshes/iga/block3d.iga

View the results using::

  sfepy-view block3d.vtk -f u:wu 1:vw


.. image:: /../doc/images/gallery/linear_elasticity-linear_elastic_iga.png


:download:`source code </../sfepy/examples/linear_elasticity/linear_elastic_iga.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/linear_elastic_iga.py

