
document.addEventListener('DOMContentLoaded', function(){
  var btns = document.querySelectorAll('.chip.filter');
  var cards = document.querySelectorAll('.post-card');
  btns.forEach(function(b){
    b.addEventListener('click', function(){
      btns.forEach(function(x){x.classList.remove('active');});
      b.classList.add('active');
      var t = b.getAttribute('data-theme');
      cards.forEach(function(c){
        var themes = c.getAttribute('data-themes') || '';
        c.style.display = (t === 'all' || themes.indexOf(t) !== -1) ? '' : 'none';
      });
    });
  });
});
