/* Northern Mile — dashboard behaviour.
   One job: copy the citation. Nothing here is required for the page to be
   readable, and nothing here touches a published figure. */
(function () {
  "use strict";
  function ready(fn) {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn);
    else fn();
  }
  ready(function () {
    try {
      var els = document.querySelectorAll("[data-copy]");
      Array.prototype.forEach.call(els, function (el) {
        el.addEventListener("click", function () {
          var target = document.getElementById(el.getAttribute("data-copy"));
          if (!target) return;
          var text = target.textContent.trim().replace(/\s+/g, " ");
          var mark = el.querySelector(".cp") || el;
          var was = mark.textContent;
          function done() { mark.textContent = "Copied"; setTimeout(function () { mark.textContent = was; }, 1800); }
          if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, function () {});
        });
      });
    } catch (e) { if (window.console) console.error("copy:", e); }
  });
})();

/* ── Nav ─────────────────────────────────────────────────────────────────────
   Two behaviours, both progressive: every group's strip is already in the HTML and
   the current one is visible, so with JS off a reader still sees their own group's
   children. This only swaps which strip is on screen. */
(function () {
  "use strict";

  var groups = document.querySelectorAll(".nav .ng");
  var strips = document.querySelectorAll(".strip");
  if (!groups.length || !strips.length) return;

  function show(name) {
    for (var i = 0; i < strips.length; i++) {
      var on = strips[i].getAttribute("data-group") === name;
      if (on) { strips[i].removeAttribute("hidden"); }
      else { strips[i].setAttribute("hidden", ""); }
    }
    for (var k = 0; k < groups.length; k++) {
      groups[k].classList.toggle("peek", groups[k].textContent.trim() === name);
    }
  }

  for (var i = 0; i < groups.length; i++) {
    (function (el) {
      var name = el.textContent.trim();
      el.addEventListener("mouseenter", function () { show(name); });
      el.addEventListener("focus", function () { show(name); });
    })(groups[i]);
  }

  /* Restore the current page's group when the pointer leaves the row, so hovering
     around does not leave a strip that has nothing to do with where you are. */
  var row = document.querySelector(".nav .wrap");
  var here = "";
  for (var n = 0; n < groups.length; n++) {
    if (groups[n].classList.contains("on")) here = groups[n].textContent.trim();
  }
  if (row && here) {
    row.addEventListener("mouseleave", function () { show(here); });
  }

  /* Drawer. */
  var btn = document.getElementById("navbtn");
  var drawer = document.getElementById("drawer");
  if (btn && drawer) {
    btn.addEventListener("click", function () {
      var open = drawer.hasAttribute("hidden");
      if (open) { drawer.removeAttribute("hidden"); } else { drawer.setAttribute("hidden", ""); }
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !drawer.hasAttribute("hidden")) {
        drawer.setAttribute("hidden", "");
        btn.setAttribute("aria-expanded", "false");
      }
    });
  }
})();
