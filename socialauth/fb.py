"""This module uses the Facebook OAuth2 API to let the user log in using FB.

Usefull URLs:
  - http://developers.facebook.com/docs/api
  - http://developers.facebook.com/docs/authentication/
  - http://github.com/facebook/python-sdk/blob/master/examples/oauth/facebookoauth.py
"""
import cgi
try:
    import json
except ImportError:
    import simplejson as json
import urllib

import socialauth
from socialauth import utils


app_id = None
api_key = None
application_secret = None

redirect_uri = '%s/socialauth/fb/process/'
fb_authorize_url = 'https://graph.facebook.com/oauth/authorize?display=popup&%s'
fb_access_token_url = 'https://graph.facebook.com/oauth/access_token?%s'
fb_profile_url = 'https://graph.facebook.com/me?access_token=%s'


def init(app_id_, api_key_, application_secret_):
    """Set the app id, th api key and the application secret for the module.
    """
    global app_id, api_key, application_secret
    app_id = app_id_
    api_key = api_key_
    application_secret = application_secret_


def login(request, environ, start_response):
    """Redirects client to FB login page.
    """
    args = dict(client_id=app_id, redirect_uri=redirect_uri % request.host_url)
    url = fb_authorize_url % urllib.urlencode(args)
    start_response('302 Redirect', [('Location', url)])
    return ['']


def process(request, environ, start_response):
    """Process information returned by client and server
    to log in the user.
    """
    code = request.GET.get('code')
    if not code: # Probably cancel from user
        start_response('302 Redirect', [('Location', utils.LOGIN_PATH)])
        return ['']
    args = dict(client_id=app_id, 
                redirect_uri=redirect_uri % request.host_url,
                client_secret=application_secret,
                code=code)
    url = fb_access_token_url % urllib.urlencode(args)
    res = urllib.urlopen(url).read()
    response = cgi.parse_qs(res)
    access_token = response['access_token'][-1]

    # The token contains the FB userid, but the token changes from times to 
    # times, so we can not really rely on it to find users in DB.
    # The token format is not garanted, so we do not try to extract 
    # userid from it.
    req = urllib.urlopen(fb_profile_url % access_token)
    profile = json.load(req)
    fb_userid = profile['id']

    user = socialauth.User.getByFacebookUID(fb_userid)

    if not user:
        user = socialauth.User.create(firstname=profile.get('first_name'), 
                           lastname=profile.get('last_name'),
                           fb_id=profile['id'],
                           fb_oauth2_token=access_token)
    elif user.fb_oauth2_token != access_token:
        user.fb_oauth2_token = access_token
        user.save()
    
    session = environ['beaker.session']
    session['user_id'] = user._id
    session['user_human_id'] = user.human_id
    session.save()

    return utils.close_window_refresh_opener(start_response)


