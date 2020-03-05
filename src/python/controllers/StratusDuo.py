import time
import usb.core
import usb.util

import utils
from controllers.ButtonData import ButtonData
from controllers.Controller import Controller


class StratusDuo(Controller):
    # --- Eight Way Button ---
    BUTTONS_EIGHT_WAY_UP = ButtonData(2, 1 << 0)
    BUTTONS_EIGHT_WAY_DOWN = ButtonData(2, 1 << 1)
    BUTTONS_EIGHT_WAY_LEFT = ButtonData(2, 1 << 2)
    BUTTONS_EIGHT_WAY_RIGHT = ButtonData(2, 1 << 3)
    # --- Buttons in the middle (backward, forward, joystick buttons) ---
    BUTTONS_FORWARD = ButtonData(2, 1 << 4)
    BUTTONS_BACKWARD = ButtonData(2, 1 << 5)
    BUTTONS_JOYSTICK_LEFT = ButtonData(2, 1 << 6)
    BUTTONS_JOYSTICK_RIGHT = ButtonData(2, 1 << 7)
    # --- Top Buttons (L1, R1) ---
    BUTTONS_L1 = ButtonData(3, 1 << 0)
    BUTTONS_R1 = ButtonData(3, 1 << 1)
    # --- Home Button ---
    BUTTONS_HOME = ButtonData(3, 1 << 2)
    # --- Letter Buttons ---
    BUTTONS_A = ButtonData(3, 1 << 4)
    BUTTONS_B = ButtonData(3, 1 << 5)
    BUTTONS_X = ButtonData(3, 1 << 6)
    BUTTONS_Y = ButtonData(3, 1 << 7)
    # --- Trigger Buttons (L2, R2) ---
    BUTTONS_L2 = ButtonData(4, 0b11111111)  # Not a shared value
    BUTTONS_R2 = ButtonData(5, 0b11111111)  # Not a shared value
    # --- Left Joystick ---
    JOYSTICK_LEFT_X_LOW_BYTE = ButtonData(6, 0b11111111)
    JOYSTICK_LEFT_X_HIGH_BYTE = ButtonData(7, 0b11111111)
    JOYSTICK_LEFT_Y_LOW_BYTE = ButtonData(8, 0b11111111)
    JOYSTICK_LEFT_Y_HIGH_BYTE = ButtonData(9, 0b11111111)
    # --- Right Joystick ---
    JOYSTICK_RIGHT_X_LOW_BYTE = ButtonData(10, 0b11111111)
    JOYSTICK_RIGHT_X_HIGH_BYTE = ButtonData(11, 0b11111111)
    JOYSTICK_RIGHT_Y_LOW_BYTE = ButtonData(12, 0b11111111)
    JOYSTICK_RIGHT_Y_HIGH_BYTE = ButtonData(13, 0b11111111)

    USB_INTERFACE = 0
    JOYSTICK_RANGE = (-32768, 32767)  # Range of a signed short
    DEAD_ZONE = 500  # Ignore any values of [-500, 500]
    MAX_ZONE = 30000  # Assume anything above/below 30000/-30000 is full speed

    # The "Nothing is on" array for if the controller stops responding
    # The controller might stop responding for two reasons:
    # 1. The controller has been disconnected somehow
    # 2. The controller has no new data (very likely)
    #    The controller will only have data to be read when there is a change,
    #    so if the joysticks aren't being held, there won't be data. There's a
    #    small chance that we read so fast that there won't be data yet, which
    #    is why we allow a certain number of failures
    NO_DATA_ARRAY = bytearray([0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    READ_TIMEOUT = 60  # Based on experimentation
    MAX_FAILURES = 3  # With the timeout, this means we should have an ~180ms response time

    def __init__(self):
        self.dev = None
        self.endpoint = None

        self.last_data = StratusDuo.NO_DATA_ARRAY
        self.get_bytes_failure_count = 0

        while True:
            try:
                self.dev = usb.core.find(idVendor=0x1038, idProduct=0x1430)
                if self.dev is None:
                    # This hopefully means the device is turning on
                    print("\rUnable to find Stratus Duo device                        ", end="")
                    continue

                endpoint = self.dev[0][(0, 0)][0]
                self.endpoint_address = endpoint.bEndpointAddress
                self.endpoint_max_packet_size = endpoint.wMaxPacketSize

                if self.dev.is_kernel_driver_active(StratusDuo.USB_INTERFACE):
                    self.dev.detach_kernel_driver(StratusDuo.USB_INTERFACE)

                usb.util.claim_interface(self.dev, StratusDuo.USB_INTERFACE)

                data = self.dev.read(self.endpoint_address, self.endpoint_max_packet_size)
                if len(data) != 0:
                    print("\rController connected                                                     ")
                    break
            except usb.core.USBError as e:
                # If we get a timeout error, we're okay, it's from the read.
                if e.errno == 110:
                    print("\rController connected                                                     ")
                    break

                print("\rWaiting for controller to be connected -- Error " + str(e.errno) + ": " + str(e.strerror),
                      end="                    ")

                # If it wasn't connected, then once it does, we need to get a new handle
                self.dev = None
                time.sleep(1)

    def get_bytes(self):
        """
        Gives back an array of bytes like the following:
        array('B', [0, 20, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        """
        try:
            # Store the data in case we need to use it again due to a one-off failure
            self.last_data = self.dev.read(
                self.endpoint_address,
                self.endpoint_max_packet_size,
                StratusDuo.READ_TIMEOUT)

            # Reset how many failures we have gotten since the last valid data
            self.get_bytes_failure_count = 0
            return self.last_data
        except usb.core.USBError as e:
            if self.get_bytes_failure_count >= StratusDuo.MAX_FAILURES:
                return StratusDuo.NO_DATA_ARRAY
            else:
                self.get_bytes_failure_count = self.get_bytes_failure_count + 1
                return self.last_data

    def get_left_joystick_xy_values(self, desired_range: (int, int)):
        data = self.get_bytes()

        x = Controller._get_short_button(
            data,
            StratusDuo.JOYSTICK_LEFT_X_LOW_BYTE,
            StratusDuo.JOYSTICK_LEFT_X_HIGH_BYTE)
        y = Controller._get_short_button(
            data,
            StratusDuo.JOYSTICK_LEFT_Y_LOW_BYTE,
            StratusDuo.JOYSTICK_LEFT_Y_HIGH_BYTE)

        x = StratusDuo.__joystick_zone_adjustment(x)
        y = StratusDuo.__joystick_zone_adjustment(y)

        x = int(utils.translate(x, StratusDuo.JOYSTICK_RANGE, desired_range))
        y = int(utils.translate(y, StratusDuo.JOYSTICK_RANGE, desired_range))

        return x, y

    def get_right_joystick_xy_values(self, desired_range: (int, int)):
        data = self.get_bytes()
        x = Controller._get_short_button(
            data,
            StratusDuo.JOYSTICK_RIGHT_X_LOW_BYTE,
            StratusDuo.JOYSTICK_RIGHT_X_HIGH_BYTE)
        y = Controller._get_short_button(
            data,
            StratusDuo.JOYSTICK_RIGHT_Y_LOW_BYTE,
            StratusDuo.JOYSTICK_RIGHT_Y_HIGH_BYTE)

        x = int(utils.translate(x, StratusDuo.JOYSTICK_RANGE, desired_range))
        y = int(utils.translate(y, StratusDuo.JOYSTICK_RANGE, desired_range))

        return x, y

    @staticmethod
    def __joystick_zone_adjustment(value: int):
        """
        Takes into account the DEAD_ZONE and MAX_ZONE and adjusts the number if needed
        :param value: The value to adjust
        :return: The adjusted value
        """
        abs_value = abs(value)
        if abs_value < StratusDuo.DEAD_ZONE:
            return 0
        elif abs_value > StratusDuo.MAX_ZONE:
            return StratusDuo.JOYSTICK_RANGE[1] * (-1 if value < 0 else 1)

        return value
