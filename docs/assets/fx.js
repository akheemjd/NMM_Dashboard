/* Northern Mile — currency switching.
 *
 * WHAT THIS DOES
 * The site publishes two currencies natively and never said which was which.
 * Canadian diesel is quoted in cents per litre (CAD); US diesel in dollars per
 * gallon (USD). Both rendered as a bare number with a bare "$", so a US carrier
 * reading a Canadian figure saw a dollar sign and read it as US dollars — about
 * 40% off from what they pay.
 *
 * Every money figure is now emitted with its NATIVE currency and unit:
 *
 *   <span class="fx" data-c="CAD" data-u="cpl" data-v="271.0">271.0¢/L</span>
 *
 * This file reads the live USD/CAD rate, re-renders every marked figure in the
 * reader's chosen currency, and wires the nav toggle. The default is CAD, which
 * is byte-identical to what the page already shows — so with JavaScript off, or
 * with the rate unavailable, the site is exactly as it was.
 *
 * UNITS ARE NOT CURRENCIES
 * A Canadian price is per LITRE and a US price is per GALLON. Converting only
 * the currency would produce a number nobody recognises: Canada's 271.0¢/L is
 * 7.29 USD/gal, not 1.93 USD/L. The unit conversion is applied too, because a
 * per-litre US price is not something any US carrier thinks in.
 *
 *   cpl  cents per litre, CAD      -> USD: /100, /rate, *3.785411784, -> $/gal
 *   gpg  dollars per gallon, USD   -> CAD: *rate, *3.785411784, *100  -> ¢/L
 *   cad  plain Canadian dollars    -> USD: /rate
 *   usd  plain US dollars          -> CAD: *rate
 *
 * FAILS VISIBLE
 * If the rate cannot be fetched the toggle disables itself and says so. It must
 * not look live while doing nothing — that is precisely the bug this whole
 * session was spent fixing elsewhere.
 */
