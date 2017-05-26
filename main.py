import os
import requests
import auth_config as auth
import uuid
import logging
import argparse
import json
import xml.etree.ElementTree as ET
import cherrypy
import share_unshare_libraries as plexlib


_logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s> %(message)s'))
_logger.setLevel(logging.INFO)
_logger.addHandler(ch)

_args = None

plex_headers = {
    'X-Plex-Product': 'Plex Library Util',
    'X-Plex-Version': '1.0',
    'X-Plex-Client-Identifier': str(uuid.uuid4())
}

_SERVER_ID = '383f29cc48658882f79edd40d27a654f8ffb5100'
auth_url = 'https://plex.tv/users/sign_in.json'
plex_token = None

libraries = {}
shared_servers = None


def get_libraries():
    global libraries
    url = 'https://plex.tv/api/servers/%s' % _SERVER_ID
    r = requests.get(url, headers=plex_headers)
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
    _plex_auth()

    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.quickstart(PlexUtil(), '/', {
        '/': {
            'tools.staticdir.root': os.path.abspath(os.path.join(__file__, '..', 'html')),
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '',
            'tools.staticdir.index': 'index.html'
        }
    })

def _plex_auth():
    global plex_token
    auth_data = {
        'user[login]': auth.plex_user,
        'user[password]': auth.plex_passwd

    }
    r = requests.post(auth_url,
                      headers=plex_headers,
                      data=auth_data)
    data = r.json()
    _logger.debug(data)
    plex_auth_token = data['user']['authToken']
    _logger.info('Plex token: %s' % plex_auth_token)
    plex_token = plex_auth_token
    plex_headers['X-Plex-Token'] = plex_token

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Turn on verbose logging', dest='v')
    _args = parser.parse_args()

    if _args.v:
        _logger.setLevel(logging.DEBUG)

    plex_util()


if __name__ == '__main__':
    main()