# MAGNOPY - Python package for magnons.
# Copyright (C) 2023-2025 Magnopy Team
#
# e-mail: anry@uv.es, web: magnopy.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import os

import numpy as np

from magnopy._energy import Energy
from magnopy._package_info import logo
from magnopy.io._spin_directions import plot_spin_directions

# Save local scope at this moment
old_dir = set(dir())
old_dir.add("old_dir")


def optimize_sd(
    spinham,
    magnetic_field=None,
    energy_tolerance=1e-5,
    torque_tolerance=1e-5,
    output_folder="magnopy-results",
    comment=None,
    make_sd_image=None,
) -> None:
    r"""
    Optimizes classical energy of spin Hamiltonian and finds a set of spin directions
    that describe local minima of energy landscape.

    Parameters
    ----------
    spinham : :py:class:`.SpinHamiltonian`
        Spin Hamiltonian.
    magnetic_field : (3, ) |array-like|_
        Vector of external magnetic field, given in Tesla.
    energy_tolerance : float, default 1e-5
        Tolerance parameter. Difference between classical energies of two consecutive
        optimization steps.
    torque_tolerance : float, default 1e-5
        Tolerance parameter. Maximum torque among all spins.
    output_folder : str, default "magnopy-results"
        Name for the folder where to save the output files. If the folder does not exist
        then it will be created.
    comment : str, optional
        Any comment to output right after the logo.
    make_sd_image : (3, ) tuple of int
        Whether to produce an html file that displays the spin directions. Three numbers
        are the repetitions of the unit cell along the three lattice vectors.

    """

    all_good = True

    print(logo(date_time=True))
    print(f"\n{' Comment ':=^90}\n")
    if comment is not None:
        print(comment)

    if magnetic_field is not None:
        spinham.add_magnetic_field(h=magnetic_field)

    print(f"\n{' Start optimization ':=^90}\n")

    print(f"Energy tolerance : {energy_tolerance:.5e}")
    print(f"Torque tolerance : {torque_tolerance:.5e}")
    energy = Energy(spinham=spinham)

    spin_directions = energy.optimize(
        energy_tolerance=energy_tolerance,
        torque_tolerance=torque_tolerance,
        quiet=False,
    )
    print(f"Optimization is done.")

    E_0 = energy.E_0(spin_directions=spin_directions)
    print(f"\n{'Classic ground state energy (E_0)':<51} : " f"{E_0:>15.6f} meV\n")

    print("Directions of spin vectors of the ground state and spin values are")

    print(f"{'Name':<6} {'S':>7} {'Sx':>12} {'Sy':>12} {'Sz':>12}")

    for i in range(spinham.M):
        print(
            f"{spinham.magnetic_atoms.names[i]:<6} "
            f"{spinham.magnetic_atoms.spins[i]:7.4f} "
            f"{spin_directions[i][0]:12.8f} "
            f"{spin_directions[i][1]:12.8f} "
            f"{spin_directions[i][2]:12.8f}"
        )

    # Create the output directory if it does not exist
    os.makedirs(output_folder, exist_ok=True)

    filename = os.path.join(output_folder, "SPIN_DIRECTIONS.txt")
    with open(filename, "w") as f:
        for i in range(spinham.M):
            f.write(
                f"{spin_directions[i][0]:12.8f} "
                f"{spin_directions[i][1]:12.8f} "
                f"{spin_directions[i][2]:12.8f}\n"
            )

    print(f"\nSpin directions are saved in file\n  {os.path.abspath(filename)}")

    if make_sd_image is not None:
        positions = np.array(spinham.magnetic_atoms.positions) @ spinham.cell
        filename = os.path.join(output_folder, "SPIN_DIRECTIONS")

        plot_spin_directions(
            output_name=filename,
            positions=positions,
            spin_directions=spin_directions,
            unit_cell=spinham.cell,
            repeat=make_sd_image,
        )

        print(
            f"\nImage of spin directions is saved in file\n  {os.path.abspath(filename)}.html"
        )

    print(f"\n{' Finished ':=^90}")


# Populate __all__ with objects defined in this file
__all__ = list(set(dir()) - old_dir)
# Remove all semi-private objects
__all__ = [i for i in __all__ if not i.startswith("_")]
del old_dir
