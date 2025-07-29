.. _linear_elasticity-elastic_contact_sphere:

linear_elasticity/elastic_contact_sphere.py
===========================================

**Description**


Elastic contact sphere simulating an indentation test.

Find :math:`\ul{u}` such that:

.. math::
    \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
    + \int_{\Gamma} \ul{v} \cdot f(d(\ul{u})) \ul{n}(\ul{u})
    = 0 \;,

where

.. math::
    D_{ijkl} = \mu (\delta_{ik} \delta_{jl} + \delta_{il} \delta_{jk}) +
    \lambda \ \delta_{ij} \delta_{kl}
    \;.

Notes
-----

Even though the material is linear elastic and small deformations are used, the
problem is highly nonlinear due to contacts with the sphere. See also
elastic_contact_planes.py example.


.. image:: /../doc/images/gallery/linear_elasticity-elastic_contact_sphere.png


:download:`source code </../sfepy/examples/linear_elasticity/elastic_contact_sphere.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/elastic_contact_sphere.py

