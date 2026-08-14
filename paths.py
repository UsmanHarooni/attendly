import sys
from pathlib import Path

FROZEN = getattr(sys, "frozen", False)


def _base_dir():
    if FROZEN:
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _assets_dir():
    if FROZEN:
        return Path(sys._MEIPASS) / "assets"
    return Path(__file__).resolve().parent / "assets"


BASE_DIR = _base_dir()
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = _assets_dir()