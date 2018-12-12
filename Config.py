#file pointers
dictionary_file_path = "dict.json"
google_json_file="/home/pi/Desktop/RPi_board.json"

#audio files
audio_start_game = "audio/start_game.mp3"
audio_game_over = "audio/game_over.mp3"
audio_start_record = "audio/start_record.mp3"
audio_correct_answer = "audio/correct_answer.mp3"
audio_incorrect_answer = "audio/incorrect_answer.mp3"
audio_google_api_cant_understand = "audio/google_api_cant_understand.mp3"
audio_google_api_timeout = "audio/google_api_timeout.mp3"
audio_google_api_request_err = "audio/google_api_request_err.mp3"
audio_fatal_error = "audio/fatal_error.mp3"
audio_no_internet = "audio/no_internet.mp3"
audio_correct_answers_folders = "audio/correct_answers"


#speech recognition
google_environment_variable_name = "GOOGLE_APPLICATION_CREDENTIALS"
google_recognition_language = "he-IL"
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
