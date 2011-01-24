
(function(){
  var openid_href,
      provider,
      openidurl = $('#openidurl'),
      form_socialauth = $('form.socialauth'),
      
  active_awaiting = function() {
    $('div.socialauth').hide();
    $('div.socialauth_waiting').show();
  };

  $('a.socialauth').each(function(index, elem) {
    elem.title = 'Sign in using ' + $(elem).html();
  });
  $('.socialauth.main li a.socialauth').html('');

  form_socialauth.submit(function() {
      var url = openidurl.val();
      if(url.indexOf('http://') != 0)
        url = openid_href.replace(/__.*__/, openidurl.val());
      openidurl.val(url);
      active_awaiting();
  });
  $('.socialauth.main a.socialauth').click(active_awaiting);

  $('.socialauth.secondary a.socialauth').click(function() {
    openid_href = this.href;
    provider = $(this).html();
    var res = openid_href.match(/__(.*)__/);
    if (res) {
      var var_name = res[1];
      $('#openidurl_label').html('Your '+ provider + "'s " + var_name + ':')
                           .attr('class', $(this).attr('class'));
      form_socialauth.show();
    }
    else {
      openidurl.val(openid_href);
      form_socialauth.submit();
    }
    openidurl.focus();
    return false;
  });

}());

