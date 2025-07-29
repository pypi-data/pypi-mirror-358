.. _dg-advection_1D:

dg/advection_1D.py
==================

**Description**


Transient advection equation in 1D solved using discontinous galerkin method.

.. math:: \frac{dp}{dt} + a \cdot dp/dx = 0

    p(t,0) = p(t,1)


Usage Examples
--------------
Run::

  sfepy-run sfepy/examples/dg/advection_1D.py

To view animated results use ``sfepy/examples/dg/dg_plot_1D.py`` specifing name
of the output in ``output/`` folder, default is ``dg/advection_1D``::

  python3 sfepy/examples/dg/dg_plot_1D.py dg/advection_1D

``dg_plot_1D.py`` also accepts full and relative paths::

  python3 sfepy/examples/dg/dg_plot_1D.py output/dg/advection_1D


.. image:: /../doc/images/gallery/dg-advection_1D.png


:download:`source code </../sfepy/examples/dg/advection_1D.py>`

.. literalinclude:: /../sfepy/examples/dg/advection_1D.py

