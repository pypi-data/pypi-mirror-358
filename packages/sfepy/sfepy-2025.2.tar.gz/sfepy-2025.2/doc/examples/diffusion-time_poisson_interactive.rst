.. _diffusion-time_poisson_interactive:

diffusion/time_poisson_interactive.py
=====================================

**Description**


Transient Laplace equation (heat equation) with non-constant initial conditions
given by a function, using commands for interactive use.

The script allows setting various simulation parameters, namely:

- the diffusivity coefficient
- the max. initial condition value
- temperature field approximation order
- uniform mesh refinement

The example shows also how to probe the results.

In the SfePy top-level directory the following command can be used to get usage
information::

  python sfepy/examples/diffusion/time_poisson_interactive.py -h


.. image:: /../doc/images/gallery/diffusion-time_poisson_interactive-time_poisson_interactive_probe_04.png
.. image:: /../doc/images/gallery/diffusion-time_poisson_interactive.png


:download:`source code </../sfepy/examples/diffusion/time_poisson_interactive.py>`

.. literalinclude:: /../sfepy/examples/diffusion/time_poisson_interactive.py

