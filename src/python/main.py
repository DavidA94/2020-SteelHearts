#!/usr/bin/python3

import serial
import serial.tools.list_ports

from controllers.StratusDuo import StratusDuo

TETRIX_MOTOR_SPEED_RANGE = (0, 200)
TETRIX_SET_MOTOR_IDENTIFIER = 0x10
TETRIX_WAITING_FOR_CONTROLLER_IDENTIFIER = b"\x05"  # Expected to be sent standalone
TETRIX_CONTROLLER_CONNECTED = b"\x06"  # Expected to be sent standalone


def main():
    serial_ports = serial.tools.list_ports.comports()
    serial_port = None
    for port in serial_ports:
        # I'm not 100% certain this is right for all tetrix controllers,
        # but it should eliminate the non-Tetrix one that is showing up for me
        if port.vid == 0x0403 and port.pid == 0x6001:
            serial_port = port
            break

    if serial_port is None:
        print("Failed to find a valid serial port. Try again")
        exit(1)

    tetrix = serial.Serial(port=serial_port.device, baudrate=9600)
    print("Successfully connected to tetrix serial.")
    print("Don't forget to press the green start button!")

    print("\n\nOpening connection to the controller")
    tetrix.write(TETRIX_WAITING_FOR_CONTROLLER_IDENTIFIER)
    controller = StratusDuo()
    tetrix.write(TETRIX_CONTROLLER_CONNECTED)

    while True:
        if not tetrix.isOpen():
            print("Need to reopen serial connection")
            tetrix.open()

        x, y = controller.get_left_joystick_xy_values(TETRIX_MOTOR_SPEED_RANGE)
        r, _ = controller.get_right_joystick_xy_values(TETRIX_MOTOR_SPEED_RANGE)

        data_to_send = bytearray([TETRIX_SET_MOTOR_IDENTIFIER, x, y, r])

        # print(data_to_send)
        tetrix.write(data_to_send)

        while tetrix.in_waiting:
            # print("Serial data says: ", end="")
            # print(str(x) + "\\t" + str(y) + "\\t" + str(r) + "\\t", end="")
            print(tetrix.readline())  # , end="")
            # print("  | Done")


if __name__ == "__main__":
    main()
