# nametrace: Human name detection and demographic prediction package.
# Copyright (C) 2025 Paul Bose

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Data utilities for loading and processing name datasets."""

from pathlib import Path
from typing import Set
import pandas as pd


def load_name_lists(data_dir: Path) -> Set[str]:
    """
    Load known names from nam_dict.txt and name_gender_dataset.csv.
    
    Args:
        data_dir: Path to data directory
        
    Returns:
        Set of known first names (lowercase)
    """
    known_names = set()
    
    # Load from nam_dict.txt (skip comments)
    name_txt = data_dir / "first_names.txt"
    if name_txt.exists():
        with open(name_txt, 'r', encoding='utf-8') as f:
            for line in f:
                name = line.strip()
                if name and name.isalpha():
                    known_names.add(name.lower())
    return known_names 