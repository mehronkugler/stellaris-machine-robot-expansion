from typing import List
from json import loads
from random import randint
from uuid import uuid4

LOC_KEY_PREFIX = "OXR_MDLC_MREC"
def append_guid_part(name_prefix: str) -> str:

    guid_part_ = str(uuid4()).split('-')[0]
    return f"{name_prefix}-{guid_part_}"

random_prefixes = [
    "enp",
    "wlan",
    "eth",
    "loop",
    "ath",
    "dev",
    "sd",
]

empire_names = [
    "NEM", "GORF", "S3M", "XM", "MOD",
]

"""
Land: 0
Water: 1
Space: 2
Ether: 3
Abyss: 4

defend: ICE
attack: TSR
"""