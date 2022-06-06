import serial
from . import Logger


class SevenSegmentDisplay:
    """Represents a 7-segment display controlled by a serial port.
    This implementation is tailored to SparkFun 7-segment display - https://www.sparkfun.com/products/11441
    The 7-segment display is used to display the amount of "lives" the user still has before the game is over.

    Raises:
        EnvironmentError: In case the serial port cannot be opened.

    Attributes:
        serial: A serial.Serial instance for communicating with the display controller.

    """

    @Logger.log_function
    def __init__(self, serial_port: str, bandwidth: int) -> None:
        """Constructs SevenSegementDisplay, controlled by serial port.

        Args:
            serial_port (str, optional): COM port. Defaults to '/dev/serial0'.
            bandwidth (int, optional): serial bandwidth. Defaults to 9600.

        Raises:
            EnvironmentError: In case serial port initialization failed.
            Exception: In case serial port failed to transmit non-nulled messages
        """
        self.serial = serial.Serial(serial_port, bandwidth)
        if not self.serial.isOpen():
            raise EnvironmentError(
                f"Failed to open serial port - {serial_port}. Possible solutions - (1) Check if port is used by other process. (2) Make sure the correct port number is listed in the config file. (3) If you don't have 7-segment display, please disable it in the config file"
            )

        # Set brightness to max, check if serial port successfully writes non-zero messages
        if (self.serial.write(b"\x7A") != 0) and (self.serial.write(b"FFFFF") != 0):
            raise Exception(
                "Serial port didn't write commands properly to 7-segment display."
            )

    def __del__(self):
        self.close_connection()

    @Logger.log_function
    def clear_display(self) -> bool:
        """Clear display from any characters.

        Raises:
            EnvironmentError: In case the port is closed.

        Returns:
            bool: Clear succeeded.
        """
        if not self.serial.isOpen():
            raise EnvironmentError(
                f"Failed to communicate with serial port - {self.serial.name}. Port is closed."
            )

        # Clear serial display
        return self.serial.write(b"\x76") != 0

    @Logger.log_function
    def write_lives(self, lives: int) -> bool:
        """Write lives to display, writing lives as a joined string.

        Args:
            lives (int): The lives to be written.

        Returns:
            bool: Write succeeded.
        """
        if self.clear_display():
            # Generate lives string, so if lives = 4 --> "1234" will be written
            lives_str = "".join([str(i) for i in range(1, lives + 1)])
            return self.serial.write(lives_str.encode("utf-8")) != 0
        return False

    @Logger.log_function
    def close_connection(self) -> None:
        """Close the serial connection in case it's opened."""
        if self.serial.isOpen():
            self.serial.close()
