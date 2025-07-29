.. _diffusion-poisson_nonlinear_material:

diffusion/poisson_nonlinear_material.py
=======================================

**Description**


Nonlinear Poisson's equation example demonstrating the nonlinear diffusion
and nonlinear volume force terms.

The example is an adaptation of:
:ref:`diffusion-poisson_field_dependent_material`.

Find :math:`T` such that:

.. math::
   \int_{\Omega} c(T) \nabla s \cdot \nabla T + \int_{\Omega} g(T) \cdot s
    = 0
    \;, \quad \forall s \;.

where :math:`c(T)` and :math:`g(T)`  are the :math:`T` dependent coefficients.


.. image:: /../doc/images/gallery/diffusion-poisson_nonlinear_material.png


:download:`source code </../sfepy/examples/diffusion/poisson_nonlinear_material.py>`

.. literalinclude:: /../sfepy/examples/diffusion/poisson_nonlinear_material.py

