/* Lunar Landing Site Navigator - static front end.
   Physics inputs come from the pipeline (backend/build_site_data.py): skylines from LOLA, Sun/Earth az/el from
   JPL Horizons. This file only applies the same visibility rules (DS3) to the user's settings (mast, convention,
   threshold, date slip). Equation ids refer to RESOURCE/SCIENCE/EQUATIONS_CHEATSHEET.md. No result is hard-coded. */
"use strict";
const R_SUN_KM = 695700, R_EARTH_KM = 6378.137, AU_KM = 149597870.7, C_KM_S = 299792.458; // CONSTANTS.md
const DEFAULTS = { mast: 2, conv: "centre", thr: 0, goSun: 60, goNight: 100, goEarth: 50 };
const S = { index: null, sites: {}, validation: [], scenarios: [], view: "compare", k: 0, learn: false, playing: null,
            set: { ...DEFAULTS } };
const $ = (q) => document.querySelector(q);
const GROUPS = { artemis_region: "Artemis candidate regions", artemis_2022: "Artemis III regions (2022 list)",
  clps_flown: "CLPS flown", apollo: "Apollo", other_agency: "Other agencies", custom: "Custom" };
const PRESETS = [
  { name: "Artemis regions tour", sc: [["malapert", 0], ["haworth", 0], ["nobile_rim_1", 0], ["de_gerlache_rim_2", 0]] },
  { name: "Move 2.5 km: Malapert slope vs summit", sc: [["malapert", 0], ["malapert_summit", 0]] },
  { name: "Slip a landing by 14 days", sc: [["malapert", 0], ["malapert", 14]] },
  { name: "Apollo 11 vs south pole ridge", sc: [["apollo_11", 0], ["connecting_ridge", 0]] },
];

// ---------- data ----------
async function getJSON(u) { const r = await fetch(u); if (!r.ok) throw new Error(u + " " + r.status); return r.json(); }
async function site(id) { if (!S.sites[id]) S.sites[id] = await getJSON(`data/sites/${id}.json`); return S.sites[id]; }
const perDay = (d) => (24 * 60) / d.window.step_min;
const nWin = (d) => d.window.days_default * perDay(d);
const stepH = (d) => d.window.step_min / 60;
const t0 = (d) => Date.parse(d.window.start_utc);

// ---------- physics helpers (same rules as backend/visibility.py) ----------
function skylineAt(H, az) { const n = H.length, st = 360 / n, x = (((az % 360) + 360) % 360) / st, i0 = Math.floor(x) % n, f = x - Math.floor(x); return H[i0] * (1 - f) + H[(i0 + 1) % n] * f; }
const rhoSun = (au) => Math.asin(R_SUN_KM / (au * AU_KM)) * 180 / Math.PI;         // E10
const rhoEarth = (km) => Math.asin(R_EARTH_KM / km) * 180 / Math.PI;                // E10
function litFraction(e, h, rho) { let u = Math.max(-1, Math.min(1, (h - e) / rho)); return (Math.acos(u) - u * Math.sqrt(1 - u * u)) / Math.PI; } // E11

