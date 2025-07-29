.. <Virtual Solvers with Automatic Fallback>
- :class:`ls.auto_direct <sfepy.solvers.auto_fallback.AutoDirect>`: The automatically selected linear direct solver.
- :class:`ls.auto_iterative <sfepy.solvers.auto_fallback.AutoIterative>`: The automatically selected linear iterative solver.
.. </Virtual Solvers with Automatic Fallback>

.. <Time-Stepping Solvers>
- :class:`ts.adaptive <sfepy.solvers.ts_solvers.AdaptiveTimeSteppingSolver>`: Implicit time stepping solver with an adaptive time step.
- :class:`ts.bathe <sfepy.solvers.ts_solvers.BatheTS>`: Solve elastodynamics problems by the Bathe method.
- :class:`ts.central_difference <sfepy.solvers.ts_solvers.CentralDifferenceTS>`: Solve elastodynamics problems by the explicit central difference method.
- :class:`ts.euler <sfepy.solvers.ts_dg_solvers.EulerStepSolver>`: Simple forward euler method
- :class:`ts.generalized_alpha <sfepy.solvers.ts_solvers.GeneralizedAlphaTS>`: Solve elastodynamics problems by the generalized :math:`\alpha` method.
- :class:`ts.multistaged <sfepy.solvers.ts_dg_solvers.DGMultiStageTSS>`: Explicit time stepping solver with multistage solve_step method
- :class:`ts.newmark <sfepy.solvers.ts_solvers.NewmarkTS>`: Solve elastodynamics problems by the Newmark method.
- :class:`ts.runge_kutta_4 <sfepy.solvers.ts_dg_solvers.RK4StepSolver>`: Classical 4th order Runge-Kutta method,
- :class:`ts.simple <sfepy.solvers.ts_solvers.SimpleTimeSteppingSolver>`: Implicit time stepping solver with a fixed time step.
- :class:`ts.stationary <sfepy.solvers.ts_solvers.StationarySolver>`: Solver for stationary problems without time stepping.
- :class:`ts.tvd_runge_kutta_3 <sfepy.solvers.ts_dg_solvers.TVDRK3StepSolver>`: 3rd order Total Variation Diminishing Runge-Kutta method
- :class:`ts.velocity_verlet <sfepy.solvers.ts_solvers.VelocityVerletTS>`: Solve elastodynamics problems by the explicit velocity-Verlet method.
.. </Time-Stepping Solvers>

.. <Time Step Controllers>
- :class:`tsc.ed_basic <sfepy.solvers.ts_controllers.ElastodynamicsBasicTSC>`: Adaptive time step I-controller for elastodynamics.
- :class:`tsc.ed_linear <sfepy.solvers.ts_controllers.ElastodynamicsLinearTSC>`: Adaptive time step controller for elastodynamics and linear problems.
- :class:`tsc.ed_pid <sfepy.solvers.ts_controllers.ElastodynamicsPIDTSC>`: Adaptive time step PID controller for elastodynamics.
- :class:`tsc.fixed <sfepy.solvers.ts_controllers.FixedTSC>`: Fixed (do-nothing) time step controller.
- :class:`tsc.time_sequence <sfepy.solvers.ts_controllers.TimesSequenceTSC>`: Given times sequence time step controller.
.. </Time Step Controllers>

.. <Nonlinear Solvers>
- :class:`nls.newton <sfepy.solvers.nls.Newton>`: Solves a nonlinear system :math:`f(x) = 0` using the Newton method.
- :class:`nls.oseen <sfepy.solvers.oseen.Oseen>`: The Oseen solver for Navier-Stokes equations.
- :class:`nls.petsc <sfepy.solvers.nls.PETScNonlinearSolver>`: Interface to PETSc SNES (Scalable Nonlinear Equations Solvers).
- :class:`nls.scipy_root <sfepy.solvers.nls.ScipyRoot>`: Interface to ``scipy.optimize.root()``.
- :class:`nls.semismooth_newton <sfepy.solvers.semismooth_newton.SemismoothNewton>`: The semi-smooth Newton method.
.. </Nonlinear Solvers>

