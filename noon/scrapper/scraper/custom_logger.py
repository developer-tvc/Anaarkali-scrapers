import logging

class Logger:
    def __init__(self, log_file='error.log'):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.ERROR)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.ERROR)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log_error(self, message):
        self.logger.error(message)


