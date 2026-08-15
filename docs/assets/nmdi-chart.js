/* Northern Mile — national diesel chart (D3). Loads only on home and fuel.
   Data is embedded in the page as JSON, so the figures survive if this script
   fails; the chart enhances the data, it is not the only copy of it. */
(function () {
  "use strict";
  if (typeof d3 === "undefined") return;
  var dataEl = document.getElementById("nmdi-data");
  var svgEl = document.getElementById("nmdi-chart");
  if (!dataEl || !svgEl) return;

  var payload;
  try { payload = JSON.parse(dataEl.textContent); } catch (e) { return; }
  var raw = (payload.diesel_national || payload);
  if (!raw.length) return;

  var all = raw.map(function (r) { return { date: new Date(r.d), v: r.v }; })
               .sort(function (a, b) { return a.date - b.date; });
  var loPoint = all.reduce(function (a, b) { return b.v < a.v ? b : a; });
  var hiPoint = all.reduce(function (a, b) { return b.v > a.v ? b : a; });
  var todayPoint = all[all.length - 1];

  var svg = d3.select("#nmdi-chart");
  var tip = document.getElementById("nmdi-tip");
  var readout = document.getElementById("nmdi-readout");
  var M = { t: 12, r: 16, b: 26, l: 40 };
  var iw, ih, x, y, gGrid, gLine, gArea, gAnn, gx, gy, area, line, focus, curDomain = null, _baseX = null;

  function fmtDate(d) { return d3.timeFormat("%b %Y")(d); }
  function fmtDay(d) { return d3.timeFormat("%d %b %Y")(d); }
  function baseX() { if (!_baseX) { _baseX = d3.scaleTime().range([0, iw]).domain(d3.extent(all, function (d) { return d.date; })); } return _baseX; }

  function build() {
    var W = svgEl.clientWidth, H = svgEl.clientHeight;
    iw = W - M.l - M.r; ih = H - M.t - M.b;
    svg.selectAll("*").remove();
    x = d3.scaleTime().range([0, iw]);
    y = d3.scaleLinear().range([ih, 0]);
    var root = svg.append("g").attr("transform", "translate(" + M.l + "," + M.t + ")");
    var clip = "nmdiclip" + Math.random().toString(36).slice(2);
    root.append("clipPath").attr("id", clip).append("rect").attr("width", iw).attr("height", ih);
    gGrid = root.append("g").attr("class", "grid");
    gArea = root.append("g").attr("clip-path", "url(#" + clip + ")");
    gLine = root.append("g").attr("clip-path", "url(#" + clip + ")");
    gAnn = root.append("g");
    gx = root.append("g").attr("class", "axis").attr("transform", "translate(0," + ih + ")");
    gy = root.append("g").attr("class", "axis");
    area = d3.area().x(function (d) { return x(d.date); }).y0(ih).y1(function (d) { return y(d.v); }).curve(d3.curveMonotoneX);
    line = d3.line().x(function (d) { return x(d.date); }).y(function (d) { return y(d.v); }).curve(d3.curveMonotoneX);
    gArea.append("path").attr("class", "area");
    gLine.append("path").attr("class", "line");
    focus = root.append("g").style("display", "none");
    focus.append("line").attr("class", "hover-line").attr("y1", 0).attr("y2", ih);
    focus.append("circle").attr("class", "hover-dot").attr("r", 4);
    root.append("rect").attr("width", iw).attr("height", ih).style("fill", "none").style("pointer-events", "all")
      .on("mousemove", move).on("mouseleave", function () { focus.style("display", "none"); tip.style.opacity = 0; })
      .on("touchmove", function (e) { e.preventDefault(); if (e.touches[0]) move(e.touches[0]); }, { passive: false });
    svg.call(d3.zoom().scaleExtent([1, 40]).extent([[0, 0], [iw, ih]]).translateExtent([[0, 0], [iw, ih]]).on("zoom", zoomed));
    render(curDomain);
  }

  function yPad(vis) {
    var lo = d3.min(vis, function (d) { return d.v; }), hi = d3.max(vis, function (d) { return d.v; });
    var pad = (hi - lo) * 0.08 || 5;
    y.domain([lo - pad, hi + pad]);
    return [lo, hi];
  }

  function annotate() {
    if (!gAnn) return;
    gAnn.selectAll("*").remove();
    var anns = [
      { d: loPoint, label: fmtDate(loPoint.date) + " · COVID", cls: "ann-low" },
      { d: hiPoint, label: fmtDate(hiPoint.date) + " · fuel crisis", cls: "ann-high" },
      { d: todayPoint, label: "today", cls: "ann-today" }
    ];
    anns.forEach(function (a) {
      if (a.d.date < x.domain()[0] || a.d.date > x.domain()[1]) return;
      var px = x(a.d.date);
      var anchor = px < 60 ? "start" : (px > iw - 60 ? "end" : "middle");
      var g = gAnn.append("g").attr("class", "ann " + a.cls);
      g.append("line").attr("class", "ann-line").attr("x1", px).attr("x2", px).attr("y1", 0).attr("y2", ih);
      g.append("circle").attr("class", "ann-dot").attr("cx", px).attr("cy", y(a.d.v)).attr("r", 3.5);
      g.append("text").attr("class", "ann-label").attr("x", px).attr("y", 4).attr("text-anchor", anchor).text(a.label);
    });
  }

  function render(domain) {
    x.domain(domain || d3.extent(all, function (d) { return d.date; }));
    var vis = all.filter(function (d) { return d.date >= x.domain()[0] && d.date <= x.domain()[1]; });
    var ext = yPad(vis);
    gGrid.call(d3.axisLeft(y).ticks(5).tickSize(-iw).tickFormat("")).select(".domain").remove();
    gx.call(d3.axisBottom(x).ticks(Math.max(2, Math.floor(iw / 90))).tickFormat(d3.timeFormat("%b '%y")));
    gy.call(d3.axisLeft(y).ticks(5));
    gArea.select(".area").datum(all).attr("d", area);
    gLine.select(".line").datum(all).attr("d", line);
    annotate();
    if (readout) readout.textContent = Math.round(ext[0] * 10) / 10 + "-" + Math.round(ext[1] * 10) / 10 + "\u00a2/L \u00b7 " + fmtDate(x.domain()[0]) + "-" + fmtDate(x.domain()[1]);
  }

  function zoomed(e) {
    var nx = e.transform.rescaleX(baseX());
    x.domain(nx.domain());
    var vis = all.filter(function (d) { return d.date >= x.domain()[0] && d.date <= x.domain()[1]; });
    if (vis.length) yPad(vis);
    gx.call(d3.axisBottom(x).ticks(Math.max(2, Math.floor(iw / 90))).tickFormat(d3.timeFormat("%b '%y")));
    gy.call(d3.axisLeft(y).ticks(5));
    gGrid.call(d3.axisLeft(y).ticks(5).tickSize(-iw).tickFormat("")).select(".domain").remove();
    gLine.select(".line").attr("d", line);
    gArea.select(".area").attr("d", area);
    annotate();
    if (readout) { var d0 = x.domain(); readout.textContent = Math.round(y.domain()[0]) + "-" + Math.round(y.domain()[1]) + "\u00a2/L \u00b7 " + fmtDate(d0[0]) + "-" + fmtDate(d0[1]); }
  }

  var bisect = d3.bisector(function (d) { return d.date; }).left;
  function move(ev) {
    var pt = d3.pointer(ev, gLine.node());
    var d0 = x.invert(pt[0]);
    var i = bisect(all, d0, 1), a = all[i - 1], b = all[i];
    if (!a) return;
    var d = (b && (d0 - a.date > b.date - d0)) ? b : a;
    focus.style("display", null);
    focus.select("circle").attr("cx", x(d.date)).attr("cy", y(d.v));
    focus.select("line").attr("x1", x(d.date)).attr("x2", x(d.date));
    tip.style.opacity = 1;
    tip.innerHTML = '<span class="v">' + d.v + '\u00a2/L</span><br><span class="d">' + fmtDay(d.date) + '</span>';
    var box = svgEl.getBoundingClientRect();
    tip.style.left = Math.min(M.l + x(d.date) + 12, box.width - 90) + "px";
    tip.style.top = (M.t + y(d.v) - 10) + "px";
  }

  var ranges = document.getElementById("nmdi-ranges");
  var story = document.getElementById("nmdi-story");
  function clearStory() { if (story) story.querySelectorAll("button").forEach(function (x) { x.classList.remove("on"); }); }
  function clearRanges() { if (ranges) ranges.querySelectorAll("button").forEach(function (x) { x.classList.remove("on"); }); }
  if (ranges) ranges.addEventListener("click", function (e) {
    var b = e.target.closest("button"); if (!b) return;
    clearRanges(); b.classList.add("on"); clearStory();
    var yrs = +b.dataset.years; _baseX = null;
    svg.call(d3.zoom().transform, d3.zoomIdentity);
    if (yrs === 0) curDomain = null;
    else { var end = all[all.length - 1].date; var start = new Date(end); start.setFullYear(start.getFullYear() - yrs); curDomain = [start, end]; }
    render(curDomain);
  });
  if (story) story.addEventListener("click", function (e) {
    var b = e.target.closest("button"); if (!b) return;
    clearStory(); b.classList.add("on"); clearRanges();
    var f = b.dataset.focus;
    var target = f === "low" ? loPoint : f === "high" ? hiPoint : todayPoint;
    var start = new Date(target.date), end = new Date(target.date);
    if (f === "today") { start.setFullYear(start.getFullYear() - 1); }
    else { start.setMonth(start.getMonth() - 12); end.setMonth(end.getMonth() + 12); }
    _baseX = null;
    svg.call(d3.zoom().transform, d3.zoomIdentity);
    curDomain = [start, end];
    render(curDomain);
  });

  build();
  window.addEventListener("resize", function () { _baseX = null; build(); });
})();
