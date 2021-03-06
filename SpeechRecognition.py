import os
import os.path
from subprocess import call
import Config
import json
import speech_recognition as sr
import time
import requests
import threading
import RPi.GPIO as GPIO

class SpeechRecognition:
    
    def __init__(self, logger, sound):
        logger.log_function_entry(locals())
        
        self.logger = logger
        self.sound = sound
        self.listening = False
        #reset the sound card
        call(["jack_control", "stop"])
        call(["jack_control", "start"])

        #set the environment variable to google API       
        os.environ[Config.google_environment_variable_name] = Config.google_json_file
        
        #init the recognizer
        self.recognizer = sr.Recognizer()
        mic_list = sr.Microphone.list_microphone_names()
        for i, microphone_name in enumerate(mic_list):
            if microphone_name == Config.mic_name:
                mic_device_index = i
        self.microphone = sr.Microphone(device_index = mic_device_index, sample_rate = Config.sample_rate, chunk_size = Config.chunk_size)
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.energy_threshold = 400


        #load json dictionary file
        if os.path.isfile(Config.dictionary_file_path):
            with open(Config.dictionary_file_path) as json_file:
                self.json_dict = json.load(json_file)
        else:
            raise IOError("json dictionary file not found: " + json_dict_file_path)

        self.logger.log_function_exit(str(self.__dict__))

    def recognize_letter(self, current_letter, listening_led_gpio_pins):
        self.logger.log_function_entry(locals())
        
        #return values
        hit = False
        exception_occurred = True

        #ensure we have google environment and internet connetion before calling google API
        if os.environ[Config.google_environment_variable_name] is None:
            raise EnvironmentError("Missing " + Config.google_environment_variable_name + " environment variable")
        
        if not self.connected_to_internet():
            raise EnvironmentError("No internet connection")
        
        speech_result=""
        
        #give the user feedback he can start talking
        self.sound.play_audio_file(Config.audio_start_record)
       
        try:
             #start recording
             self.logger.add_to_log("Say something")
             print("Say something")
             with self.microphone as mic:
                 print("speech_recognition threshold before: " + str(self.recognizer.energy_threshold))
                 #self.recognizer.adjust_for_ambient_noise(mic)
                 print("speech_recognition threshold after: " + str(self.recognizer.energy_threshold))
                 self.listening = True
                 t = threading.Thread(target=self.blink_listening_led, args=(listening_led_gpio_pins,))
                 t.start()
                 audio_file = self.recognizer.listen(mic, timeout=2, phrase_time_limit=Config.seconds_for_record)
                 self.listening = False
             #call google API
             speech_result = self.recognizer.recognize_google(audio_file, language=Config.google_recognition_language)
            
        #cannot reach google services / not enough credit for recognition
        except sr.RequestError as e:
            self.sound.play_audio_file(Config.audio_google_api_request_err)
            self.logger.log_exception("Could not request results from Google Speech Recognition service; {0}".format(e), str(self.__dict__))
            return hit, exception_occurred
        
        #cannot understand sound                
        except sr.UnknownValueError:
            self.sound.play_audio_file(Config.audio_google_api_cant_understand)
            self.save_record(Config.unrecognized_folder, audio_file, current_letter)
            self.logger.log_exception("Google API could not understand audio", str(self.__dict__))
            return hit, exception_occurred

        #google took too long to response (connection closed?)
        except sr.WaitTimeoutError as e:
            self.sound.play_audio_file(Config.audio_google_api_timeout)
            self.logger.log_exception("Got TIMEOUT exception; {0}".format(e), str(self.__dict__))
            return hit, exception_occurred

        finally:
            #even if exception was thrown during the record
            self.listening = False
                 
        #parse result
        exception_occurred = False
        if speech_result == "":
            self.logger.add_to_log("Google returned empty string, saving the record to unrecognized folder")
            self.save_record(Config.unrecognized_folder, audio_file, current_letter)
            self.logger.log_function_exit(str(self.__dict__))
            return hit, exception_occurred

        print("Google API returned: " + speech_result)
        print("Current letter turn on is: " + current_letter)

        if speech_result in self.json_dict.keys():               
            if current_letter == self.json_dict[speech_result]:
                hit = True
            else:
                hit = False
                self.logger.add_to_log("Got " + speech_result + " which is not defined in the json dictionary file, saving the record to misdetection foler")
                self.save_record(Config.misdetection_folder, audio_file, current_letter)
                
        self.logger.log_function_exit(str(self.__dict__))
        return hit, exception_occurred
    
    def save_record(self, folder, audio_file, expected):
        self.logger.log_function_entry(locals())
        
        folder_path=os.getcwd() + "/" + folder
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        with open(folder_path + "/" + time.strftime("%x").replace("/","_") + "_" + time.strftime("%X") + "_expected_" + expected + ".wav",'wb') as file:
            file.write(audio_file.get_wav_data())

        self.logger.log_function_exit(str(self.__dict__))
        
    def connected_to_internet(self, url='https://www.google.com/', timeout=2):
        self.logger.log_function_entry(locals())
        
        connected = True
        try:
            _ = requests.get(url, timeout=timeout)
        except requests.ConnectionError:
            connected = False
            self.sound.play_audio_file(Config.audio_no_internet)
        
        self.logger.log_function_exit(str(self.__dict__))
        return connected

    def blink_listening_led(self, listening_led_gpio_pins):
        while self.listening:
            print("Listening!")
            GPIO.output(listening_led_gpio_pins, GPIO.HIGH)
            time.sleep(.2)
            GPIO.output(listening_led_gpio_pins, GPIO.LOW)
            time.sleep(.2)