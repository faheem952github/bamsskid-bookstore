import sys
import logging
from pythonjsonlogger import jsonlogger


class LoggerFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(LoggerFormatter, self).add_fields(
            log_record, record, message_dict)
        log_record['severity'] = record.levelname


formatter = LoggerFormatter()
stream = logging.StreamHandler(stream=sys.stdout)
stream.setFormatter(formatter)

logger = logging.getLogger('store-api')
logger.setLevel(logging.INFO)
logger.addHandler(stream)
