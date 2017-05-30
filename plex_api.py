from config import appconfig
from helpers.utils import logger
import requests
import xml.etree.ElementTree as ET


_logger = logger.configure_logging(__name__, level='INFO')
shared_servers = None

def share(data):
    global shared_servers
    print(data)
    get_shared_servers()
    url = appconfig.plex_shared_servers_url % appconfig.plex_server_id
    for user_id, libs in data.items():
        try:
            ss = shared_servers[user_id]
        except KeyError:
            ss = None
        if ss is not None:
            url += '/%s' % ss
            payload = {
                'server_id': appconfig.plex_server_id,
                'shared_server': {
                    'library_section_ids': libs
                }
            }
            r = requests.put(url, headers=appconfig.plex_headers, json=payload)
            print('ran update')
            if r.status_code == 200:
                print('Successfully shared libraries with %s' % user_id)
        else:
            payload = {"server_id": appconfig.plex_server_id,
                       "shared_server": {"library_section_ids": libs, "invited_id": user_id}}
            r = requests.post(url, headers=appconfig.plex_headers, json=payload)
            if r.status_code == 200:
                print('Successfully shared libraries with %s' % user_id)


def unshare(data):
    global shared_servers
    get_shared_servers()
    url = appconfig.plex_shared_servers_url % appconfig.plex_server_id
    for user_id, libs in data.items():
        try:
            ss = shared_servers[user_id]
        except KeyError:
            ss = None
        if ss is not None:
            url += '/%s' % ss
            r = requests.delete(url, headers=appconfig.plex_headers)
            if r.status_code == 200:
                print('Successfully unshared libraries with %s' % user_id)
        else:
            print('There are no libraries shared with %s' % user_id)

def get_shared_servers():
    global shared_servers
    url = appconfig.plex_shared_servers_url % appconfig.plex_server_id
    r = requests.get(url, headers=appconfig.plex_headers)
    xml = ET.fromstring(r.text)
    shared_servers = {int(s.get('userID')): s.get('id') for s in xml.iter('SharedServer')}