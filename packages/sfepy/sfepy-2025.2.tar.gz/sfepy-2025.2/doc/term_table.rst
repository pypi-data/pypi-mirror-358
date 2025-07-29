.. _term_table_basic:

.. raw:: latex

   \newpage
Table of basic terms
""""""""""""""""""""

.. tabularcolumns:: |p{0.15\linewidth}|p{0.10\linewidth}|p{0.6\linewidth}|p{0.15\linewidth}|
.. list-table:: Basic terms
   :widths: 15 10 60 15
   :header-rows: 1
   :class: longtable

   * - name/class
     - arguments
     - definition
     - examples
   * - dw_advect_div_free

       :class:`AdvectDivFreeTerm <sfepy.terms.terms_diffusion.AdvectDivFreeTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} \nabla \cdot (\ul{y} p) q = \int_{\Omega}
           (\underbrace{(\nabla \cdot \ul{y})}_{\equiv 0} + \ul{y} \cdot
           \nabla) p) q
     - :ref:`tim.adv.dif <diffusion-time_advection_diffusion>`
   * - dw_bc_newton

       :class:`BCNewtonTerm <sfepy.terms.terms_dot.BCNewtonTerm>`
     - ``<material_1>``, ``<material_2>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Gamma} \alpha q (p - p_{\rm outer})
     - :ref:`tim.hea.equ.mul.mat <diffusion-time_heat_equation_multi_material>`
   * - dw_biot

       :class:`BiotTerm <sfepy.terms.terms_biot.BiotTerm>`
     - ``<material>``, ``<virtual/param_v>``, ``<state/param_s>``

       ``<material>``, ``<state>``, ``<virtual>``
     - .. math::
            \int_{\Omega} p\ \alpha_{ij} e_{ij}(\ul{v}) \mbox{ , }
           \int_{\Omega} q\ \alpha_{ij} e_{ij}(\ul{u})
     - :ref:`bio.npb.lag <multi_physics-biot_npbc_lagrange>`, :ref:`the.ela.ess <multi_physics-thermo_elasticity_ess>`, :ref:`bio.npb <multi_physics-biot_npbc>`, :ref:`bio.sho.syn <multi_physics-biot_short_syntax>`, :ref:`bio <multi_physics-biot>`, :ref:`the.ela <multi_physics-thermo_elasticity>`
   * - ev_biot_stress

       :class:`BiotStressTerm <sfepy.terms.terms_biot.BiotStressTerm>`
     - ``<material>``, ``<parameter>``
     - .. math::
            - \int_{\Omega} \alpha_{ij} p
     - 
   * - ev_cauchy_strain

       :class:`CauchyStrainTerm <sfepy.terms.terms_elastic.CauchyStrainTerm>`
     - ``<parameter>``
     - .. math::
            \int_{\cal{D}} \ull{e}(\ul{w})
     - 
   * - ev_cauchy_stress

       :class:`CauchyStressTerm <sfepy.terms.terms_elastic.CauchyStressTerm>`
     - ``<material>``, ``<parameter>``
     - .. math::
            \int_{\cal{D}} D_{ijkl} e_{kl}(\ul{w})
     - 
   * - dw_contact

       :class:`ContactTerm <sfepy.terms.terms_contact.ContactTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Gamma_{c}} \varepsilon_N \langle g_N(\ul{u})
           \rangle \ul{n} \ul{v}
     - :ref:`two.bod.con <linear_elasticity-two_bodies_contact>`
   * - dw_contact_ipc

       :class:`ContactIPCTerm <sfepy.terms.terms_contact.ContactIPCTerm>`
     - ``<material_m>``, ``<material_k>``, ``<material_d>``, ``<material_p>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Gamma_{c}} \sum_{k \in C} \nabla b(d_k, \ul{u})
     - 
   * - dw_contact_plane

       :class:`ContactPlaneTerm <sfepy.terms.terms_surface.ContactPlaneTerm>`
     - ``<material_f>``, ``<material_n>``, ``<material_a>``, ``<material_b>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Gamma} \ul{v} \cdot f(d(\ul{u})) \ul{n}
     - :ref:`ela.con.pla <linear_elasticity-elastic_contact_planes>`
   * - dw_contact_sphere

       :class:`ContactSphereTerm <sfepy.terms.terms_surface.ContactSphereTerm>`
     - ``<material_f>``, ``<material_c>``, ``<material_r>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Gamma} \ul{v} \cdot f(d(\ul{u})) \ul{n}(\ul{u})
     - :ref:`ela.con.sph <linear_elasticity-elastic_contact_sphere>`
   * - dw_convect

       :class:`ConvectTerm <sfepy.terms.terms_navier_stokes.ConvectTerm>`
     - ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} ((\ul{u} \cdot \nabla) \ul{u}) \cdot \ul{v}
     - :ref:`nav.sto.iga <navier_stokes-navier_stokes2d_iga>`, :ref:`nav.sto <navier_stokes-navier_stokes2d>`, :ref:`nav.sto <navier_stokes-navier_stokes>`
   * - dw_convect_v_grad_s

       :class:`ConvectVGradSTerm <sfepy.terms.terms_diffusion.ConvectVGradSTerm>`
     - ``<virtual>``, ``<state_v>``, ``<state_s>``
     - .. math::
            \int_{\Omega} q (\ul{u} \cdot \nabla p)
     - :ref:`poi.fun <diffusion-poisson_functions>`
   * - ev_def_grad

       :class:`DeformationGradientTerm <sfepy.terms.terms_hyperelastic_base.DeformationGradientTerm>`
     - ``<parameter>``
     - .. math::
            \ull{F} = \pdiff{\ul{x}}{\ul{X}}|_{qp} = \ull{I} +
           \pdiff{\ul{u}}{\ul{X}}|_{qp} \;, \\ \ul{x} = \ul{X} + \ul{u} \;, J
           = \det{(\ull{F})}
     - 
   * - dw_dg_advect_laxfrie_flux

       :class:`AdvectionDGFluxTerm <sfepy.terms.terms_dg.AdvectionDGFluxTerm>`
     - ``<opt_material>``, ``<material_advelo>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\partial{T_K}} \ul{n} \cdot \ul{f}^{*} (p_{in},
           p_{out})q

       where
           

       .. math::
            \ul{f}^{*}(p_{in}, p_{out}) = \ul{a} \frac{p_{in} +
           p_{out}}{2} + (1 - \alpha) \ul{n} C \frac{ p_{in} - p_{out}}{2},
     - :ref:`adv.1D <dg-advection_1D>`, :ref:`adv.2D <dg-advection_2D>`, :ref:`adv.dif.2D <dg-advection_diffusion_2D>`
   * - dw_dg_diffusion_flux

       :class:`DiffusionDGFluxTerm <sfepy.terms.terms_dg.DiffusionDGFluxTerm>`
     - ``<material>``, ``<state>``, ``<virtual>``

       ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\partial{T_K}} D \langle \nabla p \rangle [q] \mbox{
           , } \int_{\partial{T_K}} D \langle \nabla q \rangle [p]

       where
           

       .. math::
            \langle \nabla \phi \rangle = \frac{\nabla\phi_{in} +
           \nabla\phi_{out}}{2}

       .. math::
            [\phi] = \phi_{in} - \phi_{out}
     - :ref:`lap.2D <dg-laplace_2D>`, :ref:`bur.2D <dg-burgers_2D>`, :ref:`adv.dif.2D <dg-advection_diffusion_2D>`
   * - dw_dg_interior_penalty

       :class:`DiffusionInteriorPenaltyTerm <sfepy.terms.terms_dg.DiffusionInteriorPenaltyTerm>`
     - ``<material>``, ``<material_Cw>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\partial{T_K}} \bar{D} C_w
           \frac{Ord^2}{d(\partial{T_K})}[p][q]

       where
           

       .. math::
            [\phi] = \phi_{in} - \phi_{out}
     - :ref:`lap.2D <dg-laplace_2D>`, :ref:`bur.2D <dg-burgers_2D>`, :ref:`adv.dif.2D <dg-advection_diffusion_2D>`
   * - dw_dg_nonlinear_laxfrie_flux

       :class:`NonlinearHyperbolicDGFluxTerm <sfepy.terms.terms_dg.NonlinearHyperbolicDGFluxTerm>`
     - ``<opt_material>``, ``<fun>``, ``<fun_d>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\partial{T_K}} \ul{n} \cdot f^{*} (p_{in}, p_{out})q

       where
           

       .. math::
            \ul{f}^{*}(p_{in}, p_{out}) = \frac{\ul{f}(p_{in}) +
           \ul{f}(p_{out})}{2} + (1 - \alpha) \ul{n} C \frac{ p_{in} -
           p_{out}}{2},
     - :ref:`bur.2D <dg-burgers_2D>`
   * - dw_diffusion

       :class:`DiffusionTerm <sfepy.terms.terms_diffusion.DiffusionTerm>`
     - ``<material>``, ``<virtual/param_1>``, ``<state/param_2>``
     - .. math::
            \int_{\Omega} K_{ij} \nabla_i q \nabla_j p
     - :ref:`pie.ela <multi_physics-piezo_elasticity>`, :ref:`poi.neu <diffusion-poisson_neumann>`, :ref:`pie.ela <multi_physics-piezo_elastodynamic>`, :ref:`bio.npb.lag <multi_physics-biot_npbc_lagrange>`, :ref:`bio.npb <multi_physics-biot_npbc>`, :ref:`bio.sho.syn <multi_physics-biot_short_syntax>`, :ref:`vib.aco <acoustics-vibro_acoustic3d>`, :ref:`bio <multi_physics-biot>`, :ref:`dar.flo.mul <diffusion-darcy_flow_multicomp>`
   * - dw_diffusion_coupling

       :class:`DiffusionCoupling <sfepy.terms.terms_diffusion.DiffusionCoupling>`
     - ``<material>``, ``<virtual/param_1>``, ``<state/param_2>``

       ``<material>``, ``<state>``, ``<virtual>``
     - .. math::
            \int_{\Omega} p K_{j} \nabla_j q \mbox{ , } \int_{\Omega}
           q K_{j} \nabla_j p
     - 
   * - dw_diffusion_r

       :class:`DiffusionRTerm <sfepy.terms.terms_diffusion.DiffusionRTerm>`
     - ``<material>``, ``<virtual>``
     - .. math::
            \int_{\Omega} K_{j} \nabla_j q
     - 
   * - ev_diffusion_velocity

       :class:`DiffusionVelocityTerm <sfepy.terms.terms_diffusion.DiffusionVelocityTerm>`
     - ``<material>``, ``<parameter>``
     - .. math::
            - \int_{\cal{D}} K_{ij} \nabla_j p
     - 
   * - ev_div

       :class:`DivTerm <sfepy.terms.terms_navier_stokes.DivTerm>`
     - ``<opt_material>``, ``<parameter>``
     - .. math::
            \int_{\cal{D}} \nabla \cdot \ul{u} \mbox { , }
           \int_{\cal{D}} c \nabla \cdot \ul{u}
     - 
   * - dw_div

       :class:`DivOperatorTerm <sfepy.terms.terms_navier_stokes.DivOperatorTerm>`
     - ``<opt_material>``, ``<virtual>``
     - .. math::
            \int_{\Omega} \nabla \cdot \ul{v} \mbox { or }
           \int_{\Omega} c \nabla \cdot \ul{v}
     - 
   * - dw_div_grad

       :class:`DivGradTerm <sfepy.terms.terms_navier_stokes.DivGradTerm>`
     - ``<opt_material>``, ``<virtual/param_1>``, ``<state/param_2>``
     - .. math::
            \int_{\Omega} \nu\ \nabla \ul{v} : \nabla \ul{u} \mbox{ ,
           } \int_{\Omega} \nabla \ul{v} : \nabla \ul{u}
     - :ref:`sto.sli.bc <navier_stokes-stokes_slip_bc>`, :ref:`sto <navier_stokes-stokes>`, :ref:`nav.sto.iga <navier_stokes-navier_stokes2d_iga>`, :ref:`nav.sto <navier_stokes-navier_stokes2d>`, :ref:`sta.nav.sto <navier_stokes-stabilized_navier_stokes>`, :ref:`nav.sto <navier_stokes-navier_stokes>`
   * - dw_dot

       :class:`DotProductTerm <sfepy.terms.terms_dot.DotProductTerm>`
     - ``<opt_material>``, ``<virtual/param_1>``, ``<state/param_2>``
     - .. math::
            \int_{\cal{D}} q p \mbox{ , } \int_{\cal{D}} \ul{v} \cdot
           \ul{u}\\ \int_\Gamma \ul{v} \cdot \ul{n} p \mbox{ , } \int_\Gamma
           q \ul{n} \cdot \ul{u} \mbox{ , }\\ \int_{\cal{D}} c q p \mbox{ , }
           \int_{\cal{D}} c \ul{v} \cdot \ul{u} \mbox{ , } \int_{\cal{D}}
           \ul{v} \cdot \ull{c} \cdot \ul{u}
     - :ref:`adv.1D <dg-advection_1D>`, :ref:`wel <quantum-well>`, :ref:`lin.ela.dam <linear_elasticity-linear_elastic_damping>`, :ref:`sto.sli.bc <navier_stokes-stokes_slip_bc>`, :ref:`vib.aco <acoustics-vibro_acoustic3d>`, :ref:`tim.hea.equ.mul.mat <diffusion-time_heat_equation_multi_material>`, :ref:`poi.per.bou.con <diffusion-poisson_periodic_boundary_condition>`, :ref:`hel.apa <acoustics-helmholtz_apartment>`, :ref:`aco <acoustics-acoustics3d>`, :ref:`pie.ela <multi_physics-piezo_elasticity>`, :ref:`tim.poi <diffusion-time_poisson>`, :ref:`bal <large_deformation-balloon>`, :ref:`pie.ela <multi_physics-piezo_elastodynamic>`, :ref:`osc <quantum-oscillator>`, :ref:`bor <quantum-boron>`, :ref:`adv.2D <dg-advection_2D>`, :ref:`tim.adv.dif <diffusion-time_advection_diffusion>`, :ref:`hyd <quantum-hydrogen>`, :ref:`mod.ana.dec <linear_elasticity-modal_analysis_declarative>`, :ref:`lin.ela.up <linear_elasticity-linear_elastic_up>`, :ref:`tim.poi.exp <diffusion-time_poisson_explicit>`, :ref:`bur.2D <dg-burgers_2D>`, :ref:`ref.evp <miscellaneous-refine_evp>`, :ref:`poi.fun <diffusion-poisson_functions>`, :ref:`the.ele <multi_physics-thermal_electric>`, :ref:`aco <acoustics-acoustics>`, :ref:`dar.flo.mul <diffusion-darcy_flow_multicomp>`
   * - dw_elastic_wave

       :class:`ElasticWaveTerm <sfepy.terms.terms_elastic.ElasticWaveTerm>`
     - ``<material_1>``, ``<material_2>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} D_{ijkl}\ g_{ij}(\ul{v}) g_{kl}(\ul{u})
     - 
   * - dw_elastic_wave_cauchy

       :class:`ElasticWaveCauchyTerm <sfepy.terms.terms_elastic.ElasticWaveCauchyTerm>`
     - ``<material_1>``, ``<material_2>``, ``<virtual>``, ``<state>``

       ``<material_1>``, ``<material_2>``, ``<state>``, ``<virtual>``
     - .. math::
            \int_{\Omega} D_{ijkl}\ g_{ij}(\ul{v}) e_{kl}(\ul{u})\\
           \int_{\Omega} D_{ijkl}\ g_{ij}(\ul{u}) e_{kl}(\ul{v})
     - 
   * - dw_electric_source

       :class:`ElectricSourceTerm <sfepy.terms.terms_electric.ElectricSourceTerm>`
     - ``<material>``, ``<virtual>``, ``<parameter>``
     - .. math::
            \int_{\Omega} c s (\nabla \phi)^2
     - :ref:`the.ele <multi_physics-thermal_electric>`
   * - ev_grad

       :class:`GradTerm <sfepy.terms.terms_navier_stokes.GradTerm>`
     - ``<opt_material>``, ``<parameter>``
     - .. math::
            \int_{\cal{D}} \nabla p \mbox{ or } \int_{\cal{D}} \nabla
           \ul{u}\\ \int_{\cal{D}} c \nabla p \mbox{ or } \int_{\cal{D}} c
           \nabla \ul{u}
     - 
   * - dw_integrate

       :class:`IntegrateOperatorTerm <sfepy.terms.terms_basic.IntegrateOperatorTerm>`
     - ``<opt_material>``, ``<virtual>``
     - .. math::
            \int_{\cal{D}} q \mbox{ or } \int_{\cal{D}} c q
     - :ref:`aco <acoustics-acoustics3d>`, :ref:`poi.neu <diffusion-poisson_neumann>`, :ref:`tim.hea.equ.mul.mat <diffusion-time_heat_equation_multi_material>`, :ref:`dar.flo.mul <diffusion-darcy_flow_multicomp>`, :ref:`vib.aco <acoustics-vibro_acoustic3d>`, :ref:`aco <acoustics-acoustics>`, :ref:`hel.apa <acoustics-helmholtz_apartment>`, :ref:`poi.per.bou.con <diffusion-poisson_periodic_boundary_condition>`
   * - ev_integrate

       :class:`IntegrateTerm <sfepy.terms.terms_basic.IntegrateTerm>`
     - ``<opt_material>``, ``<parameter>``
     - .. math::
            \int_{\cal{D}} y \mbox{ , } \int_{\cal{D}} \ul{y} \mbox{ ,
           } \int_\Gamma \ul{y} \cdot \ul{n}\\ \int_{\cal{D}} c y \mbox{ , }
           \int_{\cal{D}} c \ul{y} \mbox{ , } \int_\Gamma c \ul{y} \cdot
           \ul{n} \mbox{ flux }
     - 
   * - ev_integrate_mat

       :class:`IntegrateMatTerm <sfepy.terms.terms_basic.IntegrateMatTerm>`
     - ``<material>``, ``<parameter>``
     - .. math::
            \int_{\cal{D}} c
     - 
   * - dw_jump

       :class:`SurfaceJumpTerm <sfepy.terms.terms_surface.SurfaceJumpTerm>`
     - ``<opt_material>``, ``<virtual>``, ``<state_1>``, ``<state_2>``
     - .. math::
            \int_{\Gamma} c\, q (p_1 - p_2)
     - :ref:`aco <acoustics-acoustics3d>`
   * - dw_laplace

       :class:`LaplaceTerm <sfepy.terms.terms_diffusion.LaplaceTerm>`
     - ``<opt_material>``, ``<virtual/param_1>``, ``<state/param_2>``
     - .. math::
            \int_{\Omega} c \nabla q \cdot \nabla p
     - :ref:`lap.cou.lcb <diffusion-laplace_coupling_lcbcs>`, :ref:`wel <quantum-well>`, :ref:`lap.flu.2d <diffusion-laplace_fluid_2d>`, :ref:`sto.sli.bc <navier_stokes-stokes_slip_bc>`, :ref:`sin <diffusion-sinbc>`, :ref:`vib.aco <acoustics-vibro_acoustic3d>`, :ref:`poi.iga <diffusion-poisson_iga>`, :ref:`lap.1d <diffusion-laplace_1d>`, :ref:`tim.hea.equ.mul.mat <diffusion-time_heat_equation_multi_material>`, :ref:`adv.dif.2D <dg-advection_diffusion_2D>`, :ref:`hel.apa <acoustics-helmholtz_apartment>`, :ref:`poi.per.bou.con <diffusion-poisson_periodic_boundary_condition>`, :ref:`aco <acoustics-acoustics3d>`, :ref:`tim.poi <diffusion-time_poisson>`, :ref:`osc <quantum-oscillator>`, :ref:`cub <diffusion-cube>`, :ref:`bor <quantum-boron>`, :ref:`lap.tim.ebc <diffusion-laplace_time_ebcs>`, :ref:`tim.adv.dif <diffusion-time_advection_diffusion>`, :ref:`poi.par.stu <diffusion-poisson_parametric_study>`, :ref:`poi.sho.syn <diffusion-poisson_short_syntax>`, :ref:`hyd <quantum-hydrogen>`, :ref:`poi.fie.dep.mat <diffusion-poisson_field_dependent_material>`, :ref:`poi <diffusion-poisson>`, :ref:`tim.poi.exp <diffusion-time_poisson_explicit>`, :ref:`bur.2D <dg-burgers_2D>`, :ref:`ref.evp <miscellaneous-refine_evp>`, :ref:`lap.2D <dg-laplace_2D>`, :ref:`the.ela.ess <multi_physics-thermo_elasticity_ess>`, :ref:`poi.fun <diffusion-poisson_functions>`, :ref:`the.ele <multi_physics-thermal_electric>`, :ref:`aco <acoustics-acoustics>`
   * - dw_lin_convect

       :class:`LinearConvectTerm <sfepy.terms.terms_navier_stokes.LinearConvectTerm>`
     - ``<virtual>``, ``<parameter>``, ``<state>``
     - .. math::
            \int_{\Omega} ((\ul{w} \cdot \nabla) \ul{u}) \cdot \ul{v}

       .. math::
            ((\ul{w} \cdot \nabla) \ul{u})|_{qp}
     - :ref:`sta.nav.sto <navier_stokes-stabilized_navier_stokes>`
   * - dw_lin_convect2

       :class:`LinearConvect2Term <sfepy.terms.terms_navier_stokes.LinearConvect2Term>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} ((\ul{c} \cdot \nabla) \ul{u}) \cdot \ul{v}

       .. math::
            ((\ul{c} \cdot \nabla) \ul{u})|_{qp}
     - 
   * - dw_lin_dspring

       :class:`LinearDSpringTerm <sfepy.terms.terms_elastic.LinearDSpringTerm>`
     - ``<opt_material>``, ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            f^{(i)}_k = -f^{(j)}_k = K_{kl} (u^{(j)}_l - u^{(i)}_l)\\
           \quad \forall \mbox{ elements } T_K^{i,j}\\ \mbox{ in a region
           connecting nodes } i, j
     - 
   * - dw_lin_dspring_rot

       :class:`LinearDRotSpringTerm <sfepy.terms.terms_elastic.LinearDRotSpringTerm>`
     - ``<opt_material>``, ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            f^{(i)}_k = -f^{(j)}_k = K_{kl} (u^{(j)}_l - u^{(i)}_l)\\
           \quad \forall \mbox{ elements } T_K^{i,j}\\ \mbox{ in a region
           connecting nodes } i, j
     - :ref:`mul.poi.con <linear_elasticity-multi_point_constraints>`
   * - dw_lin_elastic

       :class:`LinearElasticTerm <sfepy.terms.terms_elastic.LinearElasticTerm>`
     - ``<material>``, ``<virtual/param_1>``, ``<state/param_2>``
     - .. math::
            \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
     - :ref:`com.ela.mat <large_deformation-compare_elastic_materials>`, :ref:`sei.loa <linear_elasticity-seismic_load>`, :ref:`bio.npb.lag <multi_physics-biot_npbc_lagrange>`, :ref:`pie.ela.mac <multi_physics-piezo_elasticity_macro>`, :ref:`ela.con.pla <linear_elasticity-elastic_contact_planes>`, :ref:`bio <multi_physics-biot>`, :ref:`lin.ela.dam <linear_elasticity-linear_elastic_damping>`, :ref:`its.4 <linear_elasticity-its2D_4>`, :ref:`ela.con.sph <linear_elasticity-elastic_contact_sphere>`, :ref:`pre.fib <linear_elasticity-prestress_fibres>`, :ref:`wed.mes <linear_elasticity-wedge_mesh>`, :ref:`nod.lcb <linear_elasticity-nodal_lcbcs>`, :ref:`two.bod.con <linear_elasticity-two_bodies_contact>`, :ref:`its.2 <linear_elasticity-its2D_2>`, :ref:`its.3 <linear_elasticity-its2D_3>`, :ref:`bio.npb <multi_physics-biot_npbc>`, :ref:`lin.ela.iga <linear_elasticity-linear_elastic_iga>`, :ref:`mul.poi.con <linear_elasticity-multi_point_constraints>`, :ref:`lin.vis <linear_elasticity-linear_viscoelastic>`, :ref:`vib.aco <acoustics-vibro_acoustic3d>`, :ref:`the.ela <multi_physics-thermo_elasticity>`, :ref:`pie.ela <multi_physics-piezo_elasticity>`, :ref:`pie.ela <multi_physics-piezo_elastodynamic>`, :ref:`its.1 <linear_elasticity-its2D_1>`, :ref:`lin.ela.tra <linear_elasticity-linear_elastic_tractions>`, :ref:`bio.sho.syn <multi_physics-biot_short_syntax>`, :ref:`mod.ana.dec <linear_elasticity-modal_analysis_declarative>`, :ref:`lin.ela.mM <homogenization-linear_elastic_mM>`, :ref:`mat.non <linear_elasticity-material_nonlinearity>`, :ref:`ela <linear_elasticity-elastodynamic>`, :ref:`lin.ela.up <linear_elasticity-linear_elastic_up>`, :ref:`mix.mes <linear_elasticity-mixed_mesh>`, :ref:`the.ela.ess <multi_physics-thermo_elasticity_ess>`, :ref:`lin.ela <linear_elasticity-linear_elastic>`, :ref:`mul.nod.lcb <linear_elasticity-multi_node_lcbcs>`, :ref:`lin.ela.opt <homogenization-linear_elasticity_opt>`, :ref:`ela.shi.per <linear_elasticity-elastic_shifted_periodic>`, :ref:`tru.bri <linear_elasticity-truss_bridge3d>`
   * - dw_lin_elastic_iso

       :class:`LinearElasticIsotropicTerm <sfepy.terms.terms_elastic.LinearElasticIsotropicTerm>`
     - ``<material_1>``, ``<material_2>``, ``<virtual/param_1>``, ``<state/param_2>``
     - .. math::
            \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})\\
           \mbox{ with } \\ D_{ijkl} = \mu (\delta_{ik}
           \delta_{jl}+\delta_{il} \delta_{jk}) + \lambda \ \delta_{ij}
           \delta_{kl}
     - 
   * - dw_lin_elastic_l_ad

       :class:`LinearElasticLADTerm <sfepy.terms.terms_jax.LinearElasticLADTerm>`
     - ``<material_1>``, ``<material_2>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})\\
           \mbox{ with } \\ D_{ijkl} = \mu (\delta_{ik}
           \delta_{jl}+\delta_{il} \delta_{jk}) + \lambda \ \delta_{ij}
           \delta_{kl}
     - 
   * - dw_lin_elastic_yp_ad

       :class:`LinearElasticYPADTerm <sfepy.terms.terms_jax.LinearElasticYPADTerm>`
     - ``<material_1>``, ``<material_2>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})\\
           \mbox{ with } \\ D_{ijkl} = \mu (\delta_{ik}
           \delta_{jl}+\delta_{il} \delta_{jk}) + \lambda \ \delta_{ij}
           \delta_{kl}, \\ \mbox{ where } \\ \lambda = E \nu / ((1 + \nu)(1 -
           2\nu)), \\ \mu = E / 2(1 + \nu)
     - :ref:`ela.ide <linear_elasticity-elastodynamic_identification>`
   * - dw_lin_prestress

       :class:`LinearPrestressTerm <sfepy.terms.terms_elastic.LinearPrestressTerm>`
     - ``<material>``, ``<virtual/param>``
     - .. math::
            \int_{\Omega} \sigma_{ij} e_{ij}(\ul{v})
     - :ref:`non.hyp.mM <homogenization-nonlinear_hyperelastic_mM>`, :ref:`pre.fib <linear_elasticity-prestress_fibres>`, :ref:`pie.ela.mac <multi_physics-piezo_elasticity_macro>`
   * - dw_lin_spring

       :class:`LinearSpringTerm <sfepy.terms.terms_elastic.LinearSpringTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \ul{f}^{(i)} = - \ul{f}^{(j)} = k (\ul{u}^{(j)} -
           \ul{u}^{(i)})\\ \quad \forall \mbox{ elements } T_K^{i,j}\\ \mbox{
           in a region connecting nodes } i, j
     - 
   * - dw_lin_strain_fib

       :class:`LinearStrainFiberTerm <sfepy.terms.terms_elastic.LinearStrainFiberTerm>`
     - ``<material_1>``, ``<material_2>``, ``<virtual>``
     - .. math::
            \int_{\Omega} D_{ijkl} e_{ij}(\ul{v}) \left(d_k d_l\right)
     - :ref:`pre.fib <linear_elasticity-prestress_fibres>`
   * - dw_lin_truss

       :class:`LinearTrussTerm <sfepy.terms.terms_elastic.LinearTrussTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            F^{(i)} = -F^{(j)} = EA / l (U^{(j)} - U^{(i)})\\ \quad
           \forall \mbox{ elements } T_K^{i,j}\\ \mbox{ in a region
           connecting nodes } i, j
     - :ref:`tru.bri <linear_elasticity-truss_bridge3d>`, :ref:`tru.bri <linear_elasticity-truss_bridge>`
   * - ev_lin_truss_force

       :class:`LinearTrussInternalForceTerm <sfepy.terms.terms_elastic.LinearTrussInternalForceTerm>`
     - ``<material>``, ``<parameter>``
     - .. math::
            F = EA / l (U^{(j)} - U^{(i)})\\ \quad \forall \mbox{
           elements } T_K^{i,j}\\ \mbox{ in a region connecting nodes } i, j
     - 
   * - dw_mass_ad

       :class:`MassADTerm <sfepy.terms.terms_jax.MassADTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\cal{D}} \rho \ul{v} \cdot \ul{u}
     - :ref:`ela.ide <linear_elasticity-elastodynamic_identification>`
   * - dw_nl_diffusion

       :class:`NonlinearDiffusionTerm <sfepy.terms.terms_diffusion.NonlinearDiffusionTerm>`
     - ``<fun>``, ``<dfun>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} \nabla q \cdot \nabla p f(p)
     - :ref:`poi.non.mat <diffusion-poisson_nonlinear_material>`
   * - dw_non_penetration

       :class:`NonPenetrationTerm <sfepy.terms.terms_constraints.NonPenetrationTerm>`
     - ``<opt_material>``, ``<virtual>``, ``<state>``

       ``<opt_material>``, ``<state>``, ``<virtual>``
     - .. math::
            \int_{\Gamma} c \lambda \ul{n} \cdot \ul{v} \mbox{ , }
           \int_{\Gamma} c \hat\lambda \ul{n} \cdot \ul{u} \\ \int_{\Gamma}
           \lambda \ul{n} \cdot \ul{v} \mbox{ , } \int_{\Gamma} \hat\lambda
           \ul{n} \cdot \ul{u}
     - :ref:`bio.npb.lag <multi_physics-biot_npbc_lagrange>`
   * - dw_non_penetration_p

       :class:`NonPenetrationPenaltyTerm <sfepy.terms.terms_constraints.NonPenetrationPenaltyTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Gamma} c (\ul{n} \cdot \ul{v}) (\ul{n} \cdot
           \ul{u})
     - :ref:`bio.sho.syn <multi_physics-biot_short_syntax>`
   * - dw_nonsym_elastic

       :class:`NonsymElasticTerm <sfepy.terms.terms_elastic.NonsymElasticTerm>`
     - ``<material>``, ``<virtual/param_1>``, ``<state/param_2>``
     - .. math::
            \int_{\Omega} \ull{D} \nabla\ul{u} : \nabla\ul{v}
     - :ref:`non.hyp.mM <homogenization-nonlinear_hyperelastic_mM>`
   * - dw_ns_dot_grad_s

       :class:`NonlinearScalarDotGradTerm <sfepy.terms.terms_dg.NonlinearScalarDotGradTerm>`
     - ``<fun>``, ``<fun_d>``, ``<virtual>``, ``<state>``

       ``<fun>``, ``<fun_d>``, ``<state>``, ``<virtual>``
     - .. math::
            \int_{\Omega} q \cdot \nabla \cdot \ul{f}(p) =
           \int_{\Omega} q \cdot \text{div} \ul{f}(p) \mbox{ , }
           \int_{\Omega} \ul{f}(p) \cdot \nabla q
     - :ref:`bur.2D <dg-burgers_2D>`
   * - dw_piezo_coupling

       :class:`PiezoCouplingTerm <sfepy.terms.terms_piezo.PiezoCouplingTerm>`
     - ``<material>``, ``<virtual/param_v>``, ``<state/param_s>``

       ``<material>``, ``<state>``, ``<virtual>``
     - .. math::
            \int_{\Omega} g_{kij}\ e_{ij}(\ul{v}) \nabla_k p\\
           \int_{\Omega} g_{kij}\ e_{ij}(\ul{u}) \nabla_k q
     - :ref:`pie.ela <multi_physics-piezo_elasticity>`, :ref:`pie.ela <multi_physics-piezo_elastodynamic>`
   * - ev_piezo_strain

       :class:`PiezoStrainTerm <sfepy.terms.terms_piezo.PiezoStrainTerm>`
     - ``<material>``, ``<parameter>``
     - .. math::
            \int_{\Omega} g_{kij} e_{ij}(\ul{u})
     - 
   * - ev_piezo_stress

       :class:`PiezoStressTerm <sfepy.terms.terms_piezo.PiezoStressTerm>`
     - ``<material>``, ``<parameter>``
     - .. math::
            \int_{\Omega} g_{kij} \nabla_k p
     - 
   * - dw_point_load

       :class:`ConcentratedPointLoadTerm <sfepy.terms.terms_point.ConcentratedPointLoadTerm>`
     - ``<material>``, ``<virtual>``
     - .. math::
            \ul{f}^i = \ul{\bar f}^i \quad \forall \mbox{ FE node } i
           \mbox{ in a region }
     - :ref:`she.can <linear_elasticity-shell10x_cantilever>`, :ref:`its.3 <linear_elasticity-its2D_3>`, :ref:`tru.bri <linear_elasticity-truss_bridge>`, :ref:`its.2 <linear_elasticity-its2D_2>`, :ref:`its.1 <linear_elasticity-its2D_1>`, :ref:`its.4 <linear_elasticity-its2D_4>`
   * - dw_point_lspring

       :class:`LinearPointSpringTerm <sfepy.terms.terms_point.LinearPointSpringTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \ul{f}^i = -k \ul{u}^i \quad \forall \mbox{ FE node } i
           \mbox{ in a region }
     - 
   * - dw_s_dot_grad_i_s

       :class:`ScalarDotGradIScalarTerm <sfepy.terms.terms_dot.ScalarDotGradIScalarTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            Z^i = \int_{\Omega} q \nabla_i p
     - 
   * - dw_s_dot_mgrad_s

       :class:`ScalarDotMGradScalarTerm <sfepy.terms.terms_dot.ScalarDotMGradScalarTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``

       ``<material>``, ``<state>``, ``<virtual>``
     - .. math::
            \int_{\Omega} q \ul{y} \cdot \nabla p \mbox{ , }
           \int_{\Omega} p \ul{y} \cdot \nabla q
     - :ref:`adv.1D <dg-advection_1D>`, :ref:`adv.2D <dg-advection_2D>`, :ref:`adv.dif.2D <dg-advection_diffusion_2D>`
   * - dw_shell10x

       :class:`Shell10XTerm <sfepy.terms.terms_shells.Shell10XTerm>`
     - ``<material_d>``, ``<material_drill>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
     - :ref:`she.can <linear_elasticity-shell10x_cantilever>`
   * - dw_stokes

       :class:`StokesTerm <sfepy.terms.terms_navier_stokes.StokesTerm>`
     - ``<opt_material>``, ``<virtual/param_v>``, ``<state/param_s>``

       ``<opt_material>``, ``<state>``, ``<virtual>``
     - .. math::
            \int_{\Omega} p\ \nabla \cdot \ul{v} \mbox{ , }
           \int_{\Omega} q\ \nabla \cdot \ul{u}\\ \mbox{ or } \int_{\Omega}
           c\ p\ \nabla \cdot \ul{v} \mbox{ , } \int_{\Omega} c\ q\ \nabla
           \cdot \ul{u}
     - :ref:`lin.ela.up <linear_elasticity-linear_elastic_up>`, :ref:`sto.sli.bc <navier_stokes-stokes_slip_bc>`, :ref:`sto <navier_stokes-stokes>`, :ref:`nav.sto.iga <navier_stokes-navier_stokes2d_iga>`, :ref:`nav.sto <navier_stokes-navier_stokes2d>`, :ref:`sta.nav.sto <navier_stokes-stabilized_navier_stokes>`, :ref:`nav.sto <navier_stokes-navier_stokes>`
   * - dw_stokes_wave

       :class:`StokesWaveTerm <sfepy.terms.terms_navier_stokes.StokesWaveTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} (\ul{\kappa} \cdot \ul{v}) (\ul{\kappa}
           \cdot \ul{u})
     - 
   * - dw_stokes_wave_div

       :class:`StokesWaveDivTerm <sfepy.terms.terms_navier_stokes.StokesWaveDivTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``

       ``<material>``, ``<state>``, ``<virtual>``
     - .. math::
            \int_{\Omega} (\ul{\kappa} \cdot \ul{v}) (\nabla \cdot
           \ul{u}) \;, \int_{\Omega} (\ul{\kappa} \cdot \ul{u}) (\nabla \cdot
           \ul{v})
     - 
   * - ev_sum_vals

       :class:`SumNodalValuesTerm <sfepy.terms.terms_basic.SumNodalValuesTerm>`
     - ``<parameter>``
     - 
     - 
   * - ev_surface_flux

       :class:`SurfaceFluxTerm <sfepy.terms.terms_diffusion.SurfaceFluxTerm>`
     - ``<material>``, ``<parameter>``
     - .. math::
            \int_{\Gamma} \ul{n} \cdot K_{ij} \nabla_j p
     - 
   * - dw_surface_flux

       :class:`SurfaceFluxOperatorTerm <sfepy.terms.terms_diffusion.SurfaceFluxOperatorTerm>`
     - ``<opt_material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Gamma} q \ul{n} \cdot \ull{K} \cdot \nabla p
     - 
   * - dw_surface_ltr

       :class:`LinearTractionTerm <sfepy.terms.terms_surface.LinearTractionTerm>`
     - ``<opt_material>``, ``<virtual/param>``
     - .. math::
            \int_{\Gamma} \ul{v} \cdot \ull{\sigma} \cdot \ul{n},
           \int_{\Gamma} \ul{v} \cdot \ul{n},
     - :ref:`wed.mes <linear_elasticity-wedge_mesh>`, :ref:`mix.mes <linear_elasticity-mixed_mesh>`, :ref:`nod.lcb <linear_elasticity-nodal_lcbcs>`, :ref:`com.ela.mat <large_deformation-compare_elastic_materials>`, :ref:`lin.ela.tra <linear_elasticity-linear_elastic_tractions>`, :ref:`lin.ela.opt <homogenization-linear_elasticity_opt>`, :ref:`lin.vis <linear_elasticity-linear_viscoelastic>`, :ref:`ela.shi.per <linear_elasticity-elastic_shifted_periodic>`, :ref:`tru.bri <linear_elasticity-truss_bridge3d>`
   * - ev_surface_moment

       :class:`SurfaceMomentTerm <sfepy.terms.terms_basic.SurfaceMomentTerm>`
     - ``<material>``, ``<parameter>``
     - .. math::
            \int_{\Gamma} \ul{n} (\ul{x} - \ul{x}_0)
     - 
   * - dw_surface_ndot

       :class:`SufaceNormalDotTerm <sfepy.terms.terms_surface.SufaceNormalDotTerm>`
     - ``<material>``, ``<virtual/param>``
     - .. math::
            \int_{\Gamma} q \ul{c} \cdot \ul{n}
     - :ref:`lap.flu.2d <diffusion-laplace_fluid_2d>`
   * - ev_surface_piezo_flux

       :class:`SurfacePiezoFluxTerm <sfepy.terms.terms_multilinear.SurfacePiezoFluxTerm>`
     - ``<material>``, ``<parameter>``
     - .. math::
            \int_{\Gamma} g_{kij} e_{ij}(\ul{u}) n_k
     - 
   * - dw_v_dot_grad_s

       :class:`VectorDotGradScalarTerm <sfepy.terms.terms_dot.VectorDotGradScalarTerm>`
     - ``<opt_material>``, ``<virtual/param_v>``, ``<state/param_s>``

       ``<opt_material>``, ``<state>``, ``<virtual>``
     - .. math::
            \int_{\Omega} \ul{v} \cdot \nabla p \mbox{ , }
           \int_{\Omega} \ul{u} \cdot \nabla q \\ \int_{\Omega} c \ul{v}
           \cdot \nabla p \mbox{ , } \int_{\Omega} c \ul{u} \cdot \nabla q \\
           \int_{\Omega} \ul{v} \cdot (\ull{c} \nabla p) \mbox{ , }
           \int_{\Omega} \ul{u} \cdot (\ull{c} \nabla q)
     - :ref:`vib.aco <acoustics-vibro_acoustic3d>`
   * - dw_vm_dot_s

       :class:`VectorDotScalarTerm <sfepy.terms.terms_dot.VectorDotScalarTerm>`
     - ``<material>``, ``<virtual/param_v>``, ``<state/param_s>``

       ``<material>``, ``<state>``, ``<virtual>``
     - .. math::
            \int_{\Omega} \ul{v} \cdot \ul{c} p \mbox{ , }
           \int_{\Omega} \ul{u} \cdot \ul{c} q\\
     - 
   * - ev_volume

       :class:`VolumeTerm <sfepy.terms.terms_basic.VolumeTerm>`
     - ``<parameter>``
     - .. math::
            \int_{\cal{D}} 1
     - 
   * - dw_volume_lvf

       :class:`LinearVolumeForceTerm <sfepy.terms.terms_volume.LinearVolumeForceTerm>`
     - ``<material>``, ``<virtual>``
     - .. math::
            \int_{\Omega} \ul{f} \cdot \ul{v} \mbox{ or }
           \int_{\Omega} f q
     - :ref:`poi.par.stu <diffusion-poisson_parametric_study>`, :ref:`poi.iga <diffusion-poisson_iga>`, :ref:`bur.2D <dg-burgers_2D>`, :ref:`adv.dif.2D <dg-advection_diffusion_2D>`
   * - dw_volume_nvf

       :class:`NonlinearVolumeForceTerm <sfepy.terms.terms_volume.NonlinearVolumeForceTerm>`
     - ``<fun>``, ``<dfun>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} q f(p)
     - :ref:`poi.non.mat <diffusion-poisson_nonlinear_material>`
   * - ev_volume_surface

       :class:`VolumeSurfaceTerm <sfepy.terms.terms_basic.VolumeSurfaceTerm>`
     - ``<parameter>``
     - .. math::
            1 / D \int_\Gamma \ul{x} \cdot \ul{n}
     - 
   * - dw_zero

       :class:`ZeroTerm <sfepy.terms.terms_basic.ZeroTerm>`
     - ``<virtual>``, ``<state>``
     - .. math::
            0
     - :ref:`ela <linear_elasticity-elastodynamic>`

