.. _acoustics-helmholtz_apartment:

acoustics/helmholtz_apartment.py
================================

**Description**


A script demonstrating the solution of the scalar Helmholtz equation for a
situation inspired by the physical problem of WiFi propagation in an apartment.

The example is an adaptation of the project found here:
https://bthierry.pages.math.cnrs.fr/course-fem/projet/2017-2018/

The boundary conditions are defined as perfect radiation conditions, meaning
that on the boundary waves will radiate outside.

The PDE for this physical process implies to find :math:`E(x, t)` for :math:`x
\in \Omega` such that:

.. math::
    \left\lbrace
    \begin{aligned}
      \Delta E+ k^2 n(x)^2 E = f_s && \forall x \in \Omega \\
      \partial_n E(x)-ikn(x)E(x)=0 && \forall x \text{ on } \partial \Omega
    \end{aligned}
    \right.


Usage
-----

The mesh of the appartement and the different material ids can be visualized
with the following::

    sfepy-view meshes/2d/helmholtz_apartment.vtk -e -2

The example is run from the top level directory as::

    sfepy-run sfepy/examples/acoustics/helmholtz_apartment.py

The result of the computation can be visualized as follows::

    sfepy-view helmholtz_apartment.vtk --color-map=seismic -f imag.E:wimag.E:f10%:p0 --camera-position="-5.14968,-7.27948,7.08783,-0.463265,-0.23358,-0.350532,0.160127,0.664287,0.730124"


.. image:: /../doc/images/gallery/acoustics-helmholtz_apartment.png


:download:`source code </../sfepy/examples/acoustics/helmholtz_apartment.py>`

.. literalinclude:: /../sfepy/examples/acoustics/helmholtz_apartment.py

