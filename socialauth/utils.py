
LOGIN_PATH = None # set by middleware


def close_window_refresh_opener(start_response):
    """Returns page closing the current window and reloading the parent one.
    """
    js = ('window.opener.location.reload(true);'
          'window.opener.focus();'
          'window.close();')
    content = {'js': js, 'body': ''}
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [HTML_PAGE % content]


def display_msg(start_response, msg):
    """Returns page with msg.
    """
    content = {'js': '', 'body': '<br/>'.join(txt)}
    start_response('200 OK', [('Content-Type', 'text/html')])    
    return [HTML_PAGE % content]


HTML_PAGE = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <script type="text/javascript"><!--//
      %(js)s
    //--></script>
  </head>
  <body>
    %(body)s
  </body>
</html>
"""

