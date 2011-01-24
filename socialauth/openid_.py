from openid.consumer.consumer import Consumer
from openid.extensions import pape, sreg, ax
from openid.store import filestore

import socialauth
from socialauth import utils


SREG_FIELDS = ['nickname', 'email', 'fullname']

AX_FIELDS = {'firstname': 'http://axschema.org/namePerson/first',
             'lastname': 'http://axschema.org/namePerson/last',
             'email': 'http://axschema.org/contact/email',
             'nickname': 'http://axschema.org/namePerson/friendly',
             }

# Note:
# Google provides the email, firstname and lastname using the AX extension
# Yahoo provides the email and the friendly name (nickname) using AX extension

OPENID_STORE = None


def init_store(dir):
    """Init the OpenId store (file store).

    Arguments:
      - dir: where the store is located.
    """
    global OPENID_STORE
    OPENID_STORE = filestore.FileOpenIDStore(dir)


def get_sessions(environ):
    """Returns (session, openid_session) tuple.

    - session is the beaker session. If you change oi_session, you have to
      call session.save()
    - oi_session is the dict in session['openid.session']. This is as such so
      that this middleware doesn't pollute the session object.
    """
    session = environ['beaker.session']
    oi_session = session.setdefault('openid.session', {})
    return session, oi_session


def login(request, environ, start_response, ask_info=False):
    """Redirect the user to the openid provider.
    
    Arguments:
      - ask_info: bool, default False. If set to true, will use the sreg and ax
        extensions to ask info about the user (email, name...).
    """
    user_url = request.GET['url']
    session, oi_session = get_sessions(environ)
    trust_root = request.host_url
    return_to = "%s/socialauth/openid/process" % trust_root
    immediate = False # If set to true and the identity provider can not reply 
    # immediatly (user has to approve), then authentication will fail.
    # If set to True, then we have to handle the SetupNeeded response case in
    # process function.
    consumer = Consumer(oi_session, OPENID_STORE)
    auth_req = consumer.begin(user_url)

    if ask_info:
        sreg_request = sreg.SRegRequest(required=['email'])#, optional=SREG_FIELDS)
        auth_req.addExtension(sreg_request)
        
        ax_request = ax.FetchRequest()
        for alias, url in AX_FIELDS.iteritems():
            ax_request.add(ax.AttrInfo(url, alias=alias, required=True))
        auth_req.addExtension(ax_request)
    
    # PAPE (Provider Authentication Policy Extension):
    # TODO (an treat pape.Response as well)
    #pape_request = pape.Request([pape.AUTH_PHISHING_RESISTANT])
    #auth_req.addExtension(pape_request)

    session.save()

    if auth_req.shouldSendRedirect():
        redirect_url = auth_req.redirectURL(trust_root, return_to, 
                                            immediate=immediate)
        start_response('302 Redirect', [('Location', redirect_url)])
        return []
    else:
        form_html = auth_req.htmlMarkup(trust_root, return_to,
                                        form_tag_attrs={'id':'openid_message'},
                                        immediate=immediate)
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [form_html]


def process(request, environ, start_response):
    """Handle the redirect from the OpenID server and eventually login the user.
    """
    session, oi_session = get_sessions(environ)    
    consumer = Consumer(oi_session, OPENID_STORE)

    # Ask the library to check the response that the server sent us.
    # Status is a code indicating the response type.
    # Info is either None or a string containing more information about
    # the return type.
    url = request.host_url + request.path
    info = consumer.complete(request.params, url)
    
    oi_session.clear()

    if info.status == "success":
        user_id = info.getDisplayIdentifier()

        user_to_save = False
        user = socialauth.User.getByOpenIdIdentifier(user_id)
        if user is None:
            user = socialauth.User(openid_identifier=user_id)
            user_to_save = True

        sreg_resp = sreg.SRegResponse.fromSuccessResponse(info)
        if sreg_resp:
            for k, v in sreg_resp.iteritems():
                if v and getattr(user, k) != v: 
                    setattr(user, k, v)
                    user_to_save = True

        ax_rep = ax.FetchResponse.fromSuccessResponse(info)
        if ax_rep:
            data = {}
            for alias, url in AX_FIELDS.iteritems():
                try:
                    data[alias] = ax_rep.get(url) and ax_rep.get(url)[0]
                except KeyError, IndexError:
                    pass
            for k, v in data.iteritems():
                if v and getattr(user, k) != v:
                    setattr(user, k, v)
                    user_to_save = True

        if user_to_save: 
            user.save()
        session['user_id'] = user._id
        session['user_human_id'] = user.human_id
        session.save()
        return utils.close_window_refresh_opener(start_response)

    elif info.status == "cancel":
        # it looks like the user doesn't want to log in...
        # Let's redirect him/her to the login page
        # just in case he/she wants to pick another id provider
        start_response('302 Redirect', [('Location', utils.LOGIN_PATH)])
        return ['']

    elif info.status == "failure":
        txt = [('We are sorry, but something went wrong during'
                ' the authentication process...')]
        if info.identity_url:
            txt.append('Identity url: %s' % info.identity_url)
        if info.message:
            txt.append('Message from the identity provider: %s' % info.message)
        session.save()
        return utils.display_msg(start_response, '<br/>'.join(txt))

