import vectra
import numpy as np
from ase import units
from ase.collections import s22
import pytest


@pytest.mark.parametrize(
    "temperatures",
    [
        (100, 10, 10),
        (10, 100, 10),
        (10, 10, 100),
        (100, 100, 100),  # Test with equal temperatures
    ],
)
def test_run_isolated_molecule_vib_only(mace_mp0, temperatures):
    rot_temp, vib_temp, trans_temp = temperatures
    box = s22["Water_dimer"]
    box.calc = mace_mp0

    md = vectra.DecomposedBerendsenThermostat(
        atoms=box,
        timestep=0.5 * units.fs,
        temperature_rot=rot_temp,
        temperature_trans=trans_temp,
        temperature_vib=vib_temp,
        tau_rot=0.5 * 10 * units.fs,
        tau_trans=0.5 * 10 * units.fs,
        tau_vib=0.5 * 10 * units.fs,
    )
    md.run(1)

    trans_temps = []
    vib_temps = []
    rot_temps = []

    for _ in md.irun(10):
        trans_temps.append(md.atoms.info["trans_temp"])
        vib_temps.append(md.atoms.info["vib_temp"])
        rot_temps.append(md.atoms.info["rot_temp"])

    assert np.mean(trans_temps) == pytest.approx(trans_temp, rel=2)
    assert np.mean(vib_temps) == pytest.approx(vib_temp, rel=2)
    assert np.mean(rot_temps) == pytest.approx(rot_temp, rel=2)