function analyse(d, slip, set) {
  const H = d.skyline.by_mast[String(set.mast)].H_deg, dist = d.skyline.by_mast[String(set.mast)].dist_km;
  const n = nWin(d), off = Math.round(slip * perDay(d)), sh = stepH(d);
  const ms = new Float64Array(n), me = new Float64Array(n), su = new Uint8Array(n), eu = new Uint8Array(n);
  for (let i = 0; i < n; i++) {
    const j = off + i;
    const rs = rhoSun(d.sun.dist_au[j]), re = rhoEarth(d.earth.dist_km[j]);
    let a = d.sun.el[j] - skylineAt(H, d.sun.az[j]), b = d.earth.el[j] - skylineAt(H, d.earth.az[j]) - set.thr;
    if (set.conv === "any") { a += rs; b += re; }
    ms[i] = a; me[i] = b; su[i] = a > 0; eu[i] = b > 0;
  }
  const runs = (f, v) => { const out = []; let s = null; for (let i = 0; i <= n; i++) { const on = i < n && !!f[i] === v; if (on && s === null) s = i; if (!on && s !== null) { out.push([s, i]); s = null; } } return out; };
  const longest = (r) => r.reduce((m, [a, b]) => Math.max(m, (b - a) * sh), 0);
  const pct = (f) => 100 * f.reduce((s, x) => s + x, 0) / n;
  const both = new Uint8Array(n), none = new Uint8Array(n); for (let i = 0; i < n; i++) { both[i] = su[i] && eu[i]; none[i] = !su[i] && !eu[i]; }
  let maxEl = -90; for (let i = 0; i < n; i++) maxEl = Math.max(maxEl, d.sun.el[off + i]);
  const cross = (m) => { const out = []; for (let i = 0; i < n - 1; i++) if (Math.sign(m[i]) !== Math.sign(m[i + 1]) && m[i] !== m[i + 1]) { const f = m[i] / (m[i] - m[i + 1]); out.push({ i: i + f, kind: m[i + 1] > m[i] ? "rise" : "set" }); } return out; }; // D8
  return { d, slip, off, n, sh, H, dist, ms, me, su, eu,
    win: { sun: runs(su, true), earth: runs(eu, true), blackout: runs(none, true) },
    ev: { sun: cross(ms), earth: cross(me) },
    m: { sunlight_pct: pct(su), longest_night_h: longest(runs(su, false)), earth_pct: pct(eu), longest_no_earth_h: longest(runs(eu, false)),
         both_pct: pct(both), blackout_longest_h: longest(runs(none, true)), max_sun_el_deg: maxEl } };
}

function verdict(m, set) {
  const ok = (k) => m.sunlight_pct >= set.goSun * k && m.longest_night_h <= set.goNight / k && m.earth_pct >= set.goEarth * k;
  return ok(1) ? "GO" : ok(0.5) ? "MARGINAL" : "NO-GO";
}

// ---------- formatting ----------
const fmt = (x, p = 1) => (x === null || x === undefined || Number.isNaN(x)) ? "-" : Number(x).toFixed(p);
function dur(h) { if (h < 1) return `${Math.round(h * 60)} min`; const D = Math.floor(h / 24), Hh = Math.floor(h % 24), M = Math.round((h * 60) % 60); return D ? `${D} d ${Hh} h` : `${Hh} h ${M} min`; }
function utc(ms) { return new Date(ms).toISOString().slice(0, 16).replace("T", " ") + " UTC"; }
const timeAt = (A, i) => t0(A.d) + (A.off + i) * A.sh * 3600e3;

function countdown(A, body) {
  const k = S.k, up = body === "sun" ? A.su[k] : A.eu[k], ev = A.ev[body].find((e) => e.i > k);
  const name = body === "sun" ? (up ? "Sunset" : "Sunrise") : (up ? "Earthset" : "Earthrise");
  if (!ev) return { text: up ? `No ${name.toLowerCase()} in window` : `No ${name.toLowerCase()} in window`, sub: `> ${dur((A.n - k) * A.sh)}` };
  return { text: `${name} in ${dur((ev.i - k) * A.sh)}`, sub: utc(timeAt(A, ev.i)) };
}

