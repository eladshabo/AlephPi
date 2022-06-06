#!/usr/bin/env python3.6

# Author: Elad Shabo
# Style Guide: Google Python Style Guide - https://github.com/google/styleguide/blob/gh-pages/pyguide.md
#
#
#           _            _     _____ _
#     /\   | |          | |   |  __ (_)
#    /  \  | | ___ _ __ | |__ | |__) |
#   / /\ \ | |/ _ \ '_ \| '_ \|  ___/ |
#  / ____ \| |  __/ |_) | | | | |   | |
# /_/    \_\_|\___| .__/|_| |_|_|   |_|
#                 | |
#                 |_|
#
#       AlephPi is a game built with RPi board for helping my kids recognizing alphabetical letters correctly in a more fun way.
#       For high-level view & BOM please refer to: https://github.com/eladshabo/AlephPi

import configparser
import logging
import RPi.GPIO as GPIO

from . import Logger, Sound, AlephGame, SpeechRecognition, SevenSegmentDisplay


def main():
    try:
        config = configparser.ConfigParser("aleph_config.ini")
        logger = Logger.setup_logger(config["Log"]["app_log_file"])

        # Read GPIOs config
        start_button_gpio_pin = config["Operative GPIOs"].getint("start_button", 38)
        blink_record_gpio_pin = config["Operative GPIOs"].getint("blink_record", 40)
        letters_gpios_pins_dict = {}

        for key in config["Letters GPIOs"]:
            # Convert the key to int so we won't need to parse it evertime we're working with GPIOs
            letters_gpios_pins_dict[int(key)] = config["Letters GPIOs"][key]

        sound = Sound(config["Audio Files"])
        speech_recognition = SpeechRecognition(
            logger, sound, config["Speech Recognition"]
        )
        seven_seg_config = config["Seven Segments LEDs"]
        seven_seg_display = None
        if seven_seg_config.getboolean("use_seven_seg", False):
            seven_seg_display = SevenSegmentDisplay(
                seven_seg_config.get("serial_port", "/dev/serial0"),
                seven_seg_config.getint("serial_bandwidth", 9600),
            )

        # Init board and run game
        aleph = AlephGame(
            sound,
            speech_recognition,
            letters_gpios_pins_dict,
            start_button_gpio_pin,
            blink_record_gpio_pin,
            config["Game Properties"].getint("lives", 4),
            seven_seg_display,
            config["Game Properties"].getint("demo_sleep_timeout", 1),
            config["Game Properties"].getfloat("blink_sleep_timeout", 0.1),
        )
        aleph.run_game()

    except Exception as err:
        if "sound" in locals() and sound:
            sound.play_game_sound(Sound.GameSound.FATAL_ERROR)
        if "logger" in locals() and logger:
            logger.log(logging.ERROR, err, locals())
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
