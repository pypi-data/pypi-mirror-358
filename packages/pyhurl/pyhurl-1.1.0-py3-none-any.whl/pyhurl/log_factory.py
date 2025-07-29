import logging.config
import os
from dotenv import load_dotenv


class LogFactory:
    load_dotenv()
    log_dir = os.getenv('PYHURL_LOG_DIR', 'logs/')
    os.makedirs(log_dir, exist_ok=True)

    logging_configs = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'norm': {
                'format': '[%(asctime)s] [%(thread)d] [%(levelname)s] %(filename)s:%(lineno)d - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'norm'
            }
        },
        'loggers': {}
    }

    __loggers = {
    }

    logging.config.dictConfig(logging_configs)

    @classmethod
    def get_logger(cls, name='app', filename=None):
        if name in cls.logging_configs['loggers']:
            return logging.getLogger(name)

        cls.config_logger(name, filename)

        return logging.getLogger(name)

    @classmethod
    def config_logger(cls, name, filename):
        if filename is None:
            filename = os.path.join(cls.log_dir, name + '.log')
        cls.logging_configs['handlers'][name] = {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': filename,
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 3,
            'formatter': 'norm',
            'encoding': 'utf8'
        }
        cls.logging_configs['loggers'][name] = {
            'handlers': ['console', name],
            'level': 'INFO',
            'propagate': False
        }
        logging.config.dictConfig(cls.logging_configs)
