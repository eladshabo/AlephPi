import sys
import os
import os.path
import logging
import Config

class Logger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(Config.app_log_file)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def log_function_entry(self, function_args):
        self.logger.info(Config.log_function_entry_deco)
        self.logger.info(self.get_caller_name() + " started with args: " + str(function_args))

    def log_function_exit(self, instance_snapshot):
        self.logger.info(Config.log_function_exit_deco)
        self.logger.info(self.get_caller_name() + " exited")
        self.logger.debug("instance_snapshot: " + os.linesep + instance_snapshot)

    def get_caller_name(self):
        return sys._getframe(2).f_code.co_name

    def add_to_log(self, msg):
        self.logger.info(msg)

    def log_exception(self, excp_msg, instance_snapshot):
        self.logger.error(excp_msg + " instance_snapshot: " + instance_snapshot, exc_info=True)
