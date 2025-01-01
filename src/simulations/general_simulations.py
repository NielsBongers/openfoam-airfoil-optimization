from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution

from src.optimization.optimization import Parameters, funct
from src.utils.utils import get_cst_by_uuid


def custom_run(uuid: str):
    x = get_cst_by_uuid(uuid=uuid)
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
        run_name="5_degree_AoA_fixed_nu_tilda_reduced_yplus_penalizing_neg_cd_fixed_AoA_angles",
        cases_folder=Path("openfoam_cases"),
        template_path=Path("openfoam_template"),
        is_debug=False,
        csv_path=Path("results/csv/results.csv"),
        fluid_velocity=np.array([99.6194698092, 8.7155742748, 0]),
    )

    run_parameters.csv_path.parent.mkdir(exist_ok=True, parents=True)

    # Analyzed feasible region at one point; this is the range [0.02 - 0.98] of what worked.
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
        maxiter=100000,
        popsize=60,  # I picked 10x the parameter count.
        tol=1e-1,
        workers=15,
        seed=42,
        args=(run_parameters,),
        updating="deferred",
    )