// ---------- panorama (F6) ----------
function drawPanorama(cv, A) {
  const dpr = window.devicePixelRatio || 1, W = cv.clientWidth, Hh = cv.clientHeight;
  cv.width = W * dpr; cv.height = Hh * dpr; const g = cv.getContext("2d"); g.scale(dpr, dpr);
  const d = A.d, j = A.off + S.k, H = A.H;
  const se = d.sun.el[j], sa = d.sun.az[j], ee = d.earth.el[j], ea = d.earth.az[j];
  const top = Math.max(4, Math.ceil(Math.max(...H, se, ee) + 1)), bot = Math.min(-2, Math.floor(Math.min(...H) - 1));
  const x = (az) => (az / 360) * W, y = (el) => Hh - ((el - bot) / (top - bot)) * Hh;
  g.clearRect(0, 0, W, Hh);
  // libration / path traces over the window (F10)
  g.globalAlpha = 0.35;
  for (const [body, col] of [["earth", "#6CB4FF"], ["sun", "#F2B544"]]) { g.fillStyle = col; for (let i = 0; i < A.n; i += 6) { const k2 = A.off + i; g.fillRect(x(d[body].az[k2]), y(d[body].el[k2]), 1.2, 1.2); } }
  g.globalAlpha = 1;
  // flat horizon
  g.strokeStyle = "rgba(255,255,255,.25)"; g.setLineDash([4, 4]); g.beginPath(); g.moveTo(0, y(0)); g.lineTo(W, y(0)); g.stroke(); g.setLineDash([]);
  // terrain skyline
  g.beginPath(); g.moveTo(0, Hh); for (let i = 0; i <= H.length; i++) g.lineTo(x(i * 360 / H.length), y(H[i % H.length])); g.lineTo(W, Hh); g.closePath();
  g.fillStyle = "#2a2d33"; g.fill(); g.strokeStyle = "#B8BEC8"; g.lineWidth = 1; g.stroke();
  // bodies at true angular size
  const pxPerDeg = Hh / (top - bot);
  const disc = (az, el, rho, col, earth) => { const r = Math.max(2.5, rho * pxPerDeg); g.beginPath(); g.arc(x(az), y(el), r, 0, 2 * Math.PI); g.fillStyle = col; g.fill();
    if (earth) { g.strokeStyle = "#05070B"; g.beginPath(); g.moveTo(x(az), y(el) - r); g.lineTo(x(az), y(el) + r); g.stroke(); } };
  disc(sa, se, rhoSun(d.sun.dist_au[j]), "#F2B544", false); disc(ea, ee, rhoEarth(d.earth.dist_km[j]), "#6CB4FF", true);
  // axis labels
  g.fillStyle = "#9AA1AC"; g.font = "11px 'IBM Plex Mono', monospace";
  for (const [az, l] of [[0, "N 0"], [90, "E 90"], [180, "S 180"], [270, "W 270"]]) g.fillText(l, Math.min(x(az) + 3, W - 40), Hh - 4);
  g.fillText(`${top} deg`, 3, 12); g.fillText(`${bot} deg`, 3, Hh - 16);
  cv.setAttribute("aria-label", `Horizon panorama. Sun azimuth ${fmt(sa)} deg, elevation ${fmt(se, 2)} deg; skyline there ${fmt(skylineAt(H, sa), 2)} deg. Earth azimuth ${fmt(ea)} deg, elevation ${fmt(ee, 2)} deg.`);
}

// ---------- change explainer (F17) ----------
function explain(A, B) {
  const dS = B.m.sunlight_pct - A.m.sunlight_pct, dN = B.m.longest_night_h - A.m.longest_night_h, dE = B.m.earth_pct - A.m.earth_pct;
  const parts = [`Sunlight ${dS >= 0 ? "+" : ""}${fmt(dS)} pts, longest night ${dN >= 0 ? "+" : ""}${fmt(dN)} h, Earth ${dE >= 0 ? "+" : ""}${fmt(dE)} pts vs ${A.d.name}${A.slip ? ` (+${A.slip} d)` : ""}.`];
  // cause: where the skyline blocks the Sun the most during this scenario's nights
  let best = null;
  for (let i = 0; i < B.n; i++) if (!B.su[i]) { const j = B.off + i, az = B.d.sun.az[j], gap = skylineAt(B.H, az) - B.d.sun.el[j];
    if (B.d.sun.el[j] > 0 && (!best || gap > best.gap)) best = { az, gap, h: skylineAt(B.H, az), k: Math.round(az / 0.5) % B.H.length }; }
  if (best) parts.push(`Cause: terrain at az ${fmt(best.az, 0)} deg rises to ${fmt(best.h, 2)} deg (${fmt(B.dist[best.k], 1)} km away) and hides the Sun while it is above the flat horizon.`);
  if (A.d.id === B.d.id && A.slip !== B.slip) parts.push(`Same site, date slipped ${B.slip - A.slip} d: max Sun elevation ${fmt(A.m.max_sun_el_deg, 2)} -> ${fmt(B.m.max_sun_el_deg, 2)} deg.`);
  return parts.join(" ");
}

