import io
import sys
import os
import os.path
import time

import json
import serial
import vlc
import Config
import SpeechRecognition
import SevenSegment
import RPi.GPIO as GPIO

class Aleph:

    def __init__(self, logger, letters_gpio_dict, start_button_gpio, lives):
        logger.log_function_entry(locals())
        self.logger = logger
        
        if Config.use_seven_seg:
            self.seven_segment = SevenSegment.SevenSegment(logger)
            self.seven_segment.write_lives(lives)

        self.speech_recognition = SpeechRecognition.SpeechRecognition(self.logger)
        self.letters_gpio_dict = letters_gpio_dict
        self.start_button_gpio = start_button_gpio
        self.kLives = lives
        self.lives = lives
        
        self.init_gpios()

        #prepare game methodology
        self.standby = True
        self.letter_selected = False
        self.current_letter_gpio = -1
        
        self.logger.log_function_exit(str(self.__dict__))

    def init_gpios(self):
        self.logger.log_function_entry(locals())
        GPIO.setmode(GPIO.BOARD)
        #set all letters to output
        for key in self.letters_gpio_dict.keys():
            GPIO.setup(key, GPIO.OUT)

        GPIO.setup(self.start_button_gpio, GPIO.IN)
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
        GPIO.add_event_detect(self.start_button_gpio, GPIO.FALLING, self.start_game_callback)
        i=0
        while self.standby:
            #demo #1 - blink all leds 3 times
            while self.standby and i < 3:
                self.turn_all_letters_gpios(GPIO.HIGH)
                time.sleep(Config.demo_sleep_timeout)
                self.turn_all_letters_gpios(GPIO.LOW)
                i += 1
            #demo #2 - turn on leds one by one
            for key in self.letters_gpio_dict.keys():
                if not self.standby:
                    self.turn_all_letters_gpios(GPIO.LOW)
                    return
                else:
                    GPIO.output(key, GPIO.HIGH)
                    time.sleep(Config.demo_sleep_timeout)
            #demo #3 - turn off leds one by one
            for key in self.letters_gpio_dict.keys():
                if not self.standby:
                    self.turn_all_letters_gpios(GPIO.LOW)
                    return
                else:
                    GPIO.output(key, GPIO.LOW)
                    time.sleep(Config.demo_sleep_timeout)
            
            i=0
        self.logger.log_function_exit(str(self.__dict__))

    def select_letter(self):
        self.logger.log_function_entry(locals())
        self.letter_selected = False
        GPIO.add_event_detect(self.start_button_gpio, GPIO.RISING, self.letter_selected_callback)
        vlc.MediaPlayer(Config.audio_start_file).play()
        while not self.letter_selected:
            for key in self.letters_gpio_dict.keys():
                if self.letter_selected:
                    return

                self.current_letter_gpio = key
                GPIO.output(key, GPIO.HIGH)
                time.sleep(Config.blink_sleep_timeout)
                GPIO.output(key, GPIO.LOW)
                time.sleep(Config.blink_sleep_timeout)
        self.logger.log_function_exit(str(self.__dict__))

    def game_over(self):
        self.logger.log_function_entry(locals())
        vlc.MediaPlayer(Config.audio_game_over_file).play()
        self.lives = self.kLives
        self.seven_segment.write_lives(self.lives)
        self.standby = True
        self.logger.log_function_exit(str(self.__dict__))

    def run_game(self):
        self.logger.log_function_entry(locals())
        while True:
            if self.standby:
                #blocking call until start button is pressed
                self.run_standby_demo()
            #wait for user to press the start again to select letter
            self.select_letter()
            #make sure the chosen letter is on
            GPIO.output(self.current_letter_gpio, GPIO.HIGH)
            #call Google API and get True or False result
            speech_hit = self.speech_recognition.recognize_speech(self.letters_gpio_dict[self.current_letter_gpio])
            if speech_hit:
                vlc.MediaPlayer(Config.audio_correct_answer).play()
            else:
                vlc.MediaPlayer(Config.audio_incorrect_answer).play()
                self.lives -= 1
                if Config.use_seven_seg:
                    self.seven_segment.write_lives(self.lives)

                if self.lives == 0:
                    self.game_over()
                    
        self.logger.log_function_exit(str(self.__dict__))
