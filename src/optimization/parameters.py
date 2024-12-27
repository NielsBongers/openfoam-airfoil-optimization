from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class Parameters:
    run_name: str
    cases_folder: Path
    template_path: Path
    is_debug: bool
    csv_path: Path
    fluid_velocity: np.array
