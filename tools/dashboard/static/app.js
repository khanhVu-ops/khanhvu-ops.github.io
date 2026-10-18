// KV Studio dashboard — vanilla JS, no build step. State comes from /api/state (the repo, read live).

const $ = (sel, el = document) => el.querySelector(sel);
const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const attr = (obj) => esc(JSON.stringify(obj));

/* ---------- icons (24px stroke) ---------- */
const P = {
  home: '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V20h5v-6h4v6h5V9.5"/>',
  film: '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M7 3v18M17 3v18M3 8h4M3 16h4M17 8h4M17 16h4"/>',
  calendar: '<rect x="3" y="4.5" width="18" height="16.5" rx="3"/><path d="M8 2.5v4M16 2.5v4M3 10h18"/>',
  send: '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
  chart: '<path d="M3 3v18h18"/><path d="M7 15l4-5 3 3 5-7"/>',
  link: '<path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/>',
  users: '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M21.5 20a6.5 6.5 0 0 0-4-6"/>',
  refresh: '<path d="M20 11a8 8 0 0 0-14.5-4.5L3 9"/><path d="M3 4v5h5"/><path d="M4 13a8 8 0 0 0 14.5 4.5L21 15"/><path d="M21 20v-5h-5"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
  moon: '<path d="M20.5 14.5A8.5 8.5 0 1 1 9.5 3.5a7 7 0 0 0 11 11Z"/>',
  copy: '<rect x="8" y="8" width="13" height="13" rx="3"/><path d="M16 8V5.5A2.5 2.5 0 0 0 13.5 3h-8A2.5 2.5 0 0 0 3 5.5v8A2.5 2.5 0 0 0 5.5 16H8"/>',
  ext: '<path d="M14 3h7v7"/><path d="M21 3 11 13"/><path d="M19 14v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h5"/>',
  folder: '<path d="M3 7a2 2 0 0 1 2-2h4l2 2.5h8a2 2 0 0 1 2 2V18a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z"/>',
  upload: '<path d="M12 15V3"/><path d="m7 8 5-5 5 5"/><path d="M4 15v4a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  checkCircle: '<circle cx="12" cy="12" r="9"/><path d="m8 12.5 2.8 2.8L16.5 9.5"/>',
  alert: '<path d="M10.3 3.9 2.4 18a2 2 0 0 0 1.7 3h15.8a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4M12 17h.01"/>',
  xCircle: '<circle cx="12" cy="12" r="9"/><path d="m15 9-6 6M9 9l6 6"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 7.5h.01"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  trash: '<path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M6 6l1 14h10l1-14"/>',
  x: '<path d="M18 6 6 18M6 6l12 12"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
  play: '<path d="M7 4v16l13-8Z"/>',
  eye: '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
  sparkle: '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6"/>',
  target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
  download: '<path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M4 21h16"/>',
  clapper: '<path d="M4 11v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8Z"/><path d="m4 11-.9-3.6a2 2 0 0 1 1.5-2.4l11.6-2.9a2 2 0 0 1 2.4 1.5L19.5 7Z"/><path d="m7.5 4.3 3 3.7M12.8 3l3 3.7"/>',
  pen: '<path d="M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16Z"/>',
  youtube: '<rect x="2.5" y="5" width="19" height="14" rx="4"/><path d="m10 9 5 3-5 3Z"/>',
  tiktok: '<path d="M14 3v11.5a3.5 3.5 0 1 1-3.5-3.5"/><path d="M14 3a5 5 0 0 0 5 5"/>',
  instagram: '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.5 6.5h.01"/>',
  threads: '<path d="M16.5 11.2c-.6-3-2.7-4.2-4.9-4.2-3 0-5.1 2.3-5.1 5.3 0 3.4 2.3 5.7 5.6 5.7 2.8 0 4.8-1.6 4.8-3.8 0-2-1.6-3.2-4-3.2-1.9 0-3.1.9-3.1 2.2 0 1.1 1 1.9 2.4 1.9 2.2 0 3.3-1.8 3.3-4.6"/>',
  facebook: '<path d="M14 21v-8h3l.5-3.5H14V7.5c0-1 .4-1.8 1.8-1.8h1.8V2.6A22 22 0 0 0 15 2.5c-2.6 0-4.3 1.6-4.3 4.5v2.5H8V13h2.7v8"/>',
  reddit: '<circle cx="12" cy="13.5" r="7"/><circle cx="9.3" cy="13" r=".8"/><circle cx="14.7" cy="13" r=".8"/><path d="M9.5 16.3a4 4 0 0 0 5 0M12 6.5l1.2-3.5 3.3.8"/><circle cx="18" cy="4.3" r="1.3"/>',
  group: '<circle cx="12" cy="9" r="3.5"/><path d="M5 20a7 7 0 0 1 14 0"/>',
  server: '<rect x="3" y="4" width="18" height="7" rx="2"/><rect x="3" y="13" width="18" height="7" rx="2"/><path d="M7 7.5h.01M7 16.5h.01"/>',
};
const icon = (name, cls = "") => `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${P[name] || ""}</svg>`;
const CHANNEL_ICON = { youtube: "youtube", tiktok: "tiktok", instagram: "instagram", threads: "threads", facebook: "facebook", reddit: "reddit", "facebook-groups": "group" };
const CHANNEL_HOME = {
  youtube: "https://studio.youtube.com/", tiktok: "https://www.tiktok.com/tiktokstudio/upload",
  instagram: "https://www.instagram.com/", threads: "https://www.threads.com/", facebook: "https://www.facebook.com/",
};
const LIMITS = { tiktok: 4000, instagram: 2200, threads: 500, facebook: 63206 };
const STAGES = ["Idea", "Brief", "Producing", "Review", "Ready", "Published", "Measured", "Archived"];
const STAGE_VI = { Idea: "Ý tưởng", Brief: "Brief", Producing: "Đang làm", Review: "Duyệt", Ready: "Sẵn sàng", Published: "Đã đăng", Measured: "Đã đo", Archived: "Lưu trữ", Pack: "Pack nhập" };

/* ---------- state ---------- */
let S = null;
const ui = {
  filter: { status: "all", lang: "all", q: "" },
  chan: "all",
  hookMetric: "views",
  pub: { creative: null, variant: null, channels: new Set(["youtube", "tiktok"]) },
};

