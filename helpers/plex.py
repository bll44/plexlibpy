from helpers.utils import logger
import json
from config import appconfig
import requests
from config.appconfig import plex_headers


_logger = logger.configure_logging(__name__, level='INFO')


def load_plex_config():
    try:
        with open(appconfig.plex_config_file, 'r') as f:
            config = json.loads(f.read())
    except FileNotFoundError as e:
        _logger.error('Cannot load the plex configuration. Have you run the initial setup '
                      'by running this application with the "--setup" switch?')
        raise
    return config


def authenticate():
    """
    Authenticates with plex and sets the X-Plex-Token header
    """
    _plex_config = load_plex_config()

    headers = plex_headers
    headers['Authorization'] = 'Basic %s' % _plex_config['auth_string']
    try:
        r = requests.post(appconfig.plex_auth_url,
                          headers=headers)
        if r.status_code == 401:
            raise Exception('Invalid login information.')
    except Exception as e:
        _logger.exception(e)
        raise
    data = r.json()
    token = data['user']['authToken']
    appconfig.plex_headers['X-Plex-Token'] = token
    _logger.info('Plex token set: %s' % token)