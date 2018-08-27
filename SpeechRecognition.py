
import io
import os
import os.path
import vlc
from subprocess import call
import Config
import json
import speech_recognition as sr
import time



class SpeechRecognition:

    def __init__(self, logger):
        logger.log_function_entry(locals())
        self.logger = logger
        
        #reset the sound card
        call(["jack_control", "stop"])
        call(["jack_control", "start"])
        
        os.environ[Config.google_environment_variable_name] = Config.google_json_file

        #init the recognizer
        self.recognizer = sr.Recognizer()
        mic_list = sr.Microphone.list_microphone_names()
        for i, microphone_name in enumerate(mic_list):
            if microphone_name == Config.mic_name:
                self.device_id = i

        #load json dictionary file
        if os.path.isfile(Config.dictionary_file_path):
            with open(Config.dictionary_file_path) as json_file:
                self.json_dict = json.load(json_file)
        else:
            raise FileNotFoundError("JSON dictionary file not found: " + json_dict_file_path)

        self.logger.log_function_exit(str(self.__dict__))


    def call_google_api(self, current_letter):
        self.logger.log_function_entry(locals())
        #ensure Google env is set, otherwise GoogleAPI will throw exception
        if os.environ[Config.google_environment_variable_name] is None:
            raise EnvironmentError("[ERROR] : Missing " + Config.google_environment_variable_name + " environment variable")
        
        
        response=""
        with sr.Microphone(device_index = self.device_id, sample_rate = Config.sample_rate, chunk_size = Config.chunk_size) as source:
            self.recognizer.adjust_for_ambient_noise(source)
            vlc.MediaPlayer(Config.audio_start_record).play()
            print "Say Something"
            audio_file = self.recognizer.listen(source, timeout=Config.seconds_for_record)
            try:
                response = self.recognizer.recognize_google(audio_file, language="he-IL")
                print "you said: " + response
            except sr.UnknownValueError:
                vlc.MediaPlayer(Config.audio_error_google_api).play()
                self.add_unrecognized_file(audio_file, current_letter)
                print "Failure: Speech Recognition could not understand audio"
            except sr.RequestError as e:
                vlc.MediaPlayer(Config.audio_error_google_api).play()
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
            except sr.WaitTimeoutError as e:
                vlc.MediaPlayer(Config.audio_error_google_api).play()
                print("Got TIMEOUT exception; {0}".format(e))


        self.logger.log_function_exit(str(self.__dict__))
        print "response="
        print response
        return response

    def recognize_speech(self, current_letter):
        self.logger.log_function_entry(locals())
        speech_result = self.call_google_api(current_letter)

        if speech_result: 
            if speech_result in self.json_dict.keys():
                self.logger.log_function_exit(str(self.__dict__))
                return current_letter == self.json_dict[speech_result]
            else:
                print "got " + speech_result + " which is not defined in the json dictionary file"
                vlc.MediaPlayer(Config.audio_error_google_api).play()
                #add to learning folder
        else: #speech_result=""
            print "GOOGLE_API returned empty string"
            vlc.MediaPlayer(Config.audio_error_google_api).play()

        self.logger.log_function_exit(str(self.__dict__))
    
    def add_unrecognized_file(self, audio_file, current_letter_gpio):
        folder_path=os.getcwd() + "/" + Config.unrecognized_folder
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        with open(folder_path + "/" + time.strftime("%x").replace("/","_") + "_" + time.strftime("%X") + "_" + current_letter_gpio + ".wav",'w') as file:
            file.write(audio_file.get_wav_data())
        
