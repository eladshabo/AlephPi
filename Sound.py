import pygame

class Sound:
    def __init__(self, logger):
        logger.log_function_entry(locals())

        self.logger = logger
        pygame.mixer.init()
        if pygame.mixer.get_init() is None:
            raise EnvironmentError("Cannot init sound controller")

        self.logger.log_function_exit(str(self.__dict__))
        
    def play_audio_file(self, filepath):
        self.logger.log_function_entry(locals())

        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue
        
        self.logger.log_function_exit(str(self.__dict__))

    def __del__(self):       
        pygame.mixer.quit()
        
