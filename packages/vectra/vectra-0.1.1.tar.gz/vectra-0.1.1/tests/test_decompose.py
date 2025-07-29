import vectra
import numpy.testing as npt


def test_force_decomposition_ensemble(water_with_composed_forces):
    atoms, ft, fr, fv = water_with_composed_forces

    decomposed_molecules = vectra.decompose(atoms, atoms.get_forces())
    # For this test, we expect only one molecule
    assert len(decomposed_molecules) == 1
    atoms_trans_forces, atoms_rot_forces, atoms_vib_forces, _ = decomposed_molecules[0]

    npt.assert_allclose(ft, atoms_trans_forces, atol=1e-8)
    npt.assert_allclose(fr, atoms_rot_forces, atol=1e-8)
    npt.assert_allclose(fv, atoms_vib_forces, atol=1e-8)


def test_force_decomposition_two_waters(two_waters_with_composed_forces):
    box_atoms, (ft1, fr1, fv1), (ft2, fr2, fv2) = two_waters_with_composed_forces

    decomposed_molecules = vectra.decompose(box_atoms, box_atoms.get_forces())
    assert len(decomposed_molecules) == 2

    # For the first molecule (indices 0, 1, 2)
    atoms_trans_forces_1, atoms_rot_forces_1, atoms_vib_forces_1, _ = (
        decomposed_molecules[0]
    )
    # For the second molecule (indices 3, 4, 5)
    atoms_trans_forces_2, atoms_rot_forces_2, atoms_vib_forces_2, _ = (
        decomposed_molecules[1]
    )

    # Check forces for the first molecule
    npt.assert_allclose(ft1, atoms_trans_forces_1, atol=1e-8)
    npt.assert_allclose(fr1, atoms_rot_forces_1, atol=1e-8)
    npt.assert_allclose(fv1, atoms_vib_forces_1, atol=1e-8)

    # Check forces for the second molecule
    npt.assert_allclose(ft2, atoms_trans_forces_2, atol=1e-8)
    npt.assert_allclose(fr2, atoms_rot_forces_2, atol=1e-8)
    npt.assert_allclose(fv2, atoms_vib_forces_2, atol=1e-8)
