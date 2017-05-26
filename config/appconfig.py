import os
import uuid
import json
import requests
import xml.etree.ElementTree as ET

# region Logging configuration
appname = 'plexlibpy'
log_dir = os.path.abspath(os.path.join(__file__, '..', '..', 'logs'))
# endregion


# region Plex configuration
plex_tv_url = 'https://plex.tv'
plex_config_file = os.path.abspath(os.path.join(__file__, '..', '..', '.plex'))
plex_token = None
plex_auth_url = auth_url = 'https://plex.tv/users/sign_in.json'
plex_headers = {
    'X-Plex-Product': 'Plex Library Util',
    'X-Plex-Version': '1.0',
    'X-Plex-Client-Identifier': str(uuid.uuid4())
}
# endregion

def load_plex_config():
    with open(plex_config_file, 'r') as f:
        config = json.loads(f.read())
    return config