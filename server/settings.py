
SERVER_LISTEN_ADDRESS = '0.0.0.0'
SERVER_LISTEN_PORT = 8080

DEBUG = True

FIELD_SIZE = (20, 20)

REDIS = {
    'HOST': '127.0.0.1',
    'PORT': 6379,
    'PASSWORD': None,
    'DB': 0
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {

        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s.%(funcName)s:%(lineno)s %(process)d %(thread)d %(message)s'
        },

        'simple': {
            'format': '%(levelname)s %(message)s'
        }

    },
    'filters': {

        'require_debug_false': {
            '()': 'logger_utils.filters.RequireDebug',
            'debug': False
        },
        'require_debug_true': {
            '()': 'logger_utils.filters.RequireDebug',
            'debug': True
        }

    },

    'handlers': {

        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['require_debug_true']
        }

    },

    'loggers': {

        'TestServer': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        },

        'http_handlers': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True
        }

    }
}
