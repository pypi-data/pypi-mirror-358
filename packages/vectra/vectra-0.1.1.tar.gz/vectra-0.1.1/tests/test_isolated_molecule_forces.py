import numpy as np
import numpy.testing as npt

import vectra


def test_trans_forces(water):
    forces = water.get_forces()
    trans_forces = vectra.compute_trans_quantity(water, quantity=forces)
    npt.assert_allclose(trans_forces, 0.0, atol=1e-6)


def test_trans_forces_ensemble(water):
    forces_ensemble = water.calc.results["forces_ensemble"]
    trans_forces = vectra.compute_trans_quantity(water, quantity=forces_ensemble)
    npt.assert_allclose(trans_forces, 0.0, atol=1e-6)


def test_rot_forces(water):
    forces = water.get_forces()
    rot_forces = vectra.compute_rot_quantity(water, quantity=forces)
    npt.assert_allclose(rot_forces, 0.0, atol=1e-6)


def test_rot_forces_ensemble(water):
    forces_ensemble = water.calc.results["forces_ensemble"]
    rot_forces = vectra.compute_rot_quantity(water, quantity=forces_ensemble)
    npt.assert_allclose(rot_forces, 0.0, atol=1e-6)


def test_vib_forces(water):
    full_forces = water.get_forces()
    trans_forces = vectra.compute_trans_quantity(water, quantity=full_forces)
    rot_forces = vectra.compute_rot_quantity(water, quantity=full_forces)
    vib_forces = full_forces - trans_forces - rot_forces

    # vib should reconstruct the full force if trans and rot are zero
    npt.assert_allclose(vib_forces, full_forces, atol=1e-6)
    # Vib forces should not be all zero
    assert not np.allclose(vib_forces, 0.0, atol=1e-6)


def test_force_decomposition(water_with_composed_forces):
    atoms, ft, fr, fv = water_with_composed_forces
    forces = atoms.get_forces()

    atoms_trans_forces = vectra.compute_trans_quantity(atoms, quantity=forces)
    atoms_rot_forces = vectra.compute_rot_quantity(atoms, quantity=forces)
    atoms_vib_forces = forces - atoms_trans_forces - atoms_rot_forces

    assert np.allclose(ft, atoms_trans_forces)
    assert np.allclose(fr, atoms_rot_forces)
    assert np.allclose(fv, atoms_vib_forces)


def test_force_decomposition_ensemble(water_with_composed_forces):
    atoms, ft, fr, fv = water_with_composed_forces

    # Simulate ensemble forces by adding a new axis at the end
    ensemble_forces = atoms.get_forces()[..., None]  # shape (3, 3, 1)
    assert ensemble_forces.shape == (3, 3, 1)

    atoms_trans_forces = vectra.compute_trans_quantity(atoms, quantity=ensemble_forces)
    atoms_rot_forces = vectra.compute_rot_quantity(atoms, quantity=ensemble_forces)
    atoms_vib_forces = ensemble_forces - atoms_trans_forces - atoms_rot_forces

    # all shapes should match ensemble: (3, 3, 1)
    assert atoms_trans_forces.shape == atoms_rot_forces.shape == atoms_vib_forces.shape

    npt.assert_allclose(ft[..., None], atoms_trans_forces, atol=1e-8)
    npt.assert_allclose(fr[..., None], atoms_rot_forces, atol=1e-8)
    npt.assert_allclose(fv[..., None], atoms_vib_forces, atol=1e-8)
