import logging
import os
from datetime import datetime
from config import appconfig
import sys


# region Various logging default settings
today = datetime.today().strftime('%Y%m%d')
_pid = os.getpid()
_valid_logging_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
_log_filename = '%s_%s_%s.log' % (appconfig.appname, _pid, today)
_log_file = os.path.join(appconfig.log_dir, _log_filename)
_log_message_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s> %(message)s')
# endregion

# Local logger instance for this file
_logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setFormatter(_log_message_format)
_logger.addHandler(ch)
if '-v' in sys.argv or '--verbose' in sys.argv:
    _logger.setLevel(logging.DEBUG)
else:
    _logger.setLevel(logging.INFO)


def configure_logging(name, level='INFO', format=None, file=None):
    """
    Configures the logger for the file that calls this function
    :param name: Name of the logger
    :param level: Level of log messages to output [Default: INFO]
    :param format: (Optional) logging.Formatter formatted string 
                    [Default: %(asctime)s - %(name)s - %(levelname)s> %(message)s]
    :param file: (Optional) The file path & name to log messages to 
                    [Default: <project_dir>/logs/linetracker_<pid>_<YYMMDD>.log
    :return: a configured instance of logging.Logger
    """
    logger = logging.getLogger(name)

    # region Set logging level
    # Ensure a valid logging level has been passed in
    if level.upper() not in _valid_logging_levels:
        logger.setLevel(logging.DEBUG)
        _logger.debug('Logging level "%s" is not a valid logging level' % level)
        _logger.debug('Valid logging levels are: %s' % _valid_logging_levels)
    else:
        _logger.debug('Setting logging level to %s for %s' % (level, name))
        logger.setLevel(getattr(logging, level.upper()))
    # endregion

    # region Check the 'logs' dir exists for the FileHandler
    file_logging_enabled = True
    try:
        os.makedirs(appconfig.log_dir)
    except PermissionError as e:
        _logger.debug('Could not create logging directory at %s' % appconfig.log_dir)
        _logger.exception(e)
        _logger.debug('Logging to console stream only...')
        file_logging_enabled = False
    except FileExistsError as e:
        pass

    # endregion


    # region Handler configuration
    handlers = []

    # Create the console stream handler
    ch = logging.StreamHandler()
    handlers.append(ch)

    # Create the file stream handler if no errors with logging directory/file
    if file_logging_enabled:
        if file is not None:
            fh = logging.FileHandler(os.path.abspath(file))
        else:
            fh = logging.FileHandler(_log_file)
        handlers.append(fh)

    for h in handlers:
        if format is not None:
            h.setFormatter(logging.Formatter(format))
        else:
            h.setFormatter(_log_message_format)
        # Add the handler to the logger instance
        logger.addHandler(h)

    # endregion

    return logger