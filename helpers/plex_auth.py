import requests
from config import appconfig
import json
from config.appconfig import plex_headers
from helpers.utils import logger


_logger = logger.configure_logging(__name__, level='INFO')


def authenticate():
    """
    Authenticates with plex and sets the X-Plex-Token header
    """
    with open(appconfig.plex_config_file, 'r') as f:
        _plex_config = json.loads(f.read())

    headers = plex_headers
    headers['Authorization'] = 'Basic %s' % _plex_config['auth_string']
    r = requests.post(appconfig.plex_auth_url,
                      headers=headers)
    data = r.json()
    token = data['user']['authToken']
    appconfig.plex_headers['X-Plex-Token'] = token
    _logger.info('Plex token set: %s' % token)