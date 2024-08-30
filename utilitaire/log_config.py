import logging
import os.path
from logging import Filter
#from logging import config

self_path_from_utility = "log_config"
logsdirectory_path_from_utility = "data/logs"

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
        'debbuging_debug_only': {
            'format': '\t%(module)s - %(levelname)s: %(message)s (Line: %(lineno)d [%(funcName)s])',
        }
    },

    'handlers': {
        'console_debug_only': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'debbuging_debug_only',
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
            'filename': f'{logsdirectory_path_from_utility}/errors.log',
            'level': 'ERROR',
            'formatter': 'standard',
        },
        'file_util': {
            'class': 'logging.FileHandler',
            'filename': f'{logsdirectory_path_from_utility}/util.log',
            'level': 'INFO',
            'formatter': 'standard',
            'filters': ['util_filter'],
        },
        'file_op': {
            'class': 'logging.FileHandler',
            'filename': f'{logsdirectory_path_from_utility}/operation.log',
            'level': 'INFO',
            'formatter': 'short',
            'filters': ['operation_info_filter'],
        }
    },

    'loggers': {
        'main': {
            'handlers': ['file_error', 'file_util', 'file_op', 'console_op'],
            'level': 'DEBUG',
        },
        'debugging': {
            'handlers': ['console_info', 'console_debug_only'],
            'level': 'DEBUG',
        }
    },

    'filters': {
        'util_filter': {
            '()': f'{self_path_from_utility}.UtilFilter',
        },
        'operation_info_filter': {
            '()': f'{self_path_from_utility}.OperationFilter',
        },
        'only_debug_filter': {
            '()': f'{self_path_from_utility}.OnlyDebugFilter'
        }
    },
}


assert os.path.exists(logsdirectory_path_from_utility), f"Le dossier '{logsdirectory_path_from_utility}' n'existe pas ou n'est pas accessible."


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


if __name__ == '__main__':
    logging.config.dictConfig(config_dct)
    logger = logging.getLogger('main')
    logger.debug("Debugging message")
    logger.info("Information message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    logger.info("OP-Operation message")