.. _term_table_sensitivity:

.. raw:: latex

   \newpage
Table of sensitivity terms
""""""""""""""""""""""""""

.. tabularcolumns:: |p{0.15\linewidth}|p{0.10\linewidth}|p{0.6\linewidth}|p{0.15\linewidth}|
.. list-table:: Sensitivity terms
   :widths: 15 10 60 15
   :header-rows: 1
   :class: longtable

   * - name/class
     - arguments
     - definition
     - examples
   * - dw_adj_convect1

       :class:`AdjConvect1Term <sfepy.terms.terms_adj_navier_stokes.AdjConvect1Term>`
     - ``<virtual>``, ``<state>``, ``<parameter>``
     - .. math::
            \int_{\Omega} ((\ul{v} \cdot \nabla) \ul{u}) \cdot \ul{w}
     - 
   * - dw_adj_convect2

       :class:`AdjConvect2Term <sfepy.terms.terms_adj_navier_stokes.AdjConvect2Term>`
     - ``<virtual>``, ``<state>``, ``<parameter>``
     - .. math::
            \int_{\Omega} ((\ul{u} \cdot \nabla) \ul{v}) \cdot \ul{w}
     - 
   * - dw_adj_div_grad

       :class:`AdjDivGradTerm <sfepy.terms.terms_adj_navier_stokes.AdjDivGradTerm>`
     - ``<material_1>``, ``<material_2>``, ``<virtual>``, ``<parameter>``
     - .. math::
            w \delta_{u} \Psi(\ul{u}) \circ \ul{v}
     - 
   * - ev_sd_convect

       :class:`SDConvectTerm <sfepy.terms.terms_adj_navier_stokes.SDConvectTerm>`
     - ``<parameter_u>``, ``<parameter_w>``, ``<parameter_mv>``
     - .. math::
            \int_{\Omega} [ u_k \pdiff{u_i}{x_k} w_i (\nabla \cdot
           \Vcal) - u_k \pdiff{\Vcal_j}{x_k} \pdiff{u_i}{x_j} w_i ]
     - 
   * - ev_sd_diffusion

       :class:`SDDiffusionTerm <sfepy.terms.terms_diffusion.SDDiffusionTerm>`
     - ``<material>``, ``<parameter_q>``, ``<parameter_p>``, ``<parameter_mv>``
     - .. math::
            \int_{\Omega} \hat{K}_{ij} \nabla_i q\, \nabla_j p

       .. math::
            \hat{K}_{ij} = K_{ij}\left( \delta_{ik}\delta_{jl} \nabla
           \cdot \ul{\Vcal} - \delta_{ik}{\partial \Vcal_j \over \partial
           x_l} - \delta_{jl}{\partial \Vcal_i \over \partial x_k}\right)
     - 
   * - de_sd_diffusion

       :class:`ESDDiffusionTerm <sfepy.terms.terms_sensitivity.ESDDiffusionTerm>`
     - ``<material>``, ``<virtual/param_1>``, ``<state/param_2>``, ``<parameter_mv>``
     - .. math::
            \int_{\Omega} \hat{K}_{ij} \nabla_i q\, \nabla_j p

       .. math::
            \hat{K}_{ij} = K_{ij}\left( \delta_{ik}\delta_{jl} \nabla
           \cdot \ul{\Vcal} - \delta_{ik}{\partial \Vcal_j \over \partial
           x_l} - \delta_{jl}{\partial \Vcal_i \over \partial x_k}\right)
     - 
   * - ev_sd_div

       :class:`SDDivTerm <sfepy.terms.terms_adj_navier_stokes.SDDivTerm>`
     - ``<parameter_u>``, ``<parameter_p>``, ``<parameter_mv>``
     - .. math::
            \int_{\Omega} p [ (\nabla \cdot \ul{w}) (\nabla \cdot
           \ul{\Vcal}) - \pdiff{\Vcal_k}{x_i} \pdiff{w_i}{x_k} ]
     - 
   * - ev_sd_div_grad

       :class:`SDDivGradTerm <sfepy.terms.terms_adj_navier_stokes.SDDivGradTerm>`
     - ``<opt_material>``, ``<parameter_u>``, ``<parameter_w>``, ``<parameter_mv>``
     - .. math::
            \int_{\Omega} \hat{I} \nabla \ul{v} : \nabla \ul{u} \mbox{
           , } \int_{\Omega} \nu \hat{I} \nabla \ul{v} : \nabla \ul{u}

       .. math::
            \hat{I}_{ijkl} = \delta_{ik}\delta_{jl} \nabla \cdot
           \ul{\Vcal} - \delta_{ik}\delta_{js} {\partial \Vcal_l \over
           \partial x_s} - \delta_{is}\delta_{jl} {\partial \Vcal_k \over
           \partial x_s}
     - 
   * - de_sd_div_grad

       :class:`ESDDivGradTerm <sfepy.terms.terms_sensitivity.ESDDivGradTerm>`
     - ``<opt_material>``, ``<virtual/param_1>``, ``<state/param_2>``, ``<parameter_mv>``
     - .. math::
            \int_{\Omega} \hat{I} \nabla \ul{v} : \nabla \ul{u} \mbox{
           , } \int_{\Omega} \nu \hat{I} \nabla \ul{v} : \nabla \ul{u}

       .. math::
            \hat{I}_{ijkl} = \delta_{ik}\delta_{jl} \nabla \cdot
           \ul{\Vcal} - \delta_{ik}\delta_{js} {\partial \Vcal_l \over
           \partial x_s} - \delta_{is}\delta_{jl} {\partial \Vcal_k \over
           \partial x_s}
     - 
   * - ev_sd_dot

       :class:`SDDotTerm <sfepy.terms.terms_adj_navier_stokes.SDDotTerm>`
     - ``<parameter_1>``, ``<parameter_2>``, ``<parameter_mv>``
     - .. math::
            \int_{\Omega} p q (\nabla \cdot \ul{\Vcal}) \mbox{ , }
           \int_{\Omega} (\ul{u} \cdot \ul{w}) (\nabla \cdot \ul{\Vcal})
     - 
   * - de_sd_dot

       :class:`ESDDotTerm <sfepy.terms.terms_sensitivity.ESDDotTerm>`
     - ``<opt_material>``, ``<virtual/param_1>``, ``<state/param_2>``, ``<parameter_mv>``
     - .. math::
            \int_\Omega q p (\nabla \cdot \ul{\Vcal}) \mbox{ , }
           \int_\Omega (\ul{v} \cdot \ul{u}) (\nabla \cdot \ul{\Vcal})\\
           \int_\Omega c q p (\nabla \cdot \ul{\Vcal}) \mbox{ , } \int_\Omega
           c (\ul{v} \cdot \ul{u}) (\nabla \cdot \ul{\Vcal})\\ \int_\Omega
           \ul{v} \cdot (\ull{M}\, \ul{u}) (\nabla \cdot \ul{\Vcal})
     - 
   * - de_sd_lin_elastic

       :class:`ESDLinearElasticTerm <sfepy.terms.terms_sensitivity.ESDLinearElasticTerm>`
     - ``<material>``, ``<virtual/param_1>``, ``<state/param_2>``, ``<parameter_mv>``
     - .. math::
            \int_{\Omega} \hat{D}_{ijkl} {\partial v_i \over \partial
           x_j} {\partial u_k \over \partial x_l}

       .. math::
            \hat{D}_{ijkl} = D_{ijkl}(\nabla \cdot \ul{\Vcal}) -
           D_{ijkq}{\partial \Vcal_l \over \partial x_q} - D_{iqkl}{\partial
           \Vcal_j \over \partial x_q}
     - 
   * - ev_sd_lin_elastic

       :class:`SDLinearElasticTerm <sfepy.terms.terms_elastic.SDLinearElasticTerm>`
     - ``<material>``, ``<parameter_w>``, ``<parameter_u>``, ``<parameter_mv>``
     - .. math::
            \int_{\Omega} \hat{D}_{ijkl}\ e_{ij}(\ul{v})
           e_{kl}(\ul{u})

       .. math::
            \hat{D}_{ijkl} = D_{ijkl}(\nabla \cdot \ul{\Vcal}) -
           D_{ijkq}{\partial \Vcal_l \over \partial x_q} - D_{iqkl}{\partial
           \Vcal_j \over \partial x_q}
     - 
   * - ev_sd_piezo_coupling

       :class:`SDPiezoCouplingTerm <sfepy.terms.terms_piezo.SDPiezoCouplingTerm>`
     - ``<material>``, ``<parameter_u>``, ``<parameter_p>``, ``<parameter_mv>``
     - .. math::
            \int_{\Omega} \hat{g}_{kij}\ e_{ij}(\ul{u}) \nabla_k p

       .. math::
            \hat{g}_{kij} = g_{kij}(\nabla \cdot \ul{\Vcal}) -
           g_{kil}{\partial \Vcal_j \over \partial x_l} - g_{lij}{\partial
           \Vcal_k \over \partial x_l}
     - 
   * - de_sd_piezo_coupling

       :class:`ESDPiezoCouplingTerm <sfepy.terms.terms_sensitivity.ESDPiezoCouplingTerm>`
     - ``<material>``, ``<virtual/param_v>``, ``<state/param_s>``, ``<parameter_mv>``

       ``<material>``, ``<state>``, ``<virtual>``, ``<parameter_mv>``
     - .. math::
            \int_{\Omega} \hat{g}_{kij}\ e_{ij}(\ul{v}) \nabla_k p
           \mbox{ , } \int_{\Omega} \hat{g}_{kij}\ e_{ij}(\ul{u}) \nabla_k q

       .. math::
            \hat{g}_{kij} = g_{kij}(\nabla \cdot \ul{\Vcal}) -
           g_{kil}{\partial \Vcal_j \over \partial x_l} - g_{lij}{\partial
           \Vcal_k \over \partial x_l}
     - 
   * - de_sd_stokes

       :class:`ESDStokesTerm <sfepy.terms.terms_sensitivity.ESDStokesTerm>`
     - ``<opt_material>``, ``<virtual/param_v>``, ``<state/param_s>``, ``<parameter_mv>``

       ``<opt_material>``, ``<state>``, ``<virtual>``, ``<parameter_mv>``
     - .. math::
            \int_{\Omega} p\, \hat{I}_{ij} {\partial v_i \over
           \partial x_j} \mbox{ , } \int_{\Omega} q\, \hat{I}_{ij} {\partial
           u_i \over \partial x_j}

       .. math::
            \hat{I}_{ij} = \delta_{ij} \nabla \cdot \Vcal - {\partial
           \Vcal_j \over \partial x_i}
     - 
   * - ev_sd_surface_integrate

       :class:`SDSufaceIntegrateTerm <sfepy.terms.terms_surface.SDSufaceIntegrateTerm>`
     - ``<parameter>``, ``<parameter_mv>``
     - .. math::
            \int_{\Gamma} p \nabla \cdot \ul{\Vcal}
     - 
   * - de_sd_surface_ltr

       :class:`ESDLinearTractionTerm <sfepy.terms.terms_sensitivity.ESDLinearTractionTerm>`
     - ``<opt_material>``, ``<virtual/param>``, ``<parameter_mv>``
     - .. math::
            \int_{\Gamma} \ul{v} \cdot
           \left[\left(\ull{\hat{\sigma}}\, \nabla \cdot \ul{\cal{V}} -
           \ull{{\hat\sigma}}\, \nabla \ul{\cal{V}} \right)\ul{n}\right]

       .. math::
            \ull{\hat\sigma} = \ull{I} \mbox{ , } \ull{\hat\sigma} =
           c\,\ull{I} \mbox{ or } \ull{\hat\sigma} = \ull{\sigma}
     - 
   * - ev_sd_surface_ltr

       :class:`SDLinearTractionTerm <sfepy.terms.terms_surface.SDLinearTractionTerm>`
     - ``<opt_material>``, ``<parameter>``, ``<parameter_mv>``
     - .. math::
            \int_{\Gamma} \ul{v} \cdot (\ull{\sigma}\, \ul{n}),
           \int_{\Gamma} \ul{v} \cdot \ul{n},
     - 
   * - de_sd_v_dot_grad_s

       :class:`ESDVectorDotGradScalarTerm <sfepy.terms.terms_sensitivity.ESDVectorDotGradScalarTerm>`
     - ``<opt_material>``, ``<virtual/param_v>``, ``<state/param_s>``, ``<parameter_mv>``

       ``<opt_material>``, ``<state>``, ``<virtual>``, ``<parameter_mv>``
     - .. math::
            \int_{\Omega} \hat{I}_{ij} {\partial p \over \partial
           x_j}\, v_i \mbox{ , } \int_{\Omega} \hat{I}_{ij} {\partial q \over
           \partial x_j}\, u_i

       .. math::
            \hat{I}_{ij} = \delta_{ij} \nabla \cdot \Vcal - {\partial
           \Vcal_j \over \partial x_i}
     - 

