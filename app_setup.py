import json
import os
import logging
import base64
from config import appconfig
import xml.etree.ElementTree as ET
import time
import sys

_args = None
_logger = logging.getLogger(__name__)

def setup_environment():
    try:
        import pip
    except ImportError as e:
        print(e)
        sys.exit(1)

    try: import virtualenv
    except ImportError:
        print('Installing virtualenv...')
        try:
            pip.main(['install', '--no-index',
                      '--find-links=%s' % appconfig.packages,
                      'virtualenv'])
            import virtualenv
        except ImportError:
            print('Cannot create environment.')
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)

    if not os.path.exists(appconfig.venv_dir):
        try:
            print('Creating venv...')
            virtualenv.create_environment(appconfig.venv_dir)
        except Exception as e:
            print(e)
            sys.exit(1)

    try:
        print('Activating virtualenv...')
        cmdfile = os.path.join(appconfig.venv_dir,
                               'bin' if sys.platform != 'win32' else 'Scripts',
                               'activate_this.py')
        with open(cmdfile) as f:
            exec(f.read(), {'__file__': cmdfile})
        print('Installing packages...')
        pip.main(['install', '--prefix', appconfig.venv_dir,
                  '--no-index', '--find-links=%s' % appconfig.packages,
                  '-r', 'requirements.txt'])
    except ImportError as e:
        print('Could not import required packages')
        print(e)
        sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)


def get_server_id(name=None):
    """
    Gets the machine identifier for the given plex server hostname
    :param name: plex server hostname
    :return: machine id associated with plex server hostname
    """
    try: import requests
    except ImportError:
        print('Could not import requests library')
        sys.exit(1)
    url = appconfig.plex_tv_url + '/pms/servers.xml'
    r = requests.get(url, headers=appconfig.plex_headers)
    machine_id = None
    xml = ET.fromstring(r.text)
    for server in xml.iter('Server'):
        if server.get('name') == name:
            machine_id = server.get('machineIdentifier')

    return machine_id


def run_setup(args):
    """
    Run the initial setup for the application
    :param args: applicaion arguments
    """
    _args = args
    if _args.v:
        _logger.setLevel(logging.DEBUG)

    print('Setting up the environment...')
    setup_environment()
    print('Environment setup complete.')

    try: from helpers import plex
    except ImportError as e:
        print(e)
        sys.exit(1)
    print('Running initial setup...')
    plex_info = {}
    username = input('Enter your plex.tv username: ')
    password = input('Enter your plex.tv password: ')
    plex_info['server_name'] = input('Enter your server name: ')
    plex_info['auth_string'] = (base64.b64encode((username + ':' + password).encode('utf-8'))).decode('utf-8')

    with open(appconfig.plex_config_file, 'w') as f:
        f.write(json.dumps(plex_info, indent=1))

    try:
        _logger.info('Authenticating to Plex...')
        plex.authenticate()
        _logger.info('Successfully authenticated to Plex')
    except Exception as e:
        _logger.error('Authentication failed.')
        _logger.exception(e)
        sys.exit(1)

    plex_info['server_id'] = get_server_id(plex_info['server_name'])
    appconfig.plex_server_id = plex_info['server_id']
    _logger.info('Server info:')
    _logger.info('%s:%s' % (plex_info['server_name'], plex_info['server_id']))
    with open(appconfig.plex_config_file, 'w') as f:
        f.write(json.dumps(plex_info, indent=1))

    time.sleep(2)
    print('')
    print('Initial setup is complete.')
    print('')
    print('Start the program via the following command:')
    print('\'nohup %s %s &\'' % (os.path.join(appconfig.venv_dir,
                                  'bin' if sys.platform != 'win32' else 'Scripts',
                                  'python' if sys.platform != 'win32' else 'python.exe'),
                     os.path.join(os.path.dirname(__file__), 'main.py')))