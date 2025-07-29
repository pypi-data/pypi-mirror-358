import numpy as np
import pytest
import ase
from ase.calculators.singlepoint import SinglePointCalculator
from ase.calculators.calculator import Calculator
from rdkit2ase import smiles2atoms


@pytest.fixture
def mace_mp0() -> Calculator:
    from mace.calculators import mace_mp

    return mace_mp()


@pytest.fixture
def water(mace_mp0):
    water = smiles2atoms(smiles="O")
    # Small random displacement to create internal forces
    rng = np.random.default_rng(42)
    water.set_positions(
        water.get_positions() + rng.normal(0, 0.1, size=water.get_positions().shape)
    )
    water.calc = mace_mp0
    forces = water.get_forces()
    water.calc.results["forces_ensemble"] = forces[..., None]
    return water


@pytest.fixture
def water_with_composed_forces():
    atoms = ase.Atoms(
        "OH2",
        positions=np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ]
        ),
    )
    ft = np.array(
        [
            [0.0, 0.0, 1.0 * 15.999],
            [0.0, 0.0, 1.008],
            [0.0, 0.0, 1.008],
        ]
    )
    fr = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 1.008],
            [0.0, 0.0, -1.008],
        ]
    )
    fv = np.array(
        [
            [1.0, 1.0, 0.0],
            [-1.0, 0.0, 0.0],
            [0.0, -1.0, 0.0],
        ]
    )
    atoms.calc = SinglePointCalculator(atoms, forces=ft + fr + fv)

    return atoms, ft, fr, fv


@pytest.fixture
def two_waters_with_composed_forces():
    # First water molecule
    atoms1 = ase.Atoms(
        "OH2",
        positions=np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ]
        ),
    )
    ft1 = (
        np.array(
            [
                [0.0, 0.0, 1.0 * 15.999],
                [0.0, 0.0, 1.008],
                [0.0, 0.0, 1.008],
            ]
        )
        * 0.5
    )  # Reduced force for distinction
    fr1 = (
        np.array(
            [
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 1.008],
                [0.0, 0.0, -1.008],
            ]
        )
        * 0.5
    )
    fv1 = (
        np.array(
            [
                [1.0, 1.0, 0.0],
                [-1.0, 0.0, 0.0],
                [0.0, -1.0, 0.0],
            ]
        )
        * 0.5
    )

    # Second water molecule, shifted in position
    atoms2 = ase.Atoms(
        "OH2",
        positions=np.array(
            [
                [3.0, 0.0, 0.0],  # Shifted along x-axis
                [4.0, 0.0, 0.0],
                [3.0, 1.0, 0.0],
            ]
        ),
    )
    ft2 = (
        np.array(
            [
                [0.0, 0.0, 1.0 * 15.999],
                [0.0, 0.0, 1.008],
                [0.0, 0.0, 1.008],
            ]
        )
        * 1.5
    )  # Increased force for distinction
    fr2 = (
        np.array(
            [
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 1.008],
                [0.0, 0.0, -1.008],
            ]
        )
        * 1.5
    )
    fv2 = (
        np.array(
            [
                [1.0, 1.0, 0.0],
                [-1.0, 0.0, 0.0],
                [0.0, -1.0, 0.0],
            ]
        )
        * 1.5
    )

    # Combine atoms
    box_atoms = atoms1 + atoms2

    # Combine forces
    total_forces = np.concatenate((ft1 + fr1 + fv1, ft2 + fr2 + fv2))

    box_atoms.calc = SinglePointCalculator(box_atoms, forces=total_forces)

    return box_atoms, (ft1, fr1, fv1), (ft2, fr2, fv2)