async function api(path, { method = "GET", body } = {}) {
  const res = await fetch(path, {
    method, headers: body ? { "Content-Type": "application/json" } : {}, body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
  if (!res.ok || data.error) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

async function load({ quiet = false } = {}) {
  const btn = $("#refresh");
  btn.innerHTML = '<span class="spinner"></span>';
  try {
    S = await api("/api/state");
    derive();
    render();
    $("#sync").textContent = "Đọc lúc " + new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });
    if (!quiet) toast("Đã đọc lại repo", "ok");
  } catch (e) {
    toast("Không đọc được dữ liệu", "err", e.message);
  } finally {
    btn.innerHTML = icon("refresh");
  }
}

/* ---------- derived data ---------- */
const D = {};
function derive() {
  D.channel = Object.fromEntries(S.channels.map((c, i) => [c.key, { ...c, color: `var(--s${i + 1})` }]));
  D.creative = Object.fromEntries(S.creatives.map((c) => [c.id, c]));
  D.account = Object.fromEntries(S.accounts.filter((a) => a.channel).map((a) => [a.channel, a]));
  D.latest = {};      // url → latest snapshot (any window)
  D.windows = {};     // url → Set of windows measured
  for (const s of S.snapshots) {
    if (!D.latest[s.url] || s.captured_at >= D.latest[s.url].captured_at) D.latest[s.url] = s;
    (D.windows[s.url] ||= new Set()).add(s.window);
  }
  D.postsBy = {};
  for (const p of S.posts) if (p.creative_id) (D.postsBy[p.creative_id] ||= []).push(p);
  D.issues = { error: S.issues.filter((i) => i.level === "error"), warning: S.issues.filter((i) => i.level === "warning") };
  D.posted = (creative, variant) => (D.postsBy[creative] || []).some((p) => !variant || !p.variant || p.variant === variant);
}
const chanColor = (key) => D.channel[key]?.color || "var(--text-3)";
const chanLabel = (key) => D.channel[key]?.label || key;
const chanTag = (key) => `<span class="chan" style="--c:${chanColor(key)}"><i></i>${esc(chanLabel(key))}</span>`;
const title = (c) => (c?.concept || c?.id || "").replace(/-/g, " ");
const fmt = (n, d = 0) => (n == null || Number.isNaN(n) ? "—" : Number(n).toLocaleString("vi-VN", { maximumFractionDigits: d }));
const compact = (n) => (n == null ? "—" : n >= 1e6 ? (n / 1e6).toFixed(1).replace(".0", "") + "M" : n >= 1e3 ? (n / 1e3).toFixed(1).replace(".0", "") + "k" : String(Math.round(n)));
const stagePill = (s) => `<span class="pill stage-${esc((s || "pack").toLowerCase())}"><span class="dot"></span>${esc(STAGE_VI[s] || s)}</span>`;
const finals = (c) => c.renders.filter((r) => !r.draft && r.exists);
const media = (p) => `/media?path=${encodeURIComponent(p)}`;
const pad2 = (n) => String(n).padStart(2, "0");
const dateVN = (iso) => {
  if (!iso) return "—";
  const d = new Date(iso);
  return `${pad2(d.getDate())}/${pad2(d.getMonth() + 1)} · ${pad2(d.getHours())}:${pad2(d.getMinutes())}`;
};

/* ---------- toast / tooltip ---------- */
function toast(msg, kind = "ok", detail = "") {
  const el = document.createElement("div");
  el.className = `toast ${kind}`;
  el.innerHTML = `${icon(kind === "ok" ? "checkCircle" : "xCircle")}<div><div>${esc(msg)}</div>${detail ? `<pre>${esc(detail)}</pre>` : ""}</div>`;
  $("#toasts").append(el);
  setTimeout(() => el.remove(), kind === "ok" ? 2600 : 9000);
}
document.addEventListener("mousemove", (e) => {
  const t = e.target.closest?.("[data-tip]");
  const tip = $("#tooltip");
  if (!t) return (tip.hidden = true);
  const d = JSON.parse(t.dataset.tip);
  tip.innerHTML = `<b>${esc(d.t)}</b>${(d.r || []).map(([k, v]) => `<div class="t-row"><span>${esc(k)}</span><span>${esc(v)}</span></div>`).join("")}`;
  tip.hidden = false;
  const x = Math.min(e.clientX + 14, innerWidth - tip.offsetWidth - 10);
  const y = Math.min(e.clientY + 14, innerHeight - tip.offsetHeight - 10);
  tip.style.left = x + "px";
  tip.style.top = y + "px";
});

/* ---------- router ---------- */
const ROUTES = [
  { path: "", label: "Tổng quan", icon: "home", view: viewOverview },
  { path: "content", label: "Content", icon: "film", view: viewContent, count: () => S.creatives.length },
  { path: "plan", label: "Lịch 14 ngày", icon: "calendar", view: viewPlan },
  { path: "publish", label: "Đăng bài", icon: "send", view: viewPublish },
  { path: "analytics", label: "Số liệu", icon: "chart", view: viewAnalytics, count: () => S.posts.length || null },
  { path: "links", label: "Campaign link", icon: "link", view: viewLinks, count: () => S.campaigns.links.length || null },
  { path: "channels", label: "Kênh & tài khoản", icon: "users", view: viewChannels },
];
function current() {
  const [path, arg] = location.hash.replace(/^#\/?/, "").split("/");
  return { route: ROUTES.find((r) => r.path === path) || ROUTES[0], arg: arg && decodeURIComponent(arg) };
}
function render() {
  if (!S) return;
  const { route, arg } = current();
  $("#nav").innerHTML = ROUTES.map((r) => {
    const n = r.count?.();
    const alert = r.path === "" && D.issues.error.length;
    return `<a href="#/${r.path}" class="${r === route ? "active" : ""}">${icon(r.icon)}<span>${r.label}</span>${alert ? `<b class="count alert">${D.issues.error.length}</b>` : n ? `<b class="count">${n}</b>` : ""}</a>`;
  }).join("");
  const main = $("#main");
  const y = main.dataset.route === route.path ? scrollY : 0;
  main.dataset.route = route.path;
  main.innerHTML = `<div class="page">${route.view(arg)}</div>`;
  scrollTo(0, y);
  if (route.path === "content" && arg) openCreative(arg);
  else closeLayer("#drawer");
  afterRender();
}
function afterRender() {
  $$("[data-counter]").forEach(updateCounter);
}
addEventListener("hashchange", render);

/* ---------- views: overview ---------- */
function nextActions() {
  const out = [];
  if (D.issues.error.length) out.push({ icon: "alert", t: `Sửa ${D.issues.error.length} lỗi nội dung`, d: "check-content.py báo lỗi trong brief/metadata. Xem bảng bên dưới.", href: "#/" });
  const day = S.plan.find((p) => !(p.creative && D.posted(p.creative, p.variant)));
  if (day) {
    const c = D.creative[day.creative];
    if (c && !c.master) out.push({ icon: "clapper", t: `Quay master «${title(c)}»`, d: `Ngày ${day.day} cần ${day.video}. Đặt bản dựng sạch vào ${c.path}/exports/master.mov.`, href: `#/content/${encodeURIComponent(c.id)}` });
    else if (c && !finals(c).some((r) => r.variant === day.variant)) out.push({ icon: "film", t: `Render hook ${(day.variant || "").toUpperCase()} cho «${title(c)}»`, d: `tools/render/render.py render ${c.path} --variant ${day.variant}`, href: `#/content/${encodeURIComponent(c.id)}` });
    else if (c) out.push({ icon: "send", t: `Đăng ngày ${day.day}: ${day.hook}`, d: `${day.channels}${day.community ? " · " + day.community : ""}`, href: `#/publish`, pub: { creative: c.id, variant: day.variant } });
  }
  const due = S.posts.filter((p) => p.age_hours >= 24 && !(D.windows[p.url]?.has("24h")));
  if (due.length) out.push({ icon: "chart", t: `Nhập số 24h cho ${due.length} bài`, d: due.slice(0, 2).map((p) => `${chanLabel(p.channel)} · ${p.creative_id || p.url}`).join(" · "), href: "#/analytics" });
  if (!S.campaigns.provider_token) out.push({ icon: "link", t: "Thêm provider token App Store", d: "Để tạo campaign link theo dõi lượt tải theo kênh.", href: "#/links" });
  return out;
}

function viewOverview() {
  const h = new Date().getHours();
  const hello = h < 4 ? "Khuya rồi" : h < 11 ? "Chào buổi sáng" : h < 18 ? "Chào buổi chiều" : "Chào buổi tối";
  const acts = nextActions();
  const [first, ...rest] = acts;
  const counts = Object.fromEntries(STAGES.map((s) => [s, S.creatives.filter((c) => c.status === s).length]));
  const briefed = S.creatives.filter((c) => c.has_brief).length || 1;
  const views = S.posts.reduce((a, p) => a + (D.latest[p.url]?.views || 0), 0);
  const measured = S.posts.filter((p) => D.latest[p.url]).length;
  const rendered = S.creatives.reduce((a, c) => a + new Set(finals(c).map((r) => r.variant)).size, 0);
  const variants = S.creatives.reduce((a, c) => a + c.variants.length, 0);
  return `
  <div class="page-head"><div><div class="eyebrow">${esc(new Date().toLocaleDateString("vi-VN", { weekday: "long", day: "numeric", month: "long" }))}</div><h1>${hello}, Khanh</h1>
  <p>Toàn cảnh content, lịch đăng và số liệu của KV Apps. Dữ liệu đọc trực tiếp từ repo; số liệu riêng nằm trong máy này.</p></div>
  <div class="actions"><a class="btn" href="#/analytics">${icon("chart")}Nhập số liệu</a><a class="btn primary" href="#/publish">${icon("send")}Đăng bài</a></div></div>

  <div class="card hero">
    <div>
      <h2>${first ? "Việc tiếp theo" : "Mọi thứ đang đúng nhịp"}</h2>
      <p>${first ? "Gợi ý dựa trên lịch 14 ngày, trạng thái master/render và nhật ký đăng." : "Không có việc nào đang chờ. Xem lịch để chuẩn bị ngày tiếp theo."}</p>
      ${first ? actionRow(first, true) : ""}
      ${rest.map((a) => actionRow(a)).join("")}
    </div>
  </div>

  <div class="grid cols-4" style="margin-top:16px">
    ${kpi("film", "Creative", S.creatives.length, `${variants} biến thể hook · ${counts.Ready || 0} sẵn sàng`)}
    ${kpi("clapper", "Đã render", rendered, rendered ? "biến thể có bản cuối" : "Chờ quay master", variants ? `<small>/ ${variants}</small>` : "")}
    ${kpi("send", "Bài đã đăng", S.posts.length, S.posts.length ? `${measured} bài có số liệu` : "Chưa có bài nào được ghi")}
    ${kpi("eye", "View ghi nhận", views ? compact(views) : "—", views ? "tổng số mới nhất mỗi bài" : "Chưa có số liệu thật")}
  </div>

  <div class="section-title"><h2>Pipeline content</h2><span class="sub">Theo trạng thái trong BRIEF.md</span></div>
  <div class="card card-pad"><div class="pipeline">
    ${STAGES.map((s) => `<div class="stage ${counts[s] ? "" : "zero"}"><div class="n">${counts[s]}</div><div class="t">${STAGE_VI[s]}</div><div class="bar"><span style="width:${(counts[s] / briefed) * 100}%"></span></div></div>`).join("")}
  </div></div>

  <div class="section-title"><h2>Veilnest · 14 ngày</h2><a class="small" href="#/plan">Xem lịch →</a></div>
  <div class="card card-pad"><div class="days">
    ${S.plan.map((p) => `<div class="day ${p.creative && D.posted(p.creative, p.variant) ? "posted" : ""} ${p.video.includes("VI") ? "vi" : ""}" data-go="#/content/${encodeURIComponent(p.creative || "")}" data-tip="${attr({ t: `Ngày ${p.day} · ${p.video}`, r: [["Hook", p.hook], ["Kênh", p.channels], ["Trạng thái", p.status]] })}"><b>${esc(p.day)}</b><span>${esc((p.variant || "·").toUpperCase())}</span></div>`).join("")}
  </div></div>

  <div class="split" style="margin-top:28px">
    <div>
      <div class="section-title" style="margin-top:0"><h2>Kênh</h2><a class="small" href="#/channels">Chi tiết →</a></div>
      <div class="grid cols-2">${S.channels.filter((c) => c.account).map(channelCard).join("")}</div>
    </div>
    <div>
      <div class="section-title" style="margin-top:0"><h2>Kiểm tra nội dung</h2><span class="sub">tools/check-content.py</span></div>
      <div class="card card-pad">${issuesList()}</div>
    </div>
  </div>`;
}
function actionRow(a, primary = false) {
  const extra = a.pub ? ` data-pub='${esc(JSON.stringify(a.pub))}'` : "";
  return `<a class="next" href="${a.href}"${extra} style="${primary ? "" : "margin-top:8px;background:transparent"}"><span class="ico">${icon(a.icon)}</span><span style="min-width:0"><strong>${esc(a.t)}</strong><span class="small faint ellipsis" style="display:block">${esc(a.d)}</span></span></a>`;
}
function kpi(ic, label, value, hint, suffix = "") {
  return `<div class="card kpi"><div class="label">${icon(ic)}${esc(label)}</div><div class="value">${typeof value === "number" ? fmt(value) : esc(value)}${suffix}</div><div class="hint">${esc(hint)}</div></div>`;
}
function channelCard(c) {
  const acc = D.account[c.key];
  const posts = S.posts.filter((p) => p.channel === c.key);
  const views = posts.reduce((a, p) => a + (D.latest[p.url]?.views || 0), 0);
  const ready = acc && !/chưa tạo|chưa kiểm tra/i.test(acc.status);
  return `<div class="card channel-card" style="--c:${chanColor(c.key)}">
    <div class="top"><span class="logo">${icon(CHANNEL_ICON[c.key])}</span><div style="min-width:0"><h3>${esc(c.label)}</h3>
    <div class="small faint ellipsis">${acc?.url ? `<a href="${esc(acc.url)}" target="_blank" rel="noreferrer">${esc(acc.profile)}</a>` : esc(acc?.profile || "—")}</div></div>
    <span class="spacer"></span>${ready ? `<span class="pill good">${icon("check")}Sẵn sàng</span>` : `<span class="pill warn">Chờ</span>`}</div>
    <div class="meta"><span><b>${posts.length}</b> bài</span><span><b>${views ? compact(views) : "—"}</b> view</span></div>
    <div class="status">${esc(acc?.todo ? "Còn: " + acc.todo : acc?.status || "")}</div></div>`;
}
function issuesList() {
  if (!S.issues.length) return `<div class="allclear"><span class="ico">${icon("check")}</span><div><b style="color:var(--text)">Không có lỗi hay cảnh báo</b><div class="small">${S.creatives.length} creative, brief, metadata YouTube, render.toml và nhật ký đều khớp.</div></div></div>`;
  return S.issues.slice(0, 12).map((i) => `<div class="issue ${i.level}">${icon(i.level === "error" ? "xCircle" : "alert")}<div><div>${esc(i.message)}</div><code>${esc(i.path)}</code></div></div>`).join("") + (S.issues.length > 12 ? `<div class="small faint" style="padding-top:8px">…và ${S.issues.length - 12} mục khác</div>` : "");
}

/* ---------- views: content ---------- */
function viewContent() {
  const f = ui.filter;
  const list = S.creatives.filter((c) =>
    (f.status === "all" || (f.status === "pack" ? !c.has_brief : c.status === f.status)) &&
    (f.lang === "all" || c.lang === f.lang) &&
    (!f.q || `${c.id} ${c.variants.map((v) => v.hook).join(" ")} ${c.situation}`.toLowerCase().includes(f.q.toLowerCase())));
  const statuses = [...new Set(S.creatives.filter((c) => c.has_brief).map((c) => c.status))];
  return `
  <div class="page-head"><div><div class="eyebrow">Content</div><h1>Creative</h1><p>Mỗi creative là một thư mục trong <code>content/&lt;app&gt;/videos/</code>: brief, hook, metadata YouTube và bản render.</p></div></div>
  <div class="toolbar">
    <div class="seg" data-filter="status">${[["all", "Tất cả"], ...statuses.map((s) => [s, STAGE_VI[s] || s]), ["pack", "Pack nhập"]].map(([v, l]) => `<button class="${f.status === v ? "on" : ""}" data-val="${esc(v)}">${esc(l)}</button>`).join("")}</div>
    <div class="seg" data-filter="lang">${[["all", "Mọi ngôn ngữ"], ["en", "EN"], ["vi", "VI"]].map(([v, l]) => `<button class="${f.lang === v ? "on" : ""}" data-val="${v}">${l}</button>`).join("")}</div>
    <label class="search">${icon("search")}<input type="search" id="q" placeholder="Tìm hook, concept…" value="${esc(f.q)}"></label>
  </div>
  ${list.length ? `<div class="creatives">${list.map(creativeCard).join("")}</div>` : emptyState("search", "Không có creative khớp bộ lọc", "Thử bỏ bớt bộ lọc.")}`;
}
function poster(c) {
  const cover = c.renders.find((r) => r.cover && !r.draft)?.cover || c.renders.find((r) => r.cover)?.cover;
  const hook = c.variants[0]?.hook || title(c);
  return `<div class="poster">${cover ? `<img src="${media(cover)}" alt="" loading="lazy">` : `<div class="glow"></div><div class="phone"><span>${esc(hook)}</span></div>`}
    <div class="badges"><span class="row" style="gap:6px">${c.lang ? `<span class="tag">${c.lang.toUpperCase()}</span>` : ""}${c.pro ? `<span class="tag" style="color:#f6c453">PRO</span>` : ""}</span>${c.master ? `<span class="tag">${icon("check")} master</span>` : ""}</div></div>`;
}
function creativeCard(c) {
  const done = new Set(finals(c).map((r) => r.variant));
  return `<a class="card creative" href="#/content/${encodeURIComponent(c.id)}">${poster(c)}
    <div class="body"><div class="row" style="justify-content:space-between"><h3>${esc(title(c))}</h3>${stagePill(c.has_brief ? c.status : "Pack")}</div>
    <div class="hook">${esc(c.variants.map((v) => v.hook).join(" · ") || c.situation || c.path)}</div>
    <div class="foot">${c.variants.map((v) => `<span class="variant ${done.has(v.id) ? "done" : ""}" title="${done.has(v.id) ? "Đã render" : "Chưa render"}">${v.id.toUpperCase()}</span>`).join("")}
    <span class="spacer"></span>${(c.posted_on || []).map((k) => `<span class="chan" style="--c:${chanColor(k)}" title="${esc(chanLabel(k))}"><i></i></span>`).join("")}
    ${c.plan_days.length ? `<span class="tag">${icon("calendar", "").replace("<svg", '<svg style="width:12px;height:12px;margin-right:4px"')}${c.plan_days.length} ngày</span>` : ""}</div></div></a>`;
}

function openCreative(id) {
  const c = D.creative[id];
  if (!c) return;
  const posts = D.postsBy[c.id] || [];
  const layer = $("#drawer");
  layer.innerHTML = `<div class="drawer" role="dialog" aria-label="${esc(title(c))}">
    <div class="drawer-head"><div style="min-width:0;flex:1"><div class="eyebrow">${esc(c.app_name)} · ${esc(c.lang?.toUpperCase() || "")}</div><h2>${esc(title(c))}</h2>
    <div class="row" style="margin-top:8px">${stagePill(c.has_brief ? c.status : "Pack")}${c.pro ? '<span class="pill pro">Pro</span>' : ""}<code class="small faint">${esc(c.id)}</code></div></div>
    <button class="btn sm" data-act="reveal" data-path="${esc(c.path)}">${icon("folder")}Mở thư mục</button>
    <button class="icon-btn" data-act="close-drawer" aria-label="Đóng">${icon("x")}</button></div>
    <div class="drawer-body">
      ${c.has_brief ? `<dl class="facts">
        ${fact("Tình huống", c.situation)}${fact("Lợi ích chính", c.benefit)}${fact("CTA", c.cta)}${fact("Kênh dự kiến", c.channels_plan)}
        ${fact("Thời lượng", c.duration_plan)}${fact("Footage", c.footage)}${c.based_on && c.based_on !== "—" ? fact("Based on", c.based_on) : ""}
        ${fact("Lịch", c.plan_days.length ? "Ngày " + c.plan_days.join(", ") : "—")}
      </dl>` : `<div class="callout">${icon("info")}<div>Pack nhập từ IOS-Vault: tài liệu dựng, chưa phải video đăng được. Xem README trong thư mục.</div></div>`}
      ${c.has_brief && !c.master ? `<div class="callout warn">${icon("clapper")}<div><b>Chưa có master.</b> Quay trên build thật, dựng bản sạch không chữ rồi đặt vào <code>${esc(c.path)}/exports/master.mov</code>. Sau đó:<div class="output" style="margin-top:8px">tools/render/.venv/bin/python tools/render/render.py render ${esc(c.path)} --preview</div></div></div>` : ""}
      ${c.variants.length ? `<div><div class="section-title" style="margin-top:0"><h2>Biến thể hook</h2><span class="sub">${c.has_render_config ? "render.toml" : "chưa có render.toml"}</span></div><div class="stack">${c.variants.map((v) => variantRow(c, v)).join("")}</div></div>` : ""}
      ${c.layout ? `<div><div class="section-title" style="margin-top:0"><h2>Bố cục & vùng an toàn</h2><a class="small" href="${media(c.layout)}" target="_blank">Mở ảnh lớn →</a></div><img src="${media(c.layout)}" alt="Bố cục" style="width:100%;border-radius:14px;border:1px solid var(--border)"></div>` : ""}
      <div><div class="section-title" style="margin-top:0"><h2>Bài đã đăng</h2><span class="sub">${posts.length} bài</span></div>
      ${posts.length ? postsTable(posts) : `<div class="card card-pad small muted">Chưa có bài nào trong nhật ký kênh cho creative này.</div>`}</div>
    </div></div>`;
  layer.hidden = false;
}
const fact = (k, v) => `<dt>${esc(k)}</dt><dd>${esc(v || "—")}</dd>`;
function variantRow(c, v) {
  const r = finals(c).find((x) => x.variant === v.id) || c.renders.find((x) => x.variant === v.id && x.exists);
  const mediaEl = r?.exists
    ? `<video src="${media(r.file)}" ${r.cover ? `poster="${media(r.cover)}"` : ""} controls preload="none" playsinline></video>`
    : `<div class="empty-media">${icon("film").replace("<svg", '<svg style="width:22px;height:22px;margin-bottom:6px"')}<br>Chưa render</div>`;
  return `<div class="variant-row"><div>${mediaEl}</div><div class="stack" style="align-content:start">
    <div class="row"><span class="variant ${r ? "done" : ""}">${v.id.toUpperCase()}</span>${r?.draft ? '<span class="pill warn">draft</span>' : ""}${r && !r.draft ? '<span class="pill good">' + icon("check") + "Bản cuối</span>" : ""}</div>
    <h4>${esc(v.hook)}</h4>
    ${v.title ? `<div class="kv"><span>YouTube</span><span>${esc(v.title)}</span>${v.meta_file ? `<span>Metadata</span><span><code>${esc(v.meta_file)}</code></span>` : ""}</div>` : ""}
    ${r ? `<div class="kv"><span>File</span><span class="ellipsis"><code>${esc(r.file.split("/").pop())}</code></span><span>Thông số</span><span class="num">${fmt(r.duration, 2)}s · ${fmt(r.bytes / 1048576, 1)} MB · ${r.lufs != null ? fmt(r.lufs, 1) + " LUFS" : "—"}</span>${r.warnings.length ? `<span>Cảnh báo</span><span style="color:var(--warn)">${esc(r.warnings.join("; "))}</span>` : ""}</div>` : ""}
    <div class="row">${r ? `<button class="btn sm" data-act="reveal" data-path="${esc(r.file)}">${icon("folder")}Hiện file</button>` : ""}${r?.sheet ? `<a class="btn sm" href="${media(r.sheet)}" target="_blank">${icon("eye")}Ảnh review</a>` : ""}
    <button class="btn sm primary" data-act="publish-variant" data-creative="${esc(c.id)}" data-variant="${esc(v.id)}">${icon("send")}Đăng biến thể này</button></div>
  </div></div>`;
}

/* ---------- views: plan ---------- */
function viewPlan() {
  const weeks = [S.plan.filter((p) => +p.day <= 7), S.plan.filter((p) => +p.day > 7)];
  return `<div class="page-head"><div><div class="eyebrow">Lịch</div><h1>Veilnest · 14 ngày</h1><p>Từ <code>docs/content/VEILNEST_14_DAYS.md</code>. EN lúc 08:00 ICT, VI lúc 20:00 ICT. Ngày 1 là ngày đăng video đầu tiên.</p></div>
  <a class="btn" data-act="reveal" data-path="docs/content/VEILNEST_14_DAYS.md">${icon("pen")}Sửa lịch</a></div>
  ${weeks.map((w, i) => `<div class="week"><h3>Tuần ${i + 1}</h3><div class="plan-list">${w.map(planItem).join("")}</div></div>`).join("")}`;
}
function planItem(p) {
  const c = D.creative[p.creative];
  const posted = p.creative && D.posted(p.creative, p.variant);
  const rendered = c && finals(c).some((r) => r.variant === p.variant);
  const state = posted ? `<span class="pill good">${icon("check")}Đã đăng</span>` : rendered ? `<span class="pill stage-ready"><span class="dot"></span>Đã render</span>` : c?.master ? `<span class="pill stage-producing"><span class="dot"></span>Có master</span>` : `<span class="pill">${esc(p.status)}</span>`;
  return `<div class="plan-item" data-go="#/content/${encodeURIComponent(p.creative || "")}">
    <div class="daynum"><small>NGÀY</small><b>${esc(p.day)}</b></div>
    <div style="min-width:0"><div class="title">${esc(p.video.replace(/-/g, " "))}</div><div class="hook">${p.variant ? `<span class="variant" style="width:18px;height:18px;font-size:10.5px;margin-right:6px">${p.variant.toUpperCase()}</span>` : ""}${esc(p.hook)}</div>
    <div class="meta">${p.channels.split(/,\s*/).map((ch) => `<span class="tag">${esc(ch)}</span>`).join("")}${p.community ? `<span class="tag">${icon("users").replace("<svg", '<svg style="width:12px;height:12px;margin-right:4px"')}${esc(p.community)}</span>` : ""}</div></div>
    <div>${state}</div></div>`;
}

/* ---------- views: publish ---------- */
function viewPublish() {
  const briefed = S.creatives.filter((c) => c.has_brief && c.variants.length);
  if (!ui.pub.creative || !D.creative[ui.pub.creative]) {
    const next = S.plan.find((p) => p.creative && !D.posted(p.creative, p.variant));
    ui.pub.creative = next?.creative || briefed[0]?.id;
    ui.pub.variant = next?.variant || null;
  }
  const c = D.creative[ui.pub.creative];
  if (!c) return emptyState("film", "Chưa có creative có brief", "Tạo brief trong content/<app>/videos/.");
  if (!c.variants.some((v) => v.id === ui.pub.variant)) ui.pub.variant = c.variants[0]?.id;
  const v = c.variants.find((x) => x.id === ui.pub.variant);
  const r = finals(c).find((x) => x.variant === v.id);
  const videoChannels = ["youtube", "tiktok", "instagram", "threads", "facebook"];
  return `<div class="page-head"><div><div class="eyebrow">Đăng bài</div><h1>Bộ đăng bài</h1><p>Chọn video, chọn kênh, copy caption và file. YouTube upload <b>private</b> qua API; các kênh khác đăng tay rồi ghi URL vào nhật ký.</p></div></div>
  <div class="steps">
    <div class="card step"><div class="step-title"><span class="step-num">1</span>Chọn video</div>
      <div class="form-grid"><label class="field"><span>Creative</span><select id="pub-creative">${briefed.map((x) => `<option value="${esc(x.id)}" ${x.id === c.id ? "selected" : ""}>${esc(title(x))} · ${esc((x.lang || "").toUpperCase())}${x.status ? " — " + esc(STAGE_VI[x.status] || x.status) : ""}</option>`).join("")}</select></label>
      <label class="field"><span>Biến thể hook</span><select id="pub-variant">${c.variants.map((x) => `<option value="${esc(x.id)}" ${x.id === v.id ? "selected" : ""}>${x.id.toUpperCase()} · ${esc(x.hook)}</option>`).join("")}</select></label></div>
      <div class="preview-mini" style="margin-top:14px">${r?.cover ? `<img src="${media(r.cover)}" alt="">` : '<div class="ph"></div>'}<div class="stack" style="gap:4px">
        ${r ? `<div class="row"><span class="pill good">${icon("check")}Đã render</span><code class="small faint">${esc(r.file)}</code></div><div class="row"><button class="btn sm" data-act="reveal" data-path="${esc(r.file)}">${icon("folder")}Hiện file trong Finder</button></div>`
            : `<div class="callout warn">${icon("alert")}<div><b>Chưa có bản render cuối cho hook ${v.id.toUpperCase()}.</b> ${c.master ? `Chạy <code>render.py render ${esc(c.path)} --variant ${esc(v.id)}</code>.` : "Cần quay master trước."} Vẫn chuẩn bị caption được.</div></div>`}
      </div></div></div>

    <div class="card step"><div class="step-title"><span class="step-num">2</span>Chọn kênh</div>
      <div class="channel-pick">${videoChannels.map((k) => {
        const acc = D.account[k];
        const off = acc && /chưa tạo/i.test(acc.status);
        return `<label style="--c:${chanColor(k)}" class="${off ? "disabled" : ""}" title="${off ? "Tài khoản chưa tạo" : ""}"><input type="checkbox" data-pub-chan="${k}" ${ui.pub.channels.has(k) && !off ? "checked" : ""} ${off ? "disabled" : ""}>${icon(CHANNEL_ICON[k]).replace("<svg", '<svg style="width:16px;height:16px;color:var(--c)"')}${esc(chanLabel(k))}</label>`;
      }).join("")}</div>
      <div class="small faint" style="margin-top:10px">Reddit và nhóm Facebook đăng theo nháp trong <code>docs/social/channels/</code>; ghi URL qua nút “Ghi bài đã đăng”.</div></div>

    <div class="step-title" style="margin:10px 2px 0"><span class="step-num">3</span>Đăng và ghi lại</div>
    ${[...ui.pub.channels].filter((k) => videoChannels.includes(k)).map((k) => kit(k, c, v, r)).join("") || `<div class="card card-pad muted">Chọn ít nhất một kênh.</div>`}
  </div>
  <div class="section-title"><h2>Bài gần đây</h2><button class="btn sm" data-act="log-post">${icon("plus")}Ghi bài đã đăng</button></div>
  ${S.posts.length ? `<div class="card">${postsTable([...S.posts].sort((a, b) => (b.at || "").localeCompare(a.at || "")).slice(0, 10))}</div>` : `<div class="card">${emptyState("send", "Chưa có bài nào trong nhật ký", "Sau khi đăng, dán URL bài vào “Đã đăng xong” để ghi vào docs/social/channels/<kênh>/POSTS.md.")}</div>`}`;
}
function captionFor(k, c, v) {
  const first = c.variants[0];
  let cap = c.caption || `${v.hook}. ${c.benefit || ""} ${c.lang === "vi" ? "Tìm Veilnest trên App Store." : "Search Veilnest on the App Store."}`;
  if (first && v.id !== first.id && cap.startsWith(first.hook)) cap = v.hook + cap.slice(first.hook.length);
  if (k === "threads") cap = cap.replace(/(\s#\S+)+\s*$/, "");
  return cap.trim();
}
function campaignFor(k, c, v) {
  return S.campaigns.links.find((l) => l.channel === k && l.creative === c.id && (!l.variant || l.variant === v.id))
      || S.campaigns.links.find((l) => l.channel === k && !l.creative);
}
function kit(k, c, v, r) {
  const link = campaignFor(k, c, v);
  const acc = D.account[k];
  const head = `<div class="kit-head">${chanTag(k)}<span class="spacer"></span>
    ${CHANNEL_HOME[k] ? `<a class="btn sm" href="${CHANNEL_HOME[k]}" target="_blank" rel="noreferrer">${icon("ext")}Mở ${esc(chanLabel(k).split(" ")[0])}</a>` : ""}
    <button class="btn sm primary" data-act="log-post" data-channel="${k}" data-creative="${esc(c.id)}" data-variant="${esc(v.id)}">${icon("check")}Đã đăng xong</button></div>`;
  if (k === "youtube") {
    const desc = link?.url ? (v.description || "").replace(/https:\/\/apps\.apple\.com\/\S+/, link.url) : v.description || "";
    return `<div class="card kit" style="--c:${chanColor(k)}">${head}
      ${v.title ? `<div class="field"><span>Tiêu đề <span class="faint">(≤ 100)</span></span><div class="copybox">${esc(v.title)}${copyBtn(v.title)}</div></div>
      <div class="field"><span>Mô tả${link ? ` <span class="pill stage-ready" style="height:18px">campaign ${esc(link.ct)}</span>` : ""}</span><div class="copybox">${esc(desc)}${copyBtn(desc)}</div></div>` : `<div class="callout warn">${icon("alert")}<div>Biến thể chưa có <code>youtube-${esc(v.id)}.toml</code>.</div></div>`}
      <div class="row">${S.youtube.token ? "" : `<span class="small faint">Upload qua API cần đăng nhập một lần: <code>upload.py auth</code> (xem tab Kênh).</span>`}<span class="spacer"></span>
        <button class="btn sm" data-act="yt-upload" data-dry="1" data-creative="${esc(c.id)}" data-variant="${esc(v.id)}" ${r && v.meta_file && S.youtube.venv ? "" : "disabled"}>${icon("check")}Kiểm tra (dry-run)</button>
        <button class="btn sm" data-act="yt-upload" data-creative="${esc(c.id)}" data-variant="${esc(v.id)}" ${r && v.meta_file && S.youtube.token ? "" : "disabled"}>${icon("upload")}Upload private</button></div>
      <div class="small faint">Public/hẹn giờ làm trong YouTube Studio hoặc bằng <code>upload.py --publish-at</code> (có bước xác nhận). Dashboard không tự public video.</div></div>`;
  }
  const cap = captionFor(k, c, v);
  const limit = LIMITS[k];
  return `<div class="card kit" style="--c:${chanColor(k)}">${head}
    ${acc && /chưa/i.test(acc.todo || "") ? `<div class="small faint">${esc(acc.todo)}</div>` : ""}
    <label class="field"><span>Caption</span><textarea data-counter="${limit}" rows="4">${esc(cap)}</textarea><div class="row"><span class="small faint">${k === "tiktok" ? "TikTok chưa có link bio: CTA là tìm “Veilnest” trên App Store." : k === "threads" ? "Threads: giọng solo dev, kể chuyện làm app; không nhồi hashtag." : ""}</span><span class="spacer"></span><span class="counter"></span><button class="btn sm ghost" data-act="copy-area">${icon("copy")}Copy</button></div></label>
    ${link ? `<div class="field"><span>Campaign link (${esc(link.ct)})</span><div class="copybox url">${esc(link.url)}${copyBtn(link.url)}</div></div>` : ""}
  </div>`;
}
const copyBtn = (text) => `<button class="icon-btn" data-act="copy" data-text="${esc(text)}" title="Copy">${icon("copy")}</button>`;
function updateCounter(area) {
  const limit = +area.dataset.counter;
  const counter = area.closest(".field")?.querySelector(".counter");
  if (!counter) return;
  const n = [...area.value].length;
  counter.textContent = `${fmt(n)} / ${fmt(limit)}`;
  counter.classList.toggle("over", n > limit);
}

function postsTable(posts) {
  return `<div class="table-wrap"><table><thead><tr><th>Thời gian</th><th>Kênh</th><th>Creative</th><th class="num">View</th><th class="num">Xem hết</th><th>24h</th><th>7d</th><th></th></tr></thead><tbody>
  ${posts.map((p) => {
    const s = D.latest[p.url];
    const w = D.windows[p.url] || new Set();
    const due24 = p.age_hours >= 24, due7 = p.age_hours >= 168;
    const mark = (has, due) => has ? `<span class="pill good" style="height:20px">${icon("check")}</span>` : due ? `<span class="pill warn" style="height:20px">thiếu</span>` : `<span class="faint small">chờ</span>`;
    return `<tr><td class="nowrap">${dateVN(p.at)}</td><td>${chanTag(p.channel)}</td>
      <td style="max-width:260px"><div class="ellipsis">${p.creative_id ? `<a href="#/content/${encodeURIComponent(p.creative_id)}">${esc(title(D.creative[p.creative_id]) || p.creative_id)}</a>${p.variant ? ` <span class="variant" style="width:18px;height:18px;font-size:10.5px">${p.variant.toUpperCase()}</span>` : ""}` : esc(p.place || p.app || "—")}</div>
      ${p.url ? `<a class="small url" href="${esc(p.url)}" target="_blank" rel="noreferrer">${esc(p.url.replace(/^https:\/\/(www\.)?/, "").slice(0, 46))}</a>` : ""}</td>
      <td class="num">${s?.views != null ? compact(s.views) : "—"}</td><td class="num">${s?.completion_pct != null ? fmt(s.completion_pct, 0) + "%" : "—"}</td>
      <td>${mark(w.has("24h"), due24)}</td><td>${mark(w.has("7d"), due7)}</td>
      <td class="nowrap"><button class="btn sm" data-act="add-metric" data-url="${esc(p.url || "")}" data-channel="${esc(p.channel)}" data-creative="${esc(p.creative_id || "")}" data-variant="${esc(p.variant || "")}" data-age="${p.age_hours ?? ""}">${icon("plus")}Số liệu</button>
      ${s ? `<button class="btn sm ghost" data-act="write-result" data-url="${esc(p.url)}" data-channel="${esc(p.channel)}" title="Ghi tóm tắt 24h/7d vào POSTS.md">${icon("pen")}POSTS.md</button>` : ""}</td></tr>`;
  }).join("")}</tbody></table></div>`;
}

/* ---------- views: analytics ---------- */
function viewAnalytics() {
  const ch = ui.chan;
  const posts = S.posts.filter((p) => ch === "all" || p.channel === ch);
  const latest = posts.map((p) => ({ p, s: D.latest[p.url] })).filter((x) => x.s);
  const views = latest.reduce((a, x) => a + (x.s.views || 0), 0);
  const comp = latest.filter((x) => x.s.completion_pct != null);
  const installs = latest.reduce((a, x) => a + (x.s.installs || 0), 0);
  const used = [...new Set(S.posts.map((p) => p.channel))];
  return `<div class="page-head"><div><div class="eyebrow">Số liệu</div><h1>Hiệu quả từng bài</h1><p>Chỉ số thật, có nguồn và thời điểm đo. Lưu trong <code>.dashboard/</code> (không vào repo public). Thiếu thì để trống, không điền 0.</p></div>
  <div class="actions"><button class="btn" data-act="yt-sync" ${S.youtube.token ? "" : "disabled"} title="${S.youtube.token ? "" : "Cần upload.py auth"}">${icon("youtube")}Đồng bộ YouTube</button><button class="btn primary" data-act="add-metric">${icon("plus")}Nhập số liệu</button></div></div>
  <div class="toolbar"><div class="seg" data-filter="chan">${[["all", "Mọi kênh"], ...used.map((k) => [k, chanLabel(k)])].map(([v, l]) => `<button class="${ch === v ? "on" : ""}" data-val="${esc(v)}">${esc(l)}</button>`).join("")}</div></div>
  ${S.posts.length ? `
  <div class="grid cols-4">
    ${kpi("eye", "Tổng view", views ? compact(views) : "—", "số mới nhất mỗi bài")}
    ${kpi("target", "Xem hết trung bình", comp.length ? fmt(comp.reduce((a, x) => a + x.s.completion_pct, 0) / comp.length, 0) + "%" : "—", comp.length ? `trên ${comp.length} bài có số` : "chưa có số")}
    ${kpi("checkCircle", "Bài đã đo", latest.length, `trên ${posts.length} bài`, `<small>/ ${posts.length}</small>`)}
    ${kpi("download", "Lượt tải ghi nhận", installs || "—", "từ App Store Connect · Sources")}
  </div>
  <div class="grid cols-2" style="margin-top:16px">
    <div class="card"><div class="card-head"><h3>View theo bài</h3><span class="sub">số mới nhất</span></div><div class="card-body">${barsByPost(latest)}</div></div>
    <div class="card"><div class="card-head"><h3>So sánh hook A/B/C</h3><div class="seg" data-filter="hookMetric">${[["views", "View"], ["completion_pct", "Xem hết"]].map(([v, l]) => `<button class="${ui.hookMetric === v ? "on" : ""}" data-val="${v}">${l}</button>`).join("")}</div></div><div class="card-body">${hookChart(latest)}</div></div>
  </div>
  <div class="section-title"><h2>Bài đăng</h2><span class="sub">từ docs/social/channels/*/POSTS.md</span></div>
  <div class="card">${postsTable(posts)}</div>
  ${snapshotTable(posts)}` : `<div class="card">${emptyState("chart", "Chưa có bài nào để đo", "Quy trình: đăng bài → ghi URL ở trang Đăng bài → sau 24h và 7 ngày, nhập số từ TikTok Studio / Instagram Insights hoặc bấm Đồng bộ YouTube.", `<a class="btn primary" href="#/publish">${icon("send")}Tới trang Đăng bài</a>`)}</div>`}`;
}
function barsByPost(rows) {
  const data = rows.filter((x) => x.s.views != null).sort((a, b) => b.s.views - a.s.views).slice(0, 10);
  if (!data.length) return `<div class="small faint">Chưa có bài nào có số view.</div>`;
  const W = 520, rowH = 30, left = 150, max = Math.max(...data.map((x) => x.s.views)) || 1;
  const H = data.length * rowH + 6;
  const bars = data.map((x, i) => {
    const w = Math.max(3, ((W - left - 56) * x.s.views) / max);
    const y = i * rowH + 4;
    const label = `${title(D.creative[x.p.creative_id]) || x.p.place || "bài"}${x.p.variant ? " · " + x.p.variant.toUpperCase() : ""}`;
    const tip = attr({ t: label, r: [["Kênh", chanLabel(x.p.channel)], ["View", fmt(x.s.views)], ["Xem hết", x.s.completion_pct != null ? fmt(x.s.completion_pct, 0) + "%" : "—"], ["Đo lúc", dateVN(x.s.captured_at) + " · " + x.s.window], ["Nguồn", x.s.source]] });
    return `<g class="mark" data-tip="${tip}"><rect x="0" y="${y - 2}" width="${W}" height="${rowH}" fill="transparent"/>
      <text class="label-2" x="${left - 10}" y="${y + 15}" text-anchor="end">${esc(label.length > 22 ? label.slice(0, 21) + "…" : label)}</text>
      <rect x="${left}" y="${y + 3}" width="${w}" height="18" rx="4" fill="${chanColor(x.p.channel)}"/>
      <text class="label" x="${left + w + 7}" y="${y + 16}">${compact(x.s.views)}</text></g>`;
  }).join("");
  const chans = [...new Set(data.map((x) => x.p.channel))];
  return `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="View theo bài">${bars}</svg>
    ${chans.length > 1 ? `<div class="legend" style="margin-top:10px">${chans.map((k) => `<span style="--c:${chanColor(k)}"><i></i>${esc(chanLabel(k))}</span>`).join("")}</div>` : ""}`;
}
function hookChart(rows) {
  const metric = ui.hookMetric;
  const groups = {};
  for (const x of rows) {
    if (!x.p.creative_id || !x.p.variant || x.s[metric] == null) continue;
    const key = `${x.p.creative_id}|${x.p.channel}`;
    const g = (groups[key] ||= { creative: x.p.creative_id, channel: x.p.channel, v: {} });
    g.v[x.p.variant] = x.s[metric];
  }
  const list = Object.values(groups).filter((g) => Object.keys(g.v).length >= 1);
  if (!list.length) return `<div class="small faint">Cần ít nhất một bài có ghi biến thể hook (creative ID dạng <code>…-hooka</code>) và số ${metric === "views" ? "view" : "xem hết"}.</div>`;
  const variants = ["a", "b", "c"];
  const W = 520, gh = 74, left = 150, max = Math.max(...list.flatMap((g) => Object.values(g.v))) || 1;
  const H = list.length * gh;
  const svg = list.map((g, gi) => {
    const y0 = gi * gh + 6;
    const name = `${title(D.creative[g.creative])} · ${chanLabel(g.channel).split(" ")[0]}`;
    const bars = variants.map((vid, i) => {
      const val = g.v[vid];
      if (val == null) return `<text class="axis" x="${left}" y="${y0 + i * 21 + 14}">${vid.toUpperCase()} · chưa có</text>`;
      const w = Math.max(3, ((W - left - 64) * val) / max);
      const shown = metric === "views" ? compact(val) : fmt(val, 0) + "%";
      return `<g class="mark" data-tip="${attr({ t: `${name} · hook ${vid.toUpperCase()}`, r: [[metric === "views" ? "View" : "Xem hết", shown]] })}"><rect x="${left}" y="${y0 + i * 21 + 2}" width="${w}" height="17" rx="4" fill="var(--s${i + 1})"/><text class="label" x="${left + w + 7}" y="${y0 + i * 21 + 15}">${vid.toUpperCase()} ${shown}</text></g>`;
    }).join("");
    return `<text class="label-2" x="${left - 10}" y="${y0 + 26}" text-anchor="end">${esc(name.length > 22 ? name.slice(0, 21) + "…" : name)}</text>${bars}`;
  }).join("");
  return `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="So sánh hook">${svg}</svg>
    <div class="legend" style="margin-top:10px">${variants.map((v, i) => `<span style="--c:var(--s${i + 1})"><i></i>Hook ${v.toUpperCase()}</span>`).join("")}</div>`;
}
function snapshotTable(posts) {
  const urls = new Set(posts.map((p) => p.url));
  const rows = S.snapshots.filter((s) => urls.has(s.url)).reverse();
  if (!rows.length) return "";
  return `<div class="section-title"><h2>Lịch sử đo</h2><span class="sub">${rows.length} bản ghi</span></div>
  <div class="card"><div class="table-wrap"><table><thead><tr><th>Đo lúc</th><th>Kênh</th><th>Khoảng</th><th class="num">View</th><th class="num">Like</th><th class="num">Xem hết</th><th class="num">Tải</th><th>Nguồn</th><th></th></tr></thead><tbody>
  ${rows.map((s) => `<tr><td class="nowrap">${dateVN(s.captured_at)}</td><td>${chanTag(s.channel)}</td><td><span class="tag">${esc(s.window)}</span></td>
    <td class="num">${fmt(s.views)}</td><td class="num">${fmt(s.likes)}</td><td class="num">${s.completion_pct != null ? fmt(s.completion_pct, 0) + "%" : "—"}</td><td class="num">${fmt(s.installs)}</td>
    <td class="small muted">${esc(s.source)}${s.note ? ` · ${esc(s.note)}` : ""}</td><td><button class="icon-btn" data-act="del-snap" data-id="${s.id}" title="Xoá">${icon("trash")}</button></td></tr>`).join("")}
  </tbody></table></div></div>`;
}

/* ---------- views: campaign links ---------- */
function viewLinks() {
  const c = S.campaigns;
  const creatives = S.creatives.filter((x) => x.has_brief);
  return `<div class="page-head"><div><div class="eyebrow">App Store</div><h1>Campaign link</h1><p>Link có <code>pt</code>/<code>ct</code> để App Store Connect tách lượt xem trang và lượt tải theo kênh, ngôn ngữ và creative. Lưu ở <code>docs/social/campaign-links.json</code>.</p></div></div>
  <div class="split">
    <div class="card"><div class="card-head"><h3>Tạo link mới</h3></div><div class="card-body">
      <form id="link-form" class="form-grid">
        <label class="field"><span>App</span><select name="app">${Object.entries(S.apps).map(([k, a]) => `<option value="${k}" ${a.app_store_id ? "" : "disabled"}>${esc(a.name)}${a.app_store_id ? "" : " (chưa có ID)"}</option>`).join("")}</select></label>
        <label class="field"><span>Kênh</span><select name="channel">${S.channels.map((ch) => `<option value="${ch.key}">${esc(ch.label)}</option>`).join("")}</select></label>
        <label class="field"><span>Ngôn ngữ</span><select name="lang"><option value="en">EN</option><option value="vi">VI</option></select></label>
        <label class="field"><span>Creative <span class="faint">(tuỳ chọn)</span></span><select name="creative"><option value="">— Cả kênh —</option>${creatives.map((x) => `<option value="${esc(x.id)}">${esc(title(x))} · ${esc((x.lang || "").toUpperCase())}</option>`).join("")}</select></label>
        <label class="field"><span>Hook <span class="faint">(tuỳ chọn)</span></span><select name="variant"><option value="">—</option><option value="a">A</option><option value="b">B</option><option value="c">C</option></select></label>
        <label class="field"><span>Campaign token (ct)</span><input type="text" name="ct" maxlength="40" required pattern="[A-Za-z0-9_.\\-]{1,40}"><small>Tự gợi ý, tối đa 40 ký tự.</small></label>
        <label class="field"><span>Custom Product Page ID <span class="faint">(ppid)</span></span><input type="text" name="ppid" placeholder="khi CPP được duyệt"></label>
        <label class="field"><span>Tên CPP</span><input type="text" name="cpp_name" placeholder="vd: decoy"></label>
        <label class="field full"><span>Ghi chú</span><input type="text" name="note" placeholder="vd: link trong mô tả YouTube Shorts"></label>
        <div class="field full"><span>Xem trước</span><div class="copybox url" id="link-preview">—</div></div>
        <div class="full row"><span class="spacer"></span><button class="btn primary" type="submit">${icon("plus")}Lưu link</button></div>
      </form></div></div>
    <div class="stack">
      <div class="card card-pad"><h3 style="font-size:15px">Provider token (pt)</h3>
        <p class="small muted" style="margin:6px 0 12px">Lấy trong App Store Connect → Apps → Veilnest → Analytics → Acquisition → Campaigns → “Generate a campaign link”. Đây là số định danh nhà cung cấp, không phải mật khẩu.</p>
        <form id="pt-form" class="row"><input type="text" name="pt" inputmode="numeric" placeholder="vd: 123456789" value="${esc(c.provider_token)}" style="flex:1;min-width:140px"><button class="btn" type="submit">Lưu</button></form>
        ${c.provider_token ? "" : `<div class="callout warn" style="margin-top:12px">${icon("alert")}<div>Chưa có pt: link vẫn tạo được nhưng App Store Connect chỉ ghi nhận khi có pt đúng.</div></div>`}</div>
      <div class="callout">${icon("info")}<div>Kết quả xem ở App Store Connect → Analytics → <b>Sources</b> (lọc Campaign). Apple chỉ hiện số khi đủ ngưỡng người dùng và có độ trễ 1–2 ngày; click không đồng nghĩa lượt tải.</div></div>
      <div class="callout">${icon("link")}<div>TikTok chưa có link bio, nên link chỉ dùng được ở mô tả YouTube, link trên Instagram/Threads và bài Reddit/nhóm (nếu nội quy cho phép).</div></div>
    </div>
  </div>
  <div class="section-title"><h2>Link đã tạo</h2><span class="sub">${c.links.length} link</span></div>
  ${c.links.length ? `<div class="card"><div class="table-wrap"><table><thead><tr><th>ct</th><th>Kênh</th><th>Creative</th><th>URL</th><th>Tạo</th><th></th></tr></thead><tbody>
  ${[...c.links].reverse().map((l) => `<tr><td><code>${esc(l.ct)}</code>${l.cpp_name ? ` <span class="tag">CPP ${esc(l.cpp_name)}</span>` : ""}</td><td>${l.channel ? chanTag(l.channel) : "—"} ${l.lang ? `<span class="tag">${esc(l.lang.toUpperCase())}</span>` : ""}</td>
    <td class="small">${l.creative ? esc(title(D.creative[l.creative]) || l.creative) + (l.variant ? " · " + l.variant.toUpperCase() : "") : "—"}${l.note ? `<div class="faint">${esc(l.note)}</div>` : ""}</td>
    <td style="max-width:340px"><div class="url ellipsis">${esc(l.url || "")}</div></td><td class="nowrap small">${esc(l.created)}</td>
    <td class="nowrap">${copyBtn(l.url || "")}<button class="icon-btn" data-act="del-link" data-id="${esc(l.id)}" title="Xoá">${icon("trash")}</button></td></tr>`).join("")}
  </tbody></table></div></div>` : `<div class="card">${emptyState("link", "Chưa có campaign link", "Tạo một link cho mỗi kênh × ngôn ngữ (vd. yt_shorts_en). Khi một creative chạy tốt, tạo link riêng cho creative đó để so sánh.")}</div>`}`;
}

/* ---------- views: channels ---------- */
function viewChannels() {
  const yt = S.youtube;
  const infra = S.accounts.filter((a) => !a.channel);
  const check = (ok, label) => `<div class="row" style="gap:8px">${ok ? `<span style="color:var(--good)">${icon("checkCircle").replace("<svg", '<svg style="width:17px;height:17px"')}</span>` : `<span style="color:var(--text-3)">${icon("xCircle").replace("<svg", '<svg style="width:17px;height:17px"')}</span>`}<span class="${ok ? "" : "muted"}">${label}</span></div>`;
  return `<div class="page-head"><div><div class="eyebrow">Tài khoản</div><h1>Kênh & tài khoản</h1><p>Từ <code>docs/social/ACCOUNTS.md</code>: nguồn sự thật về tài khoản. Dashboard chỉ đọc; cập nhật trạng thái trong file đó.</p></div>
  <a class="btn" data-act="reveal" data-path="docs/social/ACCOUNTS.md">${icon("pen")}Mở ACCOUNTS.md</a></div>
  <div class="grid cols-3">${S.channels.filter((c) => c.account).map((c) => {
    const a = D.account[c.key];
    return `<div class="card channel-card" style="--c:${chanColor(c.key)}"><div class="top"><span class="logo">${icon(CHANNEL_ICON[c.key])}</span><div style="min-width:0"><h3>${esc(c.label)}</h3><div class="small faint ellipsis">${a?.url ? `<a href="${esc(a.url)}" target="_blank" rel="noreferrer">${esc(a.profile)}</a>` : esc(a?.profile || "—")}</div></div></div>
      <div class="small"><span class="faint">Trạng thái · </span>${esc(a?.status || "—")}</div>
      ${a?.todo ? `<div class="small"><span class="faint">Còn lại · </span>${esc(a.todo)}</div>` : ""}
      <div class="small"><span class="faint">Quản trị · </span>${esc(a?.owner || "—")}</div></div>`;
  }).join("")}</div>
  <div class="section-title"><h2>Kết nối API</h2></div>
  <div class="grid cols-2">
    <div class="card card-pad stack"><div class="row">${chanTag("youtube")}<span class="spacer"></span>${yt.token ? '<span class="pill good">Đã kết nối</span>' : '<span class="pill warn">Chưa kết nối</span>'}</div>
      ${check(yt.venv, "Môi trường <code>tools/youtube/.venv</code>")}${check(yt.client, "OAuth client <code>.secrets/youtube-client.json</code>")}${check(yt.token, "Token đăng nhập (<code>upload.py auth</code>)")}
      <div class="small muted">Dùng cho upload private và đồng bộ view, thời gian xem, tỷ lệ xem hết. Bật thêm <b>YouTube Analytics API</b> trong Google Cloud. <a href="#" data-act="reveal" data-path="tools/youtube/README.md">Hướng dẫn</a></div></div>
    <div class="card card-pad stack"><div class="row"><b>Instagram · Threads · TikTok</b><span class="spacer"></span><span class="pill">Giai đoạn sau</span></div>
      <div class="small muted">Instagram và Threads cần một Meta app (dùng ở chế độ dev cho tài khoản của mình). TikTok cần app được TikTok duyệt mới đăng public và đọc số. Trong lúc chờ: đăng tay, nhập số ở trang Số liệu.</div></div>
  </div>
  ${infra.length ? `<div class="section-title"><h2>Hạ tầng</h2></div><div class="card"><div class="table-wrap"><table><thead><tr><th>Dịch vụ</th><th>Trạng thái</th><th>Còn lại</th></tr></thead><tbody>${infra.map((a) => `<tr><td class="nowrap"><b>${esc(a.platform)}</b>${a.url ? ` <a href="${esc(a.url)}" target="_blank" rel="noreferrer">${icon("ext").replace("<svg", '<svg style="width:13px;height:13px;vertical-align:-2px"')}</a>` : ""}</td><td class="small muted">${esc(a.status)}</td><td class="small">${esc(a.todo)}</td></tr>`).join("")}</tbody></table></div></div>` : ""}`;
}

function emptyState(ic, h, p, cta = "") {
  return `<div class="empty"><span class="ico">${icon(ic)}</span><h3>${esc(h)}</h3><p>${esc(p)}</p>${cta}</div>`;
}

/* ---------- modals ---------- */
function openModal(html) {
  const m = $("#modal");
  m.innerHTML = `<div class="modal" role="dialog">${html}</div>`;
  m.hidden = false;
  setTimeout(() => $("input,select,textarea", m)?.focus(), 30);
}
function closeLayer(sel) {
  const el = $(sel);
  if (el.hidden) return;
  el.hidden = true;
  el.innerHTML = "";
}
function localNow() {
  const d = new Date();
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
  return d.toISOString().slice(0, 16);
}
function withOffset(local) {
  const off = -new Date(local).getTimezoneOffset();
  const sign = off >= 0 ? "+" : "-";
  const a = Math.abs(off);
  return `${local}${sign}${String(Math.floor(a / 60)).padStart(2, "0")}:${String(a % 60).padStart(2, "0")}`;
}
function logPostModal(pre = {}) {
  const creatives = S.creatives.filter((c) => c.has_brief);
  const c = D.creative[pre.creative];
  const link = c && pre.channel ? campaignFor(pre.channel, c, { id: pre.variant }) : null;
  openModal(`<form id="post-form"><div class="modal-head"><h2>Ghi bài đã đăng</h2><button type="button" class="icon-btn" data-act="close-modal">${icon("x")}</button></div>
    <div class="modal-body"><div class="form-grid">
      <label class="field"><span>Kênh</span><select name="channel">${S.channels.map((ch) => `<option value="${ch.key}" ${ch.key === pre.channel ? "selected" : ""}>${esc(ch.label)}</option>`).join("")}</select></label>
      <label class="field"><span>Thời điểm đăng</span><input type="datetime-local" name="when" value="${localNow()}" required></label>
      <label class="field"><span>Creative</span><select name="creative"><option value="">—</option>${creatives.map((x) => `<option value="${esc(x.id)}" ${x.id === pre.creative ? "selected" : ""}>${esc(title(x))} · ${esc((x.lang || "").toUpperCase())}</option>`).join("")}</select></label>
      <label class="field"><span>Hook</span><select name="variant"><option value="">—</option>${["a", "b", "c"].map((v) => `<option value="${v}" ${v === pre.variant ? "selected" : ""}>${v.toUpperCase()}</option>`).join("")}</select></label>
      <label class="field full"><span>URL bài đăng (public)</span><input type="url" name="url" placeholder="https://www.tiktok.com/@khanhvuapps/video/…" required></label>
      <label class="field full"><span>Link đích</span><input type="text" name="link" value="${esc(link?.url || (pre.channel === "tiktok" ? "Tìm “Veilnest” trên App Store" : ""))}" placeholder="campaign link hoặc mô tả CTA"></label>
      <label class="field"><span>Subreddit / nhóm <span class="faint">(nếu có)</span></span><input type="text" name="place"></label>
      <label class="field"><span>Nội quy đã đọc ngày <span class="faint">(Reddit/nhóm)</span></span><input type="text" name="rules_read" placeholder="2026-10-20"></label>
    </div><div class="callout" style="margin-top:14px">${icon("info")}<div>Thêm một dòng vào <code>docs/social/channels/&lt;kênh&gt;/POSTS.md</code>. Chỉ ghi bài đã public thật.</div></div></div>
    <div class="modal-foot"><button type="button" class="btn ghost" data-act="close-modal">Huỷ</button><button class="btn primary" type="submit">${icon("check")}Ghi vào nhật ký</button></div></form>`);
}
function metricModal(pre = {}) {
  const posts = S.posts.filter((p) => p.url);
  if (!posts.length) return toast("Chưa có bài nào trong nhật ký để nhập số", "err", "Ghi bài đã đăng trước (trang Đăng bài).");
  const sel = pre.url || posts[0].url;
  const age = pre.age != null && pre.age !== "" ? +pre.age : null;
  const win = age == null ? "24h" : age >= 168 ? "7d" : "24h";
  const defs = S.metric_defs;
  const main = ["views", "completion_pct", "avg_view_s", "likes", "comments", "shares", "saves", "profile_visits", "followers", "link_clicks", "installs", "watch_time_min"];
  openModal(`<form id="metric-form"><div class="modal-head"><h2>Nhập số liệu</h2><button type="button" class="icon-btn" data-act="close-modal">${icon("x")}</button></div>
    <div class="modal-body"><div class="form-grid">
      <label class="field full"><span>Bài đăng</span><select name="url">${posts.map((p) => `<option value="${esc(p.url)}" ${p.url === sel ? "selected" : ""}>${esc(chanLabel(p.channel))} · ${esc(title(D.creative[p.creative_id]) || p.place || "")}${p.variant ? " " + p.variant.toUpperCase() : ""} · ${dateVN(p.at)}</option>`).join("")}</select></label>
      <label class="field"><span>Khoảng đo</span><select name="window">${S.windows.map((w) => `<option ${w === win ? "selected" : ""}>${w}</option>`).join("")}</select></label>
      <label class="field"><span>Nguồn</span><input type="text" name="source" list="sources" placeholder="TikTok Studio" required><datalist id="sources"><option>TikTok Studio</option><option>Instagram Insights</option><option>YouTube Studio</option><option>Threads Insights</option><option>App Store Connect · Sources</option></datalist></label>
      ${main.map((k) => `<label class="field"><span>${esc(defs[k].label)}</span><input type="number" name="${k}" min="0" step="${defs[k].kind === "int" ? 1 : 0.1}" placeholder="chưa có"></label>`).join("")}
      <label class="field full"><span>Ghi chú</span><input type="text" name="note" placeholder="vd: số đọc lúc 09:00, tab Overview"></label>
    </div><div class="small faint" style="margin-top:12px">Ô để trống = chưa có số (không tính là 0). Lưu trong <code>.dashboard/dashboard.db</code>.</div></div>
    <div class="modal-foot"><button type="button" class="btn ghost" data-act="close-modal">Huỷ</button><button class="btn primary" type="submit">${icon("check")}Lưu số liệu</button></div></form>`);
}

/* ---------- events ---------- */
async function busy(btn, fn) {
  const html = btn?.innerHTML;
  if (btn) { btn.disabled = true; btn.innerHTML = `<span class="spinner"></span>${btn.textContent.trim()}`; }
  try { return await fn(); } finally { if (btn && btn.isConnected) { btn.disabled = false; btn.innerHTML = html; } }
}

document.addEventListener("click", async (e) => {
  const go = e.target.closest("[data-go]");
  if (go && !e.target.closest("a,button")) { location.hash = go.dataset.go; return; }
  const pubLink = e.target.closest("[data-pub]");
  if (pubLink) { const p = JSON.parse(pubLink.dataset.pub); ui.pub.creative = p.creative; ui.pub.variant = p.variant; }
  const seg = e.target.closest("[data-filter] button");
  if (seg) {
    const key = seg.parentElement.dataset.filter;
    if (key === "chan") ui.chan = seg.dataset.val;
    else if (key === "hookMetric") ui.hookMetric = seg.dataset.val;
    else ui.filter[key] = seg.dataset.val;
    return render();
  }
  if (e.target.classList.contains("drawer-layer")) { location.hash = "#/content"; return; }
  if (e.target.classList.contains("modal-layer")) return closeLayer("#modal");
  const btn = e.target.closest("[data-act]");
  if (!btn) return;
  const a = btn.dataset;
  if (btn.tagName === "A") e.preventDefault();
  try {
    switch (a.act) {
      case "close-drawer": location.hash = "#/content"; break;
      case "close-modal": closeLayer("#modal"); break;
      case "copy": await navigator.clipboard.writeText(a.text); toast("Đã copy"); break;
      case "copy-area": await navigator.clipboard.writeText(btn.closest(".field").querySelector("textarea").value); toast("Đã copy caption"); break;
      case "reveal": await api("/api/reveal", { method: "POST", body: { path: a.path } }); break;
      case "publish-variant": ui.pub.creative = a.creative; ui.pub.variant = a.variant; location.hash = "#/publish"; break;
      case "log-post": logPostModal({ channel: a.channel, creative: a.creative, variant: a.variant }); break;
      case "add-metric": metricModal({ url: a.url, age: a.age }); break;
      case "write-result": {
        const r = await busy(btn, () => api("/api/posts/result", { method: "POST", body: { channel: a.channel, url: a.url } }));
        toast("Đã ghi vào " + r.file, "ok", r.text); await load({ quiet: true }); break;
      }
      case "del-snap":
        if (!confirm("Xoá bản ghi số liệu này?")) return;
        await api(`/api/snapshots/${a.id}`, { method: "DELETE", body: {} }); await load({ quiet: true }); toast("Đã xoá"); break;
      case "del-link":
        if (!confirm("Xoá campaign link này khỏi danh sách? (Link đã đăng vẫn hoạt động)")) return;
        await api(`/api/campaigns/${a.id}`, { method: "DELETE", body: {} }); await load({ quiet: true }); toast("Đã xoá link"); break;
      case "yt-sync": {
        const r = await busy(btn, () => api("/api/youtube/sync", { method: "POST", body: {} }));
        toast(`Đồng bộ YouTube: thêm ${r.added} bản ghi`, "ok", (r.notes || []).join("\n")); await load({ quiet: true }); break;
      }
      case "yt-upload": {
        const dry = !!a.dry;
        if (!dry && !confirm("Upload video này lên YouTube ở chế độ PRIVATE?\nVideo chưa public; xem lại trong YouTube Studio.")) return;
        const r = await busy(btn, () => api("/api/youtube/upload", { method: "POST", body: { creative: a.creative, variant: a.variant, dry_run: dry } }));
        toast(dry ? "Dry-run hợp lệ" : "Đã upload private", "ok", r.output); if (!dry) await load({ quiet: true }); break;
      }
    }
  } catch (err) {
    toast("Không thực hiện được", "err", err.message);
  }
});

document.addEventListener("input", (e) => {
  if (e.target.id === "q") {
    ui.filter.q = e.target.value;
    const pos = e.target.selectionStart;
    render();
    const q = $("#q"); q.focus(); q.setSelectionRange(pos, pos);
  }
  if (e.target.matches("textarea[data-counter]")) updateCounter(e.target);
  if (e.target.closest("#link-form")) linkPreview(e.target.name !== "ct");
});
document.addEventListener("change", (e) => {
  if (e.target.id === "pub-creative") { ui.pub.creative = e.target.value; ui.pub.variant = null; render(); }
  if (e.target.id === "pub-variant") { ui.pub.variant = e.target.value; render(); }
  if (e.target.dataset.pubChan) { e.target.checked ? ui.pub.channels.add(e.target.dataset.pubChan) : ui.pub.channels.delete(e.target.dataset.pubChan); render(); }
  if (e.target.closest("#link-form")) linkPreview(e.target.name !== "ct");
});

let suggestTimer;
function linkPreview(resuggest) {
  const f = $("#link-form");
  if (!f) return;
  const data = Object.fromEntries(new FormData(f));
  const show = (ct) => {
    const app = S.apps[data.app];
    const params = [S.campaigns.provider_token ? `pt=${S.campaigns.provider_token}` : "pt=…", `ct=${encodeURIComponent(ct || "…")}`, data.ppid ? `ppid=${encodeURIComponent(data.ppid)}` : "", "mt=8"].filter(Boolean);
    $("#link-preview").textContent = app?.app_store_id ? `https://apps.apple.com/app/apple-store/id${app.app_store_id}?${params.join("&")}` : "App chưa có App Store ID";
  };
  if (resuggest) {
    clearTimeout(suggestTimer);
    suggestTimer = setTimeout(async () => {
      const r = await api("/api/campaigns/suggest", { method: "POST", body: data }).catch(() => null);
      if (r && f.isConnected) { f.ct.value = r.ct; show(r.ct); }
    }, 120);
  }
  show(data.ct);
}

document.addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target;
  const data = Object.fromEntries(new FormData(f));
  const btn = f.querySelector('[type="submit"]');
  try {
    if (f.id === "post-form") {
      const body = { ...data, when: withOffset(data.when), lang: D.creative[data.creative]?.lang || "", app: D.creative[data.creative]?.app || "veilnest" };
      if (data.creative && data.variant) body.creative = `${data.creative}-hook${data.variant}`;
      const r = await busy(btn, () => api("/api/posts", { method: "POST", body }));
      closeLayer("#modal"); toast("Đã ghi vào " + r.file); await load({ quiet: true });
    } else if (f.id === "metric-form") {
      const post = S.posts.find((p) => p.url === data.url);
      const body = { ...data, channel: post?.channel, creative_id: post?.creative_id, variant: post?.variant };
      await busy(btn, () => api("/api/snapshots", { method: "POST", body }));
      closeLayer("#modal"); toast("Đã lưu số liệu"); await load({ quiet: true });
    } else if (f.id === "link-form") {
      await busy(btn, () => api("/api/campaigns", { method: "POST", body: data }));
      toast("Đã lưu campaign link"); await load({ quiet: true });
    } else if (f.id === "pt-form") {
      await busy(btn, () => api("/api/campaigns/provider", { method: "POST", body: { provider_token: data.pt } }));
      toast("Đã lưu provider token"); await load({ quiet: true });
    }
  } catch (err) {
    toast("Chưa lưu được", "err", err.message);
  }
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") { if (!$("#modal").hidden) closeLayer("#modal"); else if (!$("#drawer").hidden) location.hash = "#/content"; }
  if (e.key === "r" && !e.metaKey && !e.ctrlKey && !e.target.closest("input,textarea,select")) load();
});

/* ---------- theme ---------- */
function applyTheme(t) {
  if (t) document.documentElement.dataset.theme = t; else delete document.documentElement.dataset.theme;
  const dark = t ? t === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
  $("#theme").innerHTML = icon(dark ? "sun" : "moon");
}
$("#theme").addEventListener("click", () => {
  const dark = document.documentElement.dataset.theme ? document.documentElement.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
  const next = dark ? "light" : "dark";
  try { localStorage.setItem("kv-theme", next); } catch {}
  applyTheme(next);
});
$("#refresh").addEventListener("click", () => load());
let saved = null;
try { saved = localStorage.getItem("kv-theme"); } catch {}
applyTheme(saved);
load({ quiet: true }).then(() => { if ($("#link-form")) linkPreview(true); });
addEventListener("hashchange", () => setTimeout(() => $("#link-form") && linkPreview(true), 0));
