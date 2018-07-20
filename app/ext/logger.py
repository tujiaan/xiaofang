import logging

from app.utils.tools import ContextualFilter


class Logger:
    def __init__(self, app=None, **kwargs):
        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        request_handler = logging.FileHandler('request.log', encoding='UTF-8')
        request_handler.setLevel(logging.INFO)
        logging_format = logging.Formatter("%(utcnow)s\t%(levelname)s\t%(ip)s\t%(method)s\t%(url)s\t%(message)s")
        request_handler.setFormatter(logging_format)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)

        app.logger.addFilter(ContextualFilter())
        app.logger.setLevel(logging.DEBUG)
        app.logger.addHandler(request_handler)
        app.logger.addHandler(stream_handler)

        default_handler = logging.FileHandler('flask.log', encoding='UTF-8')
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.addHandler(default_handler)


logger = Logger()
