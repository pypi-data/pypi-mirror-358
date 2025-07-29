.. _diffusion-poisson_functions:

diffusion/poisson_functions.py
==============================

**Description**


Poisson equation with source term.

Find :math:`u` such that:

.. math::
    \int_{\Omega} c \nabla v \cdot \nabla u
    = - \int_{\Omega_L} b v = - \int_{\Omega_L} f v p
    \;, \quad \forall v \;,

where :math:`b(x) = f(x) p(x)`, :math:`p` is a given FE field and :math:`f` is
a given general function of space.

This example demonstrates use of functions for defining material parameters,
regions, parameter variables or boundary conditions. Notably, it demonstrates
the following:

1. How to define a material parameter by an arbitrary function - see the
   function :func:`get_pars()` that evaluates :math:`f(x)` in quadrature
   points.
2. How to define a known function that belongs to a given FE space (field) -
   this function, :math:`p(x)`, is defined in a FE sense by its nodal values
   only - see the function :func:`get_load_variable()`.

In order to define the load :math:`b(x)` directly, the term ``dw_dot``
should be replaced by ``dw_integrate``.


.. image:: /../doc/images/gallery/diffusion-poisson_functions.png


:download:`source code </../sfepy/examples/diffusion/poisson_functions.py>`

.. literalinclude:: /../sfepy/examples/diffusion/poisson_functions.py

