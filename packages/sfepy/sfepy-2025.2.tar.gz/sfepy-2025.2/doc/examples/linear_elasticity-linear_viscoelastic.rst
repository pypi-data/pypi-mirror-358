.. _linear_elasticity-linear_viscoelastic:

linear_elasticity/linear_viscoelastic.py
========================================

**Description**


Linear viscoelasticity with pressure traction load on a surface and constrained
to one-dimensional motion.

The fading memory terms require an unloaded initial configuration, so the load
starts in the second time step. The load is then held for the first half of the
total time interval, and released afterwards.

This example uses exponential fading memory kernel
:math:`\Hcal_{ijkl}(t) = \Hcal_{ijkl}(0) e^{-d t}` with decay
:math:`d`. Two equation kinds are supported - 'th' and 'eth'. In 'th'
mode the tabulated kernel is linearly interpolated to required times
using :func:`interp_conv_mat()`. In 'eth' mode, the computation is exact
for exponential kernels.

Find :math:`\ul{u}` such that:

.. math::
    \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u}) \\
    + \int_{\Omega} \left [\int_0^t
    \Hcal_{ijkl}(t-\tau)\,e_{kl}(\pdiff{\ul{u}}{\tau}(\tau)) \difd{\tau}
    \right]\,e_{ij}(\ul{v}) \\
    = - \int_{\Gamma_{right}} \ul{v} \cdot \ull{\sigma} \cdot \ul{n}
    \;, \quad \forall \ul{v} \;,

where

.. math::
    D_{ijkl} = \mu (\delta_{ik} \delta_{jl}+\delta_{il} \delta_{jk}) +
    \lambda \ \delta_{ij} \delta_{kl}
    \;,

:math:`\Hcal_{ijkl}(0)` has the same structure as :math:`D_{ijkl}` and
:math:`\ull{\sigma} \cdot \ul{n} = \bar{p} \ull{I} \cdot \ul{n}` with
given traction pressure :math:`\bar{p}`.

Notes
-----

Because this example is run also as a test, it uses by default very few time
steps. Try changing that.

Visualization
-------------

The output file is assumed to be 'block.h5' in the working directory. Change it
appropriately for your situation.

Deforming mesh
^^^^^^^^^^^^^^

Try to run the following::

  sfepy-view block.h5 -s 20 -f u:wu:f1e0:p0 1:vw:p0 total_stress:p1

to see the results.

Time history plots
^^^^^^^^^^^^^^^^^^

Run the following::

  python3 sfepy/examples/linear_elasticity/linear_viscoelastic.py -h
  python3 sfepy/examples/linear_elasticity/linear_viscoelastic.py block.h5

Try comparing 'th' and 'eth' versions, e.g., for n_step = 201, and f_n_step =
51. There is a visible notch on viscous stress curves in the 'th' mode, as the
fading memory kernel is cut off before it goes close enough to zero.


.. image:: /../doc/images/gallery/linear_elasticity-linear_viscoelastic.png


:download:`source code </../sfepy/examples/linear_elasticity/linear_viscoelastic.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/linear_viscoelastic.py

