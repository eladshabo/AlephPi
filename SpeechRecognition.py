import os
import json
import time
import threading
import logging
import configparser
from typing import List, Tuple

import RPi.GPIO as GPIO
import speech_recognition as sr
import requests

from . import Logger, Sound


class SpeechRecognition:
    """Responsible for recording user, submitting the audio file to Google for recognition and analyzing the result.

    Attributes:
        recognizer (speech_recognition.Recognizer): Google API recognizer.
        microphone (speech_recognition.Microphone): Google API microphone instance. This microphone will capture the user's input and use recognizer to recognize it.

    """

    @Logger.log_function
    def __init__(
        self,
        logger: logging.Logger,
        sound: Sound,
        config_sr_section: configparser.SectionProxy,
    ) -> None:
        """_summary_

        Args:
            logger (logging.Logger): Logger instance for logging all Google's result and failures.
            sound (Sound): Sound instance for playing sounds, giving the user the approperiate feedback - success / failure / internal error.
            config_sr_section (dict): Configuration file Speech Recognition section. Will override defaults.

        Raises:
            IOError: In case the required JSON file with the recognition options wasn't found.
        """
        self.logger = logger
        self.sound = sound
        self._listening = False
        self.recognition_options = None

        self._recognition_options_file_path = "recognition_options.json"
        # Google credentails file
        self._google_json_file = "/home/pi/Desktop/RPi_board.json"
        self._google_environment_variable_name = "GOOGLE_APPLICATION_CREDENTIALS"  # Environment variable name, to be used by SpeechRecognition.
        self._google_recognition_language = "he-IL"
        self._mic_name = "USB PnP Sound Device: Audio (hw:1,0)"
        self._sample_rate = 48000
        self._chunk_size = 2048
        self._seconds_for_record = 2
        self._unrecognized_folder = "unrecognized"
        self._misdetection_folder = "misdetection"

        # Override default values with config values
        for key in config_sr_section:
            self.__dict__[f"_{key}"] = config_sr_section[key]

        # Set the environment variable to google API
        os.environ[self._google_environment_variable_name] = self._google_json_file

        # Init recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.energy_threshold = 400

        # Init mic
        mic_list = sr.Microphone.list_microphone_names()
        for i, microphone_name in enumerate(mic_list):
            if microphone_name == self._mic_name:
                mic_device_index = i
                break

        self.microphone = sr.Microphone(
            device_index=mic_device_index,
            sample_rate=int(
                self._sample_rate
            ),  # Parse to int - if value was pulled from config file its type is str.
            chunk_size=int(self._chunk_size),
        )

        # Load correct answers dictionary file
        if os.path.isfile(self._recognition_options_file_path):
            with open(self._recognition_options_file_path) as json_file:
                self.recognition_options = json.load(json_file)
        else:
            raise IOError(
                f"JSON file with valid recognition options wasn't found - {self._recognition_options_file_path}"
            )

    @Logger.log_function
    def recognize_letter(
        self, current_letter: str, listening_led_gpio_pins: List[int]
    ) -> Tuple[bool, bool]:
        """Records the user, recognizing its input, and returns if it's matching the current letter.

        Args:
            current_letter (str): The verbal value of the selected letter by the user. (for example: "aleph")
            listening_led_gpio_pins (List[int]): List of GPIOs - the current letter GPIO + the push button GPIO.

        Raises:
            EnvironmentError: In case the record wasn't successful / No internet connection.

        Returns:
            Tuple[bool, bool]: A tuple with 2 boolean arguments - (1) if the user said the letter correctly. (2) if some internal exception occourd.
        """
        # Return values - will be returned in any case.
        hit = False
        exception_occurred = True

        # Ensure we have google environment and internet connetion before calling google's API
        if os.environ[self._google_environment_variable_name] is None:
            raise EnvironmentError(
                f"Missing {self._google_environment_variable_name} environment variable wasn't found"
            )

        if not self.connected_to_internet():
            raise EnvironmentError("No internet connection")

        # Start the logic - open mic, record user, and send audio to Google for recognition
        speech_result = ""
        # Signal the user he can start talking
        self.sound.play_game_sound(Sound.GameSound.START_RECORD)
        try:
            # Record the user
            with self.microphone as mic:
                self._listening = True
                # Signaling the user that record has started by blinking the letter's and the push button LEDs
                threading.Thread(
                    target=self.blink_listening_led, args=(listening_led_gpio_pins,)
                ).start()
                audio_file = self.recognizer.listen(
                    mic, timeout=2, phrase_time_limit=int(self._seconds_for_record)
                )
                self._listening = False
            # Call google API for recognizing the audio file
            speech_result = self.recognizer.recognize_google(
                audio_file, language=self._google_recognition_language
            )

        # Cannot reach google services / not enough credit for recognition
        except sr.RequestError as ex:
            self.sound.play_game_sound(Sound.GameSound.GOOGLE_API_REQUEST_ERROR)
            self.logger.log(
                logging.ERROR,
                f"Could not request results from Google Speech Recognition service; {ex}",
                str(self.__dict__),
            )

        # Cannot recognize sound
        except sr.UnknownValueError as ex:
            self.sound.play_game_sound(Sound.GameSound.GOOGLE_API_RECOGNITION_ERROR)
            self.save_record(self._unrecognized_folder, audio_file, current_letter)
            self.logger.log_exception(
                logging.ERROR,
                f"Google API could not understand audio - {ex}",
                str(self.__dict__),
            )

        # Google took too long to response (connection closed?)
        except sr.WaitTimeoutError as ex:
            self.sound.play_game_sound(Sound.GameSound.GOOGLE_API_TIMEOUT)
            self.logger.log_exception(
                logging.ERROR, f"Got TIMEOUT exception - {ex}", str(self.__dict__)
            )

        # Parse result
        else:
            exception_occurred = False
            self.logger.log(
                logging.INFO,
                f"Google API returned: {speech_result}, current letter turn on is: {current_letter}",
            )

            if not speech_result:
                self.logger.log(
                    logging.ERROR,
                    "Google returned empty string, saving the record to unrecognized folder",
                )
                self.save_record(self._unrecognized_folder, audio_file, current_letter)

            else:
                if speech_result in self._recognition_options_file_path:
                    if (
                        current_letter
                        == self._recognition_options_file_path[speech_result]
                    ):
                        hit = True
                    else:
                        self.logger.log(
                            logging.INFO,
                            f"Got {speech_result} which is not defined in the json dictionary file, saving the record to misdetection folder",
                        )
                        self.save_record(
                            self._misdetection_folder, audio_file, current_letter
                        )

        finally:
            self._listening = False
            return hit, exception_occurred

    @Logger.log_function
    def save_record(
        self, folder: str, audio_file: speech_recognition.AudioData, expected: str
    ) -> None:
        """Saving the audio file for a later debug.

        Args:
            folder (str): folder path to save the audio file to.
            audio_file (speech_recognition.AudioData): The recorded file.
            expected (str): The verbal value of the letter in the selected GPIO.
        """
        folder_path = os.path.join(os.getcwd(), folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Name the audio file with the timestamp and expected result for later debug
        debug_audio_file = os.path.join(
            folder_path,
            f"{time.strftime('%x').replace('/','_')}_{time.strftime('%X')}_expected_{expected}.wav",
        )
        with open(debug_audio_file, "wb") as file:
            file.write(audio_file.get_wav_data())

    @Logger.log_function
    def connected_to_internet(self, url="https://www.google.com/", timeout=2) -> bool:
        """Detects if the PC has a valid internet connection.

        Args:
            url (str, optional): Url to be used for detecting internet connection. Defaults to 'https://www.google.com/'.
            timeout (int, optional): timeout for the test. Defaults to 2.

        Returns:
            bool: _description_
        """
        connected = True
        try:
            _ = requests.get(url, timeout=timeout)
        except requests.ConnectionError:
            connected = False
            self.sound.play_game_sound(Sound.GameSound.NO_INTERNET)
        return connected

    @Logger.log_function
    def blink_listening_led(self, listening_led_gpio_pins: List[int]) -> None:
        """Blinking the LEDs of the selected letter and the game push button. To be called in a new thread.

        Args:
            listening_led_gpio_pins (List[int]): The GPIOs to tuggle.
        """
        while self._listening:
            GPIO.output(listening_led_gpio_pins, GPIO.HIGH)
            time.sleep(0.2)
            GPIO.output(listening_led_gpio_pins, GPIO.LOW)
            time.sleep(0.2)
