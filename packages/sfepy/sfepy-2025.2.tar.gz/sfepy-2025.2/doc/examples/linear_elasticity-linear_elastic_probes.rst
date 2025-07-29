.. _linear_elasticity-linear_elastic_probes:

linear_elasticity/linear_elastic_probes.py
==========================================

**Description**


This example shows how to use the post_process_hook to probe the output data.

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


.. image:: /../doc/images/gallery/linear_elasticity-linear_elastic_probes-cylinder_probe_line.png
.. image:: /../doc/images/gallery/linear_elasticity-linear_elastic_probes-cylinder_probe_circle.png
.. image:: /../doc/images/gallery/linear_elasticity-linear_elastic_probes-cylinder_probe_ray.png
.. image:: /../doc/images/gallery/linear_elasticity-linear_elastic_probes.png


:download:`source code </../sfepy/examples/linear_elasticity/linear_elastic_probes.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/linear_elastic_probes.py

