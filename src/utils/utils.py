from pathlib import Path

import numpy as np
import pandas as pd


def get_cst_by_uuid(uuid: str, csv_path: Path = Path("results/csv/results.csv")):
    df = pd.read_csv(csv_path)

    selected_run = df[df["UUID"] == uuid]

    if len(selected_run) == 0:
        raise ValueError("Selected run does not exist.")

    x = np.array(
        [
            selected_run[column].item()
            for column in [str(f"x{index}") for index in range(0, 6)]
        ]
    )

    return x
