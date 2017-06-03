import os
import uuid
import json
import sys

# region Logging configuration
appname = 'plexlibpy'
log_dir = os.path.abspath(os.path.join(__file__, '..', '..', 'logs'))
# endregion

# region Plex configuration
plex_config_file = os.path.abspath(os.path.join(__file__, '..', '..', '.plex'))
plex_token = None
plex_server_id = None
plex_headers = {
    'X-Plex-Product': 'Plex Library Util',
    'X-Plex-Version': '1.0',
    'X-Plex-Client-Identifier': str(uuid.uuid4())
}
# Plex urls
plex_tv_url = 'https://plex.tv'
plex_auth_url = auth_url = plex_tv_url + '/users/sign_in.json'
plex_shared_servers_url = plex_tv_url + '/api/servers/%s/shared_servers'
plex_users_url = plex_tv_url + '/api/users'
plex_libraries_url = plex_tv_url + '/api/servers/%s'
# endregion

# region Setup config
venv_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'venv'))
packages = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pkg'))
# endregion