// ---------- learn sentences (F14) ----------
const L = {
  sunEl: (A, c) => `The Sun is ${fmt(Math.abs(c), 2)} deg ${c >= 0 ? "above" : "below"} the local terrain line. Near the pole it never climbs more than a few degrees.`,
  cd: () => `On the Moon a full day-night cycle lasts 29.5 Earth days, so sunsets are days apart, not hours.`,
  sun: (m) => `This spot gets sunlight ${fmt(m.sunlight_pct, 0)} % of the time in these 30 days; the longest dark spell, ${dur(m.longest_night_h)}, sets the battery size.`,
  earth: (m) => `Earth is in view ${fmt(m.earth_pct, 0)} % of the time. When it is hidden, a lander needs a relay satellite to talk home.`,
};

// ---------- render: compare (F3, F6-F10, F17-F20, F23) ----------
async function renderCompare() {
  const box = $("#cards"); box.innerHTML = "";
  const As = [];
  for (const sc of S.scenarios) As.push(analyse(await site(sc.id), sc.slip, S.set));
  As.forEach((A, idx) => {
    const d = A.d, j = A.off + S.k, k = S.k, m = A.m, v = verdict(m, S.set);
    const clr = d.sun.el[j] - skylineAt(A.H, d.sun.az[j]), lf = litFraction(d.sun.el[j], skylineAt(A.H, d.sun.az[j]), rhoSun(d.sun.dist_au[j]));
    const cdS = countdown(A, "sun"), cdE = countdown(A, "earth");
    const card = document.createElement("article"); card.className = "card glass";
    const vcls = v === "GO" ? "" : v === "MARGINAL" ? "marginal" : "nogo";
    card.innerHTML = `
      <div class="card-head"><div><h2>${d.name}</h2>
        <div class="sub mono">${fmt(d.lat, 3)}, ${fmt(d.lon_e, 3)} E · ${utc(timeAt(A, k))}${A.slip ? ` · slip +${A.slip} d` : ""}</div></div>
        <span class="chip ${vcls}" title="Thresholds: GO if sunlight >= ${S.set.goSun} %, longest night <= ${S.set.goNight} h, Earth >= ${S.set.goEarth} %">${v === "NO-GO" ? "&#9650; " : ""}${v}</span></div>
      <canvas class="pano"></canvas>
      <div class="nums">
        <div class="num"><div class="label">Sun elevation (flat / above terrain)</div><div class="value sun">${fmt(d.sun.el[j], 2)}<span class="unit"> deg</span></div><div class="mono">${clr >= 0 ? "+" : ""}${fmt(clr, 2)} deg clearance · lit ${fmt(100 * lf, 0)} %</div>${S.learn ? `<div class="learn">${L.sunEl(A, clr)}</div>` : ""}</div>
        <div class="num"><div class="label">Countdown</div><div class="value" style="font-size:18px">${cdS.text}</div><div class="mono earth" style="color:var(--earth)">${cdE.text}</div>${S.learn ? `<div class="learn">${L.cd()}</div>` : ""}</div>
        <div class="num"><div class="label">Sunlight in 30 days</div><div class="value sun">${fmt(m.sunlight_pct)}<span class="unit"> %</span></div><div class="mono">longest night ${dur(m.longest_night_h)}</div>${S.learn ? `<div class="learn">${L.sun(m)}</div>` : ""}</div>
        <div class="num"><div class="label">Earth in view</div><div class="value earth">${fmt(m.earth_pct)}<span class="unit"> %</span></div><div class="mono">longest gap ${dur(m.longest_no_earth_h)}</div>${S.learn ? `<div class="learn">${L.earth(m)}</div>` : ""}</div>
      </div>
      <div class="badges"><span class="badge">terrain ${d.terrain_source}${d.terrain_coverage < 1 ? ` (${fmt(100 * d.terrain_coverage, 0)} % covered)` : ""}</span><span class="badge">ephemeris Horizons precomputed</span><span class="badge">${d.status}</span><span class="badge">mast ${S.set.mast} m · ${S.set.conv}</span></div>
      <details class="more"><summary>More</summary>
        <table><tbody>
          <tr><th>Both Sun and Earth up</th><td class="mono">${fmt(m.both_pct)} %</td></tr>
          <tr><th><span class="alert-text">&#9650; Blackout</span>, longest (no Sun, no Earth)</th><td class="mono">${dur(m.blackout_longest_h)}</td></tr>
          <tr><th>Max Sun elevation in window</th><td class="mono">${fmt(m.max_sun_el_deg, 2)} deg</td></tr>
          <tr><th>Panel factor now: horizontal / vertical / tracking</th><td class="mono">${fmt(Math.max(0, Math.sin(d.sun.el[j] * Math.PI / 180)) * lf, 3)} / ${fmt(Math.max(0, Math.cos(d.sun.el[j] * Math.PI / 180)) * lf, 3)} / ${fmt(lf, 3)}</td></tr>
          <tr><th>Solar flux now (E19)</th><td class="mono">${fmt(1360.8 / d.sun.dist_au[j] ** 2, 0)} W/m2</td></tr>
          <tr><th>Earth elevation now / distance / light time</th><td class="mono">${fmt(d.earth.el[j], 2)} deg / ${fmt(d.earth.dist_km[j], 0)} km / ${fmt(d.earth.dist_km[j] / C_KM_S, 3)} s</td></tr>
          <tr><th>Site height (LOLA, above 1737.4 km)</th><td class="mono">${d.h_site_m === null ? "smooth sphere" : fmt(d.h_site_m, 1) + " m"}</td></tr>
          <tr><th>Source</th><td>${d.source}</td></tr>
        </tbody></table>
        ${idx > 0 ? `<p class="explain">${explain(As[0], A)}</p>` : ""}
        <h3>Windows (UTC)</h3><div class="tbl-scroll"><table><thead><tr><th>Kind</th><th>Start</th><th>End</th><th>Hours</th></tr></thead><tbody>
        ${["sun", "earth", "blackout"].flatMap((kind) => A.win[kind].map(([a, b]) => `<tr><td>${kind}</td><td class="mono">${utc(timeAt(A, a))}</td><td class="mono">${utc(timeAt(A, b))}</td><td class="mono">${fmt((b - a) * A.sh)}</td></tr>`)).join("")}
        </tbody></table></div>
      </details>`;
    box.appendChild(card);
    drawPanorama(card.querySelector(".pano"), A);
  });
  if (!As.length) box.innerHTML = `<p class="note">No scenario yet. Open Plan and add a site.</p>`;
  S.last = As; updateClock();
}

