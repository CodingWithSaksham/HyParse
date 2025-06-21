from typing import Protocol, Dict
from ctypes import Structure

SHARED_FILE_PATH: str
JSON_PATH: str

class SkillInfo(Structure):
    skill_level: int
    remaining_xp: float
    xp_required_to_level_up: float

class SharedLibProtocol(Protocol):
    def getSkillInfo(
        self, skill_xp: float, skill_name: bytes, json_path: bytes
    ) -> SkillInfo: ...

lib: SharedLibProtocol

def getSkillLevel(
    skill_xp: float, is_catacombs: bool = ...
) -> Dict[str, int | float]: ...
