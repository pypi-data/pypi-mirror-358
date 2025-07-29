.. _linear_elasticity-elastic_shifted_periodic:

linear_elasticity/elastic_shifted_periodic.py
=============================================

**Description**


Linear elasticity with linear combination constraints and periodic boundary
conditions.

The linear combination constraints are used to apply periodic boundary
conditions with a shift in the second axis direction.

Find :math:`\ul{u}` such that:

.. math::
    \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
    = - \int_{\Gamma_{bottom}} \ul{v} \cdot \ull{\sigma} \cdot \ul{n}
    \;, \quad \forall \ul{v} \;,

    \ul{u} = 0 \mbox{ on } \Gamma_{left} \;,

    u_1 = u_2 = 0 \mbox{ on } \Gamma_{right} \;,

    \ul{u}(\ul{x}) = \ul{u}(\ul{y}) \mbox{ for }
    \ul{x} \in \Gamma_{bottom}, \ul{y} \in \Gamma_{top},
    \ul{y} = P_1(\ul{x}) \;,

    \ul{u}(\ul{x}) = \ul{u}(\ul{y}) + a(\ul{y}) \mbox{ for }
    \ul{x} \in \Gamma_{near}, \ul{y} \in \Gamma_{far},
    \ul{y} = P_2(\ul{x}) \;,

where

.. math::
    D_{ijkl} = \mu (\delta_{ik} \delta_{jl}+\delta_{il} \delta_{jk}) +
    \lambda \ \delta_{ij} \delta_{kl}
    \;,

and the traction :math:`\ull{\sigma} \cdot \ul{n} = \bar{p} \ull{I} \cdot
\ul{n}` is given in terms of traction pressure :math:`\bar{p}`. The function
:math:`a(\ul{y})` is given (the shift), :math:`P_1` and :math:`P_2` are the
periodic coordinate mappings.

View the results using::

  sfepy-view block.vtk -f u:wu:f2.0:p0 1:vw:p0 von_mises_stress:p1


.. image:: /../doc/images/gallery/linear_elasticity-elastic_shifted_periodic.png


:download:`source code </../sfepy/examples/linear_elasticity/elastic_shifted_periodic.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/elastic_shifted_periodic.py

