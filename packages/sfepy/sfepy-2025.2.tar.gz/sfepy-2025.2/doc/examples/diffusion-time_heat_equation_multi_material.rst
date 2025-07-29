.. _diffusion-time_heat_equation_multi_material:

diffusion/time_heat_equation_multi_material.py
==============================================

**Description**


Transient heat equation with time-dependent source term, three different
material domains and Newton type boundary condition loss term.

Description
-----------

This example is inspired by the Laser Powder Bed Fusion additive manufacturing
process. A laser source deposits a flux on a circular surface (a full layer of
the cylinder being built) at regular time intervals. The heat propagates into
the build plate and to the sides of the cylinder into powder which is
relatively bad at conductiong heat. Heat losses through Newton type heat
exchange occur both at the surface where the heat is being deposited and at the
bottom plate.

The PDE for this physical process implies to find :math:`T(x, t)` for :math:`x
\in \Omega, t \in [0, t_{\rm final}]` such that:

.. math::
    \left\lbrace
    \begin{aligned}
    \rho(x)c_p(x)\frac{\partial T}{\partial t}(x, t)
    = -\nabla \cdot \left( -k(x) \underline{\nabla} T(x, t) \right) &&
    \forall x \in \Omega, \forall t \in [0, T_{max}] \\
    -k \underline{\nabla} T(x, t)\cdot \underline{n}
    = q(t)+h(T-T_\infty) && \forall x \in \Gamma_{source} \\
    -k \underline{\nabla} T(x, t)\cdot \underline{n}
    = q(t)+h(T-T_\infty) && \forall x \in \Gamma_{plate} \\
    \underline{\nabla} T(x, t)\cdot \underline{n}
    = 0 && \forall x \in \Gamma \setminus(\Gamma_{source}
    \cap\Gamma_{plate})
    \end{aligned}
    \right.

The weak formulation solved using `sfepy` is to find a discretized field
:math:`T` that satisfies:

.. math::
    \begin{aligned}
    \int_\Omega\rho c_p \frac{\partial T}{\partial t}(x, t) \, s
    + \int_\Omega \underline{\nabla} s \cdot (k(x)
    \underline{\nabla}
    T) =  \int_\Gamma -k \underline{\nabla} T \cdot \underline{n} s \\
    = \int_{\Gamma_{source}} q(t)   +
    \int_{\Gamma_{source}} h(T-T_\infty)
    + \int_{\Gamma_{plate}} h(T-T_\infty)  && \forall s
    \end{aligned}

Uniform initial conditions are used as a starting point of the simulation.

Usage examples
--------------
The script can be run with::

    sfepy-run sfepy/examples/diffusion/time_heat_equation_multi_material.py

The last time-step result field can then be visualized as isosurfaces with::

    sfepy-view multi_material_cylinder_plate.119.vtk -i 10 -l

The resulting time evolution of temperatures is saved as an image file in the
output directory (heat_probe_time_evolution.png).

This script uses SI units (meters, kilograms, Joules...) except for
temperature, which is expressed in degrees Celsius.


.. image:: /../doc/images/gallery/diffusion-time_heat_equation_multi_material.png


:download:`source code </../sfepy/examples/diffusion/time_heat_equation_multi_material.py>`

.. literalinclude:: /../sfepy/examples/diffusion/time_heat_equation_multi_material.py

