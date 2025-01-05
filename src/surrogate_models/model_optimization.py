import shutil
import uuid
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from src.airfoil_mesher.airfoil_mesher import mesh_airfoil
from src.kulfan_converter.kulfan_to_coord import CST_shape
from src.optimization.optimization import Parameters
from src.surrogate_models.training import train_models
from src.utils.logging_setup import get_logger
from src.utils.openfoam_interfaces import (
    run_blockmesh,
    run_checkmesh,
    set_fluid_velocities,
)


def funct(
    x: np.array, models: dict[str : RandomForestClassifier | RandomForestRegressor]
) -> float:
    logger = get_logger(__name__)

    x = x.reshape(1, -1)

    cls_model: RandomForestClassifier = models["cls_model"]
    reg_model: RandomForestRegressor = models["reg_model"]

    predicted_failure = cls_model.predict(X=x)

    if predicted_failure:
        return np.inf

    cl_cd_predicted = reg_model.predict(X=x)

    logger.info(f"Model result: {cl_cd_predicted.item()}")

    return -cl_cd_predicted.item()


def funct_hybrid(
    x: np.array,
    models: dict[str : RandomForestClassifier | RandomForestRegressor],
) -> float:
    """Optimization function.

    Args:
        x (np.array): The six CST parameters to generate the airfoil with.
        parameters (Parameters): Settings dataclass.

    Returns:
        float: Goal function performance.
    """
    logger = get_logger(__name__)
    x = x.reshape(1, -1)

    cls_model: RandomForestClassifier = models["cls_model"]
    reg_model: RandomForestRegressor = models["reg_model"]

    # This is to also catch SIMPLE-failures and convergence problems
    predicted_failure = cls_model.predict(X=x)

    if predicted_failure:
        return np.inf

    parameters = Parameters(
        run_name="svm_optimized_cl_cd",
        cases_folder=Path("custom_runs"),
        template_path=Path("openfoam_template"),
        is_debug=False,
        csv_path=Path("results/csv/custom_results.csv"),
        fluid_velocity=np.array([99.6194698092, 8.7155742748, 0]),
    )

    case_uuid = str(uuid.uuid4())

    wu = x.squeeze()[0:3]  # Upper surface
    wl = x.squeeze()[3:6]  # Lower surface

    dz = 0
    N = 50

    airfoil_CST = CST_shape(wl, wu, dz, N)
    airfoil_coordinates = airfoil_CST.airfoil_coor()

    case_path = parameters.cases_folder / case_uuid
    template_path = parameters.template_path

    # blockMesh seems to accept cases where the bottom part of the airfoil clips into the top. This should prevent that.
    top_section = airfoil_coordinates[
        1:
    ][
        0 : 25 - 1
    ]  # We skip the first entry (that's (1.0, 0.0), and the last (because that's (0.0 0.0)). Now the top section has the same x as the bottom section.

    bottom_section = airfoil_coordinates[
        1:
    ][
        25:
    ][
        ::-1
    ]  # We then do the same here, except we reverse the order, so that now the x-coordinates line up.

    top_bottom_difference = top_section[:, 1] - bottom_section[:, 1]

    if (top_bottom_difference < 0).any():
        logger.info("Airfoil clipping detected")
        return np.inf

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
        try:
            shutil.rmtree(case_path)
        except Exception:
            pass

        return np.inf

    cl_cd_predicted = reg_model.predict(X=x)

    logger.info(f"Model result: {cl_cd_predicted.item()}")

    try:
        shutil.rmtree(case_path)
    except Exception:
        pass

    return -cl_cd_predicted.item()


def run_surrogate_model():
    logger = get_logger(__name__)
    cls_model, reg_model = train_models()

    models = {"cls_model": cls_model, "reg_model": reg_model}

    bounds = [
        (-1.4400, -0.1027),
        (-1.2552, 1.2923),
        (-0.8296, 0.4836),
        (0.0359, 1.3246),
        (-0.1423, 1.4558),
        (-0.3631, 1.4440),
    ]

    res = differential_evolution(
        funct_hybrid,
        bounds,
        strategy="best1bin",
        maxiter=1000,
        popsize=30,
        tol=1e-10,
        workers=-1,
        seed=42 + 1,
        args=(models,),
        updating="deferred",
    )

    logger.info(f"Optimization result:\n{res}")
