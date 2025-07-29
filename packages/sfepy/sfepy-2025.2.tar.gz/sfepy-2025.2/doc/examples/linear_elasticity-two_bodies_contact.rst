.. _linear_elasticity-two_bodies_contact:

linear_elasticity/two_bodies_contact.py
=======================================

**Description**


Contact of two elastic bodies with a penalty function for enforcing the contact
constraints.

Find :math:`\ul{u}` such that:

.. math::
    \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
    + \int_{\Gamma_{c}} \varepsilon_N \langle g_N(\ul{u}) \rangle \ul{n} \ul{v}
    = 0
    \;, \quad \forall \ul{v} \;,

where :math:`\varepsilon_N \langle g_N(\ul{u}) \rangle` is the penalty
function, :math:`\varepsilon_N` is the normal penalty parameter, :math:`\langle
g_N(\ul{u}) \rangle` are the Macaulay's brackets of the gap function
:math:`g_N(\ul{u})` and

.. math::
    D_{ijkl} = \mu (\delta_{ik} \delta_{jl}+\delta_{il} \delta_{jk}) +
    \lambda \ \delta_{ij} \delta_{kl}
    \;.

This example also demonstrates use of an experimental contact term based on the
IPC Toolkit [1].

[1] https://github.com/ipc-sim/ipc-toolkit

Usage examples::

  # Check regions and EBC nodes.
  sfepy-run sfepy/examples/linear_elasticity/two_bodies_contact.py --save-regions-as-groups --save-ebc-nodes --solve-not

  sfepy-view two_bodies_ebc_nodes.vtk
  sfepy-view two_bodies_regions.h5

  # Run with default parameters and view results.
  sfepy-run sfepy/examples/linear_elasticity/two_bodies_contact.py

  sfepy-view output/contact/two_bodies.h5
  sfepy-view output/contact/two_bodies.h5 -f u:wu:f1:p0 1:vw:wu:f1:p0

  # Plot the nonlinear solver convergence.
  python3 sfepy/scripts/plot_logs.py output/contact/log.txt

  # Run with default parameters and IPC toolkit, view results.
  sfepy-run sfepy/examples/linear_elasticity/two_bodies_contact.py -d "contact='ipc'"
  sfepy-view output/contact/two_bodies.h5 -f u:wu:f1:p0 1:vw:wu:f1:p0

  # Plot the IPC contact parameters evolution.
  python3 sfepy/scripts/plot_logs.py output/contact/clog.txt


.. image:: /../doc/images/gallery/linear_elasticity-two_bodies_contact.png


:download:`source code </../sfepy/examples/linear_elasticity/two_bodies_contact.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/two_bodies_contact.py

