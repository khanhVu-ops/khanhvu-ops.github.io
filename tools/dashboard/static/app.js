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
  bag: '<path d="M5 8h14l-1.2 11.5a2 2 0 0 1-2 1.5H8.2a2 2 0 0 1-2-1.5Z"/><path d="M9 8V6.5a3 3 0 0 1 6 0V8"/>',
  globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
  image: '<rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="9" cy="9" r="2"/><path d="m21 15-5-5L5 21"/>',
  tag2: '<path d="M3 12V4a1 1 0 0 1 1-1h8l9 9-9 9Z"/><circle cx="8" cy="8" r="1.5"/>',
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

const OFFLINE = "Dashboard server đã dừng. Chạy lại trong Terminal: python3 tools/dashboard/server.py";
async function api(path, { method = "GET", body } = {}) {
  let res;
  try {
    res = await fetch(path, {
      method, headers: body ? { "Content-Type": "application/json" } : {}, body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new Error(OFFLINE); // fetch only rejects when nothing answers, never on an HTTP error
  }
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
    toast(e.message === OFFLINE ? "Mất kết nối tới dashboard" : "Không đọc được dữ liệu", "err", e.message);
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
  // Same message again (e.g. pressing R while the server is down) replaces the old one instead of stacking.
  $$(".toast").filter((t) => t.dataset.key === msg + detail).forEach((t) => t.remove());
  const el = document.createElement("div");
  el.dataset.key = msg + detail;
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
  { path: "store", label: "App Store", icon: "bag", view: viewStore },
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
  const stale = S.stale_code ? `<div class="callout warn" style="margin-bottom:16px">${icon("refresh")}<div><b>Code dashboard đã đổi sau khi server khởi động.</b> Trang này vẫn chạy bản cũ. Dừng server (Ctrl+C) rồi chạy lại <code>python3 tools/dashboard/server.py</code>.</div></div>` : "";
  main.innerHTML = `<div class="page">${stale}${route.view(arg)}</div>`;
  scrollTo(0, y);
  if (route.path === "content" && arg) openCreative(arg);
  else if (route.path === "store" && arg) openAscLocale(arg);
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


/* ---------- views: app store ---------- */
const FIELD_KEYS = ["name", "subtitle", "keywords", "promotional_text", "description", "whats_new"];
const FIELD_SHORT = { name: "Tên", subtitle: "Sub", keywords: "Key", promotional_text: "Promo", description: "Mô tả", whats_new: "New" };
const FIELD_LABEL = { name: "Tên app", subtitle: "Subtitle", keywords: "Keywords", promotional_text: "Promotional text", description: "Mô tả", whats_new: "What's New", screenshots: "Screenshot" };
// Mirrors appstore.py: AUTO goes out with "Chọn locale cần đẩy"; OVERRIDE needs a tick per field.
const ST = {
  same: ["Đã khớp", "Local và ASC giống nhau (kể cả khi bạn dán tay vào ASC)."],
  new: ["ASC trống", "ASC chưa có nội dung này: đẩy được."],
  ahead: ["Local mới hơn", "ASC vẫn đúng như lần khớp trước, chỉ local đổi: đẩy an toàn."],
  conflict: ["ASC sửa tay", "ASC đã đổi sau lần khớp trước (sửa trong App Store Connect). Chỉ đẩy khi tick ghi đè."],
  differs: ["Khác, chưa có mốc", "Khác nhau và chưa từng khớp: không rõ bên nào mới hơn. Chỉ đẩy khi tick ghi đè, hoặc bấm Giữ bản ASC."],
  accepted: ["Giữ bản ASC", "Bạn đã chọn giữ nội dung trên ASC. Không đẩy cho tới khi local đổi tiếp."],
  empty: ["Local trống", "Không có gì để đẩy."],
  local: ["Chưa so", "Tải từ App Store Connect để so sánh."],
  over: ["Vượt giới hạn", "Sửa trong locale.json của repo app."],
  none: ["Không có ảnh", ""],
};
const AUTO = new Set(["new", "ahead"]);
const OVERRIDE = new Set(["conflict", "differs", "accepted"]);
ui.asc = { app: null, data: null, loading: false, error: null, filter: "all", q: "", sel: new Set(), fields: new Set(FIELD_KEYS), tab: "listing", products: null, pending: null, override: new Set(), discover: null, bulkRunning: false, bulkCancel: false, bulkSets: [] };

async function ascLoad(refresh = false, btn = null) {
  const app = ui.asc.app;
  ui.asc.loading = true; ui.asc.error = null;
  try {
    const data = await busy(btn, () => api("/api/appstore/listing", { method: "POST", body: { app, refresh } }));
    if (app === ui.asc.app) ui.asc.data = data;
    if (refresh) toast("Đã tải listing từ App Store Connect");
  } catch (e) {
    ui.asc.error = e.message;
    if (refresh) toast("Không tải được từ App Store Connect", "err", e.message);
  } finally {
    ui.asc.loading = false;
    if (current().route.path === "store") render();
  }
}
const ascKey = (loc, k) => `${loc}|${k}`;
const fstate = (f) => (f.over ? "over" : f.status || "local");

const hasTodoShots = (r) => {
  if (r.shots_by_type && Object.keys(r.shots_by_type).length) {
    return Object.values(r.shots_by_type).some((t) => AUTO.has(t.status));
  }
  return AUTO.has(r.shots_status);
};
const hasCheckShots = (r) => {
  if (r.shots_by_type && Object.keys(r.shots_by_type).length) {
    return Object.values(r.shots_by_type).some((t) => ["conflict", "differs"].includes(t.status));
  }
  return ["conflict", "differs"].includes(r.shots_status);
};
const isSyncedShots = (r) => {
  if (r.shots_by_type && Object.keys(r.shots_by_type).length) {
    return Object.values(r.shots_by_type).every((t) => ["same", "accepted", "none"].includes(t.status));
  }
  return ["same", "accepted", "none"].includes(r.shots_status);
};

function ascVisible() {
  const rows = ui.asc.data?.compare.rows || [];
  const q = ui.asc.q.trim().toLowerCase();
  return rows.filter((r) => (!q || `${r.locale} ${r.fields.name.local}`.toLowerCase().includes(q)) &&
    (ui.asc.filter === "all"
      || (ui.asc.filter === "todo" && (ascAuto(r).length || hasTodoShots(r)))
      || (ui.asc.filter === "check" && (FIELD_KEYS.some((k) => ["conflict", "differs"].includes(r.fields[k].status)) || hasCheckShots(r)))
      || (ui.asc.filter === "problems" && (r.problems.length || Object.values(r.fields).some((f) => f.over)))));
}
const sendable = (f) => !f.over && f.editable;
// Fields sent without asking: chosen, safe state, within limit, editable now.
const ascAuto = (r) => FIELD_KEYS.filter((k) => ui.asc.fields.has(k) && AUTO.has(r.fields[k].status) && sendable(r.fields[k]));
// Fields that will actually be sent: the safe ones plus those ticked for override.
const ascPushable = (r) => FIELD_KEYS.filter((k) => ui.asc.fields.has(k) && sendable(r.fields[k]) &&
  (AUTO.has(r.fields[k].status) || (OVERRIDE.has(r.fields[k].status) && ui.asc.override.has(ascKey(r.locale, k)))));

function ascShotsSets(rows, targetLocales = null) {
  const list = [];
  const target = targetLocales && targetLocales.size ? rows.filter((r) => targetLocales.has(r.locale)) : rows;
  for (const r of target) {
    if (r.shots_by_type && Object.keys(r.shots_by_type).length) {
      for (const [dt, info] of Object.entries(r.shots_by_type)) {
        if (info.local_count > 0) {
          list.push({
            key: `${r.locale}:${dt}`,
            locale: r.locale,
            tier: r.tier,
            display_type: dt,
            label: info.label || dt,
            local_count: info.local_count,
            remote_count: info.remote_count || 0,
            status: info.status || "new",
            remote_exists: !!r.remote_exists,
          });
        }
      }
    } else if (r.shots > 0) {
      list.push({
        key: `${r.locale}:${r.display_type || "default"}`,
        locale: r.locale,
        tier: r.tier,
        display_type: r.display_type || null,
        label: "Screenshot",
        local_count: r.shots,
        remote_count: r.shots_remote || 0,
        status: r.shots_status || "new",
        remote_exists: !!r.remote_exists,
      });
    }
  }
  return list;
}

function fchip(r, k) {
  const f = r.fields[k];
  const st = fstate(f);
  const ov = OVERRIDE.has(st) && ui.asc.override.has(ascKey(r.locale, k));
  const tip = attr({ t: FIELD_LABEL[k], r: [["Độ dài", `${f.len} / ${f.limit}`], ["Trạng thái", ST[st][0]], ...(f.mark ? [["Mốc", `${f.mark.how} · ${dateVN(f.mark.at)}`]] : []), ...(ov ? [["Ghi đè", "sẽ thay bản trên ASC"]] : []), ...(f.why ? [["Không sửa được", f.why]] : [])] });
  return `<span class="fchip s-${st}${f.editable === false ? " locked" : ""}${ov ? " ov" : ""}" data-tip="${tip}">${FIELD_SHORT[k]}</span>`;
}

function viewStore() {
  const st = S.appstore;
  const apps = st.apps;
  if (!apps.some((a) => a.id === ui.asc.app)) ui.asc.app = (apps.find((a) => a.has_source) || apps[0])?.id;
  const app = apps.find((a) => a.id === ui.asc.app);
  if (!app) return emptyState("bag", "Chưa có app nào", "Thêm app vào docs/apps/registry.json.");
  if (!ui.asc.data && !ui.asc.loading && !ui.asc.error) setTimeout(() => ascLoad(false), 0);
  const d = ui.asc.data, remote = d?.remote;
  const linked = !!app.app_store_id;
  const head = `<div class="page-head"><div><div class="eyebrow">App Store</div><h1>Listing & screenshot</h1>
    <p>Mỗi app lấy copy và ảnh từ repo của nó trong <code>~/personal</code>, so với App Store Connect rồi đẩy những gì bạn chọn. Không bao giờ tự submit review.</p></div>
    <div class="actions"><button class="btn" data-act="asc-discover" ${st.configured ? "" : "disabled"} title="${st.configured ? "Các app của team trên App Store Connect" : "Cần API key"}">${icon("search")}App trên ASC</button>
    <button class="btn primary" data-act="asc-refresh" ${st.configured && linked ? "" : "disabled"} title="${!st.configured ? "Cần API key" : linked ? "" : "App chưa liên kết App Store Connect"}">${icon("refresh")}${remote ? "Tải lại từ ASC" : "Tải từ App Store Connect"}</button></div></div>
  <div class="app-pick">${apps.map((a) => `<button class="${a.id === app.id ? "on" : ""}" data-act="asc-app" data-app="${esc(a.id)}"><b>${esc(a.name)}</b>
    <span><i class="${a.app_store_id ? "ok" : ""}" title="App Store Connect">ASC</i><i class="${a.has_source ? "ok" : ""}" title="Listing trong repo">listing</i><i class="${a.repo_path ? "ok" : "bad"}" title="${esc(a.repo_path || "không thấy repo " + (a.repo || ""))}">repo</i></span></button>`).join("")}</div>
  ${st.configured ? "" : ascSetup(st)}
  <div class="card card-pad asc-status">
    <div><span class="faint small">Repo</span><b>${app.repo_path ? `<code>${esc(app.repo_path)}</code>` : `<span style="color:var(--bad)">không thấy ${esc(app.repo || "—")}</span>`}</b></div>
    <div><span class="faint small">Listing local</span><b>${app.source ? `<code>${esc(app.source)}</code>` : '<span class="faint">chưa có</span>'}</b></div>
    <div><span class="faint small">App Store Connect</span><b>${linked ? `<a href="https://appstoreconnect.apple.com/apps/${esc(app.app_store_id)}" target="_blank" rel="noreferrer">${esc(app.app_store_id)}</a>` : '<span class="faint">chưa liên kết</span>'}</b></div>
    ${remote ? `<div><span class="faint small">Version mới nhất</span><b>${esc(remote.version?.version || "—")}${remote.version ? verPill(remote.version) : ""}</b></div>
    ${remote.live_version && remote.live_version.id !== remote.version?.id ? `<div><span class="faint small">Đang bán</span><b>${esc(remote.live_version.version)}</b></div>` : ""}
    <div><span class="faint small">App Information</span>${remote.info ? stPill(remote.info.state, remote.info.editable) : "—"}</div>
    <div><span class="faint small">Đọc lúc</span><b>${dateVN(remote.fetched_at)}</b></div>` : ""}
  </div>`;
  if (!d) return head + (ui.asc.error ? `<div class="callout bad" style="margin-top:14px">${icon("xCircle")}<div>${esc(ui.asc.error)}</div></div>` : `<div class="loading"><span class="spinner"></span>Đang đọc listing local…</div>`);
  const rows = d.compare.rows;
  if (!rows.length) return head + ascNoSource(app, st, remote, d);
  const todo = remote ? rows.filter((r) => ascAuto(r).length || hasTodoShots(r)).length : 0;
  const check = remote ? rows.filter((r) => FIELD_KEYS.some((k) => ["conflict", "differs"].includes(r.fields[k].status)) || hasCheckShots(r)).length : 0;
  const synced = remote ? rows.filter((r) => FIELD_KEYS.every((k) => ["same", "empty", "accepted"].includes(r.fields[k].status)) && isSyncedShots(r)).length : 0;
  const v = remote?.version;
  return head + `
  <div class="grid cols-4" style="margin-top:16px">
    ${kpi("globe", "Locale local", rows.length, remote ? `${rows.filter((r) => r.remote_exists).length} đã có trên ASC` : "chưa so với ASC")}
    ${kpi("checkCircle", "Đã khớp", remote ? synced : "—", remote ? "text và ảnh giống ASC" : "Tải từ ASC để so sánh")}
    ${kpi("upload", "Cần đẩy", remote ? todo : "—", remote ? "có field ASC trống hoặc local mới hơn" : "")}
    ${kpi("alert", "Cần xem", remote ? check : rows.filter((r) => r.problems.length).length, remote ? "ASC sửa tay hoặc khác chưa có mốc" : "lỗi giới hạn")}
  </div>
  ${v && !v.editable ? `<div class="callout warn" style="margin-top:12px">${icon("info")}<div>${esc(v.locked || "")}. Trong lúc này chỉ <b>Promotional text</b> sửa được; mô tả, keyword, What's New, screenshot, tên và subtitle đều khoá.</div></div>` : ""}
  ${d.compare.remote_only.length ? `<div class="callout" style="margin-top:12px">${icon("info")}<div>ASC có ${d.compare.remote_only.length} ngôn ngữ chưa có ở local: <b>${esc(d.compare.remote_only.join(", "))}</b>. <button class="btn sm" data-act="asc-import" style="margin-left:6px">${icon("download")}Nhập về repo</button></div></div>` : ""}
  <div class="toolbar" style="margin-top:20px">
    <div class="seg">${[["listing", "Listing theo locale"], ["products", "Gói giá"]].map(([k, l]) => `<button class="${ui.asc.tab === k ? "on" : ""}" data-act="asc-tab" data-tab="${k}">${l}</button>`).join("")}</div>
  </div>
  ${ui.asc.tab === "products" ? ascProducts(st, linked) : ascListing(rows, remote)}`;
}
const verPill = (v) => `<span class="pill ${v.editable ? "good" : v.live ? "" : "warn"}" style="margin-left:8px">${esc(v.state_vi || v.state)}${v.editable ? " · sửa được" : ""}</span>`;
const stPill = (state, editable) => `<span class="pill ${editable ? "good" : ""}" style="margin-left:8px">${esc((state || "—").replaceAll("_", " ").toLowerCase())}${editable ? " · sửa được" : ""}</span>`;

function ascNoSource(app, st, remote, d) {
  const n = remote ? Object.keys(remote.locales).length : 0;
  return `<div class="card" style="margin-top:16px">${emptyState("globe", `${app.name} chưa có listing trong repo`,
    !app.app_store_id ? "Liên kết app với App Store Connect (nút App trên ASC), rồi nhập listing đang có trên ASC về repo. Hoặc tạo AppStore/locales/<locale>/locale.json trong repo app và khai store trong docs/apps/registry.json."
    : !st.configured ? "Kết nối API key để đọc listing trên App Store Connect, rồi nhập về repo."
    : remote ? `ASC đang có ${n} ngôn ngữ. Nhập về repo để quản lý từ đây; mỗi field nhập vào sẽ ở trạng thái Đã khớp, không có gì bị đẩy lại.`
    : "Tải từ App Store Connect để xem listing hiện có, rồi nhập về repo.",
    app.app_store_id && st.configured ? (remote ? `<button class="btn primary" data-act="asc-import">${icon("download")}Nhập ${n} ngôn ngữ vào ${esc(app.repo_path || app.repo)}/AppStore</button>` : `<button class="btn primary" data-act="asc-refresh">${icon("refresh")}Tải từ App Store Connect</button>`) : "")}</div>`;
}

function ascSetup(st) {
  return `<div class="card card-pad stack" style="margin-top:16px"><div class="row"><b>Kết nối App Store Connect API</b><span class="spacer"></span><span class="pill warn">Chưa kết nối</span></div>
    <div class="small muted">Không có key vẫn xem và kiểm tra copy local được. Muốn so sánh và đẩy lên ASC, cần một API key của team <b>Van Khanh Vu</b>:</div>
    <ol class="small" style="margin:0;padding-left:18px;line-height:1.7">
      <li>App Store Connect → <b>Users and Access → Integrations → App Store Connect API → Team Keys</b> → Generate. Quyền: <b>App Manager</b>.</li>
      <li>Tải file <code>AuthKey_&lt;KEY_ID&gt;.p8</code> (chỉ tải được một lần) vào <code>.secrets/appstore/</code>.</li>
      <li>Thêm vào <code>.env</code>: <code>ASC_KEY_ID=…</code> và <code>ASC_ISSUER_ID=…</code> (Issuer ID ở đầu trang Team Keys). Bấm <kbd>R</kbd>.</li>
    </ol>
    <div class="row small">${[["Key ID", !!st.key_id], ["Issuer ID", st.issuer], [st.key_path, st.key_file]].map(([l, ok]) => `<span class="pill ${ok ? "good" : ""}">${icon(ok ? "check" : "x")}${esc(l)}</span>`).join("")}</div></div>`;
}

function ascListing(rows, remote) {
  const list = ascVisible();
  const sel = ui.asc.sel;
  const pushable = [...sel].map((c) => rows.find((r) => r.locale === c)).filter((r) => r && ascPushable(r).length);
  const shotsSets = ascShotsSets(rows, sel.size ? sel : null);
  const shotsPushable = shotsSets.filter((s) => s.status !== "same" && s.remote_exists);
  const filters = [["all", "Tất cả"], ...(remote ? [["todo", "Cần đẩy"], ["check", "Cần xem"]] : []), ["problems", "Có lỗi"]];
  return `<div class="toolbar">
    <div class="seg" data-filter="asc">${filters.map(([k, l]) => `<button class="${ui.asc.filter === k ? "on" : ""}" data-val="${k}">${l}</button>`).join("")}</div>
    <label class="search">${icon("search")}<input type="search" id="asc-q" placeholder="Locale hoặc tên…" value="${esc(ui.asc.q)}"></label>
    <span class="spacer"></span>
    <div class="row field-pick">${FIELD_KEYS.map((k) => `<label><input type="checkbox" data-asc-field="${k}" ${ui.asc.fields.has(k) ? "checked" : ""}>${FIELD_LABEL[k]}</label>`).join("")}</div>
  </div>
  ${remote ? `<div class="card card-pad row asc-bulk"><span><b>${sel.size}</b> locale đã chọn${sel.size ? ` · <b>${pushable.length}</b> có field sẽ đẩy` : ""}${ui.asc.override.size ? ` · <b>${ui.asc.override.size}</b> field ghi đè` : ""}</span>
    <button class="btn sm ghost" data-act="asc-sel-changed">Chọn locale cần đẩy</button><button class="btn sm ghost" data-act="asc-sel-all">Chọn tất cả đang hiện</button>${sel.size ? `<button class="btn sm ghost" data-act="asc-sel-none">Bỏ chọn</button>` : ""}
    <span class="spacer"></span>
    <button class="btn sm" data-act="asc-bulk-shots" ${shotsPushable.length ? "" : "disabled"} title="${shotsPushable.length} bộ screenshot cần đẩy">${icon("upload")}Đẩy screenshot hàng loạt${shotsPushable.length ? ` (${shotsPushable.length} bộ)` : ""}</button>
    <button class="btn sm primary" data-act="asc-push" ${pushable.length ? "" : "disabled"}>${icon("upload")}Xem trước & đẩy metadata</button></div>` : ""}
  <div class="card"><div class="table-wrap"><table class="asc-table"><thead><tr>${remote ? "<th></th>" : ""}<th>Locale</th><th>Tên app · Subtitle</th><th>Field</th><th>Ảnh</th><th></th></tr></thead><tbody>
  ${list.map((r) => {
    const f = r.fields;
    return `<tr class="${sel.has(r.locale) ? "on" : ""}">${remote ? `<td><input type="checkbox" data-asc-sel="${esc(r.locale)}" ${sel.has(r.locale) ? "checked" : ""}></td>` : ""}
      <td class="nowrap"><b>${esc(r.locale)}</b>${r.tier ? ` <span class="tag">T${r.tier}</span>` : ""}${remote && !r.remote_exists ? ` <span class="pill warn" style="height:20px">mới</span>` : ""}</td>
      <td style="max-width:320px"><div class="ellipsis">${esc(f.name.local)}</div><div class="small faint ellipsis">${esc(f.subtitle.local)}</div>${r.problems.length ? `<div class="small" style="color:var(--bad)">${esc(r.problems.join(" · "))}</div>` : ""}</td>
      <td><div class="fchips">${FIELD_KEYS.map((k) => fchip(r, k)).join("")}</div></td>
      <td class="nowrap small">${r.shots_by_type && Object.keys(r.shots_by_type).length ? Object.values(r.shots_by_type).map((t) => `<div>${esc(t.label)}: ${t.local_count} ảnh <span class="fchip s-${t.status}" title="${esc(ST[t.status]?.[1] || '')}">${esc(ST[t.status]?.[0] || t.status)}</span></div>`).join("") : (r.shots ? `${r.shots} ảnh` : "—")}${remote && r.shots && (!r.shots_by_type || !Object.keys(r.shots_by_type).length) ? `<div><span class="fchip s-${r.shots_status}" title="${esc(ST[r.shots_status]?.[1] || "")}">${esc(ST[r.shots_status]?.[0] || r.shots_status)}</span></div>` : ""}</td>
      <td class="nowrap"><a class="btn sm" href="#/store/${encodeURIComponent(r.locale)}">${icon("eye")}Chi tiết</a></td></tr>`;
  }).join("") || `<tr><td colspan="6">${emptyState("search", "Không có locale khớp bộ lọc", "Bỏ bớt bộ lọc.")}</td></tr>`}
  </tbody></table></div></div>
  <div class="legend small asc-legend">${["same", "new", "ahead", "conflict", "differs", "accepted", "over", "local"].map((k) => `<span class="fchip s-${k}" title="${esc(ST[k][1])}">${ST[k][0]}</span>`).join("")}<span class="fchip s-ahead locked">Khoá: version không sửa được</span></div>`;
}

function openAscLocale(code) {
  const d = ui.asc.data;
  const r = d?.compare.rows.find((x) => x.locale === code);
  if (!r) return;
  const remote = d.remote;
  const local = d.local.locales[code];
  const rshots = remote ? Object.entries(remote.screenshots[code] || {}) : [];
  const app = ui.asc.app;
  const shotMark = d.marks?.[ascKey(code, "screenshots")];
  const layer = $("#drawer");
  layer.innerHTML = `<div class="drawer" role="dialog" aria-label="${esc(code)}">
    <div class="drawer-head"><div style="min-width:0;flex:1"><div class="eyebrow">${esc(S.appstore.apps.find((a) => a.id === app)?.name || app)}${r.tier ? ` · tier ${r.tier}` : ""}</div><h2 class="locale">${esc(code)}</h2>
      <div class="row" style="margin-top:8px">${remote ? (r.remote_exists ? '<span class="pill good">Đã có trên ASC</span>' : '<span class="pill warn">ASC chưa có ngôn ngữ này</span>') : '<span class="pill">Chưa tải ASC</span>'}
      ${r.whats_new_version ? `<span class="tag">What's New cho ${esc(r.whats_new_version)}</span>` : ""}${remote?.version && r.whats_new_version && r.whats_new_version !== remote.version.version ? `<span class="pill warn">ASC đang ở ${esc(remote.version.version)}</span>` : ""}</div></div>
      ${remote ? `<button class="btn sm primary" data-act="asc-push" data-locale="${esc(code)}" ${ascPushable(r).length ? "" : "disabled"}>${icon("upload")}Đẩy ${ascPushable(r).length || ""} field</button>` : ""}
      <button class="icon-btn" data-act="close-drawer" aria-label="Đóng">${icon("x")}</button></div>
    <div class="drawer-body">
      ${FIELD_KEYS.map((k) => {
        const f = r.fields[k];
        const st = fstate(f);
        const canOverride = remote && OVERRIDE.has(st) && sendable(f);
        return `<div class="asc-field"><div class="row"><b>${FIELD_LABEL[k]}</b><span class="fchip s-${st}">${ST[st][0]}</span>${f.mark ? `<span class="small faint">mốc: ${esc({ pushed: "đã đẩy", matched: "đã khớp", accepted: "giữ bản ASC" }[f.mark.how] || f.mark.how)} · ${dateVN(f.mark.at)}</span>` : ""}<span class="spacer"></span><span class="small ${f.over ? "" : "faint"}" style="${f.over ? "color:var(--bad)" : ""}">${f.len} / ${f.limit}</span></div>
          ${remote && st !== "same" && st !== "local" ? `<div class="small faint">${esc(ST[st][1])}${f.why ? " " + esc(f.why) + "." : ""}</div>` : ""}
          <div class="${remote ? "asc-cmp" : ""}"><div><span class="faint small">Local</span><div class="asc-text">${esc(f.local) || '<span class="faint">trống</span>'}</div></div>
          ${remote ? `<div><span class="faint small">App Store Connect</span><div class="asc-text ${["conflict", "differs", "accepted"].includes(st) ? "diff" : ""}">${esc(f.remote || "") || '<span class="faint">trống</span>'}</div></div>` : ""}</div>
          ${canOverride || (remote && ["conflict", "differs"].includes(st)) ? `<div class="row small">${canOverride ? `<label class="ov-pick"><input type="checkbox" data-asc-ov="${esc(ascKey(code, k))}" ${ui.asc.override.has(ascKey(code, k)) ? "checked" : ""}>Ghi đè bản trên ASC khi đẩy</label>` : ""}
            ${["conflict", "differs"].includes(st) ? `<span class="spacer"></span><button class="btn sm" data-act="asc-accept" data-locale="${esc(code)}" data-fields="${k}">${icon("check")}Giữ bản ASC</button>` : ""}</div>` : ""}</div>`;
      }).join("")}
      ${r.shots_by_type && Object.keys(r.shots_by_type).length ? Object.entries(r.shots_by_type).map(([dt, info]) => `
      <div class="asc-shot-block" style="margin-top:16px;padding-top:12px;border-top:1px solid var(--border)">
        <div class="section-title" style="margin-top:0"><h2>Screenshot ${esc(info.label)}</h2>
          <span class="sub">${info.local_count} ảnh local${remote ? ` · <span class="fchip s-${info.status}">${ST[info.status]?.[0] || info.status}</span>` : ""}${info.mark ? ` <span class="faint">mốc ${dateVN(info.mark.at)}</span>` : ""}</span>
          <span class="spacer"></span>
          ${remote && ["conflict", "differs"].includes(info.status) ? `<button class="btn sm" data-act="asc-accept" data-locale="${esc(code)}" data-fields="screenshots:${esc(dt)}">${icon("check")}Giữ ảnh ASC</button>` : ""}
          ${remote && info.local_count ? `<button class="btn sm" data-act="asc-shots" data-locale="${esc(code)}" data-display-type="${esc(dt)}" ${info.status === "same" ? "disabled" : ""}>${icon("upload")}${info.status === "same" ? "Ảnh đã khớp" : `Thay screenshot ${esc(info.label)}`}</button>` : ""}
        </div>
        ${remote && ["conflict", "differs", "accepted"].includes(info.status) ? `<div class="small faint" style="margin-bottom:8px">${esc(ST[info.status]?.[1] || "")} So khớp bằng MD5.</div>` : ""}
        ${info.local_shots && info.local_shots.length ? `<div class="shot-strip">${info.local_shots.map((s) => `<a href="/asc-shot?app=${esc(app)}&locale=${encodeURIComponent(code)}&file=${encodeURIComponent(s.file)}" target="_blank"><img loading="lazy" src="/asc-shot?app=${esc(app)}&locale=${encodeURIComponent(code)}&file=${encodeURIComponent(s.file)}" alt="${esc(s.file)}"><span>${esc(s.file)}</span></a>`).join("")}</div>` : `<div class="small muted">Chưa có ảnh local cho ${esc(info.label)}.</div>`}
        ${remote && info.remote_shots && info.remote_shots.length ? `<div class="small faint" style="margin:8px 0 4px">Đang có trên ASC (${info.remote_shots.length} ảnh):</div><div class="shot-strip">${info.remote_shots.map((i) => `<a ${i.url ? `href="${esc(i.url)}" target="_blank"` : ""}>${i.url ? `<img loading="lazy" src="${esc(i.url)}" alt="">` : `<div class="ph"></div>`}<span>${esc(i.file || "")}</span></a>`).join("")}</div>` : ""}
      </div>`).join("") : `
      <div><div class="section-title" style="margin-top:0"><h2>Screenshot</h2><span class="sub">${local.screenshots.length} ảnh local${local.screenshots[0] ? ` · ${local.screenshots[0].width}×${local.screenshots[0].height}` : ""}${remote && local.screenshots.length ? ` · <span class="fchip s-${r.shots_status}">${ST[r.shots_status][0]}</span>` : ""}${shotMark ? ` <span class="faint">mốc ${dateVN(shotMark.at)}</span>` : ""}</span>
        <span class="spacer"></span>${remote && ["conflict", "differs"].includes(r.shots_status) ? `<button class="btn sm" data-act="asc-accept" data-locale="${esc(code)}" data-fields="screenshots">${icon("check")}Giữ ảnh ASC</button>` : ""}
        ${remote && local.screenshots.length ? `<button class="btn sm" data-act="asc-shots" data-locale="${esc(code)}" ${r.shots_status === "same" ? "disabled" : ""}>${icon("upload")}${r.shots_status === "same" ? "Ảnh đã khớp" : "Thay screenshot trên ASC"}</button>` : ""}</div>
        ${remote && ["conflict", "differs", "accepted"].includes(r.shots_status) ? `<div class="small faint" style="margin-bottom:8px">${esc(ST[r.shots_status][1])} So khớp bằng MD5: ảnh export lại, dù trông giống, vẫn tính là khác.</div>` : ""}
        ${local.screenshots.length ? `<div class="shot-strip">${local.screenshots.map((s) => `<a href="/asc-shot?app=${esc(app)}&locale=${encodeURIComponent(code)}&file=${encodeURIComponent(s.file)}" target="_blank"><img loading="lazy" src="/asc-shot?app=${esc(app)}&locale=${encodeURIComponent(code)}&file=${encodeURIComponent(s.file)}" alt="${esc(s.file)}"><span>${esc(s.file)}</span></a>`).join("")}</div>` : `<div class="small muted">Không có ảnh local cho locale này.</div>`}
        ${remote ? `<div><div class="section-title" style="margin-top:12px"><h2>Screenshot trên ASC</h2><span class="sub">version ${esc(remote.version?.version || "—")}</span></div>
        ${rshots.length ? rshots.map(([t, set]) => `<div class="small faint" style="margin-bottom:6px">${esc(t)} · ${set.items.length} ảnh</div><div class="shot-strip">${set.items.map((i) => `<a ${i.url ? `href="${esc(i.url)}" target="_blank"` : ""}>${i.url ? `<img loading="lazy" src="${esc(i.url)}" alt="">` : `<div class="ph"></div>`}<span>${esc(i.file || "")}</span></a>`).join("")}</div>`).join("") : `<div class="small muted">Version này chưa có screenshot cho ${esc(code)}.</div>`}</div>` : ""}
      </div>`}
    </div></div>`;
  layer.hidden = false;
}

async function ascPush(locales, btn) {
  const rows = ui.asc.data.compare.rows;
  const items = locales.map((c) => rows.find((r) => r.locale === c)).filter(Boolean).map((r) => {
    const fields = ascPushable(r);
    return { locale: r.locale, fields, override: fields.filter((k) => OVERRIDE.has(r.fields[k].status)) };
  }).filter((i) => i.fields.length);
  if (!items.length) return toast("Không có field nào cần đẩy", "err", "Field phải ASC trống hoặc local mới hơn (hoặc được tick ghi đè), trong giới hạn và đang sửa được.");
  const r = await busy(btn, () => api("/api/appstore/metadata", { method: "POST", body: { app: ui.asc.app, items, dry_run: true } }));
  if (!r.ops.length) return toast("ASC đã khớp, không còn gì để đẩy");
  ui.asc.pending = items;
  const create = r.ops.filter((o) => o.op === "create").length;
  const overrides = items.reduce((a, i) => a + i.override.length, 0);
  openModal(`<div class="modal-head"><h2>Đẩy metadata lên App Store Connect</h2><button type="button" class="icon-btn" data-act="close-modal">${icon("x")}</button></div>
    <div class="modal-body stack">
      <div class="small muted">Version <b>${esc(r.version?.version || "—")}</b> (${esc(r.version?.state || "")}). ${r.ops.length} lệnh${create ? `, trong đó <b>${create}</b> tạo ngôn ngữ mới` : ""}. Danh sách lập từ lần đọc ASC ngay lúc này; field đã khớp được bỏ qua.</div>
      <div class="table-wrap" style="max-height:46vh"><table><thead><tr><th>Locale</th><th>Phần</th><th>Lệnh</th><th>Field</th></tr></thead><tbody>
      ${r.ops.map((o) => { const item = items.find((i) => i.locale === o.locale); return `<tr><td><b>${esc(o.locale)}</b></td><td class="small">${o.resource === "info" ? "App Information" : "Version"}</td><td>${o.op === "create" ? '<span class="pill warn" style="height:20px">Tạo</span>' : '<span class="pill" style="height:20px">Sửa</span>'}</td><td class="small">${o.fields.map((k) => FIELD_LABEL[k] + (item?.override.includes(k) ? ' <b style="color:var(--warn)">(ghi đè)</b>' : "")).join(", ")}</td></tr>`; }).join("")}
      </tbody></table></div>
      ${overrides ? `<div class="callout warn">${icon("alert")}<div><b>${overrides}</b> field sẽ thay nội dung đang có trên ASC mà không do dashboard đẩy (có thể bạn đã sửa tay).</div></div>` : ""}
      <div class="callout">${icon("info")}<div>Chỉ ghi nội dung listing. Không submit review, không đổi giá, không phát hành.</div></div></div>
    <div class="modal-foot"><button type="button" class="btn ghost" data-act="close-modal">Huỷ</button><button class="btn primary" data-act="asc-push-go">${icon("upload")}Đẩy ${r.ops.length} thay đổi</button></div>`);
}
async function ascPushGo(btn) {
  const r = await busy(btn, () => api("/api/appstore/metadata", { method: "POST", body: { app: ui.asc.app, items: ui.asc.pending, dry_run: false } }));
  closeLayer("#modal"); ui.asc.sel.clear(); ui.asc.override.clear();
  toast(`Đã đẩy ${r.done.length} thay đổi lên App Store Connect`);
  await ascLoad(false);
}
async function ascShots(locale, btn, displayType) {
  const row = ui.asc.data.compare.rows.find((r) => r.locale === locale);
  const stInfo = displayType && row?.shots_by_type ? row.shots_by_type[displayType] : null;
  const override = OVERRIDE.has(stInfo?.status || row?.shots_status);
  const r = await busy(btn, () => api("/api/appstore/screenshots", { method: "POST", body: { app: ui.asc.app, locale, display_type: displayType || null, dry_run: true, override } }));
  const p = r.plan;
  if (p.unchanged) return toast(`${locale} (${p.label}): screenshot trên ASC đã giống hệt local`);
  openModal(`<div class="modal-head"><h2>Thay screenshot · ${esc(locale)} (${esc(p.label)})</h2><button type="button" class="icon-btn" data-act="close-modal">${icon("x")}</button></div>
    <div class="modal-body stack">
      <div>Bộ <b>${esc(p.label)}</b> (${esc(p.display_type)}): ${p.delete.length ? `xoá <b>${p.delete.length}</b> ảnh đang có trên ASC, ` : ""}upload <b>${p.upload.length}</b> ảnh local theo đúng thứ tự.</div>
      ${p.remote_files.length ? `<div class="small faint">Đang có: ${esc(p.remote_files.join(", "))}</div>` : ""}
      <div class="shot-strip">${p.upload.map((s) => `<a><img src="/asc-shot?app=${esc(ui.asc.app)}&locale=${encodeURIComponent(locale)}&file=${encodeURIComponent(s.file)}" alt=""><span>${esc(s.file)}</span></a>`).join("")}</div>
      ${override ? `<div class="callout warn">${icon("alert")}<div>Ảnh trên ASC <b>${esc(ST[p.status][0].toLowerCase())}</b>: không do dashboard đẩy, có thể bạn đã upload tay. Bấm thay là ghi đè.</div></div>` : ""}
      <div class="callout warn">${icon("alert")}<div>Ảnh cũ bị xoá trước (mỗi bộ tối đa 10 ảnh). Nếu upload hỏng giữa chừng, bấm lại để chạy tiếp; bản gốc vẫn ở repo app.</div></div></div>
    <div class="modal-foot"><button type="button" class="btn ghost" data-act="close-modal">Huỷ</button><button class="btn primary" data-act="asc-shots-go" data-locale="${esc(locale)}" data-display-type="${esc(p.display_type)}" data-override="${override ? 1 : ""}">${icon("upload")}Thay ${p.upload.length} ảnh ${esc(p.label)}</button></div>`);
}
async function ascShotsGo(locale, override, btn, displayType) {
  const r = await busy(btn, () => api("/api/appstore/screenshots", { method: "POST", body: { app: ui.asc.app, locale, display_type: displayType || null, dry_run: false, override } }));
  closeLayer("#modal");
  toast(`${locale}: đã upload ${r.uploaded} ảnh, xoá ${r.deleted} ảnh cũ`, "ok", "Apple còn xử lý ảnh vài phút trước khi hiện trong App Store Connect.");
  await ascLoad(false);
}

function ascBulkShots() {
  const d = ui.asc.data;
  if (!d?.remote) return toast("Cần tải dữ liệu từ App Store Connect trước", "err");
  const rows = d.compare.rows;
  const targetLocales = ui.asc.sel.size ? ui.asc.sel : null;
  const sets = ascShotsSets(rows, targetLocales);
  if (!sets.length) return toast("Không có bộ screenshot local nào để đẩy", "err");

  ui.asc.bulkSets = sets;
  const v = d.remote.version;
  const app = S.appstore.apps.find((a) => a.id === ui.asc.app);

  const initialCheckedCount = sets.filter((s) => s.status !== "same" && s.remote_exists).length;
  const hasOverride = sets.some((s) => OVERRIDE.has(s.status));

  const html = `
    <div class="modal-head">
      <h2>Đẩy screenshot hàng loạt</h2>
      <button type="button" class="icon-btn" data-act="close-modal" id="bulk-close-btn">${icon("x")}</button>
    </div>
    <div class="modal-body stack">
      <div class="small muted">
        App <b>${esc(app?.name || ui.asc.app)}</b> · Version <b>${esc(v?.version || "—")}</b> (${esc(v?.state || "")}). 
        Upload lần lượt từng bộ ảnh (5–15 giây/bộ do Apple xử lý). Có thể bấm <b>Dừng lại</b> bất kỳ lúc nào mà không mất các bộ đã đẩy xong.
      </div>

      <div class="row small" style="gap:8px;flex-wrap:wrap">
        <button type="button" class="btn sm ghost" data-act="bulk-sel" data-which="all">Chọn tất cả</button>
        <button type="button" class="btn sm ghost" data-act="bulk-sel" data-which="todo">Chỉ bộ cần đẩy</button>
        <button type="button" class="btn sm ghost" data-act="bulk-sel" data-which="iphone">Chỉ iPhone</button>
        <button type="button" class="btn sm ghost" data-act="bulk-sel" data-which="ipad">Chỉ iPad</button>
        <button type="button" class="btn sm ghost" data-act="bulk-sel" data-which="none">Bỏ chọn</button>
        <span class="spacer"></span>
        <label class="ov-pick small"><input type="checkbox" id="bulk-override-toggle" ${hasOverride ? "checked" : ""}> Ghi đè bộ ASC khác biệt</label>
      </div>

      <div id="bulk-progress-wrap" class="bulk-progress" style="display:none">
        <div class="row small"><b id="bulk-status-text">Đang chuẩn bị...</b><span class="spacer"></span><span id="bulk-count-text" class="faint">0 / 0</span></div>
        <div class="progress-track"><div id="bulk-progress-bar" class="progress-fill" style="width:0%"></div></div>
      </div>

      <div class="table-wrap" style="max-height:48vh;border:1px solid var(--border);border-radius:var(--r-md)">
        <table>
          <thead>
            <tr>
              <th style="width:36px"><input type="checkbox" id="bulk-check-all" ${initialCheckedCount === sets.filter(s => s.remote_exists).length && initialCheckedCount > 0 ? "checked" : ""}></th>
              <th>Locale</th>
              <th>Thiết bị</th>
              <th>Ảnh local</th>
              <th>Trạng thái ASC</th>
              <th style="width:140px">Tiến trình</th>
            </tr>
          </thead>
          <tbody id="bulk-tbody">
            ${sets.map((s) => {
              const checked = s.status !== "same" && s.remote_exists;
              return `<tr data-bulk-key="${esc(s.key)}" class="${checked ? "on" : ""}">
                <td><input type="checkbox" class="bulk-item-check" data-key="${esc(s.key)}" ${checked ? "checked" : ""} ${s.remote_exists ? "" : "disabled"}></td>
                <td><b>${esc(s.locale)}</b>${s.tier ? ` <span class="tag">T${s.tier}</span>` : ""}</td>
                <td>${esc(s.label)}</td>
                <td class="small">${s.local_count} ảnh</td>
                <td>${s.remote_exists ? `<span class="fchip s-${s.status}">${esc(ST[s.status]?.[0] || s.status)}</span>` : '<span class="pill warn" style="height:20px" title="Version trên ASC chưa có locale này. Cần đẩy metadata trước.">Chưa có metadata</span>'}</td>
                <td class="small bulk-item-status" data-key="${esc(s.key)}"><span class="faint">Chờ</span></td>
              </tr>`;
            }).join("")}
          </tbody>
        </table>
      </div>

      <div class="callout small" style="margin-top:2px">
        ${icon("info")}<div>Ảnh cũ của bộ được thay sẽ xoá trước khi upload ảnh mới. Bản gốc luôn an toàn trong repo máy bạn.</div>
      </div>
    </div>
    <div class="modal-foot">
      <span id="bulk-summary" class="small faint" style="margin-right:auto">Đã chọn <b>${initialCheckedCount}</b> / ${sets.length} bộ</span>
      <button type="button" class="btn ghost" data-act="close-modal" id="bulk-cancel-btn">Huỷ</button>
      <button type="button" class="btn bad" data-act="asc-bulk-stop" id="bulk-stop-btn" style="display:none">${icon("x")}Dừng lại</button>
      <button type="button" class="btn primary" data-act="asc-bulk-start" id="bulk-start-btn" ${initialCheckedCount ? "" : "disabled"}>${icon("upload")}Bắt đầu đẩy (${initialCheckedCount} bộ)</button>
      <button type="button" class="btn primary" data-act="asc-bulk-done" id="bulk-done-btn" style="display:none">${icon("check")}Đóng & Cập nhật</button>
    </div>
  `;
  openModal(html, "wide");
}

function updateBulkSummary() {
  const checks = Array.from(document.querySelectorAll(".bulk-item-check:not(:disabled)"));
  const checked = checks.filter((c) => c.checked);
  const n = checked.length;
  const total = ui.asc.bulkSets ? ui.asc.bulkSets.length : checks.length;
  const sumEl = $("#bulk-summary");
  if (sumEl) sumEl.innerHTML = `Đã chọn <b>${n}</b> / ${total} bộ`;
  const btn = $("#bulk-start-btn");
  if (btn) {
    btn.innerHTML = `${icon("upload")}Bắt đầu đẩy (${n} bộ)`;
    btn.disabled = n === 0;
  }
  const allBox = $("#bulk-check-all");
  if (allBox && checks.length) {
    allBox.checked = n === checks.length;
    allBox.indeterminate = n > 0 && n < checks.length;
  }
  document.querySelectorAll("#bulk-tbody tr").forEach((tr) => {
    const ch = tr.querySelector(".bulk-item-check");
    if (ch) tr.classList.toggle("on", ch.checked);
  });
}

function ascBulkSelect(which) {
  if (ui.asc.bulkRunning) return;
  const sets = ui.asc.bulkSets || [];
  document.querySelectorAll(".bulk-item-check").forEach((ch) => {
    if (ch.disabled) return;
    const key = ch.dataset.key;
    const s = sets.find((item) => item.key === key);
    if (!s) return;
    let ok = false;
    if (which === "all") ok = true;
    else if (which === "none") ok = false;
    else if (which === "todo") ok = s.status !== "same";
    else if (which === "iphone") ok = s.display_type === "APP_IPHONE_67";
    else if (which === "ipad") ok = s.display_type === "APP_IPAD_PRO_3GEN_129";
    ch.checked = ok;
  });
  updateBulkSummary();
}

async function ascBulkStart(btn) {
  const checks = Array.from(document.querySelectorAll(".bulk-item-check:checked"));
  const sets = ui.asc.bulkSets || [];
  const queue = checks.map((c) => sets.find((s) => s.key === c.dataset.key)).filter(Boolean);
  if (!queue.length) return toast("Chưa chọn bộ screenshot nào", "err");

  ui.asc.bulkRunning = true;
  ui.asc.bulkCancel = false;

  const closeBtn = $("#bulk-close-btn");
  if (closeBtn) closeBtn.disabled = true;
  const cancelBtn = $("#bulk-cancel-btn");
  if (cancelBtn) cancelBtn.style.display = "none";
  if (btn) btn.style.display = "none";
  const stopBtn = $("#bulk-stop-btn");
  if (stopBtn) {
    stopBtn.style.display = "";
    stopBtn.disabled = false;
    stopBtn.innerHTML = `${icon("x")}Dừng lại`;
  }
  document.querySelectorAll(".bulk-item-check, [data-act='bulk-sel'], #bulk-check-all, #bulk-override-toggle").forEach((el) => { el.disabled = true; });
  const progWrap = $("#bulk-progress-wrap");
  if (progWrap) progWrap.style.display = "";

  const override = $("#bulk-override-toggle")?.checked ?? true;
  let success = 0, failed = 0;
  const total = queue.length;

  for (let i = 0; i < total; i++) {
    if (ui.asc.bulkCancel) break;

    const item = queue[i];
    const rowEl = document.querySelector(`tr[data-bulk-key="${item.key}"]`);
    const statusCell = document.querySelector(`td.bulk-item-status[data-key="${item.key}"]`);

    const pct = Math.round((i / total) * 100);
    const bar = $("#bulk-progress-bar");
    if (bar) bar.style.width = `${pct}%`;
    const countText = $("#bulk-count-text");
    if (countText) countText.textContent = `${i + 1} / ${total} (${pct}%)`;
    const statusText = $("#bulk-status-text");
    if (statusText) statusText.innerHTML = `<span class="spinner"></span>Đang upload <b>${esc(item.locale)}</b> · ${esc(item.label)}…`;
    if (statusCell) statusCell.innerHTML = `<span class="pill" style="color:var(--accent)"><span class="spinner"></span>Upload…</span>`;
    if (rowEl) rowEl.scrollIntoView({ block: "nearest", behavior: "smooth" });

    try {
      const res = await api("/api/appstore/screenshots", {
        method: "POST",
        body: {
          app: ui.asc.app,
          locale: item.locale,
          display_type: item.display_type,
          dry_run: false,
          override: override,
        },
      });
      success++;
      if (statusCell) statusCell.innerHTML = `<span class="pill good">${icon("check")}Xong (${res.uploaded || item.local_count})</span>`;
    } catch (err) {
      failed++;
      if (statusCell) statusCell.innerHTML = `<span class="pill bad" title="${esc(err.message)}">${icon("x")}Lỗi: ${esc(err.message)}</span>`;
    }

    if (i < total - 1 && !ui.asc.bulkCancel) {
      await new Promise((r) => setTimeout(r, 400));
    }
  }

  ui.asc.bulkRunning = false;
  if (stopBtn) stopBtn.style.display = "none";
  const doneBtn = $("#bulk-done-btn");
  if (doneBtn) doneBtn.style.display = "";
  if (closeBtn) closeBtn.disabled = false;

  const bar = $("#bulk-progress-bar");
  const countText = $("#bulk-count-text");
  const statusText = $("#bulk-status-text");

  if (ui.asc.bulkCancel) {
    if (statusText) statusText.innerHTML = `Đã dừng. Đã upload <b>${success}</b> / ${total} bộ.${failed ? ` (${failed} lỗi)` : ""}`;
    toast(`Đã dừng upload: ${success} bộ thành công`, "warn");
  } else {
    if (bar) bar.style.width = "100%";
    if (countText) countText.textContent = `${total} / ${total} (100%)`;
    if (statusText) statusText.innerHTML = `Hoàn tất! Đã upload <b>${success}</b> / ${total} bộ.${failed ? ` (${failed} lỗi)` : ""}`;
    toast(`Đã đẩy ${success}/${total} bộ screenshot`, failed ? "warn" : "ok", "Apple mất vài phút để xử lý và hiện ảnh trên store.");
  }
}

function ascBulkStop() {
  ui.asc.bulkCancel = true;
  const btn = $("#bulk-stop-btn");
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span>Đang dừng...`;
  }
}
async function ascAccept(locale, fields, btn) {
  await busy(btn, () => api("/api/appstore/accept", { method: "POST", body: { app: ui.asc.app, locale, fields } }));
  fields.forEach((k) => ui.asc.override.delete(ascKey(locale, k)));
  toast(`${locale}: giữ bản ASC cho ${fields.map((k) => FIELD_LABEL[k]).join(", ")}`);
  await ascLoad(false);
}
async function ascImport(btn) {
  const app = S.appstore.apps.find((a) => a.id === ui.asc.app);
  if (!confirm(`Ghi listing đang có trên App Store Connect vào repo ${app.repo_path || app.repo}?\nChỉ tạo file cho ngôn ngữ chưa có; không ghi đè file nào.`)) return;
  const r = await busy(btn, () => api("/api/appstore/import", { method: "POST", body: { app: ui.asc.app } }));
  toast(`Đã nhập ${r.created.length} ngôn ngữ vào ${r.folder}`, "ok", r.skipped.length ? `Giữ nguyên ${r.skipped.length} file đã có: ${r.skipped.join(", ")}` : "");
  ui.asc.data = null;
  await load({ quiet: true });
}
async function ascDiscover(btn) {
  const r = await busy(btn, () => api("/api/appstore/discover", { method: "POST", body: {} }));
  openModal(`<div class="modal-head"><h2>App trên App Store Connect</h2><button type="button" class="icon-btn" data-act="close-modal">${icon("x")}</button></div>
    <div class="modal-body stack"><div class="small muted">Mọi app của team. Liên kết để quản lý listing trên dashboard; repo được đoán theo bundle id trong <code>~/personal/Apps</code>.</div>
    <div class="table-wrap"><table><thead><tr><th>App</th><th>Bundle ID</th><th>Repo</th><th></th></tr></thead><tbody>
    ${r.apps.map((a) => `<tr><td><b>${esc(a.name)}</b><div class="small faint">${esc(a.app_store_id)}</div></td><td><code class="small">${esc(a.bundle_id)}</code></td>
      <td class="small">${a.repo ? `<code>${esc(a.repo)}</code>` : '<span class="faint">không thấy</span>'}</td>
      <td class="nowrap">${a.linked ? '<span class="pill good">Đã liên kết</span>' : `<button class="btn sm ${a.registry_id ? "primary" : ""}" data-act="asc-link" data-id="${esc(a.app_store_id)}">${icon(a.registry_id ? "link" : "plus")}${a.registry_id ? "Liên kết " + esc(a.registry_id) : "Thêm"}</button>`}</td></tr>`).join("")}
    </tbody></table></div></div>
    <div class="modal-foot"><button type="button" class="btn ghost" data-act="close-modal">Đóng</button></div>`);
}

function ascProducts(st, linked) {
  const p = ui.asc.products;
  const intro = `<div class="callout" style="margin-bottom:14px">${icon("info")}<div>Chỉ đọc: gói subscription và IAP của app, giá ở storefront Mỹ. Tạo gói và đổi giá theo nước chưa làm ở đây; làm trong App Store Connect.</div></div>`;
  if (!st.configured || !linked) return intro + `<div class="card">${emptyState("tag2", st.configured ? "App chưa liên kết App Store Connect" : "Cần API key", st.configured ? "Liên kết app qua nút App trên ASC." : "Kết nối App Store Connect API ở trên để xem gói giá.")}</div>`;
  if (!p) return intro + `<div class="card">${emptyState("tag2", "Chưa tải gói giá", "Đọc subscription group, subscription và IAP từ App Store Connect.", `<button class="btn primary" data-act="asc-products">${icon("download")}Tải gói giá</button>`)}</div>`;
  const price = (x) => x?.price ? `$${esc(x.price)}<div class="small faint">bạn nhận $${esc(x.proceeds ?? "—")}</div>` : '<span class="faint">—</span>';
  return intro + `<div class="row" style="margin-bottom:10px"><span class="spacer"></span><button class="btn sm" data-act="asc-products">${icon("refresh")}Tải lại</button></div>
  ${p.groups.map((g) => `<div class="card" style="margin-bottom:14px"><div class="card-head"><h3>${esc(g.name)}</h3><span class="sub">subscription group</span></div><div class="table-wrap"><table><thead><tr><th>Gói</th><th>Product ID</th><th>Chu kỳ</th><th>Trạng thái</th><th class="num">Giá (US)</th></tr></thead><tbody>
    ${g.subscriptions.map((s) => `<tr><td><b>${esc(s.name)}</b></td><td><code>${esc(s.product_id)}</code></td><td class="small">${esc((s.period || "").replaceAll("_", " ").toLowerCase())}</td><td>${stPill(s.state, false)}</td><td class="num">${price(s.price)}</td></tr>`).join("")}
  </tbody></table></div></div>`).join("")}
  <div class="card"><div class="card-head"><h3>In-App Purchase</h3><span class="sub">${p.iaps.length} sản phẩm</span></div>${p.iaps.length ? `<div class="table-wrap"><table><thead><tr><th>Tên</th><th>Product ID</th><th>Loại</th><th>Trạng thái</th></tr></thead><tbody>
    ${p.iaps.map((i) => `<tr><td><b>${esc(i.name)}</b></td><td><code>${esc(i.product_id)}</code></td><td class="small">${esc((i.type || "").replaceAll("_", " ").toLowerCase())}</td><td>${stPill(i.state, false)}</td></tr>`).join("")}
  </tbody></table></div>` : `<div class="card-body small muted">Không có IAP.</div>`}</div>`;
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
function openModal(html, cls = "") {
  const m = $("#modal");
  m.innerHTML = `<div class="modal ${cls}" role="dialog">${html}</div>`;
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
    else if (key === "asc") ui.asc.filter = seg.dataset.val;
    else if (key === "hookMetric") ui.hookMetric = seg.dataset.val;
    else ui.filter[key] = seg.dataset.val;
    return render();
  }
  if (e.target.classList.contains("drawer-layer")) { location.hash = `#/${current().route.path}`; return; }
  if (e.target.classList.contains("modal-layer")) { if (!ui.asc.bulkRunning) closeLayer("#modal"); return; }
  const btn = e.target.closest("[data-act]");
  if (!btn) return;
  const a = btn.dataset;
  if (btn.tagName === "A") e.preventDefault();
  try {
    switch (a.act) {
      case "close-drawer": location.hash = `#/${current().route.path}`; break;
      case "asc-refresh": await ascLoad(true, btn); break;
      case "asc-app": ui.asc.app = a.app; ui.asc.data = null; ui.asc.error = null; ui.asc.products = null; ui.asc.sel.clear(); ui.asc.override.clear(); ui.asc.bulkRunning = false; ui.asc.bulkCancel = false; render(); break;
      case "asc-tab": ui.asc.tab = a.tab; render(); break;
      case "asc-sel-all": ascVisible().forEach((r) => ui.asc.sel.add(r.locale)); render(); break;
      case "asc-sel-none": ui.asc.sel.clear(); render(); break;
      case "asc-sel-changed": ui.asc.sel = new Set(ascVisible().filter((r) => ascAuto(r).length).map((r) => r.locale)); render(); break;
      case "asc-push": await ascPush(a.locale ? [a.locale] : [...ui.asc.sel], btn); break;
      case "asc-push-go": await ascPushGo(btn); break;
      case "asc-shots": await ascShots(a.locale, btn, a.displayType); break;
      case "asc-shots-go": await ascShotsGo(a.locale, !!a.override, btn, a.displayType); break;
      case "asc-bulk-shots": ascBulkShots(); break;
      case "asc-bulk-start": await ascBulkStart(btn); break;
      case "asc-bulk-stop": ascBulkStop(); break;
      case "asc-bulk-done": closeLayer("#modal"); await ascLoad(false); break;
      case "bulk-sel": ascBulkSelect(btn.dataset.which); break;
      case "asc-accept": await ascAccept(a.locale, a.fields.split(","), btn); break;
      case "asc-import": await ascImport(btn); break;
      case "asc-discover": await ascDiscover(btn); break;
      case "asc-link": {
        const r = await busy(btn, () => api("/api/appstore/link", { method: "POST", body: { app_store_id: a.id } }));
        closeLayer("#modal"); S.appstore = r.status; ui.asc.app = r.app; ui.asc.data = null; render();
        toast(`Đã liên kết ${r.app} với App Store Connect`, "ok", "Đã ghi docs/apps/registry.json"); break;
      }
      case "asc-products": {
        ui.asc.products = await busy(btn, () => api("/api/appstore/products", { method: "POST", body: { app: ui.asc.app } }));
        render(); break;
      }
      case "close-modal":
        if (!ui.asc.bulkRunning) {
          closeLayer("#modal");
          if ($("#bulk-done-btn") && $("#bulk-done-btn").style.display !== "none") await ascLoad(false);
        }
        break;
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
  if (e.target.id === "asc-q") {
    ui.asc.q = e.target.value;
    const pos = e.target.selectionStart;
    render();
    const q = $("#asc-q"); q.focus(); q.setSelectionRange(pos, pos);
  }
});
document.addEventListener("change", (e) => {
  if (e.target.id === "bulk-check-all") {
    const val = e.target.checked;
    document.querySelectorAll(".bulk-item-check:not(:disabled)").forEach((ch) => { ch.checked = val; });
    updateBulkSummary();
    return;
  }
  if (e.target.classList.contains("bulk-item-check")) {
    updateBulkSummary();
    return;
  }
  if (e.target.dataset.ascSel) { e.target.checked ? ui.asc.sel.add(e.target.dataset.ascSel) : ui.asc.sel.delete(e.target.dataset.ascSel); render(); }
  if (e.target.dataset.ascOv) {
    e.target.checked ? ui.asc.override.add(e.target.dataset.ascOv) : ui.asc.override.delete(e.target.dataset.ascOv);
    const top = $(".drawer-body")?.scrollTop || 0;
    render();
    const body = $(".drawer-body");
    if (body) body.scrollTop = top;
    return;
  }
  if (e.target.dataset.ascField) { e.target.checked ? ui.asc.fields.add(e.target.dataset.ascField) : ui.asc.fields.delete(e.target.dataset.ascField); render(); }
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
  if (e.key === "Escape") {
    if (!$("#modal").hidden) {
      if (!ui.asc.bulkRunning) closeLayer("#modal");
    } else if (!$("#drawer").hidden) {
      location.hash = `#/${current().route.path}`;
    }
  }
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
