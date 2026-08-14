/* Northern Mile — dashboard behaviour.
   Two jobs: remember the reader's theme, and copy a citation.
   No dependencies. Nothing here is required for the page to be readable. */

(function () {
  "use strict";

  var KEY = "nm-theme";

  function apply(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    var btn = document.getElementById("themebtn");
    if (btn) {
      var dark = theme === "dark";
      btn.setAttribute("aria-pressed", dark ? "true" : "false");
      btn.querySelector(".tl").textContent = dark ? "Light" : "Dark";
    }
  }

  function stored() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function remember(theme) {
    try { localStorage.setItem(KEY, theme); } catch (e) { /* private mode */ }
  }

  // System preference wins until the reader states one.
  var initial = stored();
  if (!initial) {
    initial = window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  apply(initial);

  document.addEventListener("DOMContentLoaded", function () {
    apply(document.documentElement.getAttribute("data-theme") || initial);

    var btn = document.getElementById("themebtn");
    if (btn) {
      btn.addEventListener("click", function () {
        var next = document.documentElement.getAttribute("data-theme") === "dark"
          ? "light" : "dark";
        apply(next);
        remember(next);
      });
    }

    document.querySelectorAll("[data-copy]").forEach(function (el) {
      el.addEventListener("click", function () {
        var target = document.getElementById(el.getAttribute("data-copy"));
        if (!target) return;
        var text = target.textContent.trim().replace(/\s+/g, " ");
        var done = function () {
          var label = el.querySelector(".cp") || el;
          var was = label.textContent;
          label.textContent = "Copied";
          setTimeout(function () { label.textContent = was; }, 1800);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(done, function () {});
        }
      });
    });
  });
})();

/* Count-up on the headline figure. Cosmetic only — the final value is in the
   markup, so the number is correct before this runs and if it never runs. */
(function () {
  "use strict";
  document.addEventListener("DOMContentLoaded", function () {
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    var el = document.querySelector("[data-count]");
    if (!el) return;
    var target = parseFloat(el.textContent);
    if (isNaN(target)) return;
    var decimals = (el.textContent.split(".")[1] || "").length;
    var start = null, dur = 700, from = target * 0.985;
    function step(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = (from + (target - from) * eased).toFixed(decimals);
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = target.toFixed(decimals);
    }
    requestAnimationFrame(step);
  });
})();
