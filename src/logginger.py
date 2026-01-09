import logging
from os import getlogin ,path

class Logging:

    def __init__(self, log_path):
        self.logging_file_path = path.join(log_path,'checking_log.log')
        try:
            self.username = getlogin()
        except:
            self.username = "Unknown User"


        logging.basicConfig(
            filename=self.logging_file_path, 
            filemode='a',
            level=logging.INFO, 
            format="%(asctime)s | %(levelname)s | %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S',
            encoding='utf-8' )
        
        self.logger = logging.getLogger(self.username)

    def warning(self,message):
        self.logger.warning(message)

    def error(self,message):
        self.logger.error(message)

    def info(self,message):
        self.logger.info(message)