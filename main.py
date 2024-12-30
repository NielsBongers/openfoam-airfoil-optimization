import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution

from src.optimization.optimization import Parameters, funct


def custom_run():
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

    run_parameters = Parameters(
        run_name="5_degree_AoA_custom_run_fixed_firstLayerHeight",
        cases_folder=Path("custom_runs"),
        template_path=Path("openfoam_template"),
        is_debug=True,
        csv_path=Path("results/csv/custom_results.csv"),
        fluid_velocity=np.array([99.6194698092, 8.7155742748, 0]),
    )

    return funct(x=x, parameters=run_parameters)


def run_top_n(csv_path: Path = Path("results/csv/results.csv"), n: int = 10):
    df = pd.read_csv(csv_path)

    df_filtered = df.dropna(subset=["cl", "cd"]).copy()
    df_filtered["cl_cd_abs"] = (df["cl"] / df["cd"]).abs()
    df_filtered = df_filtered.sort_values(by="cl_cd_abs", ascending=False)

    for row in df_filtered.head(n).itertuples():
        x = np.array([row.x0, row.x1, row.x2, row.x3, row.x4, row.x5])

        run_name = f"cl_cd_{round(row.cl_cd_abs, 3)}_{row.UUID}"

        run_parameters = Parameters(
            run_name=run_name,
            cases_folder=Path("custom_runs"),
            template_path=Path("openfoam_template"),
            is_debug=True,
            csv_path=Path("results/csv/custom_results.csv"),
            fluid_velocity=np.array([99.6194698092, 8.7155742748, 0]),
        )

        case_path = run_parameters.cases_folder / Path(run_parameters.run_name)
        case_path.mkdir(exist_ok=True, parents=True)

        csv_path.parent.mkdir(exist_ok=True, parents=True)

        funct(x=x, parameters=run_parameters)


def default_run():
    run_parameters = Parameters(
        run_name="5_degree_AoA_fixed_firstLayerHeight",
        cases_folder=Path("openfoam_cases"),
        template_path=Path("openfoam_template"),
        is_debug=False,
        csv_path=Path("results/csv/results.csv"),
        fluid_velocity=np.array([99.6194698092, 8.7155742748, 0]),
    )

    run_parameters.csv_path.parent.mkdir(exist_ok=True, parents=True)

    bounds = [
        (-1.4400, -0.1027),
        (-1.2552, 1.2923),
        (-0.8296, 0.4836),
        (0.0359, 1.3246),
        (-0.1423, 1.4558),
        (-0.3631, 1.4440),
    ]

    differential_evolution(
        funct,
        bounds,
        strategy="best1bin",
        maxiter=10000000,
        popsize=60,
        tol=1e-1,
        workers=10,
        seed=42,
        args=(run_parameters,),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose the run mode.")
    parser.add_argument(
        "--custom",
        action="store_true",
        help="Run custom evaluation.",
    )
    parser.add_argument(
        "--topn",
        type=int,
        help="Simulate top-n airfoils",
    )
    args = parser.parse_args()

    if args.custom:
        custom_run()
    elif args.topn is not None:
        print(f"Simulating top-{args.topn} airfoils.")
        run_top_n(n=args.topn)
    else:
        default_run()
