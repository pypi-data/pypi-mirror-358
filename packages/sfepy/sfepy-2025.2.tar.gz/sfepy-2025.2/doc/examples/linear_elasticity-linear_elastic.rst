.. _linear_elasticity-linear_elastic:

linear_elasticity/linear_elastic.py
===================================

**Description**


Linear elasticity with given displacements.

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

This example models a cylinder that is fixed at one end while the second end
has a specified displacement of 0.01 in the x direction (this boundary
condition is named ``'Displaced'``). There is also a specified displacement of
0.005 in the z direction for points in the region labeled
``'SomewhereTop'``. This boundary condition is named
``'PerturbedSurface'``. The region ``'SomewhereTop'`` is specified as those
vertices for which::

    (z > 0.017) & (x > 0.03) & (x <  0.07)

The displacement field (three DOFs/node) in the ``'Omega region'`` is
approximated using P1 (four-node tetrahedral) finite elements. The material is
linear elastic and its properties are specified as Lamé parameters
:math:`\lambda` and :math:`\mu` (see
http://en.wikipedia.org/wiki/Lam%C3%A9_parameters)

The output is the displacement for each vertex, saved by default to
cylinder.vtk. View the results using::

  sfepy-view cylinder.vtk -f u:wu 1:vw


.. image:: /../doc/images/gallery/linear_elasticity-linear_elastic.png


:download:`source code </../sfepy/examples/linear_elasticity/linear_elastic.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/linear_elastic.py

