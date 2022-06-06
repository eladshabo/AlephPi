import os
import time
import subprocess
import configparser
from enum import Enum

from pygame import mixer

from . import Logger


class GameSound(Enum):
    """Proxy-Enum to be used for playing pre-defined sounds."""

    START_GAME = ("start_game",)
    GAME_OVER = ("game_over",)
    START_RECORD = ("start_record",)
    CORRECT_ANSWER = ("correct_answer",)
    INCORRECT_ANSWER = ("incorrect_answer",)
    GOOGLE_API_RECOGNITION_ERROR = ("google_api_recognition_error",)
    GOOGLE_API_TIMEOUT = ("google_api_timeout",)
    GOOGLE_API_REQUEST_ERROR = ("google_api_request_err",)
    FATAL_ERROR = ("fatal_error",)
    NO_INTERNET = "no_internet"


class Sound:
    """A Proxy-Class for pygame.mixer functionality - sound playing"""

    @Logger.log_function
    def __init__(self, config_audio_section: configparser.SectionProxy) -> None:
        """Constructs a Sound object, initiallizing the mixer for playback, and setting audio files.

        Attributes:
            correct_answers_folders (str): A path to a folder containing all the right answers audio files (to be played after the user said incorrect answer)
            audio_files (configparser.SectionProxy): configparser.SectionProxy for audio files. key = sound description, value = file path.

        Raises:
            EnvironmentError: In case of a mixer failure.
            FileNotFoundError: In case one of the audio file doesn't exists.
        """

        mixer.init()
        if not mixer.get_init():
            raise EnvironmentError("Cannot init sound controller - mixer init failed")

        self.correct_answers_folders = os.path.join("audio", "correct_answers")

        # Default audio files, in case a different file was supplied in the config file, override the file entry with config file input
        self.audio_files = {
            "start_game": os.path.join("audio", "start_game.mp3"),
            "game_over": os.path.join("audio", "game_over.mp3"),
            "start_record": os.path.join("audio", "start_record.mp3"),
            "correct_answer": os.path.join("audio", "correct_answer.mp3"),
            "incorrect_answer": os.path.join("audio", "incorrect_answer.mp3"),
            "google_api_recognition_error": os.path.join(
                "audio", "google_api_cant_understand.mp3"
            ),
            "google_api_timeout": os.path.join("audio", "google_api_timeout.mp3"),
            "google_api_request_err": os.path.join(
                "audio", "google_api_request_err.mp3"
            ),
            "fatal_error": os.path.join("audio", "fatal_error.mp3"),
            "no_internet": os.path.join("audio", "no_internet.mp3"),
        }

        for key in self.audio_files:
            if key in config_audio_section:
                self.audio_files[key] = config_audio_section[key]

            if not os.path.exists(self.audio_files[key]):
                raise FileNotFoundError(
                    f"Cannot find audio file {self.audio_files[key]}"
                )

        # Reset the sound card
        if (
            subprocess.call(["bash", "-c", "jack_control stop && jack_control start"])
            != 0
        ):
            raise EnvironmentError(
                "Cannot init sound card, try running jack_control command manually and make sure you have sufficient permissions."
            )

    @Logger.log_function
    def play_game_sound(self, sound: GameSound) -> None:
        """Play a pre-defined audio sound.

        Args:
            sound (GameSound): A key that describes the sound to be played.
        """
        self.play_audio_file(self.audio_files[GameSound.value])

    @Logger.log_function
    def play_audio_file(self, filepath: str) -> None:
        """Playing an audio file, while blocking the thread until sound is fully played.

        Args:
            filepath (str): path to an audio file to play.
        """
        mixer.music.load(filepath)
        mixer.music.play()

        # Make sure the mixer finished playing the audio file.
        # TODO: replace it with pygame.mixer.music.set_endevent()
        while mixer.music.get_busy():
            time.sleep(20)
        time.sleep(20)

    def __del__(self):
        mixer.quit()
