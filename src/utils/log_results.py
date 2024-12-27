from typing import Optional

import numpy as np

from ..optimization.parameters import Parameters # type: ignore


def log_result(
    x: np.array,
    parameters: Parameters,
    case_uuid: str,
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
