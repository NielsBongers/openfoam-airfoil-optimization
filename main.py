import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution

from src.simulations.aoa_simulations import run_aoa_range
from src.simulations.general_simulations import custom_run, default_run, run_top_n
from src.simulations.velocity_simulations import run_velocity_range
from src.utils.utils import get_cst_by_uuid

if __name__ == "__main__":
    # x = get_cst_by_uuid(uuid="844d53b2-85b2-4862-a182-42cf707e58ff")
    uuid = "844d53b2-85b2-4862-a182-42cf707e58ff"
    # run_aoa_range(
    #     uuid=uuid, airspeed_magnitude=100, angle_range_deg=(30, 45), n_samples=20
    # )
    run_velocity_range(uuid=uuid, aoa_deg=5, velocity_range=(20, 200), n_samples=19)

    # parser = argparse.ArgumentParser(description="Choose the run mode.")
    # parser.add_argument(
    #     "--custom",
    #     action="store_true",
    #     help="Run custom evaluation.",
    # )
    # parser.add_argument(
    #     "--topn",
    #     type=int,
    #     help="Simulate top-n airfoils",
    # )
    # args = parser.parse_args()

    # if args.custom:
    #     custom_run()
    # elif args.topn is not None:
    #     print(f"Simulating top-{args.topn} airfoils.")
    #     run_top_n(n=args.topn)
    # else:
    #     default_run()
    #     default_run()
