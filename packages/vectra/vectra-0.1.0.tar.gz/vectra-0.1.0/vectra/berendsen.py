import numpy as np
import ase
from vectra.decompose import decompose
import dataclasses
from ase import units

from ase.md.md import MolecularDynamics


class DecomposedBerendsenThermostat(MolecularDynamics):
    def __init__(
        self,
        atoms: ase.Atoms,
        timestep: float,
        temperature_trans: float,
        temperature_rot: float,
        temperature_vib: float,
        tau_trans: float,
        tau_rot: float,
        tau_vib: float,
        suggestions: tuple | list | None = None,
        connectivity: list | None = None,
    ):
        MolecularDynamics.__init__(self, atoms, timestep)
        self.temperature_trans = temperature_trans
        self.temperature_rot = temperature_rot
        self.temperature_vib = temperature_vib
        self.tau_trans = tau_trans
        self.tau_rot = tau_rot
        self.tau_vib = tau_vib
        self.kB = 1 * units.kB
        self.suggestions = suggestions
        self.connectivity = connectivity
        self.atoms = atoms
        self.timestep = timestep

    def apply_decomposed_scaling(self):
        p = self.atoms.get_momenta()
        m = self.atoms.get_masses()

        components = decompose(
            self.atoms,
            p,
            suggestions=self.suggestions,
            connectivity=self.connectivity,
        )
        new_p = np.zeros_like(p)

        trans_temp, rot_temp, vib_temp = [], [], []

        for trans_c, rot_c, vib_c, idx in components:
            m_sub = m[idx][:, None]  # reshape for broadcasting
            ekin_trans = 0.5 * np.sum(trans_c**2 / m_sub)
            ekin_rot = 0.5 * np.sum(rot_c**2 / m_sub)
            ekin_vib = 0.5 * np.sum(vib_c**2 / m_sub)

            n_atoms = len(idx)
            dof_trans = 3
            dof_rot = 0 if n_atoms == 1 else (2 if n_atoms == 2 else 3)
            dof_vib = max(0, 3 * n_atoms - dof_trans - dof_rot)

            if dof_trans > 0 and ekin_trans > 1e-12:
                T_old = 2 * ekin_trans / (dof_trans * self.kB)
                factor = np.sqrt(
                    1
                    + (self.timestep / self.tau_trans)
                    * (self.temperature_trans / T_old - 1)
                )
                trans_c *= factor
                trans_temp.append(T_old)
            elif self.temperature_trans == 0:
                trans_c[:] = 0

            if dof_rot > 0 and ekin_rot > 1e-12:
                T_old = 2 * ekin_rot / (dof_rot * self.kB)
                factor = np.sqrt(
                    1
                    + (self.timestep / self.tau_rot)
                    * (self.temperature_rot / T_old - 1)
                )
                rot_c *= factor
                rot_temp.append(T_old)
            elif self.temperature_rot == 0:
                rot_c[:] = 0

            if dof_vib > 0 and ekin_vib > 1e-12:
                T_old = 2 * ekin_vib / (dof_vib * self.kB)
                factor = np.sqrt(
                    1
                    + (self.timestep / self.tau_vib)
                    * (self.temperature_vib / T_old - 1)
                )
                vib_c *= factor
                vib_temp.append(T_old)
            elif self.temperature_vib == 0:
                vib_c[:] = 0

            new_p[idx] = trans_c + rot_c + vib_c

        self.atoms.set_momenta(new_p)

        self.atoms.info["trans_temp"] = np.mean(trans_temp) if trans_temp else 0.0
        self.atoms.info["rot_temp"] = np.mean(rot_temp) if rot_temp else 0.0
        self.atoms.info["vib_temp"] = np.mean(vib_temp) if vib_temp else 0.0

    def step(self, forces=None):
        atoms = self.atoms

        if forces is None:
            forces = atoms.get_forces(md=True)

        # Half-step momentum update
        p = atoms.get_momenta()
        p += 0.5 * self.timestep * forces
        atoms.set_momenta(p)

        # Apply scaling before position update
        self.apply_decomposed_scaling()

        # Update positions using scaled momenta
        p = atoms.get_momenta()
        atoms.set_positions(
            atoms.get_positions() + self.timestep * p / atoms.get_masses()[:, None]
        )

        # Recalculate forces
        forces = atoms.get_forces(md=True)

        # Final half-step velocity update
        p = atoms.get_momenta()
        p += 0.5 * self.timestep * forces
        atoms.set_momenta(p)

        # Apply scaling again after full step
        self.apply_decomposed_scaling()

        return forces


_DEFAULT_TAU = round(0.5 * 100 * units.fs, 3)


@dataclasses.dataclass
class DecomposedBerendsenThermostatDC:
    """
    Dataclass representing the decomposed Berendsen thermostat parameters.

    Parameters
    ----------
    timestep : float
        The integration timestep for the thermostat.
    temperature_trans : float
        Target translational temperature.
    temperature_rot : float
        Target rotational temperature.
    temperature_vib : float
        Target vibrational temperature.
    tau_trans : float
        Coupling time constant for translational degrees of freedom.
    tau_rot : float
        Coupling time constant for rotational degrees of freedom.
    tau_vib : float
        Coupling time constant for vibrational degrees of freedom.
    suggestions : tuple or list or None, optional
        Optional suggestions for thermostat configuration (default is empty tuple).
    connectivity : list or None, optional
        Optional connectivity information for the system (default is None).
    """

    timestep: float
    temperature_trans: float
    temperature_rot: float
    temperature_vib: float
    tau_trans: float = _DEFAULT_TAU
    tau_rot: float = _DEFAULT_TAU
    tau_vib: float = _DEFAULT_TAU
    suggestions: tuple | list | None = tuple()
    connectivity: list | None = None

    def get_thermostat(self, atoms: ase.Atoms) -> DecomposedBerendsenThermostat:
        return DecomposedBerendsenThermostat(
            atoms=atoms,
            timestep=self.timestep,
            temperature_trans=self.temperature_trans,
            temperature_rot=self.temperature_rot,
            temperature_vib=self.temperature_vib,
            tau_trans=self.tau_trans,
            tau_rot=self.tau_rot,
            tau_vib=self.tau_vib,
            suggestions=self.suggestions,
            connectivity=self.connectivity,
        )
