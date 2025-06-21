import io
import base64
import gzip
from json import dumps
from sqlite3 import connect
from typing import Any, Dict, List, Tuple, Union

import nbtlib
import orjson
import requests


def minecraft_uuid(playername: str):
    return (
        requests.get(
            "https://api.mojang.com/users/profiles/minecraft/" + playername
        ).json()
    )["id"]


def connect_linkdb():
    database = connect("accounts.sqlite")
    database.isolation_level = None  # Enables autocommit mode
    cursor = database.cursor()

    # Create the table if it doesn't exist
    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS accountlinks (
                        discord_uuid VARCHAR(255) PRIMARY KEY,
                        minecraft_uuid VARCHAR(255),
                        discord_name VARCHAR(255),
                        minecraft_name VARCHAR(255),
                        is_linked BOOLEAN
                        )     
        """)
    return cursor


def whodis(dcname):
    cursor = connect_linkdb()
    result = cursor.execute(
        f"SELECT discord_uuid, minecraft_uuid, discord_name, minecraft_name, is_linked FROM accountlinks WHERE discord_name = '{dcname}'"
    ).fetchone()

    if result:
        discord_uuid, minecraft_uuid, discord_name, minecraft_name, is_linked = result

    class player:
        def __init__(
            self, discord_uuid, minecraft_uuid, discord_name, minecraft_name, is_linked
        ):
            self.discordid = discord_uuid
            self.minecraftid = minecraft_uuid
            self.discordname = discord_name
            self.minecraftname = minecraft_name
            self.linked = is_linked

    return player(discord_uuid, minecraft_uuid, discord_name, minecraft_name, is_linked)


def get_skill_emote(skill_name):
    skill_emotes = {
        "Catacombs": "🪦",  # Example emoji for Catacombs
        "SKILL_FISHING": "🎣",  # Emoji for Fishing
        "SKILL_ALCHEMY": "⚗️",  # Emoji for Alchemy
        "SKILL_MINING": "⛏️",  # Emoji for Mining
        "SKILL_FARMING": "🌾",  # Emoji for Farming
        "SKILL_ENCHANTING": "✨",  # Emoji for Enchanting
        "SKILL_TAMING": "🐾",  # Emoji for Taming
        "SKILL_FORGING": "🔨",  # Emoji for Foraging
        "SKILL_CARPENTRY": "🪚",  # Emoji for Carpentry
        "SKILL_COMBAT": "⚔️",  # Emoji for Combat
    }
    return skill_emotes.get(skill_name, "❓")


def json_readable(data: Dict[str, Any] | List[Any], indent: int = 3) -> str:
    return dumps(data, indent=indent)


def nbt_to_json(b64_data) -> str:
    """
    Convert binary NBT (bytes or latin‑1 str) or a file path pointing
    at an NBT file into a JSON string. Uses orjson for maximum speed.

    Args:
      data:
        - bytes → raw NBT blob
        - str   → if `assume_path` and os.path.exists(data): treated as filename
                  otherwise treated as latin‑1–encoded binary
      assume_path: if True, try treating a str as a filepath first.

    Returns:
      A minified JSON string. No pretty‑printing (indent) for speed/memory.
    """
    """
    Decode Base64→GZIP→NBT and return (SNBT, JSON) strings.
    
    - SNBT is the compact Minecraft text format.
    - JSON is a minified dump via orjson (super fast/C).
    """
    # 1) Normalize to bytes and decode+decompress in one go
    if isinstance(b64_data, str):
        b64_data = b64_data.encode("ascii")
    raw_nbt = gzip.decompress(base64.b64decode(b64_data))

    # 2) Parse raw NBT into an nbtlib.File (a dict‑like root Compound)
    nbt_file = nbtlib.File.parse(io.BytesIO(raw_nbt))

    # 3B) Minified JSON via orjson for max throughput
    json_bytes = orjson.dumps(nbt_file, option=orjson.OPT_SERIALIZE_NUMPY)
    json_str = json_bytes.decode("utf-8")

    return json_str