.. <Linear Solvers>
- :class:`ls.cholesky <sfepy.solvers.ls.CholeskySolver>`: Interface to scikit-sparse.cholesky solver.
- :class:`ls.cm_pb <sfepy.solvers.ls.MultiProblem>`: Conjugate multiple problems.
- :class:`ls.mumps <sfepy.solvers.ls.MUMPSSolver>`: Interface to MUMPS solver.
- :class:`ls.petsc <sfepy.solvers.ls.PETScKrylovSolver>`: PETSc Krylov subspace solver.
- :class:`ls.pyamg <sfepy.solvers.ls.PyAMGSolver>`: Interface to PyAMG solvers.
- :class:`ls.pyamg_krylov <sfepy.solvers.ls.PyAMGKrylovSolver>`: Interface to PyAMG Krylov solvers.
- :class:`ls.pypardiso <sfepy.solvers.ls.PyPardisoSolver>`: PyPardiso direct solver.
- :class:`ls.rmm <sfepy.solvers.ls.RMMSolver>`: Special solver for explicit transient elastodynamics.
- :class:`ls.schur_mumps <sfepy.solvers.ls.SchurMumps>`: Mumps Schur complement solver.
- :class:`ls.scipy_direct <sfepy.solvers.ls.ScipyDirect>`: Direct sparse solver from SciPy.
- :class:`ls.scipy_iterative <sfepy.solvers.ls.ScipyIterative>`: Interface to SciPy iterative solvers.
- :class:`ls.scipy_superlu <sfepy.solvers.ls.ScipySuperLU>`: SuperLU - direct sparse solver from SciPy.
- :class:`ls.scipy_umfpack <sfepy.solvers.ls.ScipyUmfpack>`: UMFPACK - direct sparse solver from SciPy.
.. </Linear Solvers>

.. <Eigenvalue Problem Solvers>
- :class:`eig.matlab <sfepy.solvers.eigen.MatlabEigenvalueSolver>`: Matlab eigenvalue problem solver.
- :class:`eig.octave <sfepy.solvers.eigen.OctaveEigenvalueSolver>`: Octave eigenvalue problem solver.
- :class:`eig.primme <sfepy.solvers.eigen.PrimmeEigenvalueSolver>`: PRIMME eigenvalue problem solver.
- :class:`eig.scipy <sfepy.solvers.eigen.ScipyEigenvalueSolver>`: SciPy-based solver for both dense and sparse problems.
- :class:`eig.scipy_lobpcg <sfepy.solvers.eigen.LOBPCGEigenvalueSolver>`: SciPy-based LOBPCG solver for sparse symmetric problems.
- :class:`eig.sgscipy <sfepy.solvers.eigen.ScipySGEigenvalueSolver>`: SciPy-based solver for dense symmetric problems.
- :class:`eig.slepc <sfepy.solvers.eigen.SLEPcEigenvalueSolver>`: General SLEPc eigenvalue problem solver.
.. </Eigenvalue Problem Solvers>

.. <Quadratic Eigenvalue Problem Solvers>
- :class:`eig.qevp <sfepy.solvers.qeigen.LQuadraticEVPSolver>`: Quadratic eigenvalue problem solver based on the problem linearization.
.. </Quadratic Eigenvalue Problem Solvers>

.. <Optimization Solvers>
- :class:`nls.scipy_fmin_like <sfepy.solvers.optimize.ScipyFMinSolver>`: Interface to SciPy optimization solvers scipy.optimize.fmin_*.
- :class:`opt.fmin_sd <sfepy.solvers.optimize.FMinSteepestDescent>`: Steepest descent optimization solver.
.. </Optimization Solvers>

