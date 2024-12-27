from dataclasses import dataclass
from pathlib import Path


@dataclass
class Parameters:
    run_name: str
    case_path: Path
    template_path: Path
    csv_path: Path
