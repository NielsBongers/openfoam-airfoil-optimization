import shutil
from pathlib import Path
from typing import Optional

import numpy as np

from .parameters import Parameters  # type: ignore


def process_result(
    x: np.array,
    parameters: Parameters,
    case_uuid: str,
    case_path: Path,
    block_mesh_result: bool,
    check_mesh_result: bool,
    simple_result: bool,
    cl: Optional[float] = None,
    cd: Optional[float] = None,
):
    with open(parameters.csv_path, "a") as f:
        f.write(
            f"{case_uuid},{parameters.run_name},{x[0]},{x[1]},{x[2]},{x[3]},{x[4]},{x[5]},{block_mesh_result},{check_mesh_result},{simple_result},{cl},{cd}\n"
        )

    shutil.rmtree(case_path)
