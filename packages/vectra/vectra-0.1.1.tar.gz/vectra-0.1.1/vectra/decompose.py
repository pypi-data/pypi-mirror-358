import rdkit2ase
import ase
from vectra.math import compute_rot_quantity, compute_trans_quantity
from rdkit2ase.utils import find_connected_components
import numpy as np


def decompose(
    atoms: ase.Atoms,
    quantity: np.ndarray,
    suggestions: tuple | list | None = tuple(),
    connectivity: list | None = None,
):
    """Decomposes a given quantity (e.g., forces, momenta) acting on an ASE Atoms object into
    translational, rotational, and vibrational components for each molecule.

    Parameters
    ----------
    atoms : ase.Atoms
        The molecular structure.
    quantity : numpy.ndarray
        The quantity to decompose (e.g., forces, momenta). It should have the same shape
        as forces or momenta (N, 3) or (N, 3, ensemble_size).
    suggestions : tuple or list, optional
        Optional list of suggestions for molecular decomposition, typically used by `rdkit2ase.ase2networkx`
        to guide the identification of connected components. Defaults to automatically determined components if possible.
    connectivity : list, optional
        Connectivity information for the atoms. List of tuples where each tuple contains
        indices of connected atoms (i, j, bond_order).

    Returns
    -------
    list of tuple
        A list of tuples, where each tuple contains (trans_component, rot_component, vib_component)
        for a single molecule. Each component is a NumPy array with shape (N_mol, 3), where N_mol is
        the number of atoms in that molecule.
    """
    if connectivity is not None:
        atoms.info["connectivity"] = connectivity
    if isinstance(suggestions, tuple):
        suggestions = list(suggestions)

    graph = rdkit2ase.ase2networkx(atoms, suggestions=suggestions)
    # doing so will add the `connectivity` attribute to the atoms
    atoms = rdkit2ase.networkx2ase(graph)
    connectivity = atoms.info.get(
        "connectivity", []
    )  # Use .get with default empty list

    components = list(find_connected_components(connectivity))

    # If no components are found by rdkit2ase, or for single atoms, treat the whole system as one component
    if not components or len(atoms) == 1:
        components = [list(range(len(atoms)))]  # Treat all atoms as a single component

    decomposed_molecules = []

    for component in components:
        component_indices = np.array(list(component), dtype=int)
        structure = atoms[component_indices]
        structure_quantity = quantity[component_indices]

        trans_c = compute_trans_quantity(structure, structure_quantity)
        rot_c = compute_rot_quantity(structure, structure_quantity)
        vib_c = structure_quantity - rot_c - trans_c

        decomposed_molecules.append((trans_c, rot_c, vib_c, component_indices))

    return decomposed_molecules
