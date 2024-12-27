import shutil
import uuid

import numpy as np

from src.airfoil_mesher.airfoil_mesher import mesh_airfoil
from src.kulfan_converter.kulfan_to_coord import CST_shape
from src.optimization.openfoam_interfaces import (
    read_force_coefficients,
    run_blockmesh,
    run_checkmesh,
    run_simple,
    set_fluid_velocities,
)
from src.utils.logging_setup import get_logger

from ..optimization.parameters import Parameters  # type: ignore
from ..optimization.result_processing import process_result  # type: ignore


def funct(x: np.array, parameters: Parameters) -> float:
    """Optimization function.

    Args:
        x (np.array): The six CST parameters to generate the airfoil with.
        parameters (Parameters): Settings dataclass.

    Returns:
        float: Goal function performance.
    """
    logger = get_logger(__name__)

    case_uuid = str(uuid.uuid4()) if not parameters.is_debug else parameters.run_name

    wu = x[0:3]  # Upper surface
    wl = x[3:6]  # Lower surface

    dz = 0
    N = 50

    airfoil_CST = CST_shape(wl, wu, dz, N)
    airfoil_coordinates = airfoil_CST.airfoil_coor()

    logger.info(f"Running case {case_uuid} with {x}")

    case_path = parameters.cases_folder / case_uuid
    template_path = parameters.template_path

    case_path.mkdir(exist_ok=True, parents=True)
    shutil.copytree(src=template_path, dst=case_path, dirs_exist_ok=True)

    set_fluid_velocities(case_path, parameters.fluid_velocity)
    mesh_airfoil(airfoil_coordinates=airfoil_coordinates, case_path=case_path)

    block_mesh_result = run_blockmesh(case_path=case_path)
    check_mesh_result = run_checkmesh(case_path=case_path)

    if not (
        block_mesh_result and check_mesh_result
    ):  # blockMesh is giving errors or checkMesh is complaining.
        logger.debug(
            f"Encountered error. Skipping {case_uuid}. blockMesh: {block_mesh_result}. checkMesh: {check_mesh_result}"
        )
        process_result(
            x=x,
            parameters=parameters,
            case_uuid=case_uuid,
            case_path=case_path,
            block_mesh_result=block_mesh_result,
            check_mesh_result=check_mesh_result,
            simple_result=False,
        )
        return np.inf

    simple_result = run_simple(case_path)

    if not simple_result:  # SIMPLE has failed to run.
        logger.debug(f"Encountered error with SIMPLE. Skipping {case_uuid}.")
        process_result(
            x=x,
            parameters=parameters,
            case_uuid=case_uuid,
            case_path=case_path,
            block_mesh_result=block_mesh_result,
            check_mesh_result=check_mesh_result,
            simple_result=simple_result,
            cl=np.NAN,
            cd=np.NAN,
        )
        return np.inf

    # We now got data: let's read it and post-process a bit.
    df = read_force_coefficients(case_path)

    df["Cl_Cd_ratio"] = df["Cl"] / df["Cd"]
    lift_drag_ratio = df["Cl_Cd_ratio"].iloc[-1]

    logger.debug(f"Got {lift_drag_ratio}")
    logger.info(f"Successfully ran: {case_uuid} - {lift_drag_ratio}")

    process_result(
        x=x,
        parameters=parameters,
        case_uuid=case_uuid,
        case_path=case_path,
        block_mesh_result=block_mesh_result,
        check_mesh_result=check_mesh_result,
        simple_result=simple_result,
        cl=df["Cl"].iloc[-1],
        cd=df["Cd"].iloc[-1],
    )

    return -np.abs(
        lift_drag_ratio
    )  # Positive or negative doesn't matter; we can fly upside down too.
