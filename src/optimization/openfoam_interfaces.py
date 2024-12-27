import re
import subprocess
from pathlib import Path

import pandas as pd

from ..utils.logging_setup import get_logger


def run_blockmesh(case_path: Path):
    logger = get_logger(__name__)

    result = subprocess.run(
        ["blockMesh"],
        cwd=case_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    logger.debug(f"blockMesh: {result.returncode}")

    return result.returncode == 0


def run_checkmesh(case_path: Path):
    logger = get_logger(__name__)

    result = subprocess.run(
        ["checkMesh"],
        cwd=case_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    logger.debug(f"checkMesh: {result.returncode}")
    logger.debug(f"Output:\n{result.stdout}")

    if result.returncode == 0:
        mesh_checks_failed = re.search(
            pattern="Failed ([0-9]+) mesh checks", string=result.stdout
        )
        mesh_okay = "Mesh OK." in result.stdout

        if mesh_okay:
            logger.debug("Mesh OK!")
            return True

        if mesh_checks_failed:
            logger.warning(f"Mesh checks failed: {mesh_checks_failed.group(1)}")
            return False

    return False


def run_simple(case_path: Path):
    logger = get_logger(__name__)

    result = subprocess.run(
        ["simpleFoam"],
        cwd=case_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if not result.returncode == 0:
        logger.debug(f"{result.stderr}")
        logger.warning("Failed to run SIMPLE.")

    return result.returncode == 0


def read_force_coefficients(case_path: Path):
    force_coefficients_path = case_path / Path(
        r"postProcessing/forceCoeffs/0/coefficient.dat"
    )

    df = pd.read_csv(force_coefficients_path, skiprows=12, sep="\t")
    df.columns = [column_name.strip() for column_name in df.columns]

    return df
