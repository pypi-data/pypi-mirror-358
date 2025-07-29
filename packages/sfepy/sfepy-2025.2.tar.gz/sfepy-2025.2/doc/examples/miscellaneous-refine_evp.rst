.. _miscellaneous-refine_evp:

miscellaneous/refine_evp.py
===========================

**Description**


Plot the convergence of eigenvalues (or corresponding frequencies) of an
eigenvalue problem to an analytical solution, when applying the uniform
mesh refinement.

Uses the PRIMME eigenvalue solver by default (``pip install primme``).

Usage Examples
--------------

- Run without the convergence analysis, use the spectral element method (SEM)
  basis of order 5::

    sfepy-run sfepy/examples/miscellaneous/refine_evp.py -d order=5,basis=sem

- Get help::

    python3 sfepy/examples/miscellaneous/refine_evp.py -h

- Plot the convergence of the smallest eigenvalue of the Laplace Dirichlet
  problem::

    python3 sfepy/examples/miscellaneous/refine_evp.py --max-order=5 --max-refine=2

- Plot the convergence of the smallest frequency of the 1D elastic bar
  vibration problem, show relative errors::

    python3 sfepy/examples/miscellaneous/refine_evp.py --max-order=5 --max-refine=2 --kind=elasticity --transform=freqs --relative

- Using the 1D elastic bar vibration problem, compare the SEM results with the
  FEM + row-sum mass matrix lumping. Plot also the sparsity patterns of the
  mass (M) and stiffness (K) matrices::

    python3 sfepy/examples/miscellaneous/refine_evp.py --max-order=5 --max-refine=2 --evps=primme --kind=elasticity-lumping --transform=freqs --relative --beta=1 --mass-lumping='row_sum' --sparsity

    python3 sfepy/examples/miscellaneous/refine_evp.py --max-order=5 --max-refine=2 --evps=primme --kind=elasticity --basis=sem --transform=freqs --relative --beta=0 --mass-lumping='none' --sparsity


.. image:: /../doc/images/gallery/miscellaneous-refine_evp-h-refinement-0-laplace-lagrange-primme-none-a.png


:download:`source code </../sfepy/examples/miscellaneous/refine_evp.py>`

.. literalinclude:: /../sfepy/examples/miscellaneous/refine_evp.py

