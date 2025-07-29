.. _acoustics-acoustics3d:

acoustics/acoustics3d.py
========================

**Description**


Acoustic pressure distribution in 3D.

Two Laplace equations, one in :math:`\Omega_1`, other in
:math:`\Omega_2`, connected on the interface region :math:`\Gamma_{12}`
using traces of variables.

Find two complex acoustic pressures :math:`p_1`, :math:`p_2` such that:

.. math::
    \int_{\Omega} k^2 q p - \int_{\Omega} \nabla q \cdot \nabla p \\
    - i w/c \int_{\Gamma_{out}} q p
    + i w \rho/Z \int_{\Gamma_2} q (p_2 - p_1)
    + i w \rho/Z \int_{\Gamma_1}  q (p_1 - p_2) \\
    = i w \rho \int_{\Gamma_{in}} v_n q
    \;, \quad \forall q \;.


.. image:: /../doc/images/gallery/acoustics-acoustics3d_Omega_1.png
.. image:: /../doc/images/gallery/acoustics-acoustics3d_Omega_2.png


:download:`source code </../sfepy/examples/acoustics/acoustics3d.py>`

.. literalinclude:: /../sfepy/examples/acoustics/acoustics3d.py

