
(function(){
  var newwindow;
  $('a.sign-in').click(function() {
    // So that if already open, reappear on top:
    newwindow && newwindow.close();
    newwindow = window.open('/socialauth/login','Log in',
                            'height=600,width=800');
    newwindow.focus();
  });
})();

