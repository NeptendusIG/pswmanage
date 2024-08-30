import logging
from logging import Filter

config_dct = {
    'version': 1,

    'disable_existing_loggers': False,

    'formatters': {
        'standard': {
            'format': '%(levelname)s (%(asctime)s): %(message)s',
        },
        'short': {
            'format': '%(levelname)s - %(message)s',
        },
        'message': {
            'format': '%(message)s',
        },
        'debbuging_info': {
            'format': '%(module)s - %(levelname)s: %(message)s (Line: %(lineno)d [%(funcName)s])',
        },
        'debbuging_debug': {
            'format': '    %(module)s - %(levelname)s: %(message)s (Line: %(lineno)d [%(funcName)s])',
        }
    },

    'handlers': {
        'console_debug': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'debbuging_debug',
            'filters': ['only_debug_filter'],
        },
        'console_info': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'debbuging_info',
        },
        'console_op': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'message',
            'filters': ['operation_info_filter']
        },
        'file_error': {
            'class': 'logging.FileHandler',
            'filename': 'logs/errors.log',
            'level': 'ERROR',
            'formatter': 'standard',
        },
        'file_util': {
            'class': 'logging.FileHandler',
            'filename': 'logs/util.log',
            'level': 'INFO',
            'formatter': 'standard',
            'filters': ['util_filter'],
        },
        'file_op': {
            'class': 'logging.FileHandler',
            'filename': 'logs/operation.log',
            'level': 'INFO',
            'formatter': 'short',
            'filters': ['operation_info_filter'],
        }
    },

    'loggers': {
        'main': {
            'handlers': ['file_error', 'file_util', 'console_op'],
            'level': 'DEBUG',
        },
        'debugging': {
            'handlers': ['console_info'],
            'level': 'DEBUG',
        },
        'debugging_v2': {
            'handlers': ['console_debug'],
            'level': 'DEBUG',
        }
    },

    'filters': {
        'util_filter': {
            '()': 'utilitaire.log_config.UtilFilter',
        },
        'operation_info_filter': {
            '()': 'utilitaire.log_config.OperationFilter',
        },
        'only_debug_filter': {
            '()': 'utilitaire.log_config.OnlyDebugFilter'
        }
    },
}


# Filtres
class UtilFilter(Filter):
    def filter(self, record):
        return "UTIL" in record.getMessage()


class OperationFilter(Filter):
    def filter(self, record):
        if "OP" in record.getMessage():
            record.msg = record.msg.replace("OP-", "OP -> ", 1)
            return True
        return False


class OnlyDebugFilter(Filter):
    def filter(self, record):
        return record.levelno == logging.DEBUG
