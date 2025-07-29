.. _linear_elasticity-its2D_4:

linear_elasticity/its2D_4.py
============================

**Description**


Diametrically point loaded 2-D disk with postprocessing and probes. See
:ref:`sec-primer`.

1. solve the problem::

   sfepy-run sfepy/examples/linear_elasticity/its2D_4.py

2. optionally, view the results::

   sfepy-view its2D.h5 -2

3. optionally, convert results to VTK, and view again ((assumes running from
   the sfepy directory)::

   python3 sfepy/scripts/extractor.py -d its2D.h5
   sfepy-view its2D.0.vtk -2

4. probe the data::

   sfepy-probe sfepy/examples/linear_elasticity/its2D_4.py its2D.h5

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


.. image:: /../doc/images/gallery/linear_elasticity-its2D_4-its2D_0.png
.. image:: /../doc/images/gallery/linear_elasticity-its2D_4-its2D_1.png
.. image:: /../doc/images/gallery/linear_elasticity-its2D_4.png


:download:`source code </../sfepy/examples/linear_elasticity/its2D_4.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/its2D_4.py

