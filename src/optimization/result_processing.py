import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np

from .parameters import Parameters  # type: ignore


def process_result(
    x: np.array,
    parameters: Parameters,
    case_uuid: str,
    case_path: Path,
    clipping_result: bool,
    block_mesh_result: bool,
    check_mesh_result: bool,
    simple_result: bool,
    cl: Optional[float] = None,
    cd: Optional[float] = None,
):
    """Saving the results to a CSV.

    Args:
        x (np.array): The six CST parameters.
        parameters (Parameters): Settings used during the simulation.
        case_uuid (str): UUID.
        case_path (Path): Path to the case.
        block_mesh_result (bool): Results from blockMesh.
        check_mesh_result (bool): Results from checkMesh.
        simple_result (bool): Result from SIMPLE.
        cl (Optional[float], optional): Coefficient of lift. Defaults to None.
        cd (Optional[float], optional): Coefficient of drag. Defaults to None.
    """
    timestamp = datetime.now().isoformat(timespec="microseconds")
    with open(parameters.csv_path, "a") as f:
        f.write(
            f'{timestamp},{case_uuid},"{parameters.run_name}",{x[0]},{x[1]},{x[2]},{x[3]},{x[4]},{x[5]},{clipping_result},{block_mesh_result},{check_mesh_result},{simple_result},{cl},{cd}\n'
        )

    shutil.rmtree(case_path) if not parameters.is_debug else None
