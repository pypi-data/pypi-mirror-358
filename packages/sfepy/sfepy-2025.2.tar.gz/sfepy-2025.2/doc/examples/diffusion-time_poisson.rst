.. _diffusion-time_poisson:

diffusion/time_poisson.py
=========================

**Description**


Transient Laplace equation with non-constant initial conditions given by a
function.

Find :math:`T(t)` for :math:`t \in [0, t_{\rm final}]` such that:

.. math::
    \int_{\Omega} s \pdiff{T}{t}
    + \int_{\Omega} c \nabla s \cdot \nabla T
    = 0
    \;, \quad \forall s \;.


.. image:: /../doc/images/gallery/diffusion-time_poisson.png


:download:`source code </../sfepy/examples/diffusion/time_poisson.py>`

.. literalinclude:: /../sfepy/examples/diffusion/time_poisson.py

