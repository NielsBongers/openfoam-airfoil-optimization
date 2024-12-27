import subprocess
from pathlib import Path


def render_foam_cases(
    cases_path: Path = Path(
        r"\\wsl.localhost\Ubuntu-24.04\home\user\OF\attempt_2\custom_runs"
    ),
    pvpython_path: str = r"C:/Programs/ParaView/bin/pvpython",
):
    """Function to automatically render ParaView outputs with some basic settings. This is very hacked together: expect some debugging.
    ParaView packages its own Python 3.10 distribution, so I created a Python file that is called using that - it's not pretty.
    To use this, first run `run_top_n` (or `python main.py --custom`), which creates the folder `custom_runs`, from which this can subsequently be ran. 

    Args:
        cases_path (Path): Path to the folder with .foam cases to render.
        pvpython_path (_type_, optional): `pvpython` installation location. Likely in `ProgramFiles` for other users. Defaults to r"C:\Programs\ParaView\bin\pvpython".
    """
    foam_file_paths = list(cases_path.glob("**/*.foam"))

    automate_paraview_path = Path(__file__).resolve().parent / "automate_paraview.py"
    renders_path = (Path(__file__).resolve().parent.parent.parent) / "results/renders/"
    renders_path.mkdir(exist_ok=True, parents=True)

    for foam_file_path in foam_file_paths:
        case_name = "_".join(foam_file_path.stem.split("_")[0:3])
        screenshot_path = renders_path / f"{case_name}.png"

        subprocess.run(
            [
                pvpython_path,
                automate_paraview_path,
                str(foam_file_path),
                str(screenshot_path),
            ],
        )


if __name__ == "__main__":
    render_foam_cases()
