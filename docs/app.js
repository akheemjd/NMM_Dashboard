/* Northern Mile Dashboard — shared behaviour for every page. */
(function () {
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion:reduce)').matches;

  /* Split-flap odometer: builds flap tiles from a single data-value, rolls on load.
     Markup: <div class="odo" data-value="171.9" data-unit="c/L"></div>  */
  document.querySelectorAll('.odo[data-value]').forEach(function (odo) {
    var val = (odo.getAttribute('data-value') || '').trim();
    var unit = odo.getAttribute('data-unit') || '';
    odo.innerHTML = '';
    val.split('').forEach(function (ch) {
      var s = document.createElement('span');
      if (ch === '.' || ch === ',') { s.className = 'sep'; s.textContent = ch; }
      else { s.className = 'd'; s.textContent = ch; }
      odo.appendChild(s);
    });
    if (unit) { var u = document.createElement('span'); u.className = 'u'; u.textContent = unit; odo.appendChild(u); }
    if (!reduce) {
      odo.querySelectorAll('.d').forEach(function (f) {
        var target = f.textContent, ticks = 6 + Math.floor(Math.random() * 5), i = 0;
        var iv = setInterval(function () {
          if (i >= ticks) { f.textContent = target; clearInterval(iv); return; }
          f.textContent = Math.floor(Math.random() * 10); i++;
        }, 45);
      });
    }
  });

  /* Clickable rows/cards/gauges: any element with data-href navigates (mouse + Enter). */
  document.addEventListener('click', function (e) {
    if (e.target.closest('a')) return;
    var el = e.target.closest('[data-href]');
    if (el) window.location.href = el.getAttribute('data-href');
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Enter') return;
    var el = e.target.closest('[data-href]');
    if (el) window.location.href = el.getAttribute('data-href');
  });
})();

function copyLink(btn, url) {
  navigator.clipboard.writeText(url || location.href).then(function () {
    var t = btn.textContent; btn.textContent = 'Copied';
    setTimeout(function () { btn.textContent = t; }, 1500);
  });
}
