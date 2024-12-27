from dataclasses import dataclass
from pathlib import Path


@dataclass
class Parameters:
    run_name: str
    cases_folder: Path
    template_path: Path
    csv_path: Path