// ---------- render: timeline (F13, F19) ----------
async function renderTimeline() {
  const cv = $("#gantt"); const As = []; for (const sc of S.scenarios) As.push(analyse(await site(sc.id), sc.slip, S.set));
  const dpr = window.devicePixelRatio || 1, W = cv.clientWidth, rowH = 54, Hh = Math.max(120, As.length * rowH + 30);
  cv.style.height = Hh + "px"; cv.width = W * dpr; cv.height = Hh * dpr; const g = cv.getContext("2d"); g.scale(dpr, dpr);
  const left = 170, x = (i, n) => left + (i / n) * (W - left - 10);
  g.font = "12px 'IBM Plex Sans', sans-serif";
  As.forEach((A, r) => {
    const y0 = 10 + r * rowH; g.fillStyle = "#FFFFFF"; g.fillText(A.d.name.slice(0, 24), 4, y0 + 14); g.fillStyle = "#9AA1AC"; g.fillText(A.slip ? `slip +${A.slip} d` : "base date", 4, y0 + 30);
    for (const [kind, col, dy] of [["sun", "#F2B544", 0], ["earth", "#6CB4FF", 16], ["blackout", "#FF6B6B", 32]])
      for (const [a, b] of A.win[kind]) { g.fillStyle = col; g.fillRect(x(a, A.n), y0 + dy, Math.max(1, x(b, A.n) - x(a, A.n)), kind === "blackout" ? 6 : 12); }
  });
  if (As.length) { const xx = x(S.k, As[0].n); g.strokeStyle = "#FFFFFF"; g.beginPath(); g.moveTo(xx, 0); g.lineTo(xx, Hh); g.stroke(); }
  g.fillStyle = "#9AA1AC"; for (let dday = 0; dday <= 30; dday += 5) if (As.length) g.fillText(`d${dday}`, x(dday * perDay(As[0].d), As[0].n) - 6, Hh - 4);
  cv.onmousemove = (e) => { if (!As.length) return; const rect = cv.getBoundingClientRect(), px = e.clientX - rect.left, r = Math.floor((e.clientY - rect.top - 10) / rowH);
    const A = As[Math.max(0, Math.min(As.length - 1, r))], i = Math.round(((px - left) / (W - left - 10)) * A.n);
    if (i < 0 || i >= A.n) return; const find = (kind) => A.win[kind].find(([a, b]) => i >= a && i < b);
    const s = find("sun"), ea = find("earth");
    $("#ganttHover").textContent = `${A.d.name} · ${utc(timeAt(A, i))} · Sun ${s ? `up ${utc(timeAt(A, s[0]))} to ${utc(timeAt(A, s[1]))}` : "down"} · Earth ${ea ? `up ${utc(timeAt(A, ea[0]))} to ${utc(timeAt(A, ea[1]))}` : "down"}`; };
  cv.onclick = (e) => { if (!As.length) return; const rect = cv.getBoundingClientRect(); const i = Math.round(((e.clientX - rect.left - left) / (W - left - 10)) * As[0].n); if (i >= 0 && i < As[0].n) setK(i); };
  S.last = As; updateClock();
}

