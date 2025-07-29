.. _acoustics-acoustics:

acoustics/acoustics.py
======================

**Description**


Acoustic pressure distribution.

This example shows how to solve a problem in complex numbers, note the
'accoustic_pressure' field definition.

Find :math:`p` such that:

.. math::
    c^2 \int_{\Omega} \nabla q \cdot \nabla p
    - w^2 \int_{\Omega} q p
    - i w c \int_{\Gamma_{out}} q p
    = i w c^2 \rho v_n \int_{\Gamma_{in}} q
    \;, \quad \forall q \;.


.. image:: /../doc/images/gallery/acoustics-acoustics.png


:download:`source code </../sfepy/examples/acoustics/acoustics.py>`

.. literalinclude:: /../sfepy/examples/acoustics/acoustics.py

