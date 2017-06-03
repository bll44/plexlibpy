import cherrypy
import requests
from config import appconfig
import xml.etree.ElementTree as ET
import plex_api
from helpers import plex
import sys
from helpers.utils import logger
import os

_logger = logger.configure_logging(__name__, level='INFO')
_args = None

plex_config = None
libraries = {}
shared_servers = None


def get_libraries():
    global libraries
    url = appconfig.plex_libraries_url % plex_config['server_id']
    r = requests.get(url, headers=appconfig.plex_headers)
    xml = ET.fromstring(r.text)
    sections = [{'id': int(i.get('id')), 'title': i.get('title')} for i in xml.iter('Section')]
    libraries['sections'] = sections


class PlexUtil(object):

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_shared_servers(self):
        global libraries, shared_servers
        get_libraries()
        url = appconfig.plex_shared_servers_url % plex_config['server_id']
        r = requests.get(url, headers=appconfig.plex_headers)
        xml = ET.fromstring(r.text)
        shared_servers = []
        for ss in xml.iter('SharedServer'):
            library_sections = []
            for s in ss.iter('Section'):
                if bool(int(s.get('shared'))):
                    library_sections.append(int(s.get('id')))
            user = {'user_id': int(ss.get('userID')),
                    'sections': library_sections}
            shared_servers.append(user)
        libraries['shared_servers'] = shared_servers
        return libraries

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_users(self):
        url = appconfig.plex_users_url
        r = requests.get(url, headers=appconfig.plex_headers)
        xml = ET.fromstring(r.text)
        xml_users = xml.findall('User')
        users = []
        for u in xml_users:
            user = {
                'id': int(u.get('id')),
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
        shared = {}
        unshared = {}
        for i in data:
            if len(i['libs'][0]['sections']) > 0:
                shared[int(i['id'])] = i['libs'][0]['sections']
            else:
                unshared[int(i['id'])] = i['libs'][0]['sections']
        if len(shared) > 0:
            plex_api.share(shared)
        if len(unshared) > 0:
            plex_api.unshare(unshared)


def start(args):
    _args = args
    global plex_config
    # Authenticate to plex
    try:
        plex.authenticate()
    except Exception as e:
        sys.exit(1)

    plex_config = plex.load_plex_config()
    appconfig.plex_server_id = plex_config['server_id']

    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.quickstart(PlexUtil(), '/', {
        '/': {
            'tools.staticdir.root': os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'html')),
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '',
            'tools.staticdir.index': 'index.html'
        }
    })