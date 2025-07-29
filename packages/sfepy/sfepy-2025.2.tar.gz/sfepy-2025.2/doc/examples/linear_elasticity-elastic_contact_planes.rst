.. _linear_elasticity-elastic_contact_planes:

linear_elasticity/elastic_contact_planes.py
===========================================

**Description**


Elastic contact planes simulating an indentation test.

Four contact planes bounded by polygons (triangles in this case) form a very
rigid pyramid shape simulating an indentor.

Find :math:`\ul{u}` such that:

.. math::
    \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
    + \sum_{i=1}^4 \int_{\Gamma_i} \ul{v} \cdot f^i(d(\ul{u})) \ul{n^i}
    = 0 \;,

where

.. math::
    D_{ijkl} = \mu (\delta_{ik} \delta_{jl} + \delta_{il} \delta_{jk}) +
    \lambda \ \delta_{ij} \delta_{kl}
    \;.

Notes
-----

Even though the material is linear elastic and small deformations are used, the
problem is highly nonlinear due to contacts with the planes.

Checking the tangent matrix by finite differences by setting 'check' in 'nls'
solver configuration to nonzero is rather tricky - the active contact points
must not change during the test. This can be ensured by a sufficient initial
penetration and large enough contact boundary polygons (hard!), or by tweaking
the dw_contact_plane term to mask points only by undeformed coordinates.


.. image:: /../doc/images/gallery/linear_elasticity-elastic_contact_planes.png


:download:`source code </../sfepy/examples/linear_elasticity/elastic_contact_planes.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/elastic_contact_planes.py

