from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Tuple

import numpy as np

from src.optimization.optimization import Parameters, funct
from src.utils.utils import get_cst_by_uuid


def run_simulation(args):
    aoa, airspeed_magnitude, x = args
    v_x = airspeed_magnitude * np.cos(aoa)
    v_y = airspeed_magnitude * np.sin(aoa)

    run_parameters = Parameters(
        run_name=f"{airspeed_magnitude:.2f}_ms",
        cases_folder=Path("custom_runs/velocity"),
        template_path=Path("openfoam_template"),
        is_debug=True,
        csv_path=Path("results/csv/velocity_results.csv"),
        fluid_velocity=np.array([v_x, v_y, 0]),
    )

    funct(x=x, parameters=run_parameters)


def run_velocity_range(
    uuid: str,
    aoa_deg: float,
    velocity_range: Tuple[float, float],
    n_samples: int = 10,
):
    x = get_cst_by_uuid(uuid=uuid)

    min_velocity, max_velocity = velocity_range
    aoa = aoa_deg / 360 * 2 * np.pi
    velocity_range = np.linspace(start=min_velocity, stop=max_velocity, num=n_samples)

    args = [(aoa, airspeed_magnitude, x) for airspeed_magnitude in velocity_range]
    with ProcessPoolExecutor(max_workers=10) as executor:
        executor.map(run_simulation, args)
