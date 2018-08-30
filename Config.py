#file pointers
dictionary_file_path = "dict.json"
google_json_file="/home/pi/Desktop/Aleph/RPi_board.json"

#audio files
audio_start_game = "audio/start.mp3"
audio_game_over = "audio/game_over.mp3"
audio_start_record = "audio/pop.mp3"
audio_correct_answer = "audio/correct.mp3"
audio_incorrect_answer = "audio/incorrect.mp3"
audio_error_google_api = "audio/error_recognize.mp3"
audio_fatal_error = "audio/fatal_error.mp3"
audio_no_internet = "audio/no_internet.mp3"


#speech recognition
google_environment_variable_name = "GOOGLE_APPLICATION_CREDENTIALS"
mic_name = "USB PnP Sound Device: Audio (hw:1,0)"
sample_rate = 48000
chunk_size = 2048
seconds_for_record = 2
unrecognized_folder = "unrecognized"
misdetection_folder = "misdetection"


#seven segments
use_seven_seg = True
serial_port = '/dev/serial0'
serial_bandwidth = 9600


#log
log_function_entry_deco = "===================>"
log_function_exit_deco = "<==================="
app_log_file = "log.txt"


#"look & feel" properties
lives = 4
demo_sleep_timeout = 1
blink_sleep_timeout = .1
