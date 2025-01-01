from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Tuple

import numpy as np

from src.optimization.optimization import Parameters, funct


def run_simulation(args):
    aoa, airspeed_magnitude, x = args
    v_x = airspeed_magnitude * np.cos(aoa)
    v_y = airspeed_magnitude * np.sin(aoa)

    run_parameters = Parameters(
        run_name=f"{np.degrees(aoa):.2f}_degree_AoA",
        cases_folder=Path("custom_runs/aoa"),
        template_path=Path("openfoam_template"),
        is_debug=True,
        csv_path=Path("results/csv/aoa_results.csv"),
        fluid_velocity=np.array([v_x, v_y, 0]),
    )

    funct(x=x, parameters=run_parameters)


def run_aoa_range(
    x: np.array,
    airspeed_magnitude: float,  # m/s
    angle_range_deg: Tuple[float, float],
    n_samples: int = 10,
):
    x = np.array(
        [
            -0.2559407074537591,
            0.08277623156819876,
            0.012895024774770975,
            0.30075161784670684,
            0.7115298583892795,
            0.021657744269316548,
        ]
    )

    min_angle_deg, max_angle_deg = angle_range_deg
    min_angle, max_angle = (
        min_angle_deg / 360 * 2 * np.pi,
        max_angle_deg / 360 * 2 * np.pi,
    )
    aoa_range = np.linspace(start=min_angle, stop=max_angle, num=n_samples)

    args = [(aoa, airspeed_magnitude, x) for aoa in aoa_range]
    with ProcessPoolExecutor(max_workers=10) as executor:
        executor.map(run_simulation, args)
