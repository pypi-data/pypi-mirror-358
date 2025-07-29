"""
This module implements extended functionality of spherov2.commands.sensor to support Sphero BOLT+ robot.

# ====================================================================
# Authors: Kathryn Kasmarik, Reda Ghanem
# Version 0.1.7
# School of Systems and Computing, UNSW Canberra
# ==================================================================== 

"""


# ------------------------------------------------------------------------- #
# [1] Import necessary libraries
# ------------------------------------------------------------------------- #


# Import all necessary classes and functions from spherov2.commands.sensor
from spherov2.commands.sensor import *
# Import Sensor as BaseSensor to extend its functionality
from spherov2.commands.sensor import Sensor as BaseSensor




# ------------------------------------------------------------------------- #
# [2] Create a new class Sensor that inherits from BaseSensor
# ------------------------------------------------------------------------- #

class Sensor(BaseSensor):

    def __init__(self, *args, **kwargs):
        """
        Initialize the Sensor class with the same parameters as BaseSensor.
        """
        super().__init__(*args, **kwargs)
    

    # @staticmethod
    # def configure_collision_detection(toy, collision_detection_method: CollisionDetectionMethods,
    #                                   x_threshold, y_threshold, x_speed, y_speed, dead_time, proc=None):
    #     toy._execute(Sensor._encode(
    #         toy, 17, proc, [collision_detection_method, x_threshold, y_threshold, x_speed, y_speed, dead_time]))
        


    # ------------------------------------------------------------------------- #
    # [3] Create a new function to find toys of type BOLT+
    # ------------------------------------------------------------------------- #
    @staticmethod
    def __collision_detected_notify_helper(listener, packet):
        # unpacked = struct.unpack('>3hB3hBL', packet.data)           # this is the original line not working
        unpacked = struct.unpack('>3hB3hBh', packet.data)
        listener(CollisionDetected(acceleration_x=unpacked[0] / 4096, acceleration_y=unpacked[1] / 4096,
                                   acceleration_z=unpacked[2] / 4096, x_axis=bool(unpacked[3] & 1),
                                   y_axis=bool(unpacked[3] & 2), power_x=unpacked[4], power_y=unpacked[5],
                                   power_z=unpacked[6], speed=unpacked[7], time=unpacked[8] / 1000))

    collision_detected_notify = (24, 18, 0xff), __collision_detected_notify_helper.__func__
  

    # @staticmethod
    # def enable_collision_detected_notify(toy, enable: bool, proc=None):  # Untested
    #     toy._execute(Sensor._encode(toy, 20, proc, [int(enable)]))

    # @staticmethod
    # def configure_sensitivity_based_collision_detection(
    #         toy, method: SensitivityBasedCollisionDetectionMethods, level: SensitivityLevels, i,  # unknown name
    #         proc=None):
    #     toy._execute(Sensor._encode(toy, 71, proc, data=[method, level, *to_bytes(i, 2)]))

    # @staticmethod
    # def enable_sensitivity_based_collision_detection_notify(toy, enable, proc=None):
    #     toy._execute(Sensor._encode(toy, 72, proc, data=[int(enable)]))

    # sensitivity_based_collision_detected_notify = (24, 73, 0xff), lambda listener, p: listener(to_int(p.data))