// ---------- render: plan (F1, F3, F4, F22) ----------
function renderPlan() {
  const q = ($("#siteFilter").value || "").toLowerCase(), list = $("#siteList"); list.innerHTML = "";
  const groups = {}; for (const s of S.index.sites) if (s.name.toLowerCase().includes(q)) (groups[s.group] ||= []).push(s);
  for (const [gk, arr] of Object.entries(groups)) {
    const h = document.createElement("div"); h.className = "site-group"; h.textContent = GROUPS[gk] || gk; list.appendChild(h);
    for (const s of arr) { const row = document.createElement("div"); row.className = "site";
      row.innerHTML = `<div><div class="name">${s.name}</div><div class="meta mono">${fmt(s.lat, 3)}, ${fmt(s.lon_e, 3)} E · ${s.terrain_source}</div><div class="meta">${s.source}</div></div>
        <div><span class="badge">${s.status}</span> <button aria-label="Add ${s.name} to scenarios">Add</button></div>`;
      row.querySelector("button").onclick = () => { if (S.scenarios.length < 4) { S.scenarios.push({ id: s.id, slip: 0 }); saveURL(); renderPlan(); } };
      list.appendChild(row); }
  }
  const tray = $("#tray"); tray.innerHTML = S.scenarios.length ? "" : `<p class="note">Add up to 4 sites, or pick a preset.</p>`;
  S.scenarios.forEach((sc, i) => { const s = S.index.sites.find((x) => x.id === sc.id); const el = document.createElement("div"); el.className = "tray-item";
    el.innerHTML = `<span class="name">${String.fromCharCode(65 + i)}. ${s ? s.name : sc.id}</span>
      <label class="slip">Slip <input type="number" min="0" max="30" value="${sc.slip}" aria-label="Date slip in days"> d</label>
      <span><button aria-label="Duplicate with +14 d slip">+14 d copy</button> <button aria-label="Remove">Remove</button></span>`;
    el.querySelector("input").onchange = (e) => { sc.slip = Math.max(0, Math.min(30, +e.target.value || 0)); saveURL(); };
    const [dup, rm] = el.querySelectorAll("button");
    dup.onclick = () => { if (S.scenarios.length < 4) { S.scenarios.push({ id: sc.id, slip: Math.min(30, sc.slip + 14) }); saveURL(); renderPlan(); } };
    rm.onclick = () => { S.scenarios.splice(i, 1); saveURL(); renderPlan(); };
    tray.appendChild(el); });
  const pr = $("#presets"); pr.innerHTML = "";
  PRESETS.forEach((p) => { const b = document.createElement("button"); b.textContent = p.name; b.onclick = () => { S.scenarios = p.sc.map(([id, slip]) => ({ id, slip })); saveURL(); setView("compare"); }; pr.appendChild(b); });
}

