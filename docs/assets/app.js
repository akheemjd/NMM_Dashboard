/* The Bulletin — shared JS. Flat numbers, no odometer. */
(function(){
  'use strict';
  // Hero number display — plain text, no animation
  document.querySelectorAll('.odo').forEach(function(el){
    var val = el.getAttribute('data-value');
    if (val) {
      var unit = el.getAttribute('data-unit') || '';
      el.innerHTML = val + (unit ? ' <small>' + unit + '</small>' : '');
    }
  });

  // Map helpers
  window.initMap = function(id, data, tileUrl, attribution){
    if (!window.L || !document.getElementById(id)) return;
    var map = L.map(id, { scrollWheelZoom: true, zoomControl: false }).setView([52, -90], 4);
    L.tileLayer(tileUrl || 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: attribution || '&copy; OpenStreetMap',
      maxZoom: 18
    }).addTo(map);
    L.control.zoom({ position: 'bottomright' }).addTo(map);
    return map;
  };

  window.addPins = function(map, data, popupFn){
    if (!data || !data.length) return;
    var bounds = [];
    data.forEach(function(it){
      if (it.lat && it.lng) {
        var m = L.marker([it.lat, it.lng]).addTo(map);
        if (popupFn) m.bindPopup(popupFn(it));
        bounds.push([it.lat, it.lng]);
      }
    });
    if (bounds.length) map.fitBounds(bounds, { padding: [30, 30] });
  };

  // Detail panel
  window.showDetail = function(content){
    var panel = document.getElementById('inc-detail');
    if (!panel) {
      panel = document.createElement('div');
      panel.id = 'inc-detail';
      panel.className = 'detail-panel';
      document.body.appendChild(panel);
    }
    panel.innerHTML = content;
    panel.style.display = 'block';
  };
})();
