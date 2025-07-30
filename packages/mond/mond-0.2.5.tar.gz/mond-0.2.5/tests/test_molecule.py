import numpy as np
import unittest

from mond.molecule import Molecule, MoleculeCollection
from mond.utils import (
    check_overlaps_vectorized,
    create_molecule_from_smiles,
    random_pose,
)


class TestMoleculeCollection(unittest.TestCase):

    smiles_1 = "O"
    smiles_2 = "CCO"
    bounding_box = [20, 20, 20]  # in angstrom openmm
    probs = [0.5, 0.5]
    safety_buffer = 0.3  # in angstrom openmm

    def test_random_pose(self):
        molec1 = create_molecule_from_smiles(smiles=self.smiles_1)
        old_coords = molec1.coordinates
        new_coords = random_pose(old_coords, self.bounding_box)
        assert np.array(old_coords).shape == np.array(new_coords).shape

    def test_overlap_check(self):
        molec1 = create_molecule_from_smiles(smiles=self.smiles_1)
        molec2 = create_molecule_from_smiles(smiles=self.smiles_1)  # should overlap
        coll = MoleculeCollection([molec1])
        overlaps = check_overlaps_vectorized(
            existing_centers=molec1.coordinates,
            existing_radii=molec1.coordinates,
            new_centers=molec2.coordinates,
            new_radii=molec2.radii,
            safety_distance=self.safety_buffer,
        )
        assert overlaps
        non_overlap_coords = np.array(molec1.coordinates) + 2
        overlaps = check_overlaps_vectorized(
            existing_centers=molec1.coordinates,
            existing_radii=molec1.coordinates,
            new_centers=non_overlap_coords,
            new_radii=molec2.radii,
            safety_distance=self.safety_buffer,
        )
        assert overlaps == False


class TestSalt(unittest.TestCase): 
    
    anion ="[O-]Cl(=O)(=O)=O"
    cation ="[Li+]"
    
    bounding_box = [20, 20, 20]  # in angstrom openmm
    probs = [0.5, 0.5]
    safety_buffer = 0.3 

    def test_random_pose(self):
        salt1 = create_salt_from_smiles(smiles_anion=self.anion, smiles_cation=self.smiles_cation)
        old_coords_anion = salt1.get_anion_coordinates
        old_coords_cation = salt1.get_cation_coordinats

        radii_anion = get_vdw_radii(self.anion)
        radii_cation = get_vdw_radii(self.cation)


        #new_function logic
        new_coords_anion = get_perturbed_docking_pose(
                        salt1.anion,
                        self.bounding_box,
                        self.perturbation,
                        sampled_conformations=20,
                        rms_threshold=0.1,
                        num_threads=4,
                        minimize_energy=False)
        new_coords_cation = get_perturbed_docking_pose(
                        salt1.cation,
                        self.bounding_box,
                        self.perturbation,
                        sampled_conformations=20,
                        rms_threshold=0.1,
                        num_threads=4,
                        minimize_energy=False)
        assert np.array(old_coords).shape == np.array(new_coords).shape