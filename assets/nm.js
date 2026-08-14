/* Northern Mile — dashboard behaviour.
   Three jobs: remember the reader's theme, open the menu, copy a citation.
   No dependencies. Each job is isolated, so a failure in one cannot stop the
   others. Nothing here is required for the page to be readable. */

(function () {
  "use strict";

  var KEY = "nm-theme";

  function root() { return document.documentElement; }

  function label(btn, theme) {
    if (!btn) return;
    btn.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
    var tl = btn.querySelector(".tl");
    if (tl) tl.textContent = theme === "dark" ? "Light" : "Dark";
  }

  function apply(theme) {
    root().setAttribute("data-theme", theme);
    label(document.getElementById("themebtn"), theme);
  }

  function stored() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function remember(theme) {
    try { localStorage.setItem(KEY, theme); } catch (e) { /* private mode */ }
  }

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  /* Theme ---------------------------------------------------------------- */
  ready(function () {
    try {
      var current = root().getAttribute("data-theme");
      if (!current) {
        current = stored() || (window.matchMedia &&
          window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
        apply(current);
      } else {
        label(document.getElementById("themebtn"), current);
      }

      var btn = document.getElementById("themebtn");
      if (btn) {
        btn.addEventListener("click", function () {
          var next = root().getAttribute("data-theme") === "dark" ? "light" : "dark";
          apply(next);
          remember(next);
        });
      }
    } catch (e) {
      if (window.console) console.error("theme:", e);
    }
  });

  /* Menu ----------------------------------------------------------------- */
  ready(function () {
    try {
      var btn = document.getElementById("menubtn");
      var panel = document.getElementById("menu");
      if (!btn || !panel) return;

      function set(open) {
        btn.setAttribute("aria-expanded", open ? "true" : "false");
        panel.hidden = !open;
        btn.querySelector(".ml").textContent = open ? "Close" : "Menu";
      }

      set(false);

      btn.addEventListener("click", function () {
        set(panel.hidden);
      });

      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && !panel.hidden) {
          set(false);
          btn.focus();
        }
      });

      document.addEventListener("click", function (e) {
        if (panel.hidden) return;
        if (!panel.contains(e.target) && !btn.contains(e.target)) set(false);
      });
    } catch (e) {
      if (window.console) console.error("menu:", e);
    }
  });

  /* Copy citation -------------------------------------------------------- */
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
          function done() {
            mark.textContent = "Copied";
            setTimeout(function () { mark.textContent = was; }, 1800);
          }
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(done, function () {});
          }
        });
      });
    } catch (e) {
      if (window.console) console.error("copy:", e);
    }
  });

  /* Count-up — cosmetic. The final value is already in the markup. -------- */
  ready(function () {
    try {
      if (window.matchMedia &&
          window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
      var el = document.querySelector("[data-count]");
      if (!el) return;
      var target = parseFloat(el.textContent);
      if (!isFinite(target)) return;
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
    } catch (e) {
      if (window.console) console.error("count:", e);
    }
  });
})();