// ---------- evidence (F15) ----------
function renderEvidence() {
  const v = S.validation.map((r) => `<tr><td>${r.site}</td><td>${r.metric}</td><td class="mono">${r.ours}</td><td class="mono">${r.reference}</td><td class="mono">${r.difference ?? "-"}</td><td>${r.reference_source}. ${r.comment}</td></tr>`).join("");
  $("#evidenceBody").innerHTML = `
    <h3>Data sources</h3><ul>
      <li>Sun and Earth apparent azimuth/elevation: JPL Horizons observer tables (DE441), lunar site in the Moon mean-Earth frame, airless (no refraction), precomputed every ${S.index.step_min} min for ${S.index.series_days} days from ${S.index.series_start_utc}.</li>
      <li>Terrain: LRO LOLA polar gridded DEMs LDEM_85S_20M (20 m/px) and LDEM_80S_80M (80 m/px), PDS Geosciences Node; height = DN x 0.5 m above the 1737.4 km sphere (label SCALING_FACTOR).</li>
      <li>Site coordinates: team SITE_CATALOG with status per site (OFFICIAL / TEAM / SECONDARY); TEAM points are selected by maximum illumination inside the region.</li></ul>
    <h3>Conventions in force</h3><ul>
      <li>Disc: <b>${S.set.conv === "centre" ? "centre of disc" : "any part of disc"}</b> (D1; headline uses centre). Earth link threshold: ${fmt(S.set.thr)} deg above the skyline (D2). Mast: ${S.set.mast} m (D3).</li>
      <li>Skyline: 720 azimuths, rays to 150 km, Moon curvature d^2/2R subtracted (E06-E08), never below the smooth-sphere dip (E09). No atmospheric refraction.</li>
      <li>Window: 30 days at 10 min (D7); events interpolated inside the step (D8). Verdict thresholds are planner choices, not NASA criteria.</li></ul>
    <h3>Validation</h3><div class="tbl-scroll" style="max-height:none"><table><thead><tr><th>Site</th><th>Check</th><th>Ours</th><th>Reference</th><th>Diff</th><th>Source / note</th></tr></thead><tbody>${v}</tbody></table></div>
    <h3>AI disclosure</h3><p>Code written with Claude (Anthropic) under human direction; every number on screen comes from the pipeline applied to NASA data. Full log: AI_USAGE_LOG.md in the repository.</p>
    <p class="note">Data generated ${S.index.generated_utc} · pipeline ${S.index.pipeline_version}. Not affiliated with or endorsed by NASA.</p>`;
}

// ---------- shared time, views, settings ----------
function updateClock() { const A = S.last && S.last[0]; const lbl = A ? utc(timeAt(A, S.k)) : ""; $("#clock").textContent = lbl; $("#timeLabel").textContent = A ? `day ${fmt(S.k * A.sh / 24, 2)} · ${lbl}` : ""; }
let pending = null;
function setK(k) { S.k = k; $("#time").value = k; if (pending) return; pending = requestAnimationFrame(() => { pending = null; render(); }); }
async function render() { if (S.view === "compare") await renderCompare(); else if (S.view === "timeline") await renderTimeline(); else { renderPlan(); updateClock(); } }
function setView(v) { S.view = v; for (const s of ["plan", "compare", "timeline"]) $(`#view-${s}`).hidden = s !== v;
  document.querySelectorAll(".tabs button").forEach((b) => b.toggleAttribute("aria-current", b.dataset.view === v)); render(); }
