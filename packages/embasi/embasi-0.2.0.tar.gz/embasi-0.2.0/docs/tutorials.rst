====================
Tutorials
====================

Examples shown below may be found in <YOUR_EMBASI_ROOT>/examples/FHIaims.

Basic Embedding Calculation (PBE0-in-PBE)
_________________________________________

.. highlight:: python

The following example shows how projection-based embedding may be used to embed a high-level calculation for two -OH groups (PBE0) in a methanol dimer within an environment of the two methyl groups (PBE).
	       
Before running your Python input script, the environmental variables $ASI_LIB_PATH and $AIMS_SPECIES_DIR must be defined ::

  $ export ASI_LIB_PATH <PATH_TO_AIMS_BUILD>/aims.*.so
  $ export AIMS_SPECIES_DIR <PATH_TO_AIMS_ROOT>/species_defaults/defaults_2020/<BASIS_DIR>

To run this example case, we will define the required modules ::

  $ from embasi.embedding import ProjectionEmbedding
  $ from embasi.parallel_utils import root_print
  $ from ase.data.s22 import s22, s26, create_s22_system
  $ from ase.calculators.aims import Aims, AimsProfile
  $ import os

The input parameters for the higher level and lower level calculation must then be defined. This is achieved using two ASE Aims calculator objects ::

  $ calc_ll = Aims(xc='PBE', profile=AimsProfile(command="asi-doesnt-need-command"),
  $  KS_method="parallel",
  $  RI_method="LVL",
  $  collect_eigenvectors=True,
  $  density_update_method='density_matrix', # for DM export
  $  atomic_solver_xc="PBE",
  $  compute_kinetic=True,
  $  override_initial_charge_check=True,)
  $
  $ calc_hl = Aims(xc='PBE0', profile=AimsProfile(command="asi-doesnt-need-command"),
  $  KS_method="parallel",
  $  RI_method="LVL",
  $  collect_eigenvectors=True,
  $  density_update_method='density_matrix', # for DM export
  $  atomic_solver_xc="PBE",
  $  compute_kinetic=True,
  $  override_initial_charge_check=True,)

The above calculator objects show the minimal necessary directives required to run an EmbASI calculation. Experienced FHI-aims users may note that the atomic_solver_xc parameter is specified. It is necessary enforce the same free atom solver for the high and low level calculators, as discrepencies in the solution for the free atom calculations cause significant deviations in total energy for an equivalent input density. Regular FHI-aims users may also notice that tha charge checks have been unset. This is because total energy calculations for the embedded subsystem that cut across covalent bonds will often have an overall negative charge (i.e., this subystem takes the charge ). Ordinarily, the user would supply a charge for each atom to define the initial charge configuration. However, in the EmbASI workflow, pre-defined density matrices obtained from previous calculations are imported, avoiding the need to set the initial charge configuration. As such, we avoid this problem by setting this keyword.

The input structures for this example may obtained through ASE from the S22 test set ::

  $ methanol_dimer_idx = s26[22]
  $ methanol_dimer = create_s22_system(methanol_dimer_idx)

After this, one may define the mask used to specify which atoms calculated at the lower and higher levels of theory. This mask defines how the electron density of the supersystem is partitioned into two disjoint densities through the density matrix. Two disjoint density matrices are used to define the density of the active and environment subsystems. The embedding mask should defined as a list of length of the total supersystem, with 1's defining the active (higher-level) subsystem, and 2's defining the environment (low-level) subystem ::

  $ embed_mask = [2] * len(methanol_dimer)
  $ embed_mask[1], embed_mask[5], embed_mask[7], embed_mask[11] = 1, 1, 1, 1

We then recommend that directories be defined for each calculation. This is because the various calculations for the embedding workflow are overwritten for subsystem EmbASI calculations, so specifying separate directories for each calculation ensures that important debugging information is preserved in the event that an intermediate calculation gives pathological results ::

  $ 
  $

Basis Truncation (PBE0-in-PBE)
______________________________
