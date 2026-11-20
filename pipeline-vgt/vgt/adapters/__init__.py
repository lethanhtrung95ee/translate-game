from pathlib import Path

from .linguagacha import LinguaGacha
from .rpgmaker_mvmz import RpgMakerMVMZ
from .table import TableAdapter
from .unreal_locres import UnrealLocres

ADAPTERS = {a.name: a for a in (RpgMakerMVMZ, UnrealLocres, LinguaGacha, TableAdapter)}


def detect(game_dir: Path):
    for a in ADAPTERS.values():
        if a.detect(Path(game_dir)):
            return a
    return None
