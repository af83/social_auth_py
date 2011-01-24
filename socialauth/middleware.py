import webob

from socialauth import fb
from socialauth import openid_ as openid
from socialauth import twitter
from socialauth import utils


utils.LOGIN_PATH = '/socialauth/login'


class SocialAuthMiddleware(object):
    
    def __init__(self, app, config, prefix=''):
        """Init the middleware using given app, config, and prefix.

        Arguments:
          - app
          - config: a config object (dict). This object must contain the
            following keys/vals:
              - openid.store: directory where are store the openid grants.
              - twitter.key
                twitter.secret: the key/secret for twitter API.
              - fb.app_id
                fb.api_key
                fb.application_secret: FB OAuth2 params

          - prefix: optional, default to "", a string to prefix keys
            for lookup in config dict. Ex: "socialauth."

        """
        openid.init_store(config[prefix+'openid.store'])
        twitter.init_consumer_client(config[prefix+'twitter.key'],
                                     config[prefix+'twitter.secret'])
        fb.init(config[prefix+'fb.app_id'],
                config[prefix+'fb.api_key'],
                config[prefix+'fb.application_secret'])
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

