import Aleph
import vlc
import Config
import Logger
from subprocess import call

start_button_gpio_pin = 38
reset_button_gpio_pin = 40

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
                
        #start the game
        aleph = Aleph.Aleph(Logger.Logger(),
                            letters_gpios_pins_dict,
                            start_button_gpio_pin,
                            Config.lives).run_game()

    except (EnvironmentError) as err:
        print(err)
        vlc.MediaPlayer("audio/fatal_error.mp3").play()
        #logger.error(err, exc_info=True)

    finally:
        call(["jack_control", "stop"])

if __name__ == "__main__":
    main()
