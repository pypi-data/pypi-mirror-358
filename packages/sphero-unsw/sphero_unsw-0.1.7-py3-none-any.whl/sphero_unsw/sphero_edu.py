"""
This module implements extended functionality of spherov2.sphero_edu to support Sphero BOLT+ robot.

# ====================================================================
# Authors: Kathryn Kasmarik, Reda Ghanem
# Version 0.1.7
# School of Systems and Computing, UNSW Canberra
# ==================================================================== 

"""


# ------------------------------------------------------------------------- #
# [1] Import necessary libraries
# ------------------------------------------------------------------------- #
import time
from collections import defaultdict
from functools import partial
from typing import Union, List


# Import all necessary classes and functions from spherov2
from spherov2.sphero_edu import *
# Import SpheroEduAPI as BaseSpheroEduAPI to extend its functionality
from spherov2.sphero_edu import SpheroEduAPI as BaseSpheroEduAPI
# Import LedManager as BaseLedManager to extend its functionality
from spherov2.sphero_edu import LedManager as BaseLedManager
# Import our new implementation of BOLTPLUS from our new library 
from sphero_unsw.toy.boltplus import BOLTPLUS
# Import our new implementation of BOLT from our new library
from sphero_unsw.toy.bolt import BOLT



# ------------------------------------------------------------------------- #
# [2] Create a new class LedManager that inherits from BaseLedManager
# ------------------------------------------------------------------------- #
class LedManager(BaseLedManager):
    """Extended LED manager for Sphero robots, supporting different models with specific LED configurations."""
    def __init__(self, cls):
        if cls is RVR:
            self.__mapping = {
                'front': ('left_headlight', 'right_headlight'),
                'main': ('left', 'right', 'front', 'back')
            }
        elif cls in (R2D2, R2Q5, BOLT, BOLTPLUS):
            self.__mapping = {'main': ('front', 'back')}
        else:
            self.__mapping = {}
        self.__leds = defaultdict(partial(Color, 0, 0, 0))

    def __setitem__(self, key, value):
        if key in self.__mapping:
            for led in self.__mapping[key]:
                self.__setitem__(led, value)
        else:
            self.__leds[key] = value

    def __getitem__(self, item):
        if item in self.__mapping:
            return self.__getitem__(self.__mapping[item][0])
        return self.__leds[item]

    def get(self, item, default):
        if item in self.__mapping:
            return self.get(self.__mapping[item][0], default)
        return self.__leds.get(item, default)

