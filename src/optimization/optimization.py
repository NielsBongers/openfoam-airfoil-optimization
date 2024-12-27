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
)
from src.utils.logging_setup import get_logger

from ..optimization.parameters import Parameters  # type: ignore
from ..optimization.result_processing import process_result  # type: ignore


def funct(x: np.array, parameters: Parameters):
    logger = get_logger(__name__)

    case_uuid = str(uuid.uuid4())

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

    mesh_airfoil(airfoil_coordinates=airfoil_coordinates, case_path=case_path)

    block_mesh_result = run_blockmesh(case_path=case_path)
    check_mesh_result = run_checkmesh(case_path=case_path)

    if not (block_mesh_result and check_mesh_result):
        process_result(
            x=x,
            parameters=parameters,
            case_uuid=case_uuid,
            case_path=case_path,
            block_mesh_result=block_mesh_result,
            check_mesh_result=check_mesh_result,
            simple_result=False,
        )
        shutil.rmtree(case_path)
        return np.inf

    simple_result = run_simple(case_path)

    if not simple_result:
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
        shutil.rmtree(case_path)
        return np.inf

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

    return np.abs(
        lift_drag_ratio
    )  # Positive or negative doesn't matter; we can fly upside down
