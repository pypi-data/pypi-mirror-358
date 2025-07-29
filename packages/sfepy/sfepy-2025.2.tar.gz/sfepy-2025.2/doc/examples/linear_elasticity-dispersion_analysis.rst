.. _linear_elasticity-dispersion_analysis:

linear_elasticity/dispersion_analysis.py
========================================

**Description**


Dispersion analysis of a heterogeneous finite scale periodic cell.

The periodic cell mesh has to contain two subdomains Y1 (with the cell ids 1),
Y2 (with the cell ids 2), so that different material properties can be defined
in each of the subdomains (see ``--pars`` option). The command line parameters
can be given in any consistent unit set, for example the basic SI units. The
``--unit-multipliers`` option can be used to rescale the input units to ones
more suitable to the simulation, for example to prevent having different
matrix blocks with large differences of matrix entries magnitudes. The results
are then in the rescaled units.

Usage Examples
--------------

Default material parameters, a square periodic cell with a spherical inclusion,
logs also standard pressure dilatation and shear waves, no eigenvectors::

  python sfepy/examples/linear_elasticity/dispersion_analysis.py meshes/2d/special/circle_in_square.mesh --log-std-waves --eigs-only

As above, with custom eigenvalue solver parameters, and different number of
eigenvalues, mesh size and units used in the calculation::

  python sfepy/examples/linear_elasticity/dispersion_analysis.py meshes/2d/special/circle_in_square.mesh --solver-conf="kind='eig.scipy', method='eigsh', tol=1e-10, maxiter=1000, which='LM', sigma=0" --log-std-waves -n 5 --range=0,640,101 --mode=omega --unit-multipliers=1e-6,1e-2,1e-3 --mesh-size=1e-2 --eigs-only

Default material parameters, a square periodic cell with a square inclusion,
and a very small mesh to allow comparing the omega and kappa modes (full matrix
solver required!)::

  python sfepy/examples/linear_elasticity/dispersion_analysis.py meshes/2d/square_2m.mesh --solver-conf="kind='eig.scipy', method='eigh'" --log-std-waves -n 10 --range=0,640,101 --mesh-size=1e-2 --mode=omega --eigs-only --no-legends --unit-multipliers=1e-6,1e-2,1e-3 -o output/omega

  python sfepy/examples/linear_elasticity/dispersion_analysis.py meshes/2d/square_2m.mesh --solver-conf="kind='eig.qevp', method='companion', mode='inverted', solver={kind='eig.scipy', method='eig'}" --log-std-waves -n 500 --range=0,4000000,1001 --mesh-size=1e-2 --mode=kappa --eigs-only --no-legends --unit-multipliers=1e-6,1e-2,1e-3 -o output/kappa

View/compare the resulting logs::

  python script/plot_logs.py output/omega/frequencies.txt --no-legends -g 1 -o mode-omega.png
  python script/plot_logs.py output/kappa/wave-numbers.txt --no-legends -o mode-kappa.png
  python script/plot_logs.py output/kappa/wave-numbers.txt --no-legends --swap-axes -o mode-kappa-t.png

In contrast to the heterogeneous square periodic cell, a homogeneous
square periodic cell (the region Y2 is empty)::

  python sfepy/examples/linear_elasticity/dispersion_analysis.py meshes/2d/square_1m.mesh --solver-conf="kind='eig.scipy', method='eigh'" --log-std-waves -n 10 --range=0,640,101 --mesh-size=1e-2 --mode=omega --eigs-only --no-legends --unit-multipliers=1e-6,1e-2,1e-3 -o output/omega-h

  python script/plot_logs.py output/omega-h/frequencies.txt --no-legends -g 1 -o mode-omega-h.png

Use the Brillouin stepper::

  python sfepy/examples/linear_elasticity/dispersion_analysis.py meshes/2d/special/circle_in_square.mesh --log-std-waves -n=60 --eigs-only --no-legends --stepper=brillouin

  python script/plot_logs.py output/frequencies.txt -g 0 --rc="'font.size':14, 'lines.linewidth' : 3, 'lines.markersize' : 4" -o brillouin-stepper-kappas.png

  python script/plot_logs.py output/frequencies.txt -g 1 --no-legends --rc="'font.size':14, 'lines.linewidth' : 3, 'lines.markersize' : 4" -o brillouin-stepper-omegas.png

Additional arguments can be passed to the problem configuration's
:func:`define()` function using the ``--define-kwargs`` option. In this file,
only the mesh vertex separation parameter `mesh_eps` can be used::

  python sfepy/examples/linear_elasticity/dispersion_analysis.py meshes/2d/special/circle_in_square.mesh --log-std-waves --eigs-only --define-kwargs="mesh_eps=1e-10" --save-regions


.. image:: /../doc/images/gallery/linear_elasticity-dispersion_analysis-frequencies.png


:download:`source code </../sfepy/examples/linear_elasticity/dispersion_analysis.py>`

.. literalinclude:: /../sfepy/examples/linear_elasticity/dispersion_analysis.py

