import argparse
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution

from src.optimization.optimization import Parameters, funct


def custom_run():
    x = np.array(
        [-0.21256715, -0.55139223, -0.2564233, 0.07599256, -0.12636063, -0.23161034]
    )

    run_parameters = Parameters(
        run_name="Custom run",
        case_path=Path("custom_runs"),
        template_path=Path("openfoam_template"),
        csv_path=Path("results/csv/custom_results.csv"),
    )

    funct(x=x, parameters=run_parameters)


def default_run():
    run_parameters = Parameters(
        run_name="Debugging run",
        case_path=Path("openfoam_cases"),
        template_path=Path("openfoam_template"),
        csv_path=Path("results/csv/results.csv"),
    )

    # Analyzed with GPT4o, 2% - 98% of values attempted.
    bounds = [
        (-1.4400, -0.1027),
        (-1.2552, 1.2923),
        (-0.8296, 0.4836),
        (0.0359, 1.3246),
        (-0.1423, 1.4558),
        (-0.3631, 1.4440),
    ]

    result = differential_evolution(
        funct,
        bounds,
        strategy="best1bin",
        maxiter=10000000,
        popsize=60,
        tol=1e-1,
        workers=5,  # Native support for parallelization
        seed=42,
        args=(run_parameters,),
    )

    print("Optimal solution:", result.x)
    print("Objective function value:", result.fun)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose the run mode.")
    parser.add_argument(
        "--custom",
        action="store_true",
        help="Run custom logic instead of default logic",
    )
    args = parser.parse_args()

    if args.custom:
        custom_run()
    else:
        default_run()
