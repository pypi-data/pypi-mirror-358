
import numpy as np 

from ase import Atoms
from ase.calculators.psi4 import Psi4

def velocity_verlet_step(
    coll, 
    method_psi4, 
    memory_psi4, 
    basis_psi4,
    scf_type_psi4,
    maxiter_psi4, 
    positions, 
    velocities, 
    forces, 
    masses, 
    box_lengths, 
    dt, 
    periodic_boundary):
    """
    Velocity Verlet for use in Psi4
    Parameters
    ----------
    positions : (N, 3)
    velocities : (N, 3)
    forces : (N, 3)
    masses : (N,) - Massen der Teilchen
    epsilon : float
    sigma : float
    """
    masses = np.array(masses)
    acc = forces / masses[:, np.newaxis]


    positions += velocities * dt + 0.5 * acc * dt**2
    if periodic_boundary == True: 
        positions %= box_lengths  # PBC

    new_forces, potential_energy = get_energy_forces_psi4(
        coll=coll, 
        positions=positions,
        method=method_psi4, 
        memory=memory_psi4, 
        basis=basis_psi4, 
        scf_type=scf_type_psi4,
        maxiter=maxiter_psi4)
    new_acc = new_forces / masses[:, np.newaxis]
    velocities = velocities + 0.5 * (acc + new_acc) * dt
    assert np.sum(np.isnan(velocities))==0, "Velocities contain NaN values"
    return positions, velocities, new_forces, potential_energy



def apply_pbc(displacement, box_length):
    return displacement - box_length * np.round(displacement / box_length)

def noose_hover_chain(): 
    raise NotImplementedError

def get_energy_forces_psi4(coll, positions, method, memory, scf_type, basis, charge=None, multiplicity=None, reference=None, maxiter=None): 
    atoms = Atoms(
        symbols=coll.get_atom_symbols(),
        positions=positions)
    calc = Psi4(atoms = atoms,
        method = method,
        memory = memory, # this is the default, be aware!
        basis = basis, 
        charge = charge, 
        multiplicity = multiplicity, 
        reference = reference, 
        scf_type=scf_type, 
        )

    calc.set(maxiter=maxiter)
    atoms.calc = calc
    
    # Get energy and forces
    pot_energy = atoms.get_potential_energy()
    forces = atoms.get_forces()
    return forces, pot_energy

def get_energy_forces_quantum_espresso(): 
    raise NotImplementedError


def pulling_force(
    positions: np.ndarray, 
    box_lengths: np.ndarray,
    masses: np.ndarray,  
    k_pull: float, ) -> np.ndarray:
    """
    Compute harmonic restoring forces that pull each particle toward the center of the box.

    Parameters:
        positions (np.ndarray): Array of shape (N, 3) with atomic positions in Å.
        box_length (np.ndarray): Array of shape (3,) with box lengths in Å.
        k_pull (float): Force constant (in eV/Å²).

    Returns:
        np.ndarray: Array of shape (N, 3) with forces in eV/Å.
    """
    positions = np.asarray(positions)
    box_lengths = np.asarray(box_lengths)
    masses = np.asarray(masses)

    center = box_lengths / 2

    total_mass = masses.sum()
    com = np.sum(masses[:, None] * positions, axis=0) / total_mass

    # Compute COM displacement
    displacement = com - center

    # Total force on molecule
    total_force = -k_pull * displacement  # shape (3,)

    # Distribute it to atoms proportionally to their mass
    forces = (masses[:, None] / total_mass) * total_force  # shape (N, 3)

    return forces

def initialize_velocities(atom_masses, temp, remove_drift=True)->list:
    
    kB_eV_per_K = 8.617333262145e-5     # Boltzmann constant in eV/K
    amu_to_eV_fs2_per_A2 = 103.642691909  # atomic mass unit to eV·fs²/Å²

    N = len(atom_masses)
    atom_masses = np.array(atom_masses)
    masses_eV_fs2_per_A2 = atom_masses * amu_to_eV_fs2_per_A2

    # Standard deviation of velocity per dimension: sqrt(kT / m)
    sigma = np.sqrt(kB_eV_per_K * temp / masses_eV_fs2_per_A2)

    # Sample velocities from Gaussian for each atom and each coordinate
    velocities = np.random.normal(0.0, sigma[:, np.newaxis], size=(N, 3))  # Å/fs

    if remove_drift:
        # Subtract center-of-mass velocity to remove net momentum
        total_mass = masses_eV_fs2_per_A2.sum()
        com_velocity = np.sum(velocities * masses_eV_fs2_per_A2[:, np.newaxis], axis=0) / total_mass
        velocities -= com_velocity

    return velocities


def init_traj(traj_file:str)->None: 

    with open(traj_file, 'w') as f:
        pass  # just clear or create the file

def append_to_traj(traj_file:str, positions:list, symbols:list)->None: 
    N = len(symbols)
    with open(traj_file, 'a') as f:
        f.write(f"{N}\n")
        f.write(f"AIMD trajectory point of mond\n")
        for sym, pos in zip(symbols, positions):
            f.write(f"{sym} {pos[0]:.8f} {pos[1]:.8f} {pos[2]:.8f}\n")