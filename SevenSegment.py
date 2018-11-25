import io
import os
import os.path
import serial
import Config


class SevenSegment:

    def __init__(self, logger):
        logger.log_function_entry(locals())

        self.logger = logger
        self.serial = serial.Serial(Config.serial_port, Config.serial_bandwidth)
        if not self.serial.isOpen():
            raise EnvironmentError("Failed to open serial port " + Config.serial_port + " try disabling serial port in config file")

        #set brightness to max
        self.serial.write(b"\x7A")
        self.serial.write(b"FFFFF")
        
        self.logger.log_function_exit(str(self.__dict__))

    def __del__(self):
        self.close_connection()

    def write_lives(self, lives):
        self.logger.log_function_entry(locals())

        #clear serial display
        self.serial.write(b"\x76")        
        lives_str=""
        for i in range(1, lives + 1):
            lives_str += str(i)
        self.serial.write(lives_str.encode('utf-8'))

        self.logger.log_function_exit(str(self.__dict__))

    def close_connection(self):
        self.logger.log_function_entry(locals())

        if self.serial.isOpen():
            self.serial.close()

        self.logger.log_function_exit(str(self.__dict__))
