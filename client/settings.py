
SERVER_URL = 'http://127.0.0.1:8080'

UPDATE_STATE_PERIOD = 1

ADD_LIMIT = 20
REMOVE_AFTER = 100

RETRY_PERIOD = 10

DEBUG = True

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

        'Running': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        },
        'GameClient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        },

    }
}