(function () {
  "use strict";

  var STORE = "nm_currency";
  var RATE_URL = "/assets/fx.json";
  var LITRES_PER_GALLON = 3.785411784;

  var rate = null;
  var rateAsOf = "";
  var currency = "CAD";

  try {
    currency = localStorage.getItem(STORE) === "USD" ? "USD" : "CAD";
  } catch (e) {
    currency = "CAD";
  }

  function litresPerGallon() {
    return LITRES_PER_GALLON;
  }

  /* Convert a native value into the display currency. Returns a number. */
  function convert(value, fromCurrency, unit, toCurrency) {
    // CURRENCY ONLY. A Canadian figure stays per litre and a US figure stays per
    // gallon; converting the unit as well would state a price nobody pays.
    var v = Number(value);
    if (!isFinite(v) || !rate) return null;
    if (fromCurrency === toCurrency) return v;
    if (fromCurrency === "CAD" && toCurrency === "USD") return v / rate;
    if (fromCurrency === "USD" && toCurrency === "CAD") return v * rate;
    return v;
  }

  /* The unit label. The dimension is fixed by the figure's country; only the
     currency symbol follows the toggle. */
  function unitLabel(fromCurrency, unit, toCurrency) {
    var usd = toCurrency === "USD";
    if (unit === "cpl") return "¢/L";                  // Canadian: litres, always
    if (unit === "lpg") return usd ? "$/L" : "C$/L";    // dollars per litre
    // US: gallons, always. "C$" because a bare $/gal conventionally reads as USD.
    if (unit === "gpg") return usd ? "$/gal" : "C$/gal";
    return "";                                           // p4 / plain: symbol on the value
  }

  function decimalsFor(fromCurrency, unit, toCurrency) {
    // Follows the UNIT, not the label, so it no longer depends on which currency
    // is selected. ¢/L is quoted to one decimal and $/gal to three.
    if (unit === "cpl") return 1;
    if (unit === "gpg") return 3;
    // Statutory fuel tax rates are published to four decimals and a two-decimal
    // render turns California's $0.4820 into C$0.68, losing the precision the
    // figure is quoted at.
    if (unit === "p4") return 4;
    return 2;
  }

  function format(value, fromCurrency, unit, toCurrency) {
    var label = unitLabel(fromCurrency, unit, toCurrency);
    var dp = decimalsFor(fromCurrency, unit, toCurrency);
    var n = value.toLocaleString("en-CA", { minimumFractionDigits: dp, maximumFractionDigits: dp });

    // A label that carries a currency symbol puts the number after it, because
    // "$ /gal" means "$6.529/gal" — not "6.529$/gal". "C$" is two characters, so
    // slicing on the first one produced "9.229C$/gal".
    if (label.indexOf("C$") === 0) return "C$" + n + label.slice(2);
    if (label.charAt(0) === "$") return "$" + n + label.slice(1);
    if (label) return n + label;                       // ¢/L, or a per-litre label
    return (toCurrency === "USD" ? "US$" : "C$") + n;  // plain dollar amounts
  }

  function renderOptions() {
    // <option> cannot contain markup, so these are annotated with attributes by
    // the build and their label string is rebuilt here. Wrapping them in a span
    // made the browser discard the content and blanked the calculator.
    var opts = document.querySelectorAll("option[data-fxv]");
    for (var i = 0; i < opts.length; i++) {
      var o = opts[i];
      var raw = o.getAttribute("data-fxv");
      var from = o.getAttribute("data-fxc");
      var unit = o.getAttribute("data-fxu") || "plain";
      var label = o.getAttribute("data-fxlabel") || "";
      if (!rate) continue;
      var out = convert(raw, from, unit, currency);
      if (out === null) continue;
      var shown = format(out, from, unit, currency);
      o.textContent = label ? label + " — " + shown : shown;
      // The calculator reads the option's VALUE as the cents-per-litre figure.
      // It must stay in the native unit or the arithmetic would change with the
      // display currency.
      if (o.hasAttribute("value") && o.getAttribute("value") !== "custom") {
        // value is left exactly as built — do not touch it.
      }
    }
  }

  function renderUnits() {
    // Unit LABELS follow the value. If a figure converts its unit and its label
    // does not, the page states two units for one number — worse than not
    // converting at all ("$7.278/gal ¢/L").
    //
    // data-u is "<token for CAD>|<token for USD>". No native/target logic: the
    // label is just whichever token matches the currency on screen.
    var nodes = document.querySelectorAll(".fxu");
    for (var i = 0; i < nodes.length; i++) {
      var pair = (nodes[i].getAttribute("data-u") || "").split("|");
      if (pair.length !== 2) continue;
      nodes[i].textContent = currency === "USD" ? pair[1] : pair[0];
    }
  }

  function render() {
    renderOptions();
    renderUnits();
    var nodes = document.querySelectorAll(".fx");
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      var from = el.getAttribute("data-c");
      var unit = el.getAttribute("data-u") || "plain";
      var raw = el.getAttribute("data-v");
      if (raw === null || raw === "") continue;

      if (!rate) {
        // No rate: leave the native text exactly as built.
        continue;
      }
      var out = convert(raw, from, unit, currency);
      if (out === null) continue;
      if (el.getAttribute("data-bare")) {
        // The unit has its own element next to this one; adding it here doubles it.
        var dp = decimalsFor(from, unit, currency);
        el.textContent = out.toLocaleString("en-CA", {
          minimumFractionDigits: dp, maximumFractionDigits: dp
        });
      } else {
        el.textContent = format(out, from, unit, currency);
      }
      el.setAttribute("data-shown", currency);
    }
  }

  function paintToggle() {
    var btns = document.querySelectorAll(".fxtog button");
    for (var i = 0; i < btns.length; i++) {
      var on = btns[i].getAttribute("data-cur") === currency;
      btns[i].setAttribute("aria-pressed", on ? "true" : "false");
      btns[i].className = on ? "on" : "";
    }
    var note = document.querySelector(".fxnote");
    if (note) {
      note.textContent = rate
        ? "Converted at USD/CAD " + rate.toFixed(4) + (rateAsOf ? " (" + rateAsOf + ")" : "")
        : "";
    }
  }

  function set(which) {
    currency = which === "USD" ? "USD" : "CAD";
    try { localStorage.setItem(STORE, currency); } catch (e) {}
    render();
    paintToggle();
    // The calculator recomputes its own outputs; tell it the currency changed.
    if (typeof window.NMCalcRefresh === "function") {
      try { window.NMCalcRefresh(); } catch (e) {}
    }
  }

  function wire() {
    var btns = document.querySelectorAll(".fxtog button");
    for (var i = 0; i < btns.length; i++) {
      btns[i].addEventListener("click", function () {
        if (!rate) return;
        set(this.getAttribute("data-cur"));
      });
    }
  }

  function disable(reason) {
    var tog = document.querySelector(".fxtog");
    if (tog) {
      tog.className = "fxtog off";
      tog.setAttribute("title", reason);
    }
  }

  function boot() {
    wire();
    paintToggle();
    fetch(RATE_URL, { cache: "no-cache" })
      .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
      .then(function (j) {
        if (!j || !isFinite(Number(j.usd_cad)) || Number(j.usd_cad) <= 0) {
          throw new Error("bad rate");
        }
        rate = Number(j.usd_cad);
        rateAsOf = j.as_of || "";
        render();
        paintToggle();
        if (typeof window.NMCalcRefresh === "function") {
          try { window.NMCalcRefresh(); } catch (e) {}
        }
      })
      .catch(function (e) {
        // Stay on native units and SAY SO rather than looking live.
        rate = null;
        disable("Currency conversion unavailable: " + e.message);
      });
  }

  // Exposed so page scripts can render marked values they generate at runtime.
  window.NMFX = {
    convert: convert,
    format: format,
    render: render,
    currency: function () { return currency; },
    rate: function () { return rate; },
    ready: function () { return rate !== null; }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
