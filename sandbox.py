import logging.config
import utilitaire.log_config as log

logging.config.dictConfig(log.config_dct)
logger = logging.getLogger('debugging_v2')



logger.info('TEST: START')
logger.debug('TEST: debug')
