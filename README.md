# Social Auth Python

## Description

This Python package (WSGI middleware) provides authentication for your users using:

  - OpenID (Google, Yahoo, Flickr, or any other openid provider...);
  - OAuth2 (Facebook, using the OAuth2 graph API);
  - OAuth (Twitter).


## Usage

Place the middleware in your stack (here after session middleware, and before routes):

<pre><code>
from socialauth.middleware import SocialAuthMiddleware

...

# Routing/Session/Cache Middleware
app = RoutesMiddleware(app, config['routes.map'])

# CUSTOM MIDDLEWARE HERE (filtered by error handling middlewares)
app = SocialAuthMiddleware(app, config, User, prefix="socialauth.")

# Set the session obj before the custom middlewares:
app = SessionMiddleware(app, config)
</code></pre>

The SocialAuthMiddleware expects to have the "beaker.session" value set in the WSGI environment dict,
and will set 'user_id' and 'user_human_id' keys in the session object.


SocialAuthMiddleware arguments:

 - app
 - config: a config object (dict). This object must contain the
   following keys/vals:
     - openid.store: directory where are store the openid grants.
     - twitter.key, twitter.secret: the key/secret for twitter API.
     - fb.app_id, fb.api_key, fb.application_secret: FB OAuth2 params.

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


### Routes

The middleware will intercept the request having the following paths:

 - /socialauth/twitter/login
 - /socialauth/twitter/process
 - /socialauth/openid/login: expects the "url" parameters (where to redirect the user to)
 - /socialauth/openid/process
 - /socialauth/fb/login
 - /socialauth/fb/process/
 - /socialauth/logout: clear the session and redirect the user to "/".

The following will NOT be intercepted, and it is your responsibility to do something with it:

 - /socialauth/login : you should serve a page requesting the user to choose his/her identity provider.
  An example of such page can be found in the examples dir (examples/login_page.html). This page will provide a bunch of links to "/socialauth/{twitter,openid,fb}/login". The example page uses JS and CSS from the /static directory, but it is up to you to customize these.


