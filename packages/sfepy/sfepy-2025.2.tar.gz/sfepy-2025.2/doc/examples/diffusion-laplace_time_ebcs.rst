.. _diffusion-laplace_time_ebcs:

diffusion/laplace_time_ebcs.py
==============================

**Description**


Example explaining how to change Dirichlet boundary conditions depending
on time. It is shown on the stationary Laplace equation for temperature,
so there is no dynamics, only the conditions change with time.

Five time steps are solved on a cube domain, with the temperature fixed
to zero on the bottom face, and set to other values on the left, right
and top faces in different time steps.

Find :math:`t` such that:

.. math::
    \int_{\Omega} c \nabla s \cdot \nabla t
    = 0
    \;, \quad \forall s \;.


.. image:: /../doc/images/gallery/diffusion-laplace_time_ebcs.png


:download:`source code </../sfepy/examples/diffusion/laplace_time_ebcs.py>`

.. literalinclude:: /../sfepy/examples/diffusion/laplace_time_ebcs.py

