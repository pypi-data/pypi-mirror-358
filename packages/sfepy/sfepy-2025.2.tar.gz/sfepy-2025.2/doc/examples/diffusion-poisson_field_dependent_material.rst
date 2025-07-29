.. _diffusion-poisson_field_dependent_material:

diffusion/poisson_field_dependent_material.py
=============================================

**Description**


Laplace equation with a field-dependent material parameter.

Find :math:`T(t)` for :math:`t \in [0, t_{\rm final}]` such that:

.. math::
   \int_{\Omega} c(T) \nabla s \cdot \nabla T
    = 0
    \;, \quad \forall s \;.

where :math:`c(T)` is the :math:`T` dependent diffusion coefficient.
Each iteration calculates :math:`T` and adjusts :math:`c(T)`.


.. image:: /../doc/images/gallery/diffusion-poisson_field_dependent_material.png


:download:`source code </../sfepy/examples/diffusion/poisson_field_dependent_material.py>`

.. literalinclude:: /../sfepy/examples/diffusion/poisson_field_dependent_material.py

