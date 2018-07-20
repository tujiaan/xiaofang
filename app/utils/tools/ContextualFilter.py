import logging
from datetime import datetime

from flask import request


class ContextualFilter(logging.Filter):
    def filter(self, log_record):
        log_record.utcnow = (datetime.utcnow()
            .strftime('%Y-%m-%d %H:%M:%S,%f %Z'))
        log_record.url = request.path
        log_record.method = request.method
        log_record.ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        return True
