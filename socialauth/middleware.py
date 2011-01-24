import webob

import socialauth
from socialauth import fb
from socialauth import openid_ as openid
from socialauth import twitter
from socialauth import utils


utils.LOGIN_PATH = '/socialauth/login'


class SocialAuthMiddleware(object):
    
    def __init__(self, app, config, User, prefix=''):
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

          - User: a class representing a User, defining the following class 
            methods:
              - getByFacebookUID(fb_userid)
              - getByOpenIdIdentifier(openid_identifier)
              - getByTwitterId(twitter_user_id):
                  Returns user obj corresponding to FB/OpenID/Twitter ID.
              - create(**properties): Create User obj setting given properties.
            the follogin instance methods:
              - save(): save the user obj to persistance storage.

            and the following potential properties (might not be set):
              - twitter_id
              - openid_identifier
              - fb_id
              - fb_oauth2_token

              - email = StringProperty()
              - firstname
              - lastname
              - fullname
              - nickname

              - _id: an unique identifier
              - human_id: a property method returning a string describing to 
                the user the account he/she is logged-in with.

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
        socialauth.User = User

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

