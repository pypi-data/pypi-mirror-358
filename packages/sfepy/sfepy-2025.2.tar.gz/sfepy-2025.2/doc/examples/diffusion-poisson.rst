.. _diffusion-poisson:

diffusion/poisson.py
====================

**Description**


Laplace equation using the long syntax of keywords.

See the tutorial section :ref:`poisson-example-tutorial` for a detailed
explanation. See :ref:`diffusion-poisson_short_syntax` for the short syntax
version.

Find :math:`t` such that:

.. math::
    \int_{\Omega} c \nabla s \cdot \nabla t
    = 0
    \;, \quad \forall s \;.


.. image:: /../doc/images/gallery/diffusion-poisson.png


:download:`source code </../sfepy/examples/diffusion/poisson.py>`

.. literalinclude:: /../sfepy/examples/diffusion/poisson.py

