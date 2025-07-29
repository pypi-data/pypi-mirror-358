"""

# shperov2 original file: types.py

# ====================================================================
# Authors: Kathryn Kasmarik, Reda Ghanem
# Version 0.1.6
# School of Systems and Computing, UNSW Canberra
# ==================================================================== 

"""

from typing import NamedTuple, Union


class ToyType(NamedTuple):
    display_name: str
    prefix: Union[str, None]
    filter_prefix: str
    cmd_safe_interval: float


class Color(NamedTuple):
    r: int = None
    g: int = None
    b: int = None
