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
