
import time
import Config
from SpeechRecognition import SpeechRecognition
from SevenSegment import SevenSegment
import RPi.GPIO as GPIO

class Aleph:

    def __init__(self, logger, sound, letters_gpio_dict, start_button_gpio, start_button_led_gpio_pin, lives):
        logger.log_function_entry(locals())
        
        #init fields
        self.logger = logger
        self.sound = sound
        self.speech_recognition = SpeechRecognition(self.logger, self.sound)
        self.letters_gpio_dict = letters_gpio_dict
        self.start_button_gpio = start_button_gpio
        self.start_button_led_gpio_pin = start_button_led_gpio_pin
        self.kLives = lives
        self.lives = lives
        self.standby = True
        self.letter_selected = False
        self.current_letter_gpio = -1

        #init hardware
        if Config.use_seven_seg:
            self.seven_segment = SevenSegment(logger)
            self.seven_segment.write_lives(lives)
        self.init_gpios()      
        
        self.logger.log_function_exit(str(self.__dict__))

    def init_gpios(self):
        self.logger.log_function_entry(locals())

        GPIO.setmode(GPIO.BOARD)
        #set all letters to output
        for key in self.letters_gpio_dict.keys():
            GPIO.setup(key, GPIO.OUT)

        #set the start button. pull-down resistor should be soldered.
        GPIO.setup(self.start_button_gpio, GPIO.IN)
        GPIO.setup(self.start_button_led_gpio_pin, GPIO.OUT)

        self.logger.log_function_exit(str(self.__dict__))

    def start_game_callback(self, channel):
        self.logger.log_function_entry(locals())

        GPIO.remove_event_detect(self.start_button_gpio)
        self.standby = False

        self.logger.log_function_exit(str(self.__dict__))

    def letter_selected_callback(self, channel):
        self.logger.log_function_entry(locals())

        GPIO.remove_event_detect(self.start_button_gpio)
        self.letter_selected = True
        
        self.logger.log_function_exit(str(self.__dict__))

    def turn_all_letters_gpios(self, on):
        self.logger.log_function_entry(locals())

        if on:
            GPIO.output(list(self.letters_gpio_dict.keys()), GPIO.HIGH)
        else:
            GPIO.output(list(self.letters_gpio_dict.keys()), GPIO.LOW)
        
        self.logger.log_function_exit(str(self.__dict__))

    def run_standby_demo(self):
        self.logger.log_function_entry(locals())
        
        #run this demo function allong the start wasn't pressed
        GPIO.add_event_detect(self.start_button_gpio, GPIO.FALLING, self.start_game_callback, bouncetime=200)
        
        while self.standby:
            GPIO.output(self.start_button_led_gpio_pin, GPIO.LOW)

            #demo #1 - blink all leds 3 times
            for i in range(0,3):
                if not self.standby:
                    break
                self.turn_all_letters_gpios(GPIO.HIGH)
                time.sleep(Config.demo_sleep_timeout * 2)
                self.turn_all_letters_gpios(GPIO.LOW)

            #demo #2 - turn leds on one by one
            for key in self.letters_gpio_dict.keys():
                if not self.standby:
                    #reset all letters to off
                    self.turn_all_letters_gpios(GPIO.LOW)
                    break
                else:
                    GPIO.output(key, GPIO.HIGH)
                    time.sleep(Config.demo_sleep_timeout)

            #demo #3 - turn off leds one by one
            for key in self.letters_gpio_dict.keys():
                if not self.standby:
                    #reset all letters to off
                    self.turn_all_letters_gpios(GPIO.LOW)
                    break
                else:
                    GPIO.output(key, GPIO.LOW)
                    time.sleep(Config.demo_sleep_timeout)
            
        self.logger.log_function_exit(str(self.__dict__))

    def run_select_letter(self):
        self.logger.log_function_entry(locals())
        
        self.letter_selected = False
        GPIO.output(self.start_button_led_gpio_pin, GPIO.HIGH)

        #wait for the user to press the butten again to select letter
        GPIO.add_event_detect(self.start_button_gpio, GPIO.FALLING, self.letter_selected_callback, bouncetime=200)
        self.sound.play_audio_file(Config.audio_start_game)

        #run the leds on until user pressed the start button
        while not self.letter_selected:
            for key in self.letters_gpio_dict.keys():
                if self.letter_selected:
                    break
                #the bounce time insures it will give a valid value
                self.current_letter_gpio = key
                GPIO.output(key, GPIO.HIGH)
                time.sleep(Config.blink_sleep_timeout)
                GPIO.output(key, GPIO.LOW)
                time.sleep(Config.blink_sleep_timeout)

        GPIO.output(self.start_button_led_gpio_pin, GPIO.LOW)
        self.logger.log_function_exit(str(self.__dict__))

    def game_over(self):
        self.logger.log_function_entry(locals())

        self.sound.play_audio_file(Config.audio_game_over)
        #reset all game fields
        self.lives = self.kLives
        self.standby = True
        self.seven_segment.write_lives(self.lives)
        
        self.logger.log_function_exit(str(self.__dict__))

    def run_game(self):
        self.logger.log_function_entry(locals())
        
        while True:
            if self.standby:
                #blocking call until start button is pressed
                self.run_standby_demo()
            
            #wait for the user to press start button again in order to select letter
            self.run_select_letter()
            #make sure the chosen letter is on
            GPIO.output(self.current_letter_gpio, GPIO.HIGH)
            #call Google API and get True or False.
            hit, exception_occurred = self.speech_recognition.recognize_letter(self.letters_gpio_dict[self.current_letter_gpio], self.start_button_led_gpio_pin) #send the alphabetical verb of the letter
            if exception_occurred:
                self.turn_all_letters_gpios(False)
                #continue the game, without updating the lives, the user already got sound feedback from internal exceptions
                continue

            if hit:
                self.sound.play_audio_file(Config.audio_correct_answer)
                self.turn_all_letters_gpios(False)
            else:
                self.sound.play_audio_file(Config.audio_incorrect_answer)
                self.turn_all_letters_gpios(False)
                self.lives -= 1
                if Config.use_seven_seg:
                    self.seven_segment.write_lives(self.lives)
                if 0 == self.lives:
                    self.game_over()

        self.logger.log_function_exit(str(self.__dict__))
