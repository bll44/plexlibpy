import json
import logging
import base64
from config import appconfig
import requests
import xml.etree.ElementTree as ET
from helpers import plex_auth
from helpers.utils import logger
import time

_args = None
_logger = logger.configure_logging(__name__, level='INFO')

def get_server_id(name=None):
    """
    Gets the machine identifier for the given plex server hostname
    :param name: plex server hostname
    :return: machine id associated with plex server hostname
    """
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
        plex_auth.authenticate()
        _logger.info('Successfully authenticated to Plex')
    except Exception as e:
        _logger.info('Authentication failed.')
        _logger.exception(e)

    plex_info['server_id'] = get_server_id(plex_info['server_name'])
    _logger.info('Server info:')
    _logger.info('%s:%s' % (plex_info['server_name'], plex_info['server_id']))
    with open(appconfig.plex_config_file, 'w') as f:
        f.write(json.dumps(plex_info, indent=1))

    time.sleep(2)
    print('')
    print('Initial setup is complete.')