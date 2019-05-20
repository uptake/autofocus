from pathlib import Path  # noqa: D100
from typing import Union

REPO_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_DIR / "data"
PathOrStr = Union[Path, str]
