.. _navier_stokes-stabilized_navier_stokes:

navier_stokes/stabilized_navier_stokes.py
=========================================

**Description**


Stabilized Navier-Stokes problem with grad-div, SUPG and PSPG stabilization
solved by a custom Oseen solver.

The stabilization terms are described in [1].

[1] G. Matthies and G. Lube. On streamline-diffusion methods of inf-sup stable
discretisations of the generalised Oseen problem. Number 2007-02 in Preprint
Series of Institut fuer Numerische und Angewandte Mathematik,
Georg-August-Universitaet Goettingen, 2007.

Find :math:`\ul{u}`, :math:`p` such that:

.. math::
    \begin{array}{l}
    \int_{\Omega} \nu\ \nabla \ul{v} : \nabla \ul{u}
    \int_{\Omega} ((\ul{b} \cdot \nabla) \ul{u}) \cdot \ul{v}
    - \int_{\Omega} p\ \nabla \cdot \ul{v} \\
    + \gamma \int_{\Omega} (\nabla\cdot\ul{u}) \cdot (\nabla\cdot\ul{v}) \\
    + \sum_{K \in \Ical_h}\int_{T_K} \delta_K\ ((\ul{b} \cdot \nabla)
      \ul{u})\cdot ((\ul{b} \cdot \nabla) \ul{v}) \\
    + \sum_{K \in \Ical_h}\int_{T_K} \delta_K\ \nabla p\cdot ((\ul{b} \cdot
      \nabla) \ul{v})
    = 0
    \;, \quad \forall \ul{v} \;,
    \end{array}

    \begin{array}{l}
    \int_{\Omega} q\ \nabla \cdot \ul{u} \\
    + \sum_{K \in \Ical_h}\int_{T_K} \tau_K\ ((\ul{b} \cdot \nabla) \ul{u})
      \cdot \nabla q \\
    + \sum_{K \in \Ical_h}\int_{T_K} \tau_K\ \nabla p \cdot \nabla q
    = 0
    \;, \quad \forall q \;.
    \end{array}


.. image:: /../doc/images/gallery/navier_stokes-stabilized_navier_stokes.png


:download:`source code </../sfepy/examples/navier_stokes/stabilized_navier_stokes.py>`

.. literalinclude:: /../sfepy/examples/navier_stokes/stabilized_navier_stokes.py