function adjCount() { const n = ["mast", "conv", "thr", "goSun", "goNight", "goEarth"].filter((k) => S.set[k] !== DEFAULTS[k]).length; $("#adjustCount").innerHTML = n ? `<span class="dot"></span> ${n}` : ""; }
function readSettings() { S.set = { mast: +$("#mast").value, conv: $("#conv").value, thr: +$("#thr").value, goSun: +$("#goSun").value, goNight: +$("#goNight").value, goEarth: +$("#goEarth").value };
  $("#thrVal").textContent = `${fmt(S.set.thr)} deg`; adjCount(); saveURL(); render(); }
function writeSettings() { $("#mast").value = S.set.mast; $("#conv").value = S.set.conv; $("#thr").value = S.set.thr; $("#goSun").value = S.set.goSun; $("#goNight").value = S.set.goNight; $("#goEarth").value = S.set.goEarth; $("#thrVal").textContent = `${fmt(S.set.thr)} deg`; adjCount(); }
function saveURL() { const p = new URLSearchParams({ s: S.scenarios.map((x) => `${x.id}:${x.slip}`).join(","), k: S.k, ...Object.fromEntries(Object.entries(S.set).map(([a, b]) => [a, b])) });
  history.replaceState(null, "", "#" + p.toString()); }
function loadURL() { const p = new URLSearchParams(location.hash.slice(1)); if (p.get("s")) S.scenarios = p.get("s").split(",").filter(Boolean).map((t) => { const [id, slip] = t.split(":"); return { id, slip: +slip || 0 }; });
  for (const k of Object.keys(DEFAULTS)) if (p.has(k)) S.set[k] = k === "conv" ? p.get(k) : +p.get(k); if (p.has("k")) S.k = +p.get("k"); }
function drawer(id, open) { const el = $(id); el.hidden = !open; if (open) el.querySelector("select,input,button").focus(); }

async function init() {
  try { S.index = await getJSON("data/index.json"); S.validation = await getJSON("data/validation.json"); }
  catch (e) { $("#cards").innerHTML = `<p class="alert-text">&#9650; Data not found. Run <code>python -m backend.build_site_data</code> first.</p>`; return; }
  S.scenarios = [{ id: "malapert", slip: 0 }, { id: "malapert_summit", slip: 0 }, { id: "connecting_ridge", slip: 0 }];
  loadURL(); writeSettings();
  const first = await site(S.scenarios[0].id); $("#time").max = nWin(first) - 1; $("#time").value = S.k;
  document.querySelectorAll(".tabs button").forEach((b) => (b.onclick = () => setView(b.dataset.view)));
  $("#goCompare").onclick = () => setView("compare"); $("#siteFilter").oninput = renderPlan;
  $("#time").oninput = (e) => setK(+e.target.value);
  $("#play").onclick = () => { if (S.playing) { clearInterval(S.playing); S.playing = null; $("#play").textContent = "Play"; return; }
    $("#play").textContent = "Pause"; S.playing = setInterval(() => setK((S.k + 6) % (+$("#time").max + 1)), 120); };
  $("#learn").onchange = (e) => { S.learn = e.target.checked; render(); };
  for (const id of ["#mast", "#conv", "#thr", "#goSun", "#goNight", "#goEarth"]) $(id).oninput = readSettings;
  $("#reset").onclick = () => { S.set = { ...DEFAULTS }; writeSettings(); saveURL(); render(); };
  $("#adjustBtn").onclick = () => drawer("#adjust", $("#adjust").hidden); $("#closeAdjust").onclick = () => drawer("#adjust", false);
  $("#evidenceBtn").onclick = () => { renderEvidence(); drawer("#evidence", $("#evidence").hidden); }; $("#closeEvidence").onclick = () => drawer("#evidence", false);
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") { drawer("#adjust", false); drawer("#evidence", false); } });
  window.addEventListener("resize", () => render());
  setView("compare");
}
init();
