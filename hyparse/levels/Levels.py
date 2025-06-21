from ctypes import c_int, c_double, Structure, CDLL, c_char_p, create_string_buffer
from os import path

SHARED_FILE_PATH = path.join(path.dirname(__file__), "levels.so")
JSON_PATH = path.abspath(path.join(path.dirname(__file__), "json", "levels.json"))


class SkillInfo(Structure):
    _fields_ = [
        ("skill_level", c_int),
        ("remaining_xp", c_double),
        ("xp_required_to_level_up", c_double),
    ]


class SharedLibProtocol:
    pass


lib = CDLL(SHARED_FILE_PATH)
lib.getSkillInfo.argtypes = [c_double, c_char_p, c_char_p]
lib.getSkillInfo.restype = SkillInfo


def getSkillLevel(skill_xp, is_catacombs=False):
    skill_type = "Catacombs" if is_catacombs else "Skills"
    skill_buffer = create_string_buffer(skill_type.encode("utf-8"), 15)
    path_buffer = create_string_buffer(JSON_PATH.encode("utf-8"), 256)

    info = lib.getSkillInfo(skill_xp, skill_buffer, path_buffer)

    return {
        "level": info.skill_level,
        "leftover_xp": round(info.remaining_xp, 2),
        "xp_required_to_level_up": round(info.xp_required_to_level_up, 2),
    }
