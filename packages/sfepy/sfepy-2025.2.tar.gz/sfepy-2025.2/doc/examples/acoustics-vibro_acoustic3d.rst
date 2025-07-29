.. _acoustics-vibro_acoustic3d:

acoustics/vibro_acoustic3d.py
=============================

**Description**


Vibro-acoustic problem

3D acoustic domain with 2D perforated deforming interface.

Problem definition - find :math:`p` (acoustic pressure),
:math:`g` (transversal acoustic velocity),
:math:`w` (plate deflection) and :math:`\ul{\theta}` (rotation) such that:

.. math::
    c^2 \int_{\Omega} \nabla q \cdot \nabla p
    - \omega^2 \int_{\Omega} q p
    + i \omega c \int_{\Gamma_{in}} q p
    + i \omega c \int_{\Gamma_{out}} q p
    - i \omega c^2 \int_{\Gamma_0} (q^+ - q^-) g
    = 2i \omega c \int_{\Gamma_{in}} q \bar{p}
    \;, \quad \forall q \;,

    - i \omega \int_{\Gamma_0} f (p^+ - p^-)
    - \omega^2 \int_{\Gamma_0} F f g
    + \omega^2 \int_{\Gamma_0} C f w
    = 0
    \;, \quad \forall f \;,

    \omega^2 \int_{\Gamma_0} C z g
    - \omega^2 \int_{\Gamma_0} S z w
    + \int_{\Gamma_0} \nabla z \cdot \ull{G} \cdot \nabla w
    - \int_{\Gamma_0} \ul{\theta} \cdot \ull{G} \cdot \nabla z
    = 0
    \;, \quad \forall z \;,

    - \omega^2 \int_{\Gamma_0} R\, \ul{\nu} \cdot \ul{\theta}
    + \int_{\Gamma_0} D_{ijkl} e_{ij}(\ul{\nu}) e_{kl}(\ul{\theta})
    - \int_{\Gamma_0} \ul{\nu} \cdot \ull{G} \cdot \nabla w
    + \int_{\Gamma_0} \ul{\nu} \cdot \ull{G} \cdot \ul{\theta}
    = 0
    \;, \quad \forall \ul{\nu} \;,


.. image:: /../doc/images/gallery/acoustics-vibro_acoustic3d_Gamma0.png
.. image:: /../doc/images/gallery/acoustics-vibro_acoustic3d_Omega1.png
.. image:: /../doc/images/gallery/acoustics-vibro_acoustic3d_Omega2.png


:download:`source code </../sfepy/examples/acoustics/vibro_acoustic3d.py>`

.. literalinclude:: /../sfepy/examples/acoustics/vibro_acoustic3d.py

