import os
import uuid
import json

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
plex_server_id = None
plex_shared_servers_url = 'https://plex.tv/api/servers/%s/shared_servers'
plex_users_url = 'https://plex.tv/api/users'
# endregion