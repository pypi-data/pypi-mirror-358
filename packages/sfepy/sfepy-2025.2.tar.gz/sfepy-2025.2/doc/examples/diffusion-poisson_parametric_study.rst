.. _diffusion-poisson_parametric_study:

diffusion/poisson_parametric_study.py
=====================================

**Description**


Poisson equation.

This example demonstrates parametric study capabilities of Application
classes. In particular (written in the strong form):

.. math::
    c \Delta t = f \mbox{ in } \Omega,

    t = 2 \mbox{ on } \Gamma_1 \;,
    t = -2 \mbox{ on } \Gamma_2 \;,
    f = 1 \mbox{ in } \Omega_1 \;,
    f = 0 \mbox{ otherwise,}

where :math:`\Omega` is a square domain, :math:`\Omega_1 \in \Omega` is
a circular domain.

Now let's see what happens if :math:`\Omega_1` diameter changes.

Run::

  sfepy-run sfepy/examples/diffusion/poisson_parametric_study.py

and then look in 'output/r_omega1' directory, try for example::

  sfepy-view output/r_omega1/circles_in_square*.vtk -2

Remark: this simple case could be achieved also by defining
:math:`\Omega_1` by a time-dependent function and solve the static
problem as a time-dependent problem. However, the approach below is much
more general.

Find :math:`t` such that:

.. math::
    \int_{\Omega} c \nabla s \cdot \nabla t
    = 0
    \;, \quad \forall s \;.


.. image:: /../doc/images/gallery/diffusion-poisson_parametric_study.png


:download:`source code </../sfepy/examples/diffusion/poisson_parametric_study.py>`

.. literalinclude:: /../sfepy/examples/diffusion/poisson_parametric_study.py