# ------------------------------------------------------------------------- #
# [3] Create a new class BaseSpheroEduAPI that inherits from BaseSpheroEduAPI
# ------------------------------------------------------------------------- #
class SpheroEduAPI(BaseSpheroEduAPI):
    """Implementation of Sphero Edu Javascript APIs: https://sphero.docsapp.io/docs/get-started"""

    def __init__(self, *args, **kwargs):
        """Initializes the SpheroEduAPI with a toy instance and sets up the LED manager."""
        super().__init__(*args, **kwargs)
        

    # overwrite this function to call the new __start_capturing_sensor_data function whcich supports BOLT+
    def __enter__(self):
        self.__stopped.clear()
        self.__thread = threading.Thread(target=self.__background)
        self.__toy.__enter__()
        self.__thread.start()
        try:
            self.__toy.wake()
            ToyUtil.set_robot_state_on_start(self.__toy)
            self.__start_capturing_sensor_data()
        except:
            self.__exit__(None, None, None)
            raise
        return self
    

    def set_stabilization(self, stabilize: bool):
        """Turns the stabilization system on and ``set_stabilization(false)`` turns it off.
        Stabilization is normally on to keep the robot upright using the Inertial Measurement Unit (IMU),
        a combination of readings from the Accelerometer (directional acceleration), Gyroscope (rotation speed),
        and Encoders (location and distance). When ``set_stabilization(false)`` and you power the motors,
        the robot will not balance, resulting in possible unstable behaviors like wobbly driving,
        or even jumping if you set the power very high. Some use cases to turn it off are:

        1. Jumping: Set Motor Power to max values and the robot will jump off the ground!
        2. Gyro: Programs like the Spinning Top where you want to to isolate the Gyroscope readings rather than having
           the robot auto balance inside the shell.

        When stabilization is off you can't use :func:`set_speed` to set a speed because it requires the control system
        to be on to function. However, you can control the motors using Motor Power with :func:`raw_motor` when
        the control system is off."""
        self.__stabilization = stabilize
        if isinstance(self.__toy, (Sphero, Mini, Ollie, BB8, BB9E, BOLT, BOLTPLUS)): 

            ToyUtil.set_stabilization(self.__toy, stabilize)


    def calibrate_compass(self):
        """
        Calibrates the compass
        """
        if isinstance(self.__toy, (BOLT, BOLTPLUS)): 
            self.__compass_zero = None
            ToyUtil.calibrate_compass(self.__toy)
            while self.__compass_zero is None:
                time.sleep(0.1)

    # Lights: control the color and brightness of LEDs on a robot.
    def set_main_led(self, color: Color):
        """Changes the color of the main LED light, or the full matrix on Sphero BOLT. Set this using RGB
        (red, green, blue) values on a scale of 0 - 255. For example, ``set_main_led(Color(r=90, g=255, b=90))``."""

        # For Spher BOLTPLUS, use set_matrix_fill to set the main LED color instead of set_main_led
        if isinstance(self.__toy, BOLTPLUS):
            self.set_matrix_fill(0, 0, 7, 7, color)
        else:
            self.__leds['main'] = bound_color(color, self.__leds['main'])
            ToyUtil.set_main_led(self.__toy, **self.__leds['main']._asdict(), is_user_color=False)

            
    def set_front_led(self, color: Color):
        """For Sphero RVR: Changes the color of RVR's front two LED headlights together.

        For Sphero BOLT, R2D2, R2Q5: Changes the color of the front LED light.

        Set this using RGB (red, green, blue) values on a scale of 0 - 255. For example, the magenta color is expressed
        as ``set_front_color(Color(239, 0, 255))``."""
        if isinstance(self.__toy, (R2D2, R2Q5, BOLT, BOLTPLUS, RVR)):     
            self.__leds['front'] = bound_color(color, self.__leds['front'])
            ToyUtil.set_front_led(self.__toy, **self.__leds['front']._asdict())

    def set_back_led(self, color: Union[Color, int]):
        """For older Sphero:
        Sets the brightness of the back aiming LED, aka the "Tail Light." This LED is limited to blue only, with a
        brightness scale from 0 to 255. For example, use ``set_back_led(255)`` to set the back LED to full brightness.
        Use :func:`time.sleep` to set it on for a duration. For example, to create a dim and a bright blink
        sequence use::

            set_back_led(0)  # Dim
            delay(0.33)
            set_back_led(255)  # Bright
            delay(0.33)

        For Sphero BOLT, R2D2, R2Q5:
        Changes the color of the back LED light. Set this using RGB (red, green, blue) values on a scale of 0 - 255.

        For Sphero RVR:
        Changes the color of the left and right breaklight LED light. Set this using RGB (red, green, blue) values
        on a scale of 0 - 255."""
        if isinstance(color, int):
            self.__leds['back'] = Color(0, 0, bound_value(0, color, 255))
            ToyUtil.set_back_led_brightness(self.__toy, self.__leds['back'].b)
        elif isinstance(self.__toy, (R2D2, R2Q5, BOLT, BOLTPLUS, RVR, Mini)):     
            self.__leds['back'] = bound_color(color, self.__leds['back'])
            ToyUtil.set_back_led(self.__toy, **self.__leds['back']._asdict())


    def register_matrix_animation(self, frames:List[List[List[int]]], palette:List[Color], fps:int, transition:bool):
        """
        Registers a matrix animation
        Frames is a list of frame. Each frame is a list of 8 row, each row is a list of 8 ints (from 0 to 15, index in color palette)
        palette is a list of colors
        fps
        transition to true if fade between frames
        """
        if isinstance(self.__toy, (BOLT, BOLTPLUS)): 
            frame_indexes = []
            for frame in frames:
                compressed_frame = []
                for idx in range(4):
                    for row_idx in range(7, -1, -1):
                        res = 0
                        for col_idx in range(8):
                            bit = (frame[row_idx][col_idx] & 1 << idx) >> idx
                            res |= bit << (7 - col_idx)
                        compressed_frame.append(res)
                ToyUtil.save_compressed_frame_player64_bit_frame(self.__toy, self.__frame_index, compressed_frame)
                frame_indexes.append(self.__frame_index)
                self.__frame_index += 1
            palette_colors = []
            for color in palette:
                palette_colors += list(color._asdict().values())
            ToyUtil.save_compressed_frame_player_animation(self.__toy, self.__animation_index, fps, transition, palette_colors, frame_indexes)
            self.__animation_index += 1

    def play_matrix_animation(self, animation_id, loop=True):
        """
        Plays a matrix animation
        """
        if isinstance(self.__toy, (BOLT, BOLTPLUS)): 
            ToyUtil.play_compressed_frame_player_animation_with_loop_option(self.__toy, animation_id, loop)

    def pause_matrix_animation(self):
        """
        Pause a matrix animation
        """
        if isinstance(self.__toy, (BOLT, BOLTPLUS)): 
            ToyUtil.pause_compressed_frame_player_animation(self.__toy)

    def clear_matrix(self):
        """
        Clears a matrix animation
        """
        if isinstance(self.__toy, (BOLT, BOLTPLUS)): 
            ToyUtil.reset_compressed_frame_player_animation(self.__toy)

    def resume_matrix_animation(self):
        """
        Resume a matrix animation
        """
        if isinstance(self.__toy, (BOLT, BOLTPLUS)): 
            ToyUtil.resume_compressed_frame_player_animation(self.__toy)

    def override_matrix_animation_framerate(self, fps: int = 0):
        """
        Overrides animation fps
        """
        if isinstance(self.__toy, (BOLT, BOLTPLUS)): 
            self.__fps_override = fps
            ToyUtil.override_compressed_frame_player_animation_global_settings(self.__toy, self.__fps_override, self.__fade_override)

    def override_matrix_animation_transition(self, option:FadeOverrideOptions = FadeOverrideOptions.NONE):
        """
        Override animations transition
        """
        if isinstance(self.__toy, (BOLT, BOLTPLUS)): 
            self.__fade_override = option
            ToyUtil.override_compressed_frame_player_animation_global_settings(self.__toy, self.__fps_override, self.__fade_override)

    def set_matrix_rotation(self, rotation:FrameRotationOptions):
        """
        Rotates the led matrix
        """
        if isinstance(self.__toy, (BOLT, BOLTPLUS)): 
            ToyUtil.set_matrix_rotation(self.__toy, rotation)

    def scroll_matrix_text(self, text: str, color: Color, fps: int, wait: bool):
        """
        Scrolls text on the matrix, with specified color.
        text max 25 characters
        Fps 1 to 30
        wait : if the programs wait until completion
        """
        # TODO Implement wait
        if isinstance(self.__toy, (BOLT, BOLTPLUS)): 
            ToyUtil.scroll_matrix_text(self.__toy, text, color, fps)

    def set_matrix_character(self, character:str, color:Color):
        """
        Sets a character on the matrix with color specified
        """
        if isinstance(self.__toy, (BOLT, BOLTPLUS)): 
            ToyUtil.set_matrix_character(self.__toy, character, color)

    def set_matrix_line(self, x1: int, y1: int, x2: int, y2: int, color: Color):
        """For Sphero BOLT: Changes the color of BOLT's matrix from x1,y1 to x2,y2 in a line. 8x8
        """
        if isinstance(self.__toy, (BOLT, BOLTPLUS)): 
            dx = x2 - x1
            dy = y2 - y1
            if (dx != 0 and dy != 0 and dx != dy) or (dx == 0 and dy == 0):
                raise Exception("Can only draw straight lines and diagonals")
            line_length = max(dx, dy)
            for line_increment in range(line_length):
                x_ = x1 + (dx / line_length) * line_increment
                y_ = x1 + (dx / line_length) * line_increment
                strMapLoc: str = str(x_) + ':' + str(y_)
                self.__leds[strMapLoc] = bound_color(color, self.__leds[strMapLoc])
            ToyUtil.set_matrix_line(self.__toy, x1, y1, x2, y2, color.r, color.g, color.b, is_user_color=False)

    def set_matrix_fill(self, x1: int, y1: int, x2: int, y2: int, color: Color):
        """For Sphero BOLT: Changes the color of BOLT's matrix from x1,y1 to x2,y2 in a box. 8x8
        """
        if isinstance(self.__toy, (BOLT, BOLTPLUS)): 
            x_min = min(x1, x2)
            x_max = max(x1, x2)
            y_min = min(y1, y2)
            y_max = max(y1, y2)
            for x_ in range(x_min, x_max + 1):
                for y_ in range(y_min, y_max + 1):
                    strMapLoc: str = str(x_) + ':' + str(y_)
                    self.__leds[strMapLoc] = bound_color(color, self.__leds[strMapLoc])
            ToyUtil.set_matrix_fill(self.__toy, x1, y1, x2, y2, color.r, color.g, color.b, is_user_color=False)



    # Sensors: Querying sensor data allows you to react to real-time values coming from the robots' physical sensors.
    def __start_capturing_sensor_data(self):
        if isinstance(self.__toy, RVR):
            sensors = ['accelerometer', 'gyroscope', 'imu', 'locator', 'velocity', 'ambient_light', 'color_detection']
            self.__sensor_name_mapping['imu'] = 'attitude'
        elif isinstance(self.__toy, BOLT):
            sensors = ["accel_one", 'accelerometer', 'ambient_light', 'attitude', "core_time", 'gyroscope', 'locator', "quaternion", 'velocity']
 
        elif isinstance(self.__toy, BOLTPLUS):
            sensors = ["accel_one", 'accelerometer', 'ambient_light', 'attitude', "core_time", 'gyroscope', 'locator', "quaternion", 'velocity']
        else:
            sensors = ['attitude', 'accelerometer', 'gyroscope', 'locator', 'velocity']
        ToyUtil.enable_sensors(self.__toy, sensors)
