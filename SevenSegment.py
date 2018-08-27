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
            raise FileNotFoundError("Failed to open serial port " + Config.serial_port)

        #set brightness to max
        self.serial.write(b"\x7A")
        self.serial.write("FFFFF")
        
        self.logger.log_function_exit(str(self.__dict__))

    def write_lives(self, lives):
        self.logger.log_function_entry(locals())
        #clear serial display
        self.serial.write(b"\x76")

        i=0
        lives_str=""
        #write 0000 lives
        while i < lives:
            lives_str += Config.lives_char
            i += 1
        self.serial.write(lives_str.encode('utf-8'))
        self.logger.log_function_exit(str(self.__dict__))

    def close_connection(self):
        self.logger.log_function_entry(locals())
        if self.serial.isOpen():
            self.serial.close()
        self.logger.log_function_exit(str(self.__dict__))
