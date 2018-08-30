import Config
from Logger import Logger
from Sound import Sound
from Aleph import Aleph

from subprocess import call

start_button_gpio_pin = 38

letters_gpios_pins_dict = {
    3  : "aleph",
    5  : "bet",
    7  : "gimel",
    11 : "dalet",
    12 : "hey",
    13 : "vav",
    15 : "zayn",
    16 : "chet",
    18 : "tet",
    19 : "yud",
    21 : "kaf",
    22 : "lamed",
    23 : "mem",
    24 : "nun",
    26 : "samech",
    29 : "yain",
    31 : "peh",
    32 : "tzadik",
    33 : "kuf",
    35 : "resh",
    36 : "shin",
    37 : "tav"}

def main():
    try:
        logger = Logger()
        sound = Sound(logger)
        #start the game
        aleph = Aleph(logger,
                      letters_gpios_pins_dict,
                      start_button_gpio_pin,
                      Config.lives).run_game()

    except (EnvironmentError, IOError) as err:
        sound.play_audio_file(Config.audio_fatal_error).play()
        logger.log_exception(err, locals())


if __name__ == "__main__":
    main()
