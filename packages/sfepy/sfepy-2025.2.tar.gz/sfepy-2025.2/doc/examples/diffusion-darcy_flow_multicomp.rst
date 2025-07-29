.. _diffusion-darcy_flow_multicomp:

diffusion/darcy_flow_multicomp.py
=================================

**Description**


Each of the two equations describes a flow in one compartment of a porous
medium. The equations are based on the Darcy flow and the i-th compartment is
defined in :math:`\Omega_{i}`.

.. math::
    \int_{\Omega_{i}} K^{i} \nabla p^{i} \cdot \nabla q^{i}+\int_{\Omega_{i}}
    \sum_{j} \bar{G}\alpha_{k} \left( p^{i}-p^{j} \right)q^{i}
    = \int_{\Omega_{i}} f^{i} q^{i},
.. math::
    \forall q^{i} \in Q^{i}, \quad i,j=1,2 \quad \mbox{and} \quad i\neq j,

where :math:`K^{i}` is the local permeability of the i-th compartment,
:math:`\bar{G}\alpha_{k} = G^{i}_{j}` is the perfusion coefficient
related to the compartments :math:`i` and :math:`j`, :math:`f^i` are
sources or sinks which represent the external flow into the i-th
compartment and :math:`p^{i}` is the pressure in the i-th compartment.


.. image:: /../doc/images/gallery/diffusion-darcy_flow_multicomp.png


:download:`source code </../sfepy/examples/diffusion/darcy_flow_multicomp.py>`

.. literalinclude:: /../sfepy/examples/diffusion/darcy_flow_multicomp.py

