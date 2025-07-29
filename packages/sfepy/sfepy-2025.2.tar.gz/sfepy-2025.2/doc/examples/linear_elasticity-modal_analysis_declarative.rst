.. _linear_elasticity-modal_analysis_declarative:

linear_elasticity/modal_analysis_declarative.py
===============================================

**Description**


Modal analysis of a wheel set.

The first six modes are the rigid body modes because no boundary
conditions are applied.

Running the simulation::

  sfepy-run sfepy/examples/linear_elasticity/modal_analysis_declarative.py

The eigenvalues are saved to wheelset_eigs.txt and the eigenvectros to
wheelset.vtk. View the results using::

  sfepy-view wheelset.vtk -f u003:wu003:f30%:p0 1:vw:p0

The first six frequencies calculated by SfePy::

  [11.272, 11.322, 34.432, 80.711, 80.895, 93.149]

The results of modal analysis performed in Ansys::

  [11.306, 11.316, 34.486, 80.901, 81.139, 93.472]


.. image:: /../doc/images/gallery/linear_elasticity-modal_analysis_declarative.png


:download:`source code </../sfepy/examples/linear_elasticity/modal_analysis_declarative.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/modal_analysis_declarative.py

