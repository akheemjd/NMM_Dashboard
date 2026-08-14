/* Northern Mile — dashboard behaviour.
   One job: copy the citation. Nothing here is required for the page to be
   readable, and nothing here touches a published figure. An earlier version
   animated the headline number on load; it was removed because an interrupted
   animation could leave a wrong price on screen, which is not a trade worth
   making on a page built to be quoted. */

(function () {
  "use strict";

  /* Runs fn now if the document is already parsed, otherwise on DOMContentLoaded.
     A plain listener would never fire for a script at the end of <body> if the
     event had already gone. */
  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

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

})();
