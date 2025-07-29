.. _diffusion-time_poisson_explicit:

diffusion/time_poisson_explicit.py
==================================

**Description**


Transient Laplace equation.

The same example as time_poisson.py, but using the short syntax of keywords,
and explicit time-stepping.

Find :math:`T(t)` for :math:`t \in [0, t_{\rm final}]` such that:

.. math::
    \int_{\Omega} s \pdiff{T}{t}
    + \int_{\Omega} c \nabla s \cdot \nabla T
    = 0
    \;, \quad \forall s \;.


.. image:: /../doc/images/gallery/diffusion-time_poisson_explicit.png


:download:`source code </../sfepy/examples/diffusion/time_poisson_explicit.py>`

.. literalinclude:: /../sfepy/examples/diffusion/time_poisson_explicit.py

