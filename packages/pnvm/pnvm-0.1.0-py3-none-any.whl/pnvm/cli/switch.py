"""
    pnvm -- A pythonic node version manager
    Copyright (C) 2025  Axel H. Karlsson

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import shutil
from pnvm import console, utils

def switch(new_version: str) -> None:

    if not utils.is_version_installed(new_version):
        console.error("You tried to select a node version which you don't have installed.", fatal=True)

    current_version = utils.get_selected_node_version()

    if current_version == new_version:
        console.error("You've already selected this version.", fatal=True)
    
    utils.set_selected_node_version(new_version)

    path = utils.get_pnvm_directory_path() / new_version / f"node-{new_version}-linux-x64" / "bin"
    
    for binary in path.glob("*"):
        absolute_path = binary.absolute()
        shutil.copy(absolute_path, utils.get_pnvm_bin_path())

    console.ok(f"You're now using node {new_version}.")
