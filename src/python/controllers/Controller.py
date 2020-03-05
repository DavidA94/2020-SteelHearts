from controllers.ButtonData import ButtonData


# Only implementing what is needed, as it's needed
class Controller:
    """
    An abstract interface for a controller, with some common helper methods
    """

    def get_bytes(self):
        """
        Gets the raw bytes from the controller
        :return: An array of bytes
        """
        pass

    def get_left_joystick_xy_values(self, desired_range):
        """
        Gets the left joystick values in the form of (x, y)
        :param desired_range: The range to convert the x,y values to, such as (-100, 100)
        :return: A tuple with (x, y)
        """
        pass

    def get_right_joystick_xy_values(self, desired_range: (int, int)):
        """
        Gets the right joystick values in the form of (x, y)
        :param desired_range: The range to convert the x,y values to, such as (-100, 100)
        :return: A tuple with (x, y)
        """
        pass

    @staticmethod
    def _get_boolean_button(array: bytearray, button_data: ButtonData):
        """
        Gets the boolean value of a button
        :param array: The array with the full raw data from the controller
        :param button_data: The information about the button
        :return: True/False
        """
        return (array[button_data.array_index] & button_data.bit_mask) > 0

    @staticmethod
    def _get_byte_button(array: bytearray, button_data: ButtonData):
        """
        Gets the unsigned byte value of a button
        :param array: The array with the full raw data from the controller
        :param button_data: The information about the button
        :return: [0, 255]
        """
        return (array[button_data.array_index] & button_data.bit_mask) > 0

    @staticmethod
    def _get_short_button(array: bytearray, low_button_data: ButtonData, high_button_data: ButtonData):
        """
        Gets the value of a button which has two bytes passed in
        :param array: The array with the full raw data from the controller
        :param low_button_data: The information about the button, for the lower byte
        :param high_button_data: The information about the button for the higher byte
        :return: A signed short
        """
        # Assuming nobody is passing in a non-8-bit value to this method
        # These take the value from the array index, and then throw the bit mask
        # on the given value. Probably the bit mask is always 0xFF, but doing it just in case
        low_value = array[low_button_data.array_index] & low_button_data.bit_mask
        high_value = array[high_button_data.array_index] & high_button_data.bit_mask

        unsigned_short = (high_value << 8) | low_value

        # https://stackoverflow.com/a/37095855
        signed_short = (unsigned_short ^ 0x8000) - 0x8000

        return signed_short
