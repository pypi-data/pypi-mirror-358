.. _diffusion-laplace_coupling_lcbcs:

diffusion/laplace_coupling_lcbcs.py
===================================

**Description**


Two Laplace equations with multiple linear combination constraints.

The two equations are coupled by a periodic-like boundary condition constraint
with a shift, given as a non-homogeneous linear combination boundary condition.

Find :math:`u` such that:

.. math::
    \int_{\Omega_1} \nabla v_1 \cdot \nabla u_1
    = 0
    \;, \quad \forall v_1 \;,

    \int_{\Omega_2} \nabla v_2 \cdot \nabla u_2
    = 0
    \;, \quad \forall v_2 \;,

    u_1 = 0 \mbox{ on } \Gamma_{bottom} \;,

    u_2 = 1 \mbox{ on } \Gamma_{top} \;,

    u_1(\ul{x}) = u_2(\ul{x}) + a(\ul{x}) \mbox{ for }
    \ul{x} \in \Gamma = \bar\Omega_1 \cap \bar\Omega_2

    u_1(\ul{x}) = u_1(\ul{y}) + b(\ul{y}) \mbox{ for }
    \ul{x} \in \Gamma_{left}, \ul{y} \in \Gamma_{right}, \ul{y} = P(\ul{x}) \;,

    u_1 = c_{11} \mbox{ in } \Omega_{m11} \subset \Omega_1 \;,

    u_1 = c_{12} \mbox{ in } \Omega_{m12} \subset \Omega_1 \;,

    u_2 = c_2 \mbox{ in } \Omega_{m2} \subset \Omega_2 \;,

where :math:`a(\ul{x})`, :math:`b(\ul{y})` are given functions (shifts),
:math:`P` is the periodic coordinate mapping and :math:`c_{11}`, :math:`c_{12}`
and :math:`c_2` are unknown constant values - the unknown DOFs in
:math:`\Omega_{m11}`, :math:`\Omega_{m12}` and :math:`\Omega_{m2}` are replaced
by the integral mean values.

View the results using::

  sfepy-view square_quad.vtk -f u1:wu1:p0 1:vw:p0 u2:wu2:p1 1:vw:p1


.. image:: /../doc/images/gallery/diffusion-laplace_coupling_lcbcs.png


:download:`source code </../sfepy/examples/diffusion/laplace_coupling_lcbcs.py>`

.. literalinclude:: /../sfepy/examples/diffusion/laplace_coupling_lcbcs.py

