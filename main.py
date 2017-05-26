import os
import requests
import logging
import argparse
import xml.etree.ElementTree as ET
import cherrypy
import share_unshare_libraries as plexlib
from helpers.utils import logger
import app_setup
from config import appconfig
import sys
from helpers import plex_auth


_logger = logger.configure_logging(__name__, level='INFO')
_args = None

_SERVER_ID = '383f29cc48658882f79edd40d27a654f8ffb5100'
plex_token = None

libraries = {}
shared_servers = None


def get_libraries():
    global libraries
    url = 'https://plex.tv/api/servers/%s' % _SERVER_ID
    r = requests.get(url, headers=appconfig.plex_headers)
    xml = ET.fromstring(r.text)
    sections = [i.get('id') for i in xml.iter('Section')]
    libraries['sections'] = sections

class PlexUtil(object):

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_shared_servers(self):
        global libraries, shared_servers
        get_libraries()
        url = 'https://plex.tv/api/servers/%s/shared_servers' % _SERVER_ID
        r = requests.get(url, headers=plex_headers)
        xml = ET.fromstring(r.text)
        shared_servers = {int(s.get('userID')): [].append(int(i.get('id')) if bool(int(i.get('shared'))) else False) for i in s.iter('Section') for s in xml.iter('SharedServer')}
        libraries['shared_servers'] = shared_servers
        print(libraries['shared_servers'])
        # print(shared_servers)
        # sections = []
        # for section in shared_servers[0].findall('Section'):
        #     sections.append((section.get('id'), section.get('title')))
        # for section in sections:
        #     current_section_id = section[0]
        #     shared_to = []
        #     for user in shared_servers:
        #         ss_sections = list(user.iter('Section'))
        #         for s in ss_sections:
        #             if s.get('id') == current_section_id and int(s.get('shared')):
        #                 shared_to.append({'id': user.get('userID'),
        #                                   'username': user.get('username'),
        #                                   'email': user.get('email')})
        #     libraries[current_section_id] = {
        #         'title': section[1],
        #         'users': shared_to
        #     }
        # return libraries

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_users(self):
        url = 'https://plex.tv/api/users?X-Plex-Token=%s' % plex_token
        r = requests.get(url)
        xml = ET.fromstring(r.text)
        xml_users = xml.findall('User')
        users = []
        for u in xml_users:
            user = {
                'id': u.get('id'),
                'username': u.get('username'),
                'title': u.get('title'),
                'email': u.get('email'),
                'thumb': u.get('thumb')
            }
            users.append(user)
        return users

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def save_shared_servers(self):
        data = cherrypy.request.json
        print(data)
        if bool(data['share']) and bool(data['unshare']):
            plexlib.share(data['share'], _SERVER_ID, plex_token)
            plexlib.unshare(data['unshare'], _SERVER_ID, plex_token)
        elif bool(data['share']):
            plexlib.share(data['share'], _SERVER_ID, plex_token)
        elif bool(data['unshare']):
            plexlib.unshare(data['unshare'], _SERVER_ID, plex_token)
        else:
            pass

def plex_util():
    # Authenticate to plex
    plex_auth.authenticate()
    sys.exit(0)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.quickstart(PlexUtil(), '/', {
        '/': {
            'tools.staticdir.root': os.path.abspath(os.path.join(__file__, '..', 'html')),
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '',
            'tools.staticdir.index': 'index.html'
        }
    })

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Turn on verbose logging', dest='v')
    parser.add_argument('--setup', action='store_true', dest='setup',
                        help='Run the initial setup for the application '
                             '(required before first use)')
    _args = parser.parse_args()

    if _args.v:
        _logger.setLevel(logging.DEBUG)

    if _args.setup:
        app_setup.run_setup(_args)
    else:
        plex_util()


if __name__ == '__main__':
    main()