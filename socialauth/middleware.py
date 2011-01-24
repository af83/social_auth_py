import webob

from decalogy.lib.socialauth import fb
from decalogy.lib.socialauth import openid_ as openid
from decalogy.lib.socialauth import twitter
from decalogy.lib.socialauth import utils


utils.LOGIN_PATH = '/socialauth/login'


class SocialAuthMiddleware(object):
    
    def __init__(self, app, config):
        openid.init_store(config['socialauth.openid.store'])
        twitter.init_consumer_client(config['socialauth.twitter.key'],
                                     config['socialauth.twitter.secret'])
        fb.init(config['socialauth.fb.app_id'],
                config['socialauth.fb.api_key'],
                config['socialauth.fb.application_secret'])
        self.app = app

    def __call__(self, environ, start_response):
        request = webob.Request(environ)
        if not request.path.startswith('/socialauth/') or \
               request.path == '/socialauth/login':
            return self.app(environ, start_response)
        if request.path == '/socialauth/logout':
            session = environ['beaker.session']
            session.pop('user_id', None)
            session.pop('user_human_id', None)
            session.save()
            start_response('302 Redirect', [('Location', '/')])
            return ['']

        # twitter:
        if request.path == '/socialauth/twitter/login':
            return twitter.login(request, environ, start_response) 
        if request.path == '/socialauth/twitter/process':
            return twitter.process(request, environ, start_response)

        # openid:
        if request.path == '/socialauth/openid/login':
            return openid.login(request, environ, start_response, ask_info=True)
        if request.path == '/socialauth/openid/process':
            return openid.process(request, environ, start_response)

        # facebook:
        if request.path == '/socialauth/fb/login':
            return fb.login(request, environ, start_response)
        if request.path == '/socialauth/fb/process/':
            return fb.process(request, environ, start_response)

