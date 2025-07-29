"""
This module implements extended functionality of spherov2.utils for Sphero BOLT+ to support Sphero BOLT+ robot.

# ====================================================================
# Authors: Kathryn Kasmarik, Reda Ghanem
# Version 0.1.7
# School of Systems and Computing, UNSW Canberra
# ==================================================================== 

"""


# ------------------------------------------------------------------------- #
# [1] Import necessary libraries
# ------------------------------------------------------------------------- #

from enum import IntEnum
from typing import Callable, Dict, List, Iterable



# Import all necessary classes and functions from spherov2
from spherov2.utils import *
# Import ToyUtil as BaseToyUtil to extend its functionality
from spherov2.utils import ToyUtil as BaseToyUtil
# Import our new implementation of BOLTPLUS from our new library 
from sphero_unsw.toy.boltplus import BOLTPLUS



# ------------------------------------------------------------------------- #
# [2] Create a new class ToyUtil that inherits from BaseToyUtil
# ------------------------------------------------------------------------- #
class ToyUtil(BaseToyUtil):

    def __init__(self, *args, **kwargs):
        """
        Initialize the ToyUtil class with the same parameters as BaseToyUtil.
        """
        super().__init__(*args, **kwargs)
    
    @staticmethod
    def set_front_led(toy: Toy, r: int, g: int, b: int, not_supported_handler: Callable[[], None] = None):
        if isinstance(toy, RVR):
            mapping = {
                RVR.LEDs.RIGHT_HEADLIGHT_RED: r,
                RVR.LEDs.RIGHT_HEADLIGHT_GREEN: g,
                RVR.LEDs.RIGHT_HEADLIGHT_BLUE: b,
                RVR.LEDs.LEFT_HEADLIGHT_RED: r,
                RVR.LEDs.LEFT_HEADLIGHT_GREEN: g,
                RVR.LEDs.LEFT_HEADLIGHT_BLUE: b
            }
        elif isinstance(toy, (R2D2, R2Q5, BOLT, BOLTPLUS)):       
            mapping = {
                toy.LEDs.FRONT_RED: r,
                toy.LEDs.FRONT_GREEN: g,
                toy.LEDs.FRONT_BLUE: b
            }
        elif isinstance(toy, Mini):
            mapping = {
                toy.LEDs.BODY_RED: r,
                toy.LEDs.BODY_GREEN: g,
                toy.LEDs.BODY_BLUE: b
            }
        else:
            mapping = None
        ToyUtil.set_multiple_leds(toy, mapping, not_supported_handler)

    @staticmethod
    def set_back_led(toy: Toy, r: int, g: int, b: int, not_supported_handler: Callable[[], None] = None):
        if isinstance(toy, RVR):
            mapping = {
                RVR.LEDs.RIGHT_BRAKELIGHT_RED: r,
                RVR.LEDs.RIGHT_BRAKELIGHT_GREEN: g,
                RVR.LEDs.RIGHT_BRAKELIGHT_BLUE: b,
                RVR.LEDs.LEFT_BRAKELIGHT_RED: r,
                RVR.LEDs.LEFT_BRAKELIGHT_GREEN: g,
                RVR.LEDs.LEFT_BRAKELIGHT_BLUE: b
            }
        elif isinstance(toy, (R2D2, R2Q5, BOLT, BOLTPLUS)):      
            mapping = {
                toy.LEDs.BACK_RED: r,
                toy.LEDs.BACK_GREEN: g,
                toy.LEDs.BACK_BLUE: b
            }
        elif isinstance(toy, Mini):
            mapping = {
                toy.LEDs.USER_BODY_RED: r,
                toy.LEDs.USER_BODY_GREEN: g,
                toy.LEDs.USER_BODY_BLUE: b
            }
        else:
            mapping = None
        ToyUtil.set_multiple_leds(toy, mapping, not_supported_handler)

    @staticmethod
    def set_back_led_brightness(toy: Toy, brightness: int, not_supported_handler: Callable[[], None] = None):
        if isinstance(toy, (R2D2, R2Q5, BOLT, BOLTPLUS)):
            mapping = {
                toy.LEDs.BACK_RED: 0,
                toy.LEDs.BACK_GREEN: 0,
                toy.LEDs.BACK_BLUE: brightness,
            }
        elif isinstance(toy, (BB9E, Mini)):
            mapping = {
                toy.LEDs.AIMING: brightness
            }
        elif isinstance(toy, RVR):
            mapping = {
                RVR.LEDs.RIGHT_BRAKELIGHT_RED: 0,
                RVR.LEDs.RIGHT_BRAKELIGHT_GREEN: 0,
                RVR.LEDs.RIGHT_BRAKELIGHT_BLUE: brightness,
                RVR.LEDs.LEFT_BRAKELIGHT_RED: 0,
                RVR.LEDs.LEFT_BRAKELIGHT_GREEN: 0,
                RVR.LEDs.LEFT_BRAKELIGHT_BLUE: brightness
            }
        else:
            mapping = None

        def _fallback():
            if toy.implements(Sphero.set_back_led_brightness):
                toy.set_back_led_brightness(brightness)
            elif not_supported_handler:
                not_supported_handler()

        ToyUtil.set_multiple_leds(toy, mapping, _fallback)
