import ase
import numpy as np


def compute_trans_quantity(atoms: ase.Atoms, quantity: np.ndarray):
    """Compute translational component of a given quantity."""

    all_forces = np.sum(quantity, axis=0)
    masses = atoms.get_masses()
    atoms_mas = np.sum(masses)

    if len(all_forces.shape) == 1:
        mu = (masses / atoms_mas)[:, None]
    elif len(all_forces.shape) == 2:
        mu = (masses / atoms_mas)[:, None, None]
    else:
        raise ValueError("unsupported shape for the quantity")

    result = mu * all_forces
    return result


def compute_intertia_tensor(centered_positions, masses):
    r_sq = np.linalg.norm(centered_positions, ord=2, axis=1) ** 2 * masses
    r_sq = np.sum(r_sq)
    A = np.diag(np.full((3,), r_sq))
    mr_k = centered_positions * masses[:, None]
    B = np.einsum("ki, kj -> ij", centered_positions, mr_k)

    I_ab = A - B
    return I_ab


def compute_rot_quantity(atoms: ase.Atoms, quantity: np.ndarray):
    """Compute rotational component of a given quantity."""
    atom_positions = atoms.get_positions()
    atom_positions -= atoms.get_center_of_mass()
    masses = atoms.get_masses()

    if len(atoms) <= 2:
        result = np.zeros((len(atoms), 3))
        if quantity.ndim == 3:
            result = result[..., None]
        return result

    I_ab = compute_intertia_tensor(atom_positions, masses)
    I_ab_inv = np.linalg.inv(I_ab)

    masses = masses[:, None]
    mi_ri = masses * atom_positions

    contraction_idxs = "ab, b -> a"
    # Ensemble case
    if quantity.ndim == 3:
        atom_positions = atom_positions[..., None]
        contraction_idxs = "ab, nb -> na"

    f_x_r = np.sum(np.cross(quantity, atom_positions, axisa=1, axisb=1), axis=0)

    # Iinv_fxr = I_ab_inv @ f_x_r but batched for ensembles
    Iinv_fxr = np.einsum(contraction_idxs, I_ab_inv, f_x_r)

    if f_x_r.ndim == 1:
        result = np.cross(mi_ri, Iinv_fxr)
    elif f_x_r.ndim == 2:
        result = np.cross(mi_ri[:, None, :], Iinv_fxr[None, :, :], axisa=2, axisb=2)
        result = np.transpose(result, (0, 2, 1))
    else:
        raise ValueError("unsupported shape for the quantity")
    return result
