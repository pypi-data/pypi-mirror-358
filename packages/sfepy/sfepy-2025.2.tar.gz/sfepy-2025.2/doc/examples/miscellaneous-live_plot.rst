.. _miscellaneous-live_plot:

miscellaneous/live_plot.py
==========================

**Description**


Live plot demonstration.

Usage Example
-------------

- Run and plot two logs on the fly::

    python3 sfepy/examples/miscellaneous/live_plot.py --plot-log

- Run and store the two logs, plot them later::

    python3 sfepy/examples/miscellaneous/live_plot.py

    python3 sfepy/scripts/plot_logs.py live_plot.txt
    python3 sfepy/scripts/plot_logs.py live_plot2.txt


.. image:: /../doc/images/gallery/miscellaneous-live_plot-live_plot.png
.. image:: /../doc/images/gallery/miscellaneous-live_plot-live_plot2.png


:download:`source code </../sfepy/examples/miscellaneous/live_plot.py>`

.. literalinclude:: /../sfepy/examples/miscellaneous/live_plot.py

