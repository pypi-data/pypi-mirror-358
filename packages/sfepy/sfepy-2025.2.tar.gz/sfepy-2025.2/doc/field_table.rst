.. _field_table:

.. tabularcolumns:: |l|l|l|p{0.55\linewidth}|
.. list-table:: Fields
   :widths: 5 15 15 65
   :header-rows: 1

   * - space
     - basis
     - region kind
     - description
   * - H1
     - bernstein
     - :class:`cell <sfepy.discrete.fem.fields_positive.H1BernsteinVolumeField>`, :class:`facet <sfepy.discrete.fem.fields_positive.H1BernsteinSurfaceField>`
     - Bernstein basis approximation with positive-only basis function values.
   * - H1
     - iga
     - :class:`cell <sfepy.discrete.iga.fields.IGField>`
     - Bezier extraction based NURBS approximation for isogeometric analysis.
   * - H1
     - lagrange
     - :class:`cell <sfepy.discrete.fem.fields_nodal.H1NodalVolumeField>`, :class:`facet <sfepy.discrete.fem.fields_nodal.H1NodalSurfaceField>`
     - Lagrange basis nodal approximation.
   * - H1
     - lagrange_discontinuous
     - :class:`cell <sfepy.discrete.fem.fields_nodal.H1DiscontinuousField>`
     - The C0 constant-per-cell approximation.
   * - H1
     - lobatto
     - :class:`cell <sfepy.discrete.fem.fields_hierarchic.H1HierarchicVolumeField>`
     - Hierarchical basis approximation with Lobatto polynomials.
   * - H1
     - sem
     - :class:`cell <sfepy.discrete.fem.fields_nodal.H1SEMVolumeField>`, :class:`facet <sfepy.discrete.fem.fields_nodal.H1SEMSurfaceField>`
     - Spectral element method approximation.
   * - H1
     - serendipity
     - :class:`cell <sfepy.discrete.fem.fields_nodal.H1SNodalVolumeField>`, :class:`facet <sfepy.discrete.fem.fields_nodal.H1SNodalSurfaceField>`
     - Lagrange basis nodal serendipity approximation with order <= 3.
   * - H1
     - shell10x
     - :class:`cell <sfepy.discrete.structural.fields.Shell10XField>`
     - The approximation for the shell10x element.
   * - L2
     - constant
     - :class:`cell <sfepy.discrete.fem.fields_l2.L2ConstantVolumeField>`, :class:`facet <sfepy.discrete.fem.fields_l2.L2ConstantSurfaceField>`
     - The L2 constant-in-a-region approximation.
   * - DG
     - legendre_discontinuous
     - :class:`cell <sfepy.discrete.dg.fields.DGField>`
     - Discontinuous Galerkin method approximation with Legendre basis.

