#!/usr/bin/env python3.6
import os
import time
import Logger
import configparser
import RPi.GPIO as GPIO

from . import SpeechRecognition, SevenSegmentDisplay, Sound


class AlephGame:
    """AlephGame is the actual manager for this game. It initialize the GPIOs and taking care for the game logic - standby mode / game mode - selecting letter / updating lives according to answers.

    Attributes:
        sound (Sound): Sound instanse to play sounds as feedback to user.
        speech_recognition (SpeechRecognition): SpeechRecognition instance to call Google's speech recognition API
        letters_gpio_dict (dict): Dictionary of GPIO pin and it's alphabetical letter.
        start_button_gpio (int): GPIO pin for start button. when pressed Aleph will leave standby mode.
        start_button_led_gpio_pin (int): Under the big red dome button we have 3 LEDs for indicating the user we're recording his input. When record in progress those LEDs will blink.
        kLives (int): The initial lives the user has. Every game cycle the lives counter is set to this value.
        seven_segment (SevenSegmentDisplay): SevenSegmentDisplay instance controlled by serial port.
        lives (int): The current game lives count. When 0 the game is over.
        demo_sleep_timeout (int): Timeout to be used when tuggeling LEDs in demo mode.
        blink_sleep_timeout (int): Timeout for running letters GPIO LEDs after the user pressed start in the first time, and the user needs to press start again for selecting specific letter.

    """

    @Logger.log_function
    def __init__(
        self,
        sound: Sound,
        speech_recognition: SpeechRecognition,
        letters_gpio_dict: dict,
        start_button_gpio: int,
        start_button_led_gpio_pin: int,
        lives: int,
        seven_segment: SevenSegmentDisplay,
        demo_sleep_timeout: int,
        blink_sleep_timeout: float,
    ) -> None:
        """Constructs AlephGame instance, validating all GPIOs are correctly set.

        Args:
            See Attributes section in class docstring
        """

        self.sound = sound
        self.speech_recognition = speech_recognition
        self.letters_gpio_dict = letters_gpio_dict
        self.start_button_gpio = start_button_gpio
        self.start_button_led_gpio_pin = start_button_led_gpio_pin
        self.kLives = lives
        self.seven_segment = seven_segment
        self.lives = lives
        self.demo_sleep_timeout = demo_sleep_timeout
        self.blink_sleep_timeout = blink_sleep_timeout

        self._standby = True
        self._letter_selected = False
        self._current_letter_gpio = -1

        # Init hardware
        if seven_segment:
            self.seven_segment.write_lives(lives)
        self.init_gpios()

    @Logger.log_function
    def init_gpios(self) -> None:
        """Initialize all GPIOs in their approperiate state."""
        # Use RPI standard GPIO legend
        GPIO.setmode(GPIO.BOARD)
        # Set letters GPIOs to output
        for key in self.letters_gpio_dict.keys():
            GPIO.setup(key, GPIO.OUT)

        # Set the start button (firewalled by pull-down resistor)
        GPIO.setup(self.start_button_gpio, GPIO.IN)
        GPIO.setup(self.start_button_led_gpio_pin, GPIO.OUT)

    @Logger.log_function
    def start_game_callback(self, channel: int) -> None:
        """A callback function to be run when the user presses the start button #1st time. Signals the main loop to exit standby mode.

        Args:
            channel (int): N/A. required by GPIO API.
        """
        GPIO.remove_event_detect(self.start_button_gpio)
        self._standby = False

    @Logger.log_function
    def letter_selected_callback(self, channel: int) -> None:
        """A callback function to be run when the user presses the start button #2nd time (selected letter).

        Args:
            channel (int): N/A. required by GPIO API.
        """
        GPIO.remove_event_detect(self.start_button_gpio)
        self._letter_selected = True

    @Logger.log_function
    def turn_all_letters_gpios(self, on: bool) -> None:
        """Tuggle all letters GPIO pins to state

        Args:
            on (bool): The state to be set to all letters GPIOs
        """
        GPIO.output(list(self.letters_gpio_dict.keys()), GPIO.HIGH if on else GPIO.LOW)

    @Logger.log_function
    def run_standby_demo(self) -> None:
        """Run standby mode, tuggle LED's slowly, signaling the user we're waiting for his START signal"""
        # Run this demo in standby mode, until the start button is pressed
        GPIO.add_event_detect(
            self.start_button_gpio,
            GPIO.FALLING,
            self.start_game_callback,
            bouncetime=200,
        )

        while self._standby:
            GPIO.output(self.start_button_led_gpio_pin, GPIO.LOW)

            # Demo #1 - Blink all leds 3 times
            for i in range(0, 3):
                # User pressed start during the previous iteration.
                if not self._standby:
                    break
                self.turn_all_letters_gpios(GPIO.HIGH)
                time.sleep(self.demo_sleep_timeout * 2)
                self.turn_all_letters_gpios(GPIO.LOW)

            # Demo #2 - Turn leds on one by one
            for key in self.letters_gpio_dict.keys():
                if not self._standby:
                    # Clear all GPIOs signals from demo mode, reset all letters to off - game is starting.
                    self.turn_all_letters_gpios(GPIO.LOW)
                    break
                else:
                    GPIO.output(key, GPIO.HIGH)
                    time.sleep(self.demo_sleep_timeout)

            # Demo #3 - Turn leds off one by one
            for key in self.letters_gpio_dict.keys():
                if not self._standby:
                    # Clear all GPIOs signals from demo mode, reset all letters to off - game is starting.
                    self.turn_all_letters_gpios(GPIO.LOW)
                    break
                else:
                    GPIO.output(key, GPIO.LOW)
                    time.sleep(self.demo_sleep_timeout)

    @Logger.log_function
    def run_select_letter(self) -> None:
        """User pressed START, start tuggling LEDs and wait for his letter selection."""
        self._letter_selected = False
        GPIO.output(self.start_button_led_gpio_pin, GPIO.HIGH)

        # Wait for the user to press the button again to select letter, the bounce time insures it will give a valid value
        GPIO.add_event_detect(
            self.start_button_gpio,
            GPIO.FALLING,
            self.letter_selected_callback,
            bouncetime=200,
        )
        self.sound.play_game_sound(Sound.GameSound.START_GAME)

        # Run the LEDs on until user pressed the start button
        while not self._letter_selected:
            for key in self.letters_gpio_dict.keys():
                if self._letter_selected:
                    break
                self._current_letter_gpio = key
                GPIO.output(key, GPIO.HIGH)
                time.sleep(self.blink_sleep_timeout)
                GPIO.output(key, GPIO.LOW)
                time.sleep(self.blink_sleep_timeout)

        GPIO.output(self.start_button_led_gpio_pin, GPIO.LOW)

    @Logger.log_function
    def game_over(self) -> None:
        """Indicate to user that game is over (lives reached to 0)"""
        self.sound.play_game_sound(Sound.GameSound.GAME_OVER)
        # Reset all game fields
        self.lives = self.kLives
        self._standby = True
        self.seven_segment.write_lives(self.lives)

    @Logger.log_function
    def run_game(self) -> None:
        """Main entry point to run game, running standby mode until START is pressed, tuggling all GPIO letters waiting for 2nd START signal, and detecting if user recognized selected letter correctly."""
        while True:
            if self._standby:
                # Blocking call until start button is pressed
                self.run_standby_demo()

            # Wait for the user to press start button again in order to select letter
            self.run_select_letter()
            # Make sure the chosen letter is on
            GPIO.output(self._current_letter_gpio, GPIO.HIGH)
            correct_ans, exception_occurred = self.speech_recognition.recognize_letter(
                # Send the alphabetical verb of the letter
                self.letters_gpio_dict[self._current_letter_gpio],
                [self.start_button_led_gpio_pin, self._current_letter_gpio],
            )
            if exception_occurred:
                self.turn_all_letters_gpios(False)
                # Continue the game without updating the lives, internal fault occurred, not related to user input.
                # The user got sound feedback from internal exceptions so nothing required here.
                continue

            # Answer was correct
            if correct_ans:
                self.sound.play_game_sound(Sound.GameSound.CORRECT_ANSWER)
                # Clean lettes LEDs, prepare to next iteration.
                self.turn_all_letters_gpios(False)

            else:
                GPIO.output(self._current_letter_gpio, GPIO.HIGH)
                self.sound.play_game_sound(Sound.GameSound.INCORRECT_ANSWER)
                # Play the correct answer - help the user to learn the correct answer.
                self.sound.play_audio_file(
                    os.path.join(
                        self.sound.correct_answers_folders,
                        f"{self.letters_gpio_dict[self._current_letter_gpio]}.mp3",
                    )
                )
                # Clean lettes LEDs, prepare to next iteration.
                self.turn_all_letters_gpios(False)
                self.lives -= 1
                if self.seven_segment:
                    self.seven_segment.write_lives(self.lives)
                if 0 == self.lives:
                    self.game_over()
