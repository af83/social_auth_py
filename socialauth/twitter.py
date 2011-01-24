import oauth2 as oauth
import cgi

import socialauth
from socialauth import utils


request_token_url = 'http://twitter.com/oauth/request_token'
access_token_url = 'http://twitter.com/oauth/access_token'
authenticate_url = 'http://twitter.com/oauth/authenticate?oauth_token=%s'

consumer = None
client = None


def init_consumer_client(consumer_key, consumer_secret):
    """
    Arguments:
      - consumer_key: as provided by twitter
      - consumer_secret: as provided by twitter
    """
    global consumer, client
    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)


def login(request, environ, start_response):
    """Get a request token from twitter, store it and redirect the user.
    """
    #Step 1. Get a request token from Twitter.
    resp, content = client.request(request_token_url, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response from Twitter.")

    # Step 2. Store the request token in a session for later use.
    session = environ['beaker.session']
    request_token = dict(cgi.parse_qsl(content))
    session['socialauth.twitter_token'] = request_token['oauth_token_secret']
    session.save()

    # Step 3. Redirect the user to the authentication URL.
    url = authenticate_url % request_token['oauth_token']
    start_response('302 Redirect', [('Location', url)])
    return ['']


def process(request, environ, start_response):
    """Verify the returned values from twitter.

    If the user cancel once on twitter site, he/she is not redirected here,
    so not this case to handle...
    """
    session = environ['beaker.session']
    oauth_token = request.params['oauth_token']
    oauth_token_secret = session.pop('socialauth.twitter_token')
    
    # Step 1. Use the request token in the session to build a new client.
    token = oauth.Token(oauth_token, oauth_token_secret)
    client = oauth.Client(consumer, token)

    # Step 2. Request the authorized access token from Twitter.
    resp, content = client.request(access_token_url, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response from Twitter.")

    """
    This is what you'll get back from Twitter. Note that it includes the
    user's user_id and screen_name.
    {
        'oauth_token_secret': 'IcJXPiJh8be3BjDWW50uCY31chyhsMHEhqJVsphC3M',
        'user_id': '120889797', 
        'oauth_token': '120889797-H5zNnM3qE0iFoTTpNEHIz3noL9FKzXiOxwtnyVOD',
        'screen_name': 'heyismysiteup'
    }
    """
    access_token = dict(cgi.parse_qsl(content))

    # Step 3. Lookup the user or create them if they don't exist.
    user_to_save = False
    user_id = access_token['user_id']
    user = socialauth.User.getByTwitterId(user_id)
    if user is None:
        user = socialauth.User(twitter_id=user_id)
        user_to_save = True
    email = "%s@twitter.com" % access_token['screen_name']
    if user.email != email:
        user.email = email
        user_to_save = True
    if user_to_save:
        user.save()

    session['user_id'] = user._id
    session['user_human_id'] = user.human_id
    session.save()

    return utils.close_window_refresh_opener(start_response)