.. _term_table_large deformation:

.. raw:: latex

   \newpage
Table of large deformation terms
""""""""""""""""""""""""""""""""

.. tabularcolumns:: |p{0.15\linewidth}|p{0.10\linewidth}|p{0.6\linewidth}|p{0.15\linewidth}|
.. list-table:: Large deformation terms
   :widths: 15 10 60 15
   :header-rows: 1
   :class: longtable

   * - name/class
     - arguments
     - definition
     - examples
   * - dw_tl_bulk_active

       :class:`BulkActiveTLTerm <sfepy.terms.terms_hyperelastic_tl.BulkActiveTLTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} S_{ij}(\ul{u}) \delta E_{ij}(\ul{u};\ul{v})
     - 
   * - dw_tl_bulk_penalty

       :class:`BulkPenaltyTLTerm <sfepy.terms.terms_hyperelastic_tl.BulkPenaltyTLTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} S_{ij}(\ul{u}) \delta E_{ij}(\ul{u};\ul{v})
     - :ref:`com.ela.mat <large_deformation-compare_elastic_materials>`, :ref:`hyp <large_deformation-hyperelastic>`, :ref:`act.fib <large_deformation-active_fibres>`
   * - dw_tl_bulk_pressure

       :class:`BulkPressureTLTerm <sfepy.terms.terms_hyperelastic_tl.BulkPressureTLTerm>`
     - ``<virtual>``, ``<state>``, ``<state_p>``
     - .. math::
            \int_{\Omega} S_{ij}(p) \delta E_{ij}(\ul{u};\ul{v})
     - :ref:`per.tl <large_deformation-perfusion_tl>`, :ref:`bal <large_deformation-balloon>`
   * - dw_tl_diffusion

       :class:`DiffusionTLTerm <sfepy.terms.terms_hyperelastic_tl.DiffusionTLTerm>`
     - ``<material_1>``, ``<material_2>``, ``<virtual>``, ``<state>``, ``<parameter>``
     - .. math::
            \int_{\Omega} \ull{K}(\ul{u}^{(n-1)}) : \pdiff{q}{\ul{X}}
           \pdiff{p}{\ul{X}}
     - :ref:`per.tl <large_deformation-perfusion_tl>`
   * - dw_tl_fib_a

       :class:`FibresActiveTLTerm <sfepy.terms.terms_fibres.FibresActiveTLTerm>`
     - ``<material_1>``, ``<material_2>``, ``<material_3>``, ``<material_4>``, ``<material_5>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} S_{ij}(\ul{u}) \delta E_{ij}(\ul{u};\ul{v})
     - :ref:`act.fib <large_deformation-active_fibres>`
   * - dw_tl_fib_e

       :class:`FibresExponentialTLTerm <sfepy.terms.terms_fibres.FibresExponentialTLTerm>`
     - ``<material_1>``, ``<material_2>``, ``<material_3>``, ``<material_4>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} S_{ij}(\ul{u}) \delta E_{ij}(\ul{u};\ul{v})
     - 
   * - dw_tl_fib_spe

       :class:`FibresSoftPlusExponentialTLTerm <sfepy.terms.terms_fibres.FibresSoftPlusExponentialTLTerm>`
     - ``<opt_material_0>``, ``<material_1>``, ``<material_2>``, ``<material_3>``, ``<material_4>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} S_{ij}(\ul{u}) \delta E_{ij}(\ul{u};\ul{v})
     - 
   * - dw_tl_he_genyeoh

       :class:`GenYeohTLTerm <sfepy.terms.terms_hyperelastic_tl.GenYeohTLTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} S_{ij}(\ul{u}) \delta E_{ij}(\ul{u};\ul{v})
     - 
   * - dw_tl_he_mooney_rivlin

       :class:`MooneyRivlinTLTerm <sfepy.terms.terms_hyperelastic_tl.MooneyRivlinTLTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} S_{ij}(\ul{u}) \delta E_{ij}(\ul{u};\ul{v})
     - :ref:`com.ela.mat <large_deformation-compare_elastic_materials>`, :ref:`hyp <large_deformation-hyperelastic>`, :ref:`bal <large_deformation-balloon>`
   * - dw_tl_he_neohook

       :class:`NeoHookeanTLTerm <sfepy.terms.terms_hyperelastic_tl.NeoHookeanTLTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} S_{ij}(\ul{u}) \delta E_{ij}(\ul{u};\ul{v})
     - :ref:`per.tl <large_deformation-perfusion_tl>`, :ref:`bal <large_deformation-balloon>`, :ref:`com.ela.mat <large_deformation-compare_elastic_materials>`, :ref:`act.fib <large_deformation-active_fibres>`, :ref:`hyp <large_deformation-hyperelastic>`
   * - dw_tl_he_neohook_ad

       :class:`NeoHookeanTLADTerm <sfepy.terms.terms_jax.NeoHookeanTLADTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} S_{ij}(\ul{u}) \delta E_{ij}(\ul{u};\ul{v})
     - 
   * - dw_tl_he_ogden

       :class:`OgdenTLTerm <sfepy.terms.terms_hyperelastic_tl.OgdenTLTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} S_{ij}(\ul{u}) \delta E_{ij}(\ul{u};\ul{v})
     - 
   * - dw_tl_he_ogden_ad

       :class:`OgdenTLADTerm <sfepy.terms.terms_jax.OgdenTLADTerm>`
     - ``<material_mu>``, ``<material_alpha>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} S_{ij}(\ul{u}) \delta E_{ij}(\ul{u};\ul{v})
     - 
   * - dw_tl_membrane

       :class:`TLMembraneTerm <sfepy.terms.terms_membrane.TLMembraneTerm>`
     - ``<material_a1>``, ``<material_a2>``, ``<material_h0>``, ``<virtual>``, ``<state>``
     - 
     - :ref:`bal <large_deformation-balloon>`
   * - ev_tl_surface_flux

       :class:`SurfaceFluxTLTerm <sfepy.terms.terms_hyperelastic_tl.SurfaceFluxTLTerm>`
     - ``<material_1>``, ``<material_2>``, ``<parameter_1>``, ``<parameter_2>``
     - .. math::
            \int_{\Gamma} \ul{\nu} \cdot \ull{K}(\ul{u}^{(n-1)})
           \pdiff{p}{\ul{X}}
     - 
   * - dw_tl_surface_traction

       :class:`SurfaceTractionTLTerm <sfepy.terms.terms_hyperelastic_tl.SurfaceTractionTLTerm>`
     - ``<opt_material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Gamma} \ul{\nu} \cdot \ull{F}^{-1} \cdot
           \ull{\sigma} \cdot \ul{v} J
     - :ref:`per.tl <large_deformation-perfusion_tl>`
   * - dw_tl_volume

       :class:`VolumeTLTerm <sfepy.terms.terms_hyperelastic_tl.VolumeTLTerm>`
     - ``<virtual>``, ``<state>``
     - .. math::
            \begin{array}{l} \int_{\Omega} q J(\ul{u}) \\ \mbox{volume
           mode: vector for } K \from \Ical_h: \int_{T_K} J(\ul{u}) \\
           \mbox{rel\_volume mode: vector for } K \from \Ical_h: \int_{T_K}
           J(\ul{u}) / \int_{T_K} 1 \end{array}
     - :ref:`per.tl <large_deformation-perfusion_tl>`, :ref:`bal <large_deformation-balloon>`
   * - ev_tl_volume_surface

       :class:`VolumeSurfaceTLTerm <sfepy.terms.terms_hyperelastic_tl.VolumeSurfaceTLTerm>`
     - ``<parameter>``
     - .. math::
            1 / D \int_{\Gamma} \ul{\nu} \cdot \ull{F}^{-1} \cdot
           \ul{x} J
     - 
   * - dw_ul_bulk_penalty

       :class:`BulkPenaltyULTerm <sfepy.terms.terms_hyperelastic_ul.BulkPenaltyULTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} \mathcal{L}\tau_{ij}(\ul{u})
           e_{ij}(\delta\ul{v})/J
     - :ref:`hyp.ul <large_deformation-hyperelastic_ul>`
   * - dw_ul_bulk_pressure

       :class:`BulkPressureULTerm <sfepy.terms.terms_hyperelastic_ul.BulkPressureULTerm>`
     - ``<virtual>``, ``<state>``, ``<state_p>``
     - .. math::
            \int_{\Omega} \mathcal{L}\tau_{ij}(\ul{u})
           e_{ij}(\delta\ul{v})/J
     - :ref:`hyp.ul.up <large_deformation-hyperelastic_ul_up>`
   * - dw_ul_compressible

       :class:`CompressibilityULTerm <sfepy.terms.terms_hyperelastic_ul.CompressibilityULTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``, ``<parameter_u>``
     - .. math::
            \int_{\Omega} 1\over \gamma p \, q
     - :ref:`hyp.ul.up <large_deformation-hyperelastic_ul_up>`
   * - dw_ul_he_by_fun

       :class:`HyperelasticByFunULTerm <sfepy.terms.terms_hyperelastic_ul.HyperelasticByFunULTerm>`
     - ``<fun>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} \mathcal{L}\tau_{ij}(\ul{u})
           e_{ij}(\delta\ul{v})/J
     - :ref:`hyp.ul.by.fun <large_deformation-hyperelastic_ul_by_fun>`
   * - dw_ul_he_mooney_rivlin

       :class:`MooneyRivlinULTerm <sfepy.terms.terms_hyperelastic_ul.MooneyRivlinULTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} \mathcal{L}\tau_{ij}(\ul{u})
           e_{ij}(\delta\ul{v})/J
     - :ref:`hyp.ul.up <large_deformation-hyperelastic_ul_up>`, :ref:`hyp.ul <large_deformation-hyperelastic_ul>`
   * - dw_ul_he_neohook

       :class:`NeoHookeanULTerm <sfepy.terms.terms_hyperelastic_ul.NeoHookeanULTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} \mathcal{L}\tau_{ij}(\ul{u})
           e_{ij}(\delta\ul{v})/J
     - :ref:`hyp.ul.up <large_deformation-hyperelastic_ul_up>`, :ref:`hyp.ul <large_deformation-hyperelastic_ul>`
   * - dw_ul_volume

       :class:`VolumeULTerm <sfepy.terms.terms_hyperelastic_ul.VolumeULTerm>`
     - ``<virtual>``, ``<state>``
     - .. math::
            \begin{array}{l} \int_{\Omega} q J(\ul{u}) \\ \mbox{volume
           mode: vector for } K \from \Ical_h: \int_{T_K} J(\ul{u}) \\
           \mbox{rel\_volume mode: vector for } K \from \Ical_h: \int_{T_K}
           J(\ul{u}) / \int_{T_K} 1 \end{array}
     - :ref:`hyp.ul.up <large_deformation-hyperelastic_ul_up>`

.. _term_table_special:

.. raw:: latex

   \newpage
Table of special terms
""""""""""""""""""""""

.. tabularcolumns:: |p{0.15\linewidth}|p{0.10\linewidth}|p{0.6\linewidth}|p{0.15\linewidth}|
.. list-table:: Special terms
   :widths: 15 10 60 15
   :header-rows: 1
   :class: longtable

   * - name/class
     - arguments
     - definition
     - examples
   * - dw_biot_eth

       :class:`BiotETHTerm <sfepy.terms.terms_biot.BiotETHTerm>`
     - ``<ts>``, ``<material_0>``, ``<material_1>``, ``<virtual>``, ``<state>``

       ``<ts>``, ``<material_0>``, ``<material_1>``, ``<state>``, ``<virtual>``
     - .. math::
            \begin{array}{l} \int_{\Omega} \left [\int_0^t
           \alpha_{ij}(t-\tau)\,p(\tau)) \difd{\tau} \right]\,e_{ij}(\ul{v})
           \mbox{ ,} \\ \int_{\Omega} \left [\int_0^t \alpha_{ij}(t-\tau)
           e_{kl}(\ul{u}(\tau)) \difd{\tau} \right] q \end{array}
     - 
   * - dw_biot_th

       :class:`BiotTHTerm <sfepy.terms.terms_biot.BiotTHTerm>`
     - ``<ts>``, ``<material>``, ``<virtual>``, ``<state>``

       ``<ts>``, ``<material>``, ``<state>``, ``<virtual>``
     - .. math::
            \begin{array}{l} \int_{\Omega} \left [\int_0^t
           \alpha_{ij}(t-\tau)\,p(\tau)) \difd{\tau} \right]\,e_{ij}(\ul{v})
           \mbox{ ,} \\ \int_{\Omega} \left [\int_0^t \alpha_{ij}(t-\tau)
           e_{kl}(\ul{u}(\tau)) \difd{\tau} \right] q \end{array}
     - 
   * - ev_cauchy_stress_eth

       :class:`CauchyStressETHTerm <sfepy.terms.terms_elastic.CauchyStressETHTerm>`
     - ``<ts>``, ``<material_0>``, ``<material_1>``, ``<parameter>``
     - .. math::
            \int_{\Omega} \int_0^t
           \Hcal_{ijkl}(t-\tau)\,e_{kl}(\ul{w}(\tau)) \difd{\tau}
     - 
   * - ev_cauchy_stress_th

       :class:`CauchyStressTHTerm <sfepy.terms.terms_elastic.CauchyStressTHTerm>`
     - ``<ts>``, ``<material>``, ``<parameter>``
     - .. math::
            \int_{\Omega} \int_0^t
           \Hcal_{ijkl}(t-\tau)\,e_{kl}(\ul{w}(\tau)) \difd{\tau}
     - 
   * - dw_lin_elastic_eth

       :class:`LinearElasticETHTerm <sfepy.terms.terms_elastic.LinearElasticETHTerm>`
     - ``<ts>``, ``<material_0>``, ``<material_1>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} \left [\int_0^t
           \Hcal_{ijkl}(t-\tau)\,e_{kl}(\ul{u}(\tau)) \difd{\tau}
           \right]\,e_{ij}(\ul{v})
     - :ref:`lin.vis <linear_elasticity-linear_viscoelastic>`
   * - dw_lin_elastic_th

       :class:`LinearElasticTHTerm <sfepy.terms.terms_elastic.LinearElasticTHTerm>`
     - ``<ts>``, ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Omega} \left [\int_0^t
           \Hcal_{ijkl}(t-\tau)\,e_{kl}(\ul{u}(\tau)) \difd{\tau}
           \right]\,e_{ij}(\ul{v})
     - 
   * - ev_of_ns_surf_min_d_press

       :class:`NSOFSurfMinDPressTerm <sfepy.terms.terms_adj_navier_stokes.NSOFSurfMinDPressTerm>`
     - ``<material_1>``, ``<material_2>``, ``<parameter>``
     - .. math::
            \delta \Psi(p) = \delta \left( \int_{\Gamma_{in}}p -
           \int_{\Gamma_{out}}bpress \right)
     - 
   * - dw_of_ns_surf_min_d_press_diff

       :class:`NSOFSurfMinDPressDiffTerm <sfepy.terms.terms_adj_navier_stokes.NSOFSurfMinDPressDiffTerm>`
     - ``<material>``, ``<virtual>``
     - .. math::
            w \delta_{p} \Psi(p) \circ q
     - 
   * - ev_sd_st_grad_div

       :class:`SDGradDivStabilizationTerm <sfepy.terms.terms_adj_navier_stokes.SDGradDivStabilizationTerm>`
     - ``<material>``, ``<parameter_u>``, ``<parameter_w>``, ``<parameter_mv>``
     - .. math::
            \gamma \int_{\Omega} [ (\nabla \cdot \ul{u}) (\nabla \cdot
           \ul{w}) (\nabla \cdot \ul{\Vcal}) - \pdiff{u_i}{x_k}
           \pdiff{\Vcal_k}{x_i} (\nabla \cdot \ul{w}) - (\nabla \cdot \ul{u})
           \pdiff{w_i}{x_k} \pdiff{\Vcal_k}{x_i} ]
     - 
   * - ev_sd_st_pspg_c

       :class:`SDPSPGCStabilizationTerm <sfepy.terms.terms_adj_navier_stokes.SDPSPGCStabilizationTerm>`
     - ``<material>``, ``<parameter_b>``, ``<parameter_u>``, ``<parameter_r>``, ``<parameter_mv>``
     - .. math::
            \sum_{K \in \Ical_h}\int_{T_K} \delta_K\ [ \pdiff{r}{x_i}
           (\ul{b} \cdot \nabla u_i) (\nabla \cdot \Vcal) - \pdiff{r}{x_k}
           \pdiff{\Vcal_k}{x_i} (\ul{b} \cdot \nabla u_i) - \pdiff{r}{x_k}
           (\ul{b} \cdot \nabla \Vcal_k) \pdiff{u_i}{x_k} ]
     - 
   * - ev_sd_st_pspg_p

       :class:`SDPSPGPStabilizationTerm <sfepy.terms.terms_adj_navier_stokes.SDPSPGPStabilizationTerm>`
     - ``<material>``, ``<parameter_r>``, ``<parameter_p>``, ``<parameter_mv>``
     - .. math::
            \sum_{K \in \Ical_h}\int_{T_K} \tau_K\ [ (\nabla r \cdot
           \nabla p) (\nabla \cdot \Vcal) - \pdiff{r}{x_k} (\nabla \Vcal_k
           \cdot \nabla p) - (\nabla r \cdot \nabla \Vcal_k) \pdiff{p}{x_k} ]
     - 
   * - ev_sd_st_supg_c

       :class:`SDSUPGCStabilizationTerm <sfepy.terms.terms_adj_navier_stokes.SDSUPGCStabilizationTerm>`
     - ``<material>``, ``<parameter_b>``, ``<parameter_u>``, ``<parameter_w>``, ``<parameter_mv>``
     - .. math::
            \sum_{K \in \Ical_h}\int_{T_K} \delta_K\ [ (\ul{b} \cdot
           \nabla u_k) (\ul{b} \cdot \nabla w_k) (\nabla \cdot \Vcal) -
           (\ul{b} \cdot \nabla \Vcal_i) \pdiff{u_k}{x_i} (\ul{b} \cdot
           \nabla w_k) - (\ul{u} \cdot \nabla u_k) (\ul{b} \cdot \nabla
           \Vcal_i) \pdiff{w_k}{x_i} ]
     - 
   * - dw_st_adj1_supg_p

       :class:`SUPGPAdj1StabilizationTerm <sfepy.terms.terms_adj_navier_stokes.SUPGPAdj1StabilizationTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``, ``<parameter>``
     - .. math::
            \sum_{K \in \Ical_h}\int_{T_K} \delta_K\ \nabla p (\ul{v}
           \cdot \nabla \ul{w})
     - 
   * - dw_st_adj2_supg_p

       :class:`SUPGPAdj2StabilizationTerm <sfepy.terms.terms_adj_navier_stokes.SUPGPAdj2StabilizationTerm>`
     - ``<material>``, ``<virtual>``, ``<parameter>``, ``<state>``
     - .. math::
            \sum_{K \in \Ical_h}\int_{T_K} \tau_K\ \nabla r (\ul{v}
           \cdot \nabla \ul{u})
     - 
   * - dw_st_adj_supg_c

       :class:`SUPGCAdjStabilizationTerm <sfepy.terms.terms_adj_navier_stokes.SUPGCAdjStabilizationTerm>`
     - ``<material>``, ``<virtual>``, ``<parameter>``, ``<state>``
     - .. math::
            \sum_{K \in \Ical_h}\int_{T_K} \delta_K\ [ ((\ul{v} \cdot
           \nabla) \ul{u}) ((\ul{u} \cdot \nabla) \ul{w}) + ((\ul{u} \cdot
           \nabla) \ul{u}) ((\ul{v} \cdot \nabla) \ul{w}) ]
     - 
   * - dw_st_grad_div

       :class:`GradDivStabilizationTerm <sfepy.terms.terms_navier_stokes.GradDivStabilizationTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \gamma \int_{\Omega} (\nabla\cdot\ul{u}) \cdot
           (\nabla\cdot\ul{v})
     - :ref:`sta.nav.sto <navier_stokes-stabilized_navier_stokes>`
   * - dw_st_pspg_c

       :class:`PSPGCStabilizationTerm <sfepy.terms.terms_navier_stokes.PSPGCStabilizationTerm>`
     - ``<material>``, ``<virtual>``, ``<parameter>``, ``<state>``
     - .. math::
            \sum_{K \in \Ical_h}\int_{T_K} \tau_K\ ((\ul{b} \cdot
           \nabla) \ul{u}) \cdot \nabla q
     - :ref:`sta.nav.sto <navier_stokes-stabilized_navier_stokes>`
   * - dw_st_pspg_p

       :class:`PSPGPStabilizationTerm <sfepy.terms.terms_navier_stokes.PSPGPStabilizationTerm>`
     - ``<opt_material>``, ``<virtual/param_1>``, ``<state/param_2>``
     - .. math::
            \sum_{K \in \Ical_h}\int_{T_K} \tau_K\ \nabla p \cdot
           \nabla q
     - :ref:`sta.nav.sto <navier_stokes-stabilized_navier_stokes>`
   * - dw_st_supg_c

       :class:`SUPGCStabilizationTerm <sfepy.terms.terms_navier_stokes.SUPGCStabilizationTerm>`
     - ``<material>``, ``<virtual>``, ``<parameter>``, ``<state>``
     - .. math::
            \sum_{K \in \Ical_h}\int_{T_K} \delta_K\ ((\ul{b} \cdot
           \nabla) \ul{u})\cdot ((\ul{b} \cdot \nabla) \ul{v})
     - :ref:`sta.nav.sto <navier_stokes-stabilized_navier_stokes>`
   * - dw_st_supg_p

       :class:`SUPGPStabilizationTerm <sfepy.terms.terms_navier_stokes.SUPGPStabilizationTerm>`
     - ``<material>``, ``<virtual>``, ``<parameter>``, ``<state>``
     - .. math::
            \sum_{K \in \Ical_h}\int_{T_K} \delta_K\ \nabla p\cdot
           ((\ul{b} \cdot \nabla) \ul{v})
     - :ref:`sta.nav.sto <navier_stokes-stabilized_navier_stokes>`
   * - dw_volume_dot_w_scalar_eth

       :class:`DotSProductVolumeOperatorWETHTerm <sfepy.terms.terms_dot.DotSProductVolumeOperatorWETHTerm>`
     - ``<ts>``, ``<material_0>``, ``<material_1>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_\Omega \left [\int_0^t \Gcal(t-\tau) p(\tau)
           \difd{\tau} \right] q
     - 
   * - dw_volume_dot_w_scalar_th

       :class:`DotSProductVolumeOperatorWTHTerm <sfepy.terms.terms_dot.DotSProductVolumeOperatorWTHTerm>`
     - ``<ts>``, ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_\Omega \left [\int_0^t \Gcal(t-\tau) p(\tau)
           \difd{\tau} \right] q
     - 

.. _term_table_multi-linear:

.. raw:: latex

   \newpage
Table of multi-linear terms
"""""""""""""""""""""""""""

.. tabularcolumns:: |p{0.15\linewidth}|p{0.10\linewidth}|p{0.6\linewidth}|p{0.15\linewidth}|
.. list-table:: Multi-linear terms
   :widths: 15 10 60 15
   :header-rows: 1
   :class: longtable

   * - name/class
     - arguments
     - definition
     - examples
   * - de_cauchy_stress

       :class:`ECauchyStressTerm <sfepy.terms.terms_multilinear.ECauchyStressTerm>`
     - ``<material>``, ``<parameter>``
     - .. math::
            \int_{\Omega} D_{ijkl} e_{kl}(\ul{w})
     - 
   * - de_convect

       :class:`EConvectTerm <sfepy.terms.terms_multilinear.EConvectTerm>`
     - ``<opt_material>``, ``<virtual/param_1>``, ``<state/param_2>``
     - .. math::
            \int_{\Omega} c ((\ul{u} \cdot \nabla) \ul{u}) \cdot
           \ul{v}
     - 
   * - de_diffusion

       :class:`EDiffusionTerm <sfepy.terms.terms_multilinear.EDiffusionTerm>`
     - ``<material>``, ``<virtual/param_1>``, ``<state/param_2>``
     - .. math::
            \int_{\Omega} K_{ij} \nabla_i q\, \nabla_j p
     - 
   * - de_div

       :class:`EDivTerm <sfepy.terms.terms_multilinear.EDivTerm>`
     - ``<opt_material>``, ``<virtual/param>``
     - .. math::
            \int_{\Omega} \nabla \cdot \ul{v} \mbox { , }
           \int_{\Omega} c \nabla \cdot \ul{v}
     - 
   * - de_div_grad

       :class:`EDivGradTerm <sfepy.terms.terms_multilinear.EDivGradTerm>`
     - ``<opt_material>``, ``<virtual/param_1>``, ``<state/param_2>``
     - .. math::
            \int_{\Omega} \nabla \ul{v} : \nabla \ul{u} \mbox{ , }
           \int_{\Omega} \nu\ \nabla \ul{v} : \nabla \ul{u}
     - 
   * - de_dot

       :class:`EDotTerm <sfepy.terms.terms_multilinear.EDotTerm>`
     - ``<opt_material>``, ``<virtual/param_1>``, ``<state/param_2>``
     - .. math::
            \int_{\cal{D}} q p \mbox{ , } \int_{\cal{D}} \ul{v} \cdot
           \ul{u}\\ \int_{\cal{D}} c q p \mbox{ , } \int_{\cal{D}} c \ul{v}
           \cdot \ul{u}\\ \int_{\cal{D}} \ul{v} \cdot (\ull{c}\, \ul{u})
     - 
   * - de_grad

       :class:`EGradTerm <sfepy.terms.terms_multilinear.EGradTerm>`
     - ``<opt_material>``, ``<parameter>``
     - .. math::
            \int_{\Omega} \nabla \ul{v} \mbox { , } \int_{\Omega} c
           \nabla \ul{v} \mbox { , } \int_{\Omega} \ul{c} \cdot \nabla \ul{v}
           \mbox { , } \int_{\Omega} \ull{c} \cdot \nabla \ul{v}
     - 
   * - de_integrate

       :class:`EIntegrateOperatorTerm <sfepy.terms.terms_multilinear.EIntegrateOperatorTerm>`
     - ``<opt_material>``, ``<virtual>``
     - .. math::
            \int_{\cal{D}} q \mbox{ or } \int_{\cal{D}} c q
     - 
   * - de_laplace

       :class:`ELaplaceTerm <sfepy.terms.terms_multilinear.ELaplaceTerm>`
     - ``<opt_material>``, ``<virtual/param_1>``, ``<state/param_2>``
     - .. math::
            \int_{\Omega} \nabla q \cdot \nabla p \mbox{ , }
           \int_{\Omega} c \nabla q \cdot \nabla p
     - 
   * - de_lin_convect

       :class:`ELinearConvectTerm <sfepy.terms.terms_multilinear.ELinearConvectTerm>`
     - ``<virtual/param_1>``, ``<parameter>``, ``<state/param_3>``
     - .. math::
            \int_{\Omega} ((\ul{w} \cdot \nabla) \ul{u}) \cdot \ul{v}
     - 
   * - de_lin_elastic

       :class:`ELinearElasticTerm <sfepy.terms.terms_multilinear.ELinearElasticTerm>`
     - ``<material>``, ``<virtual/param_1>``, ``<state/param_2>``
     - .. math::
            \int_{\Omega} D_{ijkl}\ e_{ij}(\ul{v}) e_{kl}(\ul{u})
     - 
   * - de_m_flexo

       :class:`MixedFlexoTerm <sfepy.terms.terms_flexo.MixedFlexoTerm>`
     - ``<virtual/param_v>``, ``<state/param_t>``

       ``<state>``, ``<virtual>``
     - .. math::
            \int_{\Omega} v_{i,j} a_{ij} \\ \int_{\Omega} u_{i,j}
           \delta a_{ij}
     - 
   * - de_m_flexo_coupling

       :class:`MixedFlexoCouplingTerm <sfepy.terms.terms_flexo.MixedFlexoCouplingTerm>`
     - ``<material>``, ``<virtual/param_t>``, ``<state/param_s>``

       ``<material>``, ``<state>``, ``<virtual>``
     - .. math::
            \int_{\Omega} f_{ijkl}\ e_{jk,l}(\ull{\delta w}) \nabla_i
           p \\ \int_{\Omega} f_{ijkl}\ e_{jk,l}(\ull{w}) \nabla_i q
     - 
   * - de_m_sg_elastic

       :class:`MixedStrainGradElasticTerm <sfepy.terms.terms_flexo.MixedStrainGradElasticTerm>`
     - ``<material>``, ``<virtual/param_1>``, ``<state/param_2>``
     - .. math::
            \int_{\Omega} a_{ijklmn}\ e_{ij,k}(\ull{\delta w}) \
           e_{lm,n}(\ull{w})
     - 
   * - de_mass

       :class:`MassTerm <sfepy.terms.terms_mass.MassTerm>`
     - ``<material_rho>``, ``<material_lumping>``, ``<material_beta>``, ``<virtual>``, ``<state>``
     - .. math::
            M^C = \int_{\cal{D}} \rho \ul{v} \cdot \ul{u} \\ M^L =
           \mathrm{lumping}(M^C) \\ M^A = (1 - \beta) M^C + \beta M^L \\ A =
           \sum_e A_e \\ C = \sum_e A_e^T (M_e^A)^{-1} A_e
     - :ref:`sei.loa <linear_elasticity-seismic_load>`, :ref:`ela <linear_elasticity-elastodynamic>`
   * - de_non_penetration_p

       :class:`ENonPenetrationPenaltyTerm <sfepy.terms.terms_multilinear.ENonPenetrationPenaltyTerm>`
     - ``<material>``, ``<virtual>``, ``<state>``
     - .. math::
            \int_{\Gamma} c (\ul{n} \cdot \ul{v}) (\ul{n} \cdot
           \ul{u})
     - 
   * - de_nonsym_elastic

       :class:`ENonSymElasticTerm <sfepy.terms.terms_multilinear.ENonSymElasticTerm>`
     - ``<material>``, ``<virtual/param_1>``, ``<state/param_2>``
     - .. math::
            \int_{\Omega} \ull{D} \nabla \ul{v} : \nabla \ul{u}
     - 
   * - de_s_dot_mgrad_s

       :class:`EScalarDotMGradScalarTerm <sfepy.terms.terms_multilinear.EScalarDotMGradScalarTerm>`
     - ``<material>``, ``<virtual/param_1>``, ``<state/param_2>``

       ``<material>``, ``<state>``, ``<virtual>``
     - .. math::
            \int_{\Omega} q \ul{y} \cdot \nabla p \mbox{ , }
           \int_{\Omega} p \ul{y} \cdot \nabla q
     - 
   * - de_stokes

       :class:`EStokesTerm <sfepy.terms.terms_multilinear.EStokesTerm>`
     - ``<opt_material>``, ``<virtual/param_v>``, ``<state/param_s>``

       ``<opt_material>``, ``<state>``, ``<virtual>``
     - .. math::
            \int_{\Omega} p\, \nabla \cdot \ul{v} \mbox{ , }
           \int_{\Omega} q\, \nabla \cdot \ul{u}\\ \int_{\Omega} c\, p\,
           \nabla \cdot \ul{v} \mbox{ , } \int_{\Omega} c\, q\, \nabla \cdot
           \ul{u}
     - 
   * - de_stokes_traction

       :class:`StokesTractionTerm <sfepy.terms.terms_multilinear.StokesTractionTerm>`
     - ``<opt_material>``, ``<virtual/param_1>``, ``<state/param_2>``
     - .. math::
            \int_{\Gamma} \nu \ul{v}\cdot(\nabla \ul{u} \cdot \ul{n})
     - 
   * - de_surface_flux

       :class:`SurfaceFluxOperatorTerm <sfepy.terms.terms_multilinear.SurfaceFluxOperatorTerm>`
     - ``<material>``, ``<virtual/param_1>``, ``<state/param_2>``

       ``<material>``, ``<state>``, ``<virtual>``
     - .. math::
            \int_{\Gamma} q \ul{n} \cdot \ull{K} \cdot \nabla p \mbox{
           , } \int_{\Gamma} p \ul{n} \cdot \ull{K} \cdot \nabla q
     - :ref:`pie.ela <multi_physics-piezo_elastodynamic>`
   * - de_surface_ltr

       :class:`ELinearTractionTerm <sfepy.terms.terms_multilinear.ELinearTractionTerm>`
     - ``<opt_material>``, ``<virtual/param>``
     - .. math::
            \int_{\Gamma} \ul{v} \cdot \ul{n} \mbox{ , } \int_{\Gamma}
           c\, \ul{v} \cdot \ul{n}\\ \int_{\Gamma} \ul{v} \cdot
           (\ull{\sigma}\, \ul{n}) \mbox{ , } \int_{\Gamma} \ul{v} \cdot
           \ul{f}
     - 
   * - de_surface_piezo_flux

       :class:`SurfacePiezoFluxOperatorTerm <sfepy.terms.terms_multilinear.SurfacePiezoFluxOperatorTerm>`
     - ``<material>``, ``<virtual/param_1>``, ``<state/param_2>``

       ``<material>``, ``<state>``, ``<virtual>``
     - .. math::
            \int_{\Gamma} q g_{kij} e_{ij}(\ul{u}) n_k \mbox{ , }
           \int_{\Gamma} p g_{kij} e_{ij}(\ul{v}) n_k
     - 


.. raw:: latex

   \newpage
