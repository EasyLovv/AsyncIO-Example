from settings import DEBUG

import logging


class RequireDebug(logging.Filter):

    def __init__(self, debug=True):
        super().__init__()
        self.debug = debug

    def filter(self, record):
        return DEBUG is self.debug
