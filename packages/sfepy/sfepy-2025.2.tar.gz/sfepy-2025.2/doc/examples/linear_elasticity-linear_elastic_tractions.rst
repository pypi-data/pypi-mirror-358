.. _linear_elasticity-linear_elastic_tractions:

linear_elasticity/linear_elastic_tractions.py
=============================================

**Description**


Linear elasticity with pressure traction load on a surface and constrained to
one-dimensional motion.

Find :math:`\ul{u}` such that:

.. math::
    \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
    = - \int_{\Gamma_{right}} \ul{v} \cdot \ull{\sigma} \cdot \ul{n}
    \;, \quad \forall \ul{v} \;,

where

.. math::
    D_{ijkl} = \mu (\delta_{ik} \delta_{jl}+\delta_{il} \delta_{jk}) +
    \lambda \ \delta_{ij} \delta_{kl}
    \;.

and :math:`\ull{\sigma} \cdot \ul{n} = \bar{p} \ull{I} \cdot \ul{n}`
with given traction pressure :math:`\bar{p}`.

The function :func:`verify_tractions()` is called after the solution to verify
that the inner surface tractions correspond to the load applied to the external
surface. Try running the example with different approximation orders and/or uniform refinement levels:

- the default options::

    sfepy-run sfepy/examples/linear_elasticity/linear_elastic_tractions.py -O refinement_level=0 -d approx_order=1

- refine once::

    sfepy-run sfepy/examples/linear_elasticity/linear_elastic_tractions.py -O refinement_level=1 -d approx_order=1

- use the tri-quadratic approximation (Q2)::

    sfepy-run sfepy/examples/linear_elasticity/linear_elastic_tractions.py -O refinement_level=0 -d approx_order=2


.. image:: /../doc/images/gallery/linear_elasticity-linear_elastic_tractions.png


:download:`source code </../sfepy/examples/linear_elasticity/linear_elastic_tractions.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/linear_elastic_tractions.py

