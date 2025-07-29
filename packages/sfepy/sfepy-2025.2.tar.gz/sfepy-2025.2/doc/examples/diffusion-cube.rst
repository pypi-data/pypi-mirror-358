.. _diffusion-cube:

diffusion/cube.py
=================

**Description**


Laplace equation (e.g. temperature distribution) on a cube geometry with
different boundary condition values on the cube sides. This example was
used to create the SfePy logo.

Find :math:`T` such that:

.. math::
    \int_{\Omega} c \nabla s \cdot \nabla T
    = 0
    \;, \quad \forall s \;.


.. image:: /../doc/images/gallery/diffusion-cube.png


:download:`source code </../sfepy/examples/diffusion/cube.py>`

.. literalinclude:: /../sfepy/examples/diffusion/cube.py

