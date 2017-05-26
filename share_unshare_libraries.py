# Run this script using "share" or "unshare" as arguments:
# To share the Plex libraries:
#     python share_unshare_libraries.py share
# To unshare the Plex libraries:
#     python share_unshare_libraries.py unshare

import uuid
import requests
import sys
from xml.dom import minidom
from config.appconfig import plex_headers
from helpers.utils import logger

_logger = logger.configure_logging(__name__, level='INFO')

## EDIT THESE SETTINGS ###

# PLEX_TOKEN = "ENTER_YOUR_PLEX_TOKEN_HERE"
# server_id = "ENTER_YOUR_SERVER_ID_HERE"  # Example: https://i.imgur.com/EjaMTUk.png

# Get the User IDs and Library IDs from
# https://plex.tv/api/servers/SERVER_ID/shared_servers
# Example: https://i.imgur.com/yt26Uni.png
# Enter the User IDs and Library IDs in this format below:
#     {UserID1: [LibraryID1, LibraryID2],
#      UserID2: [LibraryID1, LibraryID2]}

# user_libraries = {1234567: [1234567, 1234567]}

## DO NOT EDIT BELOW ##

# plex_headers = {
#     'X-Plex-Product': 'Plex Library Util',
#     'X-Plex-Version': '1.0',
#     'X-Plex-Client-Identifier': str(uuid.uuid4())
# }

def get_shared_server(user_id, shared_servers):
    shared_server = None
    for i in shared_servers:
        if i.get('userID') == str(user_id):
            shared_server = i.get('id')
    return shared_server

def share(user_libraries, _server_id, token):
    # global plex_headers
    plex_headers['X-Plex-Token'] = token
    # headers = {"X-Plex-Token": token,
    #            "Accept": "application/json"}

    base_url = "https://plex.tv/api/servers/%s/shared_servers" % _server_id
    r = requests.get(base_url, headers=plex_headers)
    if r.status_code == 401:
        print("Invalid Plex token")
        return
    elif r.status_code == 400:
        print(r.text)
        return
    elif r.status_code == 200:
        response_xml = minidom.parseString(r.content)
        MediaContainer = response_xml.getElementsByTagName("MediaContainer")[0]
        SharedServer = MediaContainer.getElementsByTagName("SharedServer")
        shared_servers = {int(s.getAttribute("userID")): int(s.getAttribute("id"))
                          for s in SharedServer}

    for user_id, library_ids in user_libraries.items():
        _logger.debug('Adding share for user: %s' % user_id)

        if shared_servers.get(int(user_id)) is not None:
            _logger.debug('User %s shared servers: %s' % (user_id, shared_servers.get(int(user_id))))
            url = '%s/%s' % (base_url, str(shared_servers.get(int(user_id))))
            _logger.debug('mode PUT')
            payload = {
                "server_id": str(_server_id),
                "shared_server": {"library_section_ids": library_ids}
            }
            r = requests.put(url, headers=plex_headers, json=payload)
        else:
            url = base_url
            _logger.debug('mode POST')
            payload = {
                "server_id": str(_server_id),
                "shared_server": {"library_section_ids": library_ids,
                                  "invited_id": int(user_id)}
            }
            r = requests.post(url, headers=plex_headers, json=payload)

        if r.status_code == 401:
            print("Invalid Plex token")
            return
        elif r.status_code == 400:
            print(r.content)
        elif r.status_code == 200:
            print("Shared libraries with user %s" % str(user_id))
        else:
            print(r.content)
    return
    
def unshare(user_libraries, _server_id, token):
    plex_headers['X-Plex-Token'] = token
               
    url = "https://plex.tv/api/servers/" + _server_id + "/shared_servers"
    r = requests.get(url, headers=plex_headers)

    if r.status_code == 401:
        print("Invalid Plex token")
        return
        
    elif r.status_code == 400:
        print(r.content)
        return

    elif r.status_code == 200:
        response_xml = minidom.parseString(r.content)
        MediaContainer = response_xml.getElementsByTagName("MediaContainer")[0]
        SharedServer = MediaContainer.getElementsByTagName("SharedServer")
        
        shared_servers = {int(s.getAttribute("userID")): int(s.getAttribute("id"))
                          for s in SharedServer}
        _logger.debug(shared_servers)
        for user_id, library_ids in user_libraries.items():
            server_id = shared_servers.get(int(user_id))
            _logger.debug(server_id)
            if server_id:
                url = "https://plex.tv/api/servers/" + _server_id + "/shared_servers/" + str(server_id)
                r = requests.delete(url, headers=plex_headers)
                
                if r.status_code == 200:
                    print("Unshared libraries with user %s" % str(user_id))
            else:
                print("No libraries shared with user %s" % str(user_id))
    return