import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

import logging
import argparse
from helpers.utils import logger
import app_setup
from config import appconfig


_logger = logger.configure_logging(__name__, level='INFO')
_args = None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Turn on verbose logging', dest='v')
    parser.add_argument('--setup', action='store_true', dest='setup',
                        help='Run the initial setup for the application '
                             '(required before first use)')
    parser.add_argument('-p', '--port', metavar='<port_number>', type=int, dest='port',
                        help='Specify the port the server is accessible on')
    parser.add_argument('--test', action='store_true', dest='test',
                        help='Enable test mode', default=8080)
    _args = parser.parse_args()

    if _args.v:
        _logger.setLevel(logging.DEBUG)

    if _args.setup:
        app_setup.run_setup(_args)
    else:
        try:
            import plextool
            plextool.start(_args)
        except ImportError as e:
            print(e)
            print('')
            print('Make sure you have run the initial setup first via the \'--setup\' option.')
            sys.exit(1)


if __name__ == '__main__':
    main()