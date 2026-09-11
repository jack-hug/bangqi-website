/* ============================================================
 * 邦琪药业 - 后台管理 SPA
 * ============================================================ */

// ---- 色块选项 ----
const COLORS = [
  {v: "ph-green", t: "玉绿"}, {v: "ph-ta", t: "青苔"}, {v: "ph-am", t: "琥珀"},
  {v: "ph-li", t: "青莲"}, {v: "ph-ti", t: "青黛"}, {v: "ph-gy", t: "灰绿"},
  {v: "ph-gr", t: "翠绿"}, {v: "ph-cp", t: "铜绿"}, {v: "ph-pi", t: "黛紫"},
  {v: "ph-gray", t: "浅灰"},
];

// Dropzone 手动初始化，禁用自动发现
if (typeof Dropzone !== "undefined") Dropzone.autoDiscover = false;

// ---- 资源配置 ----
const RESOURCES = {
  banner: {
    name: "Banner轮播", endpoint: "/api/banner",
    fields: [
      {k: "kicker", l: "标签文字", t: "text"},
      {k: "title", l: "主标题（支持<br>换行）", t: "text"},
      {k: "subtitle", l: "副标题", t: "text"},
      {k: "btn_text", l: "按钮文字", t: "text"},
      {k: "btn_link", l: "按钮链接", t: "text"},
      {k: "image", l: "Banner图片（1920×750）", t: "image"},
      {k: "color", l: "占位图颜色", t: "select", opts: COLORS},
      {k: "sort_order", l: "排序", t: "number", def: 0},
      {k: "is_active", l: "启用", t: "checkbox", def: true},
    ],
    cols: ["image", "kicker", "title", "color", "sort_order", "is_active"],
    search: ["kicker", "title", "subtitle"],
  },
  "home-stat": {
    name: "首页统计", endpoint: "/api/home-stat",
    fields: [
      {k: "label", l: "标签名称", t: "text"},
      {k: "value", l: "数值", t: "text"},
      {k: "unit", l: "单位", t: "text"},
      {k: "sort_order", l: "排序", t: "number", def: 0},
    ],
    cols: ["label", "value", "unit", "sort_order"],
  },
  "company-image": {
    name: "厂区图片", endpoint: "/api/company-image",
    fields: [
      {k: "title", l: "图片标题", t: "text"},
      {k: "image", l: "厂区图片（960×540）", t: "image"},
      {k: "color", l: "占位图颜色", t: "select", opts: COLORS},
      {k: "sort_order", l: "排序", t: "number", def: 0},
      {k: "is_active", l: "启用", t: "checkbox", def: true},
    ],
    cols: ["image", "title", "color", "sort_order", "is_active"],
  },
  "enterprise-card": {
    name: "企业卡片", endpoint: "/api/enterprise-card",
    fields: [
      {k: "title", l: "卡片标题", t: "text"},
      {k: "description", l: "描述文字", t: "text"},
      {k: "link", l: "跳转链接", t: "text"},
      {k: "image", l: "卡片图片（370×650）", t: "image"},
      {k: "color", l: "占位图颜色", t: "select", opts: COLORS},
      {k: "sort_order", l: "排序", t: "number", def: 0},
    ],
    cols: ["image", "title", "description", "color", "sort_order"],
  },
  "dosage-form": {
    name: "剂型管理", endpoint: "/api/dosage-form",
    fields: [
      {k: "name", l: "剂型名称", t: "text"},
      {k: "description", l: "剂型简介", t: "text"},
      {k: "image", l: "剂型图片（推荐 450×600，比例 3:4）", t: "image"},
      {k: "sort_order", l: "排序", t: "number", def: 0},
    ],
    cols: ["name", "description", "image", "sort_order"],
  },
  trademark: {
    name: "商标管理", endpoint: "/api/trademark",
    fields: [
      {k: "name", l: "商标名称", t: "text"},
      {k: "sort_order", l: "排序", t: "number", def: 0},
    ],
    cols: ["name", "sort_order"],
  },
  "func-category": {
    name: "功能分类", endpoint: "/api/func-category",
    fields: [
      {k: "name", l: "功能名称", t: "text"},
      {k: "sort_order", l: "排序", t: "number", def: 0},
    ],
    cols: ["name", "sort_order"],
  },
  manufacturer: {
    name: "生产企业", endpoint: "/api/manufacturer",
    fields: [
      {k: "name", l: "企业名称", t: "text", required: true},
      {k: "description", l: "企业简介", t: "textarea"},
      {k: "sort_order", l: "排序", t: "number", def: 0},
    ],
    cols: ["name", "description", "sort_order"],
    search: ["name", "description"],
  },
  product: {
    name: "产品管理", endpoint: "/api/product",
    fields: [
      {k: "name", l: "产品名称", t: "text", required: true},
      {k: "code", l: "产品编号（SKU，批量上传匹配键）", t: "text", placeholder: "例：BQ-001"},
      {k: "manufacturer_id", l: "生产企业", t: "fk", fk: "manufacturer", fkLabel: "name"},
      {k: "dosage_form_id", l: "剂型", t: "fk", fk: "dosage-form", fkLabel: "name"},
      {k: "trademark_id", l: "商标", t: "fk", fk: "trademark", fkLabel: "name"},
      {k: "func_category_id", l: "功能分类", t: "fk", fk: "func-category", fkLabel: "name"},
      {k: "spec", l: "规格", t: "text"},
      {k: "image", l: "产品主图（480×320）", t: "image"},
      {k: "indications", l: "功能主治", t: "textarea"},
      {k: "usage", l: "用法用量", t: "textarea"},
      {k: "content", l: "产品介绍（图文编辑，可插入图片）", t: "richtext"},
      {k: "date", l: "发布日期", t: "date"},
      {k: "clicks", l: "点击量", t: "number", def: 0},
      {k: "color", l: "占位图颜色", t: "select", opts: COLORS},
    ],
    cols: ["image", "name", "manufacturer", "form", "trademark", "func", "spec", "clicks"],
    search: ["name", "spec", "form", "trademark", "func", "manufacturer", "indications"],
  },
  "product-image": {
    name: "产品图片", endpoint: "/api/product-image",
    fields: [
      {k: "product_id", l: "所属产品", t: "fk", fk: "product", fkLabel: "name", required: true},
      {k: "title", l: "图片标题（如：包装实拍）", t: "text"},
      {k: "image", l: "产品图片（640×640）", t: "image"},
      {k: "color", l: "占位图颜色", t: "select", opts: COLORS},
      {k: "sort_order", l: "排序", t: "number", def: 0},
    ],
    cols: ["image", "product_id", "title", "sort_order"],
    search: ["title", "product_name"],
  },
  "news-category": {
    name: "新闻分类", endpoint: "/api/news-category",
    fields: [
      {k: "name", l: "分类名称", t: "text"},
      {k: "sort_order", l: "排序", t: "number", def: 0},
    ],
    cols: ["name", "sort_order"],
  },
  news: {
    name: "新闻文章", endpoint: "/api/news",
    fields: [
      {k: "title", l: "文章标题", t: "text", required: true},
      {k: "category_id", l: "新闻分类", t: "fk", fk: "news-category", fkLabel: "name"},
      {k: "image", l: "文章配图（960×520）", t: "image"},
      {k: "content", l: "文章内容（图文编辑，可插入图片）", t: "richtext"},
      {k: "date", l: "发布日期", t: "date"},
      {k: "clicks", l: "点击量", t: "number", def: 0},
    ],
    cols: ["image", "title", "category", "date", "clicks"],
    search: ["title", "category", "content"],
  },
};

// ---- 侧边栏菜单 ----
const MENU = [
  {id: "dashboard", icon: "▦", label: "仪表盘", type: "dashboard"},
  {group: "首页配置", items: [
    {id: "banner", icon: "▣", label: "Banner轮播"},
    {id: "home-stat", icon: "◉", label: "首页统计"},
    {id: "company-image", icon: "▣", label: "厂区图片"},
    {id: "enterprise-card", icon: "▣", label: "企业卡片"},
  ]},
  {group: "产品管理", items: [
    {id: "product", icon: "⬚", label: "产品列表"},
    {id: "product-image", icon: "▣", label: "产品图片"},
    {id: "batch-product", icon: "⇪", label: "批量上传产品"},
    {id: "dosage-form", icon: "▸", label: "剂型管理"},
    {id: "trademark", icon: "▸", label: "商标管理"},
    {id: "func-category", icon: "▸", label: "功能分类"},
    {id: "manufacturer", icon: "⌂", label: "生产企业"},
  ]},
  {group: "资讯管理", items: [
    {id: "news", icon: "✎", label: "文章列表"},
    {id: "news-category", icon: "▸", label: "新闻分类"},
  ]},
  {group: "栏目管理", items: [
    {id: "page-about", icon: "▤", label: "公司介绍"},
    {id: "page-research", icon: "▤", label: "研发生产"},
    {id: "page-contact", icon: "▤", label: "联系我们"},
  ]},
  {group: "系统设置", items: [
    {id: "company", icon: "⚙", label: "公司信息"},
  ]},
];

// ---- 全局状态 ----
let state = {
  currentView: "dashboard",
  fkCache: {},
  editingId: null,
  deletingId: null,
  deletingResource: null,
  currentSection: null,
  selectedPageId: null,
  piFilter: "",   // 产品图片管理：按产品筛选
  richTextInstances: {},   // 富文本编辑器实例（key -> Quill）
  pendingRichText: {},     // 待初始化的富文本初始内容（key -> html）
};

let editModal, deleteModal, toastEl;

// ============================================================
// API 辅助
// ============================================================
async function api(method, path, body) {
  const opts = { method, headers: {} };
  if (body !== undefined) {
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(path, opts);
  if (res.status === 401) {
    showLogin();
    throw new Error("未登录");
  }
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "请求失败");
  return data;
}

async function loadFkData() {
  for (const key of ["dosage-form", "trademark", "func-category", "manufacturer", "news-category", "product"]) {
    state.fkCache[key] = await api("GET", `/api/${key}`);
  }
}

// ============================================================
// 认证
// ============================================================
async function checkAuth() {
  try {
    const r = await api("GET", "/api/auth/check");
    if (r.logged_in) {
      state.loggedIn = true;
      document.getElementById("topbarUser").textContent = r.username;
      return true;
    }
  } catch (e) {}
  return false;
}

function hideBootSplash() {
  const s = document.getElementById("bootSplash");
  if (s) s.style.display = "none";
}

function showLogin() {
  state.loggedIn = false;
  hideBootSplash();
  document.getElementById("loginPage").style.display = "flex";
  document.getElementById("adminApp").style.display = "none";
}

function showAdmin() {
  state.loggedIn = true;
  hideBootSplash();
  document.getElementById("loginPage").style.display = "none";
  document.getElementById("adminApp").style.display = "flex";
  buildSidebar();
  navigate("dashboard");
}

async function doLogin() {
  const u = document.getElementById("loginUser").value.trim();
  const p = document.getElementById("loginPass").value.trim();
  const errEl = document.getElementById("loginError");
  errEl.textContent = "";
  if (!u || !p) { errEl.textContent = "请输入用户名和密码"; return; }
  try {
    const r = await api("POST", "/api/login", { username: u, password: p });
    document.getElementById("topbarUser").textContent = r.username;
    await loadFkData();
    showAdmin();
    showToast("登录成功");
  } catch (e) {
    errEl.textContent = "用户名或密码错误";
  }
}

async function doLogout() {
  await api("POST", "/api/logout");
  showLogin();
  document.getElementById("loginUser").value = "";
  document.getElementById("loginPass").value = "";
}

// ============================================================
// 导航
// ============================================================
function buildSidebar() {
  const nav = document.getElementById("sidebarNav");
  nav.innerHTML = "";
  for (const item of MENU) {
    if (item.group) {
      const title = document.createElement("div");
      title.className = "nav-group-title";
      title.textContent = item.group;
      nav.appendChild(title);
      for (const sub of item.items) {
        nav.appendChild(createNavItem(sub));
      }
    } else {
      nav.appendChild(createNavItem(item));
    }
  }
}

function createNavItem(item) {
  const el = document.createElement("div");
  el.className = "nav-item" + (state.currentView === item.id ? " active" : "");
  el.innerHTML = `<span class="nav-icon">${item.icon}</span>${item.label}`;
  el.onclick = () => navigate(item.id);
  return el;
}

function navigate(view) {
  state.currentView = view;
  document.querySelectorAll(".sidebar-nav .nav-item").forEach(el => el.classList.remove("active"));
  const items = document.querySelectorAll(".sidebar-nav .nav-item");
  // rebuild sidebar to update active state
  buildSidebar();
  const pageTitle = document.getElementById("pageTitle");

  if (view === "dashboard") {
    pageTitle.textContent = "仪表盘";
    renderDashboard();
  } else if (view === "company") {
    pageTitle.textContent = "公司信息";
    renderCompanyInfo();
  } else if (view === "batch-product") {
    pageTitle.textContent = "批量上传产品";
    renderBatchUpload();
  } else if (view.startsWith("page-")) {
    const section = view.replace("page-", "");
    const titles = { about: "公司介绍", research: "研发生产", contact: "联系我们" };
    pageTitle.textContent = `栏目管理 - ${titles[section]}`;
    state.currentSection = section;
    state.selectedPageId = null;   // 切换栏目分组时重置选中，避免残留上一分组的栏目
    renderPageManager(section);
  } else if (RESOURCES[view]) {
    pageTitle.textContent = RESOURCES[view].name;
    renderCrudTable(view);
  }
}

// ============================================================
// 仪表盘
// ============================================================
// ============================================================
// 仪表盘
// ============================================================
let DASH_DAYS = 7;                 // 趋势图天数：7 / 30
let DASH_CACHE = {};               // 已加载的仪表盘数据

function timeAgo(str) {
  if (!str) return "—";
  const t = new Date(str.replace(/-/g, "/"));
  const diff = (Date.now() - t.getTime()) / 1000;
  if (isNaN(diff)) return str;
  if (diff < 60) return "刚刚";
  if (diff < 3600) return Math.floor(diff / 60) + " 分钟前";
  if (diff < 86400) return Math.floor(diff / 3600) + " 小时前";
  if (diff < 86400 * 30) return Math.floor(diff / 86400) + " 天前";
  return str.slice(0, 10);
}

/** 手绘 SVG 折线图：PV 面积 + UV 折线，含网格、坐标、悬浮提示 */
function trendChartSVG(series) {
  if (!series || !series.length) return `<div class="dash-empty">暂无访问数据</div>`;
  const W = 920, H = 280, PL = 48, PR = 18, PT = 20, PB = 38;
  const iw = W - PL - PR, ih = H - PT - PB;
  const maxV = Math.max(1, ...series.map(s => Math.max(s.pv, s.uv)));
  const niceMax = (() => {
    const pow = Math.pow(10, Math.floor(Math.log10(maxV)));
    return Math.ceil(maxV / pow) * pow;
  })();
  const step = series.length > 1 ? iw / (series.length - 1) : 0;
  const px = i => PL + (series.length > 1 ? i * step : iw / 2);
  const py = v => PT + ih - (v / niceMax) * ih;

  // 网格 + Y 轴刻度
  let grid = "";
  for (let i = 0; i <= 4; i++) {
    const v = (niceMax / 4) * i;
    const yy = py(v);
    grid += `<line x1="${PL}" y1="${yy}" x2="${W - PR}" y2="${yy}" stroke="#e9edf2" stroke-width="1"/>`;
    grid += `<text x="${PL - 10}" y="${yy + 4}" text-anchor="end" font-size="11" fill="#8a94a6">${Math.round(v)}</text>`;
  }

  const pts = series.map((s, i) => ({ x: px(i), y: py(s.pv), yu: py(s.uv), s }));
  const line = pts.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ");
  const lineU = pts.map(p => `${p.x.toFixed(1)},${p.yu.toFixed(1)}`).join(" ");
  const area = `${PL},${PT + ih} ${line} ${(W - PR)},${PT + ih}`;

  // X 轴标签：7 天全显示，30 天每 5 天显示一次
  const every = series.length > 10 ? 5 : 1;
  let xlabels = "";
  pts.forEach((p, i) => {
    if (i % every !== 0 && i !== series.length - 1) return;
    xlabels += `<text x="${p.x.toFixed(1)}" y="${H - 14}" text-anchor="middle" font-size="11" fill="#8a94a6">${p.s.label}</text>`;
  });

  // 数据点 + 悬浮提示
  let dots = "";
  pts.forEach(p => {
    dots += `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="3.5" fill="#fff" stroke="#1c7a5a" stroke-width="2"><title>${p.s.date} PV ${p.s.pv} / UV ${p.s.uv}</title></circle>`;
    dots += `<circle cx="${p.x.toFixed(1)}" cy="${p.yu.toFixed(1)}" r="3" fill="#fff" stroke="#c98a3c" stroke-width="2"><title>${p.s.date} UV ${p.s.uv}</title></circle>`;
  });

  return `
  <svg viewBox="0 0 ${W} ${H}" class="trend-svg" preserveAspectRatio="xMidYMid meet" role="img">
    <defs>
      <linearGradient id="pvGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#1c7a5a" stop-opacity="0.28"/>
        <stop offset="100%" stop-color="#1c7a5a" stop-opacity="0.02"/>
      </linearGradient>
    </defs>
    ${grid}
    <polygon points="${area}" fill="url(#pvGrad)"/>
    <polyline points="${line}" fill="none" stroke="#1c7a5a" stroke-width="2.4" stroke-linejoin="round"/>
    <polyline points="${lineU}" fill="none" stroke="#c98a3c" stroke-width="2" stroke-dasharray="5 4" stroke-linejoin="round"/>
    ${dots}
    ${xlabels}
  </svg>`;
}

function alertBadge(level) {
  const map = { high: ["高危", "al-high"], medium: ["可疑", "al-mid"], low: ["提示", "al-low"] };
  const [txt, cls] = map[level] || ["提示", "al-low"];
  return `<span class="alert-badge ${cls}">${txt}</span>`;
}

async function renderDashboard() {
  const c = document.getElementById("adminContent");
  c.innerHTML = `<div class="dash-loading">仪表盘数据加载中…</div>`;
  try {
    const [counts, ov, trend, lg, al, mu, ssl] = await Promise.all([
      api("GET", "/api/dashboard"),
      api("GET", "/api/stats/overview"),
      api("GET", "/api/stats/visits?days=" + DASH_DAYS),
      api("GET", "/api/stats/logins?limit=12"),
      api("GET", "/api/stats/alerts"),
      api("GET", "/api/stats/module_updates"),
      api("GET", "/api/stats/ssl"),
    ]);
    DASH_CACHE = { counts, ov, trend, lg, al, mu, ssl };
    drawDashboard();
  } catch (e) {
    c.innerHTML = `<div class="alert alert-danger">仪表盘加载失败：${escapeHtml(e.message || String(e))}</div>`;
  }
}

function drawDashboard() {
  const c = document.getElementById("adminContent");
  const { counts, ov, trend, lg, al, mu, ssl } = DASH_CACHE;
  const dPv = ov.today.pv - ov.yesterday.pv;
  const dUv = ov.today.uv - ov.yesterday.uv;
  const deltaHtml = v => v === 0 ? `<span class="delta flat">持平</span>`
    : `<span class="delta ${v > 0 ? "up" : "down"}">${v > 0 ? "▲" : "▼"} ${Math.abs(v)}</span>`;

  const alertTotal = (al.counts.high || 0) + (al.counts.medium || 0) + (al.counts.low || 0);
  const sslDays = ssl.days_left;
  const sslStatus = ssl.status || "unknown";

  // ---- 核心指标卡 ----
  const metrics = [
    { label: "今日 PV", val: ov.today.pv, sub: `昨日 ${ov.yesterday.pv}`, delta: deltaHtml(dPv), tone: "green" },
    { label: "今日 UV", val: ov.today.uv, sub: `昨日 ${ov.yesterday.uv}`, delta: deltaHtml(dUv), tone: "amber" },
    { label: "今日独立 IP", val: ov.today.ip, sub: `近 7 天 UV ${ov.last7.uv}`, delta: "", tone: "blue" },
    { label: "近 7 天 PV", val: ov.last7.pv, sub: `累计访问 ${ov.total.pv}`, delta: "", tone: "green" },
    { label: "安全预警", val: alertTotal, sub: `高危 ${al.counts.high || 0} 条`, delta: "", tone: alertTotal ? "red" : "green" },
    { label: "SSL 剩余", val: sslDays === null || sslDays === undefined ? "—" : sslDays,
      sub: ssl.configured ? (ssl.valid_to ? "到期 " + ssl.valid_to : ssl.error || "") : "未配置域名",
      delta: "", tone: sslStatus === "ok" ? "green" : (sslStatus === "warning" ? "amber" : "red"),
      unit: sslDays === null || sslDays === undefined ? "" : "天" },
  ];

  // ---- 趋势图 ----
  const trendHtml = `
    <div class="dash-panel-head">
      <div>
        <h5>访问趋势</h5>
        <div class="panel-sub">总 PV ${trend.total_pv} · 总 UV ${trend.total_uv} · 日均 ${trend.avg_pv}
          ${trend.peak && trend.peak.pv ? ` · 峰值 ${trend.peak.pv}（${trend.peak.label}）` : ""}</div>
      </div>
      <div class="seg-tabs">
        <button class="${DASH_DAYS === 7 ? "active" : ""}" onclick="switchTrend(7)">近 7 天</button>
        <button class="${DASH_DAYS === 30 ? "active" : ""}" onclick="switchTrend(30)">近 30 天</button>
      </div>
    </div>
    <div class="trend-legend">
      <span><i class="lg-pv"></i>PV（浏览量）</span>
      <span><i class="lg-uv"></i>UV（独立访客）</span>
    </div>
    <div id="trendBody">${trendChartSVG(trend.series)}</div>`;

  // ---- 最近登录记录 ----
  const loginRows = lg.items.length ? lg.items.map(it => `
    <tr>
      <td class="nowrap">${escapeHtml(it.created_at || "")}</td>
      <td>${escapeHtml(it.username || "-")}</td>
      <td class="mono">${escapeHtml(it.ip || "-")}</td>
      <td>${it.success ? `<span class="tag ok">成功</span>` : `<span class="tag fail">失败</span>`}</td>
      <td class="ua-cell" title="${escapeHtml(it.ua || "")}">${escapeHtml((it.ua || "-").slice(0, 42))}</td>
    </tr>`).join("") : `<tr><td colspan="5" class="dash-empty">暂无登录记录</td></tr>`;

  // ---- SSL ----
  let sslBody;
  if (!ssl.configured) {
    sslBody = `
      <div class="ssl-setup">
        <p class="panel-sub">配置域名后将自动检查证书有效期（每 6 小时刷新一次）</p>
        <div class="ssl-form">
          <input type="text" id="sslHostInput" class="form-control form-control-sm" placeholder="例如：www.bangqi.com">
          <button class="btn btn-sm btn-bq-dark" onclick="saveSslHost()">开始监控</button>
        </div>
      </div>`;
  } else if (ssl.status === "error") {
    sslBody = `
      <div class="ssl-error">
        <div class="ssl-big err">无法连接</div>
        <p class="panel-sub">${escapeHtml(ssl.error || "证书检查失败")}</p>
        <button class="btn btn-sm btn-outline-secondary" onclick="refreshSsl()">重新检查</button>
        <button class="btn btn-sm btn-link" onclick="editSslHost()">更换域名</button>
      </div>`;
  } else {
    const pct = sslDays === null ? 0 : Math.max(0, Math.min(100, (sslDays / 90) * 100));
    sslBody = `
      <div class="ssl-head">
        <div class="ssl-days ${sslStatus}">
          <strong>${sslDays}</strong><span>天</span>
        </div>
        <div class="ssl-meta">
          <div class="ssl-host">${escapeHtml(ssl.host)}</div>
          <div class="panel-sub">${sslStatus === "expired" ? "证书已过期" : "到期 " + escapeHtml(ssl.valid_to || "")}</div>
        </div>
      </div>
      <div class="ssl-bar"><div class="ssl-bar-in ${sslStatus}" style="width:${pct}%"></div></div>
      <dl class="ssl-detail">
        <div><dt>颁发机构</dt><dd>${escapeHtml(ssl.issuer || "-")}</dd></div>
        <div><dt>生效日期</dt><dd>${escapeHtml(ssl.valid_from || "-")}</dd></div>
        <div><dt>证书域名</dt><dd>${escapeHtml(ssl.subject || "-")}</dd></div>
        <div><dt>检查时间</dt><dd>${escapeHtml(ssl.checked_at || "-")}${ssl.cached ? "（缓存）" : ""}</dd></div>
      </dl>
      <div class="ssl-actions">
        <button class="btn btn-sm btn-outline-secondary" onclick="refreshSsl()">立即检查</button>
        <button class="btn btn-sm btn-link" onclick="editSslHost()">更换域名</button>
      </div>`;
  }

  // ---- 安全预警 ----
  const alertHtml = al.items.length ? al.items.map(a => `
    <div class="alert-row ${a.level}">
      <div class="alert-main">
        ${alertBadge(a.level)}
        <strong>${escapeHtml(a.title)}</strong>
      </div>
      <div class="alert-detail">${escapeHtml(a.detail)}</div>
      <div class="alert-foot">
        <span class="mono">IP ${escapeHtml(a.ip || "-")}</span>
        <span>${escapeHtml(a.type)}</span>
        <span>${escapeHtml(a.last_at || "")}</span>
      </div>
    </div>`).join("") : `<div class="dash-empty">暂无异常，站点运行正常</div>`;

  // ---- 模块更新时间 ----
  const moduleHtml = mu.items.map(m => `
    <tr>
      <td><strong>${escapeHtml(m.label)}</strong></td>
      <td class="num">${m.count}</td>
      <td class="nowrap">${m.updated_at ? timeAgo(m.updated_at) : "—"}</td>
      <td class="nowrap">${escapeHtml(m.updated_at ? m.updated_at.slice(5, 16) : "—")}</td>
      <td>${m.last_action ? `<span class="tag act">${escapeHtml(m.last_action)}</span> ${escapeHtml(m.last_target || "")}` : `<span class="panel-sub">—</span>`}</td>
    </tr>`).join("");

  // ---- 内容数量概览（原有） ----
  const contentCards = [
    { num: counts.products, label: "产品数量" },
    { num: counts.news, label: "新闻文章" },
    { num: counts.banners, label: "Banner" },
    { num: counts.dosage_forms, label: "剂型" },
    { num: counts.trademarks, label: "商标" },
    { num: counts.news_categories, label: "新闻分类" },
    { num: counts.pages, label: "栏目页面" },
  ];

  const topPaths = ov.top_paths.length ? ov.top_paths.map(p => `
    <div class="hot-row"><span class="hot-path mono">${escapeHtml(p.path)}</span><span class="hot-num">${p.count}</span></div>`).join("")
    : `<div class="dash-empty">今日暂无访问</div>`;

  c.innerHTML = `
  <div class="dash-wrap">
    <div class="dash-metrics">
      ${metrics.map(m => `
        <div class="metric-card ${m.tone}">
          <div class="metric-label">${m.label}</div>
          <div class="metric-val">${m.val}${m.unit ? `<span class="metric-unit">${m.unit}</span>` : ""}</div>
          <div class="metric-sub">${escapeHtml(m.sub || "")} ${m.delta || ""}</div>
        </div>`).join("")}
    </div>

    <section class="dash-panel">${trendHtml}</section>

    <div class="dash-row">
      <section class="dash-panel">
        <div class="dash-panel-head">
          <div><h5>最近登录记录</h5>
            <div class="panel-sub">今日失败 ${lg.stats.today_fail} 次 · 累计成功 ${lg.stats.total_ok} 次 · 累计失败 ${lg.stats.total_fail} 次</div>
          </div>
        </div>
        <div class="table-scroll">
          <table class="dash-table">
            <thead><tr><th>时间</th><th>账号</th><th>IP 地址</th><th>结果</th><th>客户端</th></tr></thead>
            <tbody>${loginRows}</tbody>
          </table>
        </div>
      </section>

      <section class="dash-panel">
        <div class="dash-panel-head"><div><h5>SSL 证书</h5></div></div>
        <div id="sslBody">${sslBody}</div>
      </section>
    </div>

    <div class="dash-row">
      <section class="dash-panel">
        <div class="dash-panel-head">
          <div><h5>异常登录 / 攻击预警</h5>
            <div class="panel-sub">高危 ${al.counts.high || 0} · 可疑 ${al.counts.medium || 0} · 提示 ${al.counts.low || 0}</div>
          </div>
          <button class="btn btn-sm btn-outline-secondary" onclick="renderDashboard()">刷新</button>
        </div>
        <div class="alert-list">${alertHtml}</div>
      </section>

      <section class="dash-panel">
        <div class="dash-panel-head"><div><h5>各模块最后更新时间</h5>
          <div class="panel-sub">按最近更新排序，含操作类型与操作对象</div></div></div>
        <div class="table-scroll">
          <table class="dash-table">
            <thead><tr><th>模块</th><th>数量</th><th>距今</th><th>更新时间</th><th>最近操作</th></tr></thead>
            <tbody>${moduleHtml}</tbody>
          </table>
        </div>
      </section>
    </div>

    <div class="dash-row">
      <section class="dash-panel">
        <div class="dash-panel-head"><div><h5>今日热门页面</h5></div></div>
        <div class="hot-list">${topPaths}</div>
      </section>
      <section class="dash-panel">
        <div class="dash-panel-head"><div><h5>内容概览</h5></div></div>
        <div class="mini-grid">
          ${contentCards.map(cc => `<div class="mini-card"><b>${cc.num}</b><span>${cc.label}</span></div>`).join("")}
        </div>
      </section>
    </div>
  </div>`;
}

async function switchTrend(days) {
  if (DASH_DAYS === days) return;
  DASH_DAYS = days;
  document.querySelectorAll(".seg-tabs button").forEach((b, i) => {
    b.classList.toggle("active", (i === 0 && days === 7) || (i === 1 && days === 30));
  });
  const box = document.getElementById("trendBody");
  if (box) box.innerHTML = `<div class="dash-loading">加载中…</div>`;
  try {
    const trend = await api("GET", "/api/stats/visits?days=" + days);
    DASH_CACHE.trend = trend;
    drawDashboard();
  } catch (e) {
    if (box) box.innerHTML = `<div class="dash-empty">趋势数据加载失败</div>`;
  }
}

async function refreshSsl() {
  const box = document.getElementById("sslBody");
  if (box) box.innerHTML = `<div class="dash-loading">证书检查中…</div>`;
  try {
    const ssl = await api("GET", "/api/stats/ssl?refresh=1");
    DASH_CACHE.ssl = ssl;
    drawDashboard();
  } catch (e) {
    if (box) box.innerHTML = `<div class="dash-empty">检查失败</div>`;
  }
}

async function saveSslHost() {
  const input = document.getElementById("sslHostInput");
  if (!input || !input.value.trim()) return;
  const box = document.getElementById("sslBody");
  if (box) box.innerHTML = `<div class="dash-loading">证书检查中…</div>`;
  try {
    const ssl = await api("POST", "/api/stats/ssl", { host: input.value.trim() });
    DASH_CACHE.ssl = ssl;
    drawDashboard();
  } catch (e) {
    if (box) box.innerHTML = `<div class="dash-empty">检查失败，请确认域名可访问</div>`;
  }
}

function editSslHost() {
  const box = document.getElementById("sslBody");
  if (!box) return;
  box.innerHTML = `
    <div class="ssl-setup">
      <p class="panel-sub">输入新的监控域名（不含 http://）</p>
      <div class="ssl-form">
        <input type="text" id="sslHostInput" class="form-control form-control-sm" placeholder="例如：www.bangqi.com">
        <button class="btn btn-sm btn-bq-dark" onclick="saveSslHost()">保存并检查</button>
      </div>
    </div>`;
}

// ============================================================
// 通用 CRUD 表格
// ============================================================
async function renderCrudTable(resourceKey) {
  const res = RESOURCES[resourceKey];
  const c = document.getElementById("adminContent");
  let toolbar = "";
  // 产品图片管理：可搜索的产品筛选器（产品多时可输入关键字过滤）
  if (resourceKey === "product-image") {
    const products = state.fkCache["product"] || [];
    const cur = products.find(p => String(p.id) === String(state.piFilter));
    toolbar = `
    <div class="fk-select pi-filter" data-fk="product" data-label="name" style="width:240px">
      <input type="hidden" value="${state.piFilter}">
      <input type="text" class="form-control form-control-sm fk-search" placeholder="筛选产品（输入关键字）" value="${cur ? escapeHtml(cur.name) : ""}" autocomplete="off"
        oninput="fkFilter(this)" onfocus="fkFilter(this)" onblur="fkBlur(this)">
      <div class="fk-dropdown"></div>
    </div>`;
  }
  // 通用关键字搜索框（按 search 配置的列过滤表格行）
  if (res.search) {
    toolbar = `<input type="text" class="table-search" placeholder="输入关键字筛选..." oninput="filterCrudRows(this)">` + toolbar;
  }
  const hint = resourceKey === "product-image"
    ? `<div class="pi-hint" style="margin:1rem 1.2rem 0">💡 推荐在「产品列表 → 编辑」弹窗底部直接拖拽批量上传产品图片；本页用于维护已有图片的标题与排序。</div>`
    : "";
  c.innerHTML = `<div class="data-card"><div class="data-toolbar"><h6>${res.name}</h6><div class="d-flex align-items-center gap-2">${toolbar}<button class="btn btn-primary" onclick="openCreate('${resourceKey}')">+ 新增</button></div></div>${hint}<div id="tableBody" style="padding:0 1.2rem 1rem;"><p class="text-muted p-3">加载中...</p></div></div>`;
  try {
    let list = await api("GET", res.endpoint);
    if (resourceKey === "product-image" && state.piFilter) {
      list = list.filter(i => String(i.product_id) === String(state.piFilter));
    }
    const tbody = document.getElementById("tableBody");
    if (!list.length) {
      tbody.innerHTML = `<p class="text-muted text-center py-4">暂无数据，点击右上角"新增"添加</p>`;
      return;
    }
    // 产品图片：把产品名并入行搜索数据，方便按产品名搜索
    let productMap = null;
    if (resourceKey === "product-image") {
      productMap = {};
      for (const p of (state.fkCache["product"] || [])) productMap[p.id] = p.name;
    }
    let html = `<table class="data-table"><thead><tr>`;
    for (const col of res.cols) {
      html += `<th>${colLabel(res, col)}</th>`;
    }
    html += `<th>操作</th></tr></thead><tbody>`;
    for (const item of list) {
      let searchText = (res.search || []).map(k => (item[k] === null || item[k] === undefined) ? "" : String(item[k])).join(" ");
      if (productMap) searchText += " " + (productMap[item.product_id] || "");
      html += `<tr data-search="${escapeHtml(searchText)}">`;
      for (const col of res.cols) {
        html += `<td>${renderCell(col, item[col], item)}</td>`;
      }
      html += `<td class="td-actions">
        <button class="btn-edit" onclick="openEdit('${resourceKey}', ${item.id})">编辑</button>
        <button class="btn-del" onclick="confirmDelete('${resourceKey}', ${item.id})">删除</button>
      </td></tr>`;
    }
    html += `</tbody></table>`;
    tbody.innerHTML = html;
  } catch (e) {
    c.innerHTML = `<div class="alert alert-danger m-3">加载失败: ${e.message}</div>`;
  }
}

function colLabel(res, col) {
  const labels = {
    is_active: "状态", color: "占位色", sort_order: "排序",
    clicks: "点击量", date: "日期", form: "剂型",
    trademark: "商标", func: "功能", category: "分类",
    unit: "单位", value: "数值", label: "标签",
    image: "图片", product_id: "所属产品",
  };
  return labels[col] || col;
}

function renderCell(col, val, item) {
  if (col === "is_active") return val ? `<span class="td-tag" style="background:#e8f3ef;color:#67c23a">启用</span>` : `<span class="td-tag" style="background:#fef0f0;color:#f56c6c">停用</span>`;
  if (col === "image") {
    if (!val) return `<span class="text-muted" style="font-size:.78rem">未上传 · 占位图</span>`;
    return `<img class="td-thumb" src="${escapeHtml(val)}" loading="lazy" onerror="this.replaceWith('图片缺失')">`;
  }
  if (col === "product_id") {
    const p = (state.fkCache["product"] || []).find(x => x.id === val);
    return p ? escapeHtml(p.name) : (val || "-");
  }
  if (col === "color") {
    const c = COLORS.find(x => x.v === val);
    return `<span class="td-color-chip" style="background:${colorHex(val)}">${c ? c.t : val}</span>`;
  }
  if (val === null || val === undefined) return `<span class="text-muted">-</span>`;
  if (typeof val === "string" && val.length > 50) return val.substring(0, 50) + "...";
  if (col === "title" && typeof val === "string") return val.replace(/<br>/g, " ");
  return String(val);
}

function colorHex(cls) {
  const map = {
    "ph-green": "#14513f", "ph-ta": "#3d7a5c", "ph-am": "#b9893d",
    "ph-li": "#5b6c8f", "ph-ti": "#3a5a6a", "ph-gy": "#6a8a7a",
    "ph-gr": "#2d8a5e", "ph-cp": "#4a7a6a", "ph-pi": "#5a4a6a", "ph-gray": "#999",
  };
  return map[cls] || "#666";
}

// ============================================================
// 表单弹窗
// ============================================================
function openCreate(resourceKey) {
  state.editingId = null;
  const res = RESOURCES[resourceKey];
  document.getElementById("modalTitle").textContent = `新增${res.name}`;
  const body = document.getElementById("modalBody");
  body.innerHTML = buildForm(res, {});
  if (resourceKey === "product") {
    body.innerHTML += `<div class="pi-hint">💡 产品图片：保存产品后，重新点击该产品的「编辑」，即可在弹窗底部拖拽批量上传多张产品图片。</div>`;
  }
  initRichTextEditors();
  document.getElementById("modalSave").onclick = () => saveItem(resourceKey);
  editModal.show();
}

async function openEdit(resourceKey, id) {
  state.editingId = id;
  const res = RESOURCES[resourceKey];
  document.getElementById("modalTitle").textContent = `编辑${res.name}`;
  const body = document.getElementById("modalBody");
  body.innerHTML = `<p class="text-muted">加载中...</p>`;
  editModal.show();
  try {
    const data = await api("GET", `${res.endpoint}/${id}`);
    body.innerHTML = buildForm(res, data);
    if (resourceKey === "product") {
      body.innerHTML += buildProductImagesPanel(data.images || [], id);
      initProductDropzone(id);
    }
    initRichTextEditors();
  } catch (e) {
    body.innerHTML = `<div class="alert alert-danger">加载失败</div>`;
  }
  document.getElementById("modalSave").onclick = () => saveItem(resourceKey);
}

function buildForm(res, data) {
  let html = "";
  for (const f of res.fields) {
    const val = data[f.k] !== undefined ? data[f.k] : (f.def !== undefined ? f.def : "");
    const req = f.required ? " required" : "";
    html += `<div class="form-row">`;
    html += `<label>${f.l}${f.required ? ' <span class="text-danger">*</span>' : ''}</label>`;
    if (f.t === "text") {
      html += `<input type="text" class="form-control" name="${f.k}" value="${escapeHtml(val)}"${req}>`;
    } else if (f.t === "textarea") {
      html += `<textarea class="form-control" name="${f.k}" rows="3"${req}>${escapeHtml(val)}</textarea>`;
    } else if (f.t === "richtext") {
      state.pendingRichText[f.k] = val || "";
      html += `<div class="quill-editor" id="rt_${f.k}"></div>`;
    } else if (f.t === "number") {
      html += `<input type="number" class="form-control" name="${f.k}" value="${val}"${req}>`;
    } else if (f.t === "date") {
      html += `<input type="date" class="form-control" name="${f.k}" value="${val}"${req}>`;
    } else if (f.t === "checkbox") {
      html += `<div class="form-check"><input type="checkbox" class="form-check-input" name="${f.k}" ${val ? "checked" : ""}><label class="form-check-label">${f.l}</label></div>`;
    } else if (f.t === "select") {
      html += `<select class="form-select" name="${f.k}">`;
      for (const o of f.opts) {
        html += `<option value="${o.v}" ${val === o.v ? "selected" : ""}>${o.t}</option>`;
      }
      html += `</select>`;
    } else if (f.t === "fk") {
      html += buildFkField(f, val);
    } else if (f.t === "image") {
      html += buildImageField(f.k, f.l, val);
    }
    html += `</div>`;
  }
  return html;
}

// ============================================================
// 富文本编辑器（Quill）—— 用于产品介绍等图文混排字段
// ============================================================
const RICH_TOOLBAR = [
  [{ header: [1, 2, 3, false] }],
  ["bold", "italic", "underline", "strike"],
  [{ color: [] }, { background: [] }],
  [{ list: "ordered" }, { list: "bullet" }],
  [{ align: [] }],
  ["image", "link"],
  ["clean"],
];

function initRichTextEditors() {
  if (typeof Quill === "undefined") return;
  for (const key in state.pendingRichText) {
    const el = document.getElementById("rt_" + key);
    if (!el) continue;
    const quill = new Quill(el, {
      theme: "snow",
      modules: {
        toolbar: {
          container: RICH_TOOLBAR,
          handlers: { image: quillImageHandler },
        },
      },
      placeholder: "可输入文字，也可通过工具栏图片按钮插入图片，支持图文混排…",
    });
    const html = state.pendingRichText[key];
    if (html) {
      const delta = quill.clipboard.convert(html);
      quill.setContents(delta, "silent");
    }
    state.richTextInstances[key] = quill;
  }
  state.pendingRichText = {};
}

function quillImageHandler() {
  const quill = this.quill;   // Quill 1.x 中 handler 的 this 为 toolbar，this.quill 为编辑器
  const input = document.createElement("input");
  input.type = "file";
  input.accept = "image/png,image/jpeg,image/gif,image/webp";
  input.onchange = async () => {
    const file = input.files && input.files[0];
    if (!file) return;
    if (file.size > 8 * 1024 * 1024) { showToast("图片超过 8MB 限制", true); return; }
    const fd = new FormData();
    fd.append("file", file);
    try {
      const res = await fetch("/api/upload", { method: "POST", body: fd });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "上传失败");
      const range = quill.getSelection(true);
      quill.insertEmbed(range.index, "image", data.url, "user");
      quill.setSelection(range.index + 1, "silent");
    } catch (e) {
      showToast("图片上传失败: " + e.message, true);
    }
  };
  input.click();
}

// ---- 图片上传字段（预览 + 上传 + 移除；未上传时前台显示纯色占位 PNG） ----
function buildImageField(key, label, val) {
  return `
  <div class="img-field">
    <input type="hidden" name="${key}" value="${escapeHtml(val)}">
    <div class="img-preview-wrap ${val ? "has-img" : "empty"}">
      <img id="imgPrev_${key}" src="${val ? escapeHtml(val) : ""}" style="${val ? "" : "display:none"}" alt="预览">
      <span class="img-preview-tip ${val ? "d-none" : ""}">尚未上传图片<br><span style="font-size:.74rem;color:#909399;">支持 PNG / JPG / GIF / WEBP，最大 8MB</span></span>
    </div>
    <div class="img-actions">
      <button type="button" class="btn btn-primary" onclick="this.nextElementSibling.click()">📁 选择图片上传</button>
      <input type="file" accept="image/png,image/jpeg,image/gif,image/webp" hidden onchange="handleImgUpload(this, '${key}')">
      <button type="button" class="btn btn-light" onclick="clearImgField('${key}')">移除图片</button>
    </div>
  </div>`;
}

async function handleImgUpload(input, key) {
  const file = input.files && input.files[0];
  if (!file) return;
  if (file.size > 8 * 1024 * 1024) {
    showToast("文件超过 8MB 限制", true);
    input.value = "";
    return;
  }
  const fd = new FormData();
  fd.append("file", file);
  try {
    const res = await fetch("/api/upload", { method: "POST", body: fd });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "上传失败");
    const hidden = document.querySelector(`#modalBody [name="${key}"]`);
    if (hidden) hidden.value = data.url;
    const prev = document.getElementById("imgPrev_" + key);
    if (prev) {
      prev.src = data.url;
      prev.style.display = "";
      prev.parentElement.classList.remove("empty");
      prev.parentElement.classList.add("has-img");
      const tip = prev.parentElement.querySelector(".img-preview-tip");
      if (tip) tip.classList.add("d-none");
    }
    showToast("上传成功，保存后生效");
  } catch (e) {
    showToast("上传失败: " + e.message, true);
  }
  input.value = "";
}

function clearImgField(key) {
  const hidden = document.querySelector(`#modalBody [name="${key}"]`);
  if (hidden) hidden.value = "";
  const prev = document.getElementById("imgPrev_" + key);
  if (prev) {
    prev.style.display = "none";
    prev.src = "";
    prev.parentElement.classList.add("empty");
    prev.parentElement.classList.remove("has-img");
    const tip = prev.parentElement.querySelector(".img-preview-tip");
    if (tip) tip.classList.remove("d-none");
  }
}

// ============================================================
// 产品图片面板（编辑弹窗内：已有图片 + Dropzone 拖拽批量上传）
// ============================================================
let productDropzone = null;

function piThumbHtml(img, productId) {
  return `
  <div class="pi-thumb" title="${escapeHtml(img.title || "")}">
    <img src="${escapeHtml(img.image || "")}" loading="lazy" onerror="this.style.display='none'">
    <span class="pi-order">${img.sort_order}</span>
    <button type="button" class="pi-remove" onclick="deleteProductImage(${img.id}, ${productId})" title="删除此图">×</button>
  </div>`;
}

function buildProductImagesPanel(images, productId) {
  const gallery = images.length
    ? images.map(img => piThumbHtml(img, productId)).join("")
    : `<p class="text-muted mb-0" style="font-size:.85rem">暂无产品图片，前台将显示纯色占位图；将图片拖到下方区域即可批量上传。</p>`;
  return `
  <div class="pi-panel">
    <div class="pi-panel-header">
      <span>产品图片（多图）</span>
      <span class="text-muted" style="font-size:.75rem;font-weight:400">拖拽或点击上传，支持一次选择多张</span>
    </div>
    <div class="pi-gallery" id="productImageGallery">${gallery}</div>
    <div id="productDropzone" class="dropzone"></div>
  </div>`;
}

function initProductDropzone(productId) {
  if (productDropzone) { productDropzone.destroy(); productDropzone = null; }
  const el = document.getElementById("productDropzone");
  if (!el || typeof Dropzone === "undefined") return;
  productDropzone = new Dropzone(el, {
    url: `/api/product/${productId}/images`,
    paramName: "file",
    acceptedFiles: "image/png,image/jpeg,image/gif,image/webp",
    maxFilesize: 8,
    parallelUploads: 4,
    addRemoveLinks: false,
    dictDefaultMessage: "拖拽图片到此处，或点击选择（可一次多选）",
    dictFileTooBig: "文件超过 8MB 限制",
    dictInvalidFileType: "仅支持 PNG / JPG / GIF / WEBP",
    dictResponseError: "上传失败",
    init: function () {
      let okCount = 0;
      this.on("success", (file, resp) => {
        if (resp && resp.created) okCount += resp.created.length;
      });
      this.on("error", (file, msg) => {
        showToast("上传失败: " + (typeof msg === "string" ? msg : "未知错误"), true);
      });
      this.on("queuecomplete", async () => {
        if (okCount > 0) showToast(`成功上传 ${okCount} 张产品图片`);
        okCount = 0;
        this.removeAllFiles(true);
        await refreshProductGallery(productId);
      });
    },
  });
}

async function refreshProductGallery(productId) {
  const el = document.getElementById("productImageGallery");
  if (!el) return;
  try {
    const p = await api("GET", `/api/product/${productId}`);
    const images = p.images || [];
    el.innerHTML = images.length
      ? images.map(img => piThumbHtml(img, productId)).join("")
      : `<p class="text-muted mb-0" style="font-size:.85rem">暂无产品图片，前台将显示纯色占位图。</p>`;
  } catch (e) { /* 静默失败，保持原列表 */ }
}

function deleteProductImage(imageId, productId) {
  state.deletingResource = "product-image";
  state.deletingId = imageId;
  state._afterDelete = () => refreshProductGallery(productId);
  deleteModal.show();
}

// ============================================================
// 可搜索下拉选择（fk-select）：适用于产品等大量选项场景
// ============================================================
function buildFkField(f, val) {
  const fkData = state.fkCache[f.fk] || [];
  const v = (val === undefined || val === null) ? "" : val;
  const cur = fkData.find(x => String(x.id) === String(v));
  return `
  <div class="fk-select" data-fk="${f.fk}" data-label="${f.fkLabel}">
    <input type="hidden" name="${f.k}" value="${v}">
    <input type="text" class="form-control fk-search" placeholder="输入关键字筛选后选择" value="${cur ? escapeHtml(cur[f.fkLabel]) : ""}" autocomplete="off"
      oninput="fkFilter(this)" onfocus="fkFilter(this)" onblur="fkBlur(this)">
    <div class="fk-dropdown"></div>
  </div>`;
}

function fkFilter(input) {
  const wrap = input.closest(".fk-select");
  if (!wrap) return;
  const fk = wrap.dataset.fk, labelKey = wrap.dataset.label;
  const isFilter = wrap.classList.contains("pi-filter");
  const all = state.fkCache[fk] || [];
  const hidden = wrap.querySelector("input[type=hidden]");
  const curId = hidden ? hidden.value : "";
  const curItem = curId ? all.find(x => String(x.id) === String(curId)) : null;
  // 聚焦且未修改关键字（文本仍为当前选中项名称）时显示全部选项
  let kw = input.value.trim().toLowerCase();
  if (curItem && input.value.trim() === String(curItem[labelKey])) kw = "";
  const items = kw ? all.filter(x => String(x[labelKey] || "").toLowerCase().includes(kw)) : all;
  const MAX = 60;
  let html = `<div class="fk-opt ${String(curId) === "" ? "cur" : ""}" data-id="" onclick="fkPick(this)">${isFilter ? "全部产品" : "（不选择）"}</div>`;
  for (const x of items.slice(0, MAX)) {
    html += `<div class="fk-opt ${String(x.id) === String(curId) ? "cur" : ""}" data-id="${x.id}" onclick="fkPick(this)"><span>${escapeHtml(x[labelKey])}</span><span class="fk-id">#${x.id}</span></div>`;
  }
  if (!items.length) {
    html += `<div class="fk-empty">无匹配结果</div>`;
  } else if (items.length > MAX) {
    html += `<div class="fk-more">已显示前 ${MAX} 条（共 ${items.length} 条），请继续输入关键字缩小范围</div>`;
  }
  wrap.querySelector(".fk-dropdown").innerHTML = html;
  wrap.classList.add("open");
}

function fkPick(optEl) {
  const wrap = optEl.closest(".fk-select");
  const id = optEl.dataset.id || "";
  const labelKey = wrap.dataset.label;
  const hidden = wrap.querySelector("input[type=hidden]");
  if (hidden) hidden.value = id;
  const item = id ? (state.fkCache[wrap.dataset.fk] || []).find(x => String(x.id) === String(id)) : null;
  wrap.querySelector(".fk-search").value = item ? item[labelKey] : "";
  wrap.classList.remove("open");
  // 产品图片管理页的工具栏筛选：选中即重新加载表格
  if (wrap.classList.contains("pi-filter")) {
    state.piFilter = id;
    renderCrudTable("product-image");
  }
}

function fkBlur(input) {
  // 未选择时恢复为当前选中项名称，并收起下拉
  setTimeout(() => {
    const wrap = input.closest(".fk-select");
    if (!wrap) return;
    wrap.classList.remove("open");
    const labelKey = wrap.dataset.label;
    const hidden = wrap.querySelector("input[type=hidden]");
    const id = hidden ? hidden.value : "";
    const item = id ? (state.fkCache[wrap.dataset.fk] || []).find(x => String(x.id) === String(id)) : null;
    input.value = item ? item[labelKey] : "";
  }, 180);
}

// 表格关键字筛选（不重新请求，直接隐藏不匹配行）
function filterCrudRows(input) {
  const kw = input.value.trim().toLowerCase();
  document.querySelectorAll("#tableBody tbody tr").forEach(tr => {
    const s = (tr.dataset.search || "").toLowerCase();
    tr.style.display = (!kw || s.includes(kw)) ? "" : "none";
  });
}

function escapeHtml(s) {
  if (s === null || s === undefined) return "";
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function collectFormData(res) {
  const data = {};
  for (const f of res.fields) {
    if (f.t === "richtext") {
      const q = state.richTextInstances[f.k];
      data[f.k] = q ? q.root.innerHTML : (state.pendingRichText[f.k] || "");
      continue;
    }
    const el = document.querySelector(`#modalBody [name="${f.k}"]`);
    if (!el) continue;
    if (f.t === "checkbox") {
      data[f.k] = el.checked;
    } else if (f.t === "number") {
      data[f.k] = el.value ? parseInt(el.value) : 0;
    } else {
      data[f.k] = el.value;
    }
  }
  return data;
}

async function saveItem(resourceKey) {
  const res = RESOURCES[resourceKey];
  const data = collectFormData(res);
  try {
    if (state.editingId) {
      await api("PUT", `${res.endpoint}/${state.editingId}`, data);
      showToast("修改成功");
    } else {
      await api("POST", res.endpoint, data);
      showToast("新增成功");
    }
    editModal.hide();
    renderCrudTable(resourceKey);
  } catch (e) {
    showToast("保存失败: " + e.message, true);
  }
}

function confirmDelete(resourceKey, id) {
  state.deletingResource = resourceKey;
  state.deletingId = id;
  deleteModal.show();
}

async function doDelete() {
  const res = RESOURCES[state.deletingResource];
  try {
    await api("DELETE", `${res.endpoint}/${state.deletingId}`);
    showToast("删除成功");
    deleteModal.hide();
    if (state._afterDelete) {
      const fn = state._afterDelete;
      state._afterDelete = null;
      fn();
    } else {
      renderCrudTable(state.deletingResource);
    }
  } catch (e) {
    showToast("删除失败: " + e.message, true);
  }
}

// ============================================================
// 栏目页面管理（特殊视图）
// ============================================================
async function renderPageManager(section) {
  const c = document.getElementById("adminContent");
  c.innerHTML = `<div class="page-mgr"><div class="page-mgr-list" id="pageList"><p class="text-muted p-2">加载中...</p></div><div class="page-mgr-detail" id="pageDetail"></div></div>`;
  try {
    const pages = await api("GET", `/api/page?section=${section}`);
    const listEl = document.getElementById("pageList");
    let html = "";
    for (const p of pages) {
      html += `<div class="pm-item ${state.selectedPageId === p.id ? 'active' : ''}" onclick="selectPage(${p.id})">${p.title}</div>`;
    }
    html += `<div class="pm-item" style="border:1px dashed #ccc;margin-top:.4rem" onclick="addPage('${section}')"><span style="opacity:.5">+ 新增栏目</span></div>`;
    listEl.innerHTML = html;
    if (pages.length && !state.selectedPageId) {
      state.selectedPageId = pages[0].id;
    }
    if (state.selectedPageId) {
      await renderPageDetail(state.selectedPageId);
    } else {
      document.getElementById("pageDetail").innerHTML = `<div class="data-card p-4 text-muted">请选择左侧栏目或新增栏目</div>`;
    }
  } catch (e) {
    c.innerHTML = `<div class="alert alert-danger">加载失败: ${e.message}</div>`;
  }
}

async function selectPage(id) {
  state.selectedPageId = id;
  await renderPageManager(state.currentSection);
}

async function renderPageDetail(pageId) {
  const detail = document.getElementById("pageDetail");
  try {
    const page = await api("GET", `/api/page/${pageId}`);
    detail.innerHTML = `
      <div class="sub-section">
        <div class="ss-header"><h6>栏目信息</h6><div class="d-flex gap-2"><button class="btn btn-sm btn-primary" onclick="editPageInfo(${pageId})">编辑栏目</button><button class="btn btn-sm btn-danger" onclick="deletePage(${pageId})">删除栏目</button></div></div>
        <div class="p-3">
          <p class="mb-1"><strong>标题：</strong>${escapeHtml(page.title)}</p>
          <p class="mb-1"><strong>排序：</strong>${page.sort_order}</p>
          <p class="mb-1"><strong>头图：</strong>${page.image
            ? `<img src="${escapeHtml(page.image)}" style="height:60px;border-radius:6px;border:1px solid #e4e7ed;object-fit:cover" onerror="this.replaceWith('图片缺失')">`
            : `<span class="text-muted" style="font-size:.8rem">未上传（前台显示纯色占位图）</span>`}</p>
        </div>
      </div>
      <div class="sub-section">
        <div class="ss-header"><h6>内容段落</h6><button class="btn btn-sm btn-primary" onclick="addSection(${pageId})">+ 新增段落</button></div>
        <div id="sectionList" class="p-3">${renderSectionList(page.sections, pageId)}</div>
      </div>
      <div class="sub-section">
        <div class="ss-header"><h6>统计数据</h6><button class="btn btn-sm btn-primary" onclick="addStat(${pageId})">+ 新增统计</button></div>
        <div class="p-3">${renderStatList(page.stats, pageId)}</div>
      </div>
    `;
  } catch (e) {
    detail.innerHTML = `<div class="alert alert-danger">加载失败</div>`;
  }
}

function renderSectionList(sections, pageId) {
  if (!sections.length) return `<p class="text-muted mb-0">暂无段落</p>`;
  return `<table class="data-table"><tbody>${sections.map(s => `
    <tr><td style="width:160px;font-weight:600">${escapeHtml(s.subtitle)}</td>
    <td>${escapeHtml(s.content).substring(0, 80)}${s.content && s.content.length > 80 ? '...' : ''}</td>
    <td class="td-actions" style="width:120px">
      <button class="btn-edit" onclick="editSection(${s.id})">编辑</button>
      <button class="btn-del" onclick="deleteSection(${s.id})">删除</button>
    </td></tr>`).join("")}</tbody></table>`;
}

function renderStatList(stats, pageId) {
  if (!stats.length) return `<p class="text-muted mb-0">暂无统计</p>`;
  return `<table class="data-table"><tbody>${stats.map(s => `
    <tr><td style="font-weight:600">${escapeHtml(s.label)}</td>
    <td style="color:var(--ad-primary);font-weight:700">${escapeHtml(s.value)}</td>
    <td class="td-actions" style="width:120px">
      <button class="btn-edit" onclick="editStat(${s.id})">编辑</button>
      <button class="btn-del" onclick="deleteStat(${s.id})">删除</button>
    </td></tr>`).join("")}</tbody></table>`;
}

// 页面 CRUD
function addPage(section) {
  state.editingId = null;
  document.getElementById("modalTitle").textContent = "新增栏目";
  document.getElementById("modalBody").innerHTML = `
    <div class="form-row"><label>栏目标题 <span class="text-danger">*</span></label><input type="text" class="form-control" name="title" required></div>
    <div class="form-row"><label>栏目头图（960×300）</label>${buildImageField("image", "栏目头图", "")}</div>
    <div class="form-row"><label>排序</label><input type="number" class="form-control" name="sort_order" value="0"></div>`;
  document.getElementById("modalSave").onclick = async () => {
    const title = document.querySelector('#modalBody [name="title"]').value;
    const image = document.querySelector('#modalBody [name="image"]').value;
    const sort_order = parseInt(document.querySelector('#modalBody [name="sort_order"]').value) || 0;
    if (!title) { showToast("请输入标题", true); return; }
    try {
      await api("POST", "/api/page", { section, title, image, sort_order });
      showToast("新增成功"); editModal.hide();
      await renderPageManager(section);
    } catch (e) { showToast("失败: " + e.message, true); }
  };
  editModal.show();
}

function editPageInfo(pageId) {
  state.editingId = pageId;
  api("GET", `/api/page/${pageId}`).then(page => {
    document.getElementById("modalTitle").textContent = "编辑栏目";
    document.getElementById("modalBody").innerHTML = `
      <div class="form-row"><label>栏目标题 <span class="text-danger">*</span></label><input type="text" class="form-control" name="title" value="${escapeHtml(page.title)}" required></div>
      <div class="form-row"><label>栏目头图（960×300）</label>${buildImageField("image", "栏目头图", page.image || "")}</div>
      <div class="form-row"><label>排序</label><input type="number" class="form-control" name="sort_order" value="${page.sort_order}"></div>`;
    document.getElementById("modalSave").onclick = async () => {
      const title = document.querySelector('#modalBody [name="title"]').value;
      const image = document.querySelector('#modalBody [name="image"]').value;
      const sort_order = parseInt(document.querySelector('#modalBody [name="sort_order"]').value) || 0;
      try {
        await api("PUT", `/api/page/${pageId}`, { title, image, sort_order });
        showToast("修改成功"); editModal.hide();
        await renderPageManager(state.currentSection);
      } catch (e) { showToast("失败: " + e.message, true); }
    };
    editModal.show();
  });
}

// 页面删除
function deletePage(pageId) {
  state.deletingResource = "page";
  state.deletingId = pageId;
  state._afterDelete = () => {
    state.selectedPageId = null;
    renderPageManager(state.currentSection);
  };
  deleteModal.show();
}

// 段落 CRUD（content 使用 Quill 富文本，与产品介绍、新闻一致）
function addSection(pageId) {
  state.editingId = null;
  state._sectionPageId = pageId;
  document.getElementById("modalTitle").textContent = "新增段落";
  document.getElementById("modalBody").innerHTML = `
    <div class="form-row"><label>小标题</label><input type="text" class="form-control" name="subtitle"></div>
    <div class="form-row"><label>正文内容（图文编辑，可插入图片）</label><div class="quill-editor" id="rt_ps_content"></div></div>
    <div class="form-row"><label>排序</label><input type="number" class="form-control" name="sort_order" value="0"></div>`;
  state.pendingRichText["ps_content"] = "";
  initRichTextEditors();
  document.getElementById("modalSave").onclick = async () => {
    const q = state.richTextInstances["ps_content"];
    const data = {
      page_id: pageId,
      subtitle: document.querySelector('#modalBody [name="subtitle"]').value,
      content: q ? q.root.innerHTML : "",
      sort_order: parseInt(document.querySelector('#modalBody [name="sort_order"]').value) || 0,
    };
    try {
      await api("POST", "/api/page-section", data);
      showToast("新增成功"); editModal.hide();
      await renderPageDetail(pageId);
    } catch (e) { showToast("失败: " + e.message, true); }
  };
  editModal.show();
}

function editSection(sectionId) {
  state.editingId = sectionId;
  api("GET", `/api/page-section/${sectionId}`).then(s => {
    state._sectionPageId = s.page_id;
    document.getElementById("modalTitle").textContent = "编辑段落";
    document.getElementById("modalBody").innerHTML = `
      <div class="form-row"><label>小标题</label><input type="text" class="form-control" name="subtitle" value="${escapeHtml(s.subtitle)}"></div>
      <div class="form-row"><label>正文内容（图文编辑，可插入图片）</label><div class="quill-editor" id="rt_ps_content"></div></div>
      <div class="form-row"><label>排序</label><input type="number" class="form-control" name="sort_order" value="${s.sort_order}"></div>`;
    state.pendingRichText["ps_content"] = s.content || "";
    initRichTextEditors();
    document.getElementById("modalSave").onclick = async () => {
      const q = state.richTextInstances["ps_content"];
      const data = {
        page_id: s.page_id,
        subtitle: document.querySelector('#modalBody [name="subtitle"]').value,
        content: q ? q.root.innerHTML : "",
        sort_order: parseInt(document.querySelector('#modalBody [name="sort_order"]').value) || 0,
      };
      try {
        await api("PUT", `/api/page-section/${sectionId}`, data);
        showToast("修改成功"); editModal.hide();
        await renderPageDetail(s.page_id);
      } catch (e) { showToast("失败: " + e.message, true); }
    };
    editModal.show();
  });
}

function deleteSection(sectionId) {
  state.deletingResource = "page-section";
  state.deletingId = sectionId;
  state._afterDelete = () => renderPageDetail(state._sectionPageId);
  deleteModal.show();
}

// 统计 CRUD
function addStat(pageId) {
  state.editingId = null;
  state._statPageId = pageId;
  document.getElementById("modalTitle").textContent = "新增统计";
  document.getElementById("modalBody").innerHTML = `
    <div class="form-row"><label>标签名称</label><input type="text" class="form-control" name="label"></div>
    <div class="form-row"><label>数值</label><input type="text" class="form-control" name="value"></div>
    <div class="form-row"><label>排序</label><input type="number" class="form-control" name="sort_order" value="0"></div>`;
  document.getElementById("modalSave").onclick = async () => {
    const data = {
      page_id: pageId,
      label: document.querySelector('#modalBody [name="label"]').value,
      value: document.querySelector('#modalBody [name="value"]').value,
      sort_order: parseInt(document.querySelector('#modalBody [name="sort_order"]').value) || 0,
    };
    try {
      await api("POST", "/api/page-stat", data);
      showToast("新增成功"); editModal.hide();
      await renderPageDetail(pageId);
    } catch (e) { showToast("失败: " + e.message, true); }
  };
  editModal.show();
}

function editStat(statId) {
  state.editingId = statId;
  api("GET", `/api/page-stat/${statId}`).then(s => {
    state._statPageId = s.page_id;
    document.getElementById("modalTitle").textContent = "编辑统计";
    document.getElementById("modalBody").innerHTML = `
      <div class="form-row"><label>标签名称</label><input type="text" class="form-control" name="label" value="${escapeHtml(s.label)}"></div>
      <div class="form-row"><label>数值</label><input type="text" class="form-control" name="value" value="${escapeHtml(s.value)}"></div>
      <div class="form-row"><label>排序</label><input type="number" class="form-control" name="sort_order" value="${s.sort_order}"></div>`;
    document.getElementById("modalSave").onclick = async () => {
      const data = {
        page_id: s.page_id,
        label: document.querySelector('#modalBody [name="label"]').value,
        value: document.querySelector('#modalBody [name="value"]').value,
        sort_order: parseInt(document.querySelector('#modalBody [name="sort_order"]').value) || 0,
      };
      try {
        await api("PUT", `/api/page-stat/${statId}`, data);
        showToast("修改成功"); editModal.hide();
        await renderPageDetail(s.page_id);
      } catch (e) { showToast("失败: " + e.message, true); }
    };
    editModal.show();
  });
}

function deleteStat(statId) {
  state.deletingResource = "page-stat";
  state.deletingId = statId;
  state._afterDelete = () => renderPageDetail(state._statPageId);
  deleteModal.show();
}

// ============================================================
// 公司信息（单条编辑）
// ============================================================
async function renderCompanyInfo() {
  const c = document.getElementById("adminContent");
  c.innerHTML = `<div class="data-card"><div class="data-toolbar"><h6>公司信息</h6><button class="btn btn-primary" onclick="editCompany()">编辑信息</button></div><div class="p-3" id="companyView"><p class="text-muted">加载中...</p></div></div>`;
  try {
    const company = await api("GET", "/api/company");
    const fields = [
      {l: "公司简称", k: "name"}, {l: "公司全称", k: "full_name"},
      {l: "联系电话", k: "phone"}, {l: "电子邮箱", k: "email"},
      {l: "公司地址", k: "address"},
    ];
    let html = "";
    for (const f of fields) {
      html += `<p class="mb-2"><strong style="display:inline-block;width:90px;color:#888">${f.l}：</strong>${escapeHtml(company[f.k] || "")}</p>`;
    }
    html += `<hr><p class="mb-1"><strong style="color:#888">公司简介：</strong></p><p style="line-height:1.8;color:#555">${escapeHtml(company.intro || "")}</p>`;
    html += `<hr><p class="mb-1"><strong style="color:#888">资讯页尾文案：</strong></p><p style="line-height:1.8;color:#555">${escapeHtml(company.news_footer || "")}</p>`;
    document.getElementById("companyView").innerHTML = html;
  } catch (e) {
    document.getElementById("companyView").innerHTML = `<div class="alert alert-danger">加载失败</div>`;
  }
}

function editCompany() {
  api("GET", "/api/company").then(company => {
    document.getElementById("modalTitle").textContent = "编辑公司信息";
    document.getElementById("modalBody").innerHTML = `
      <div class="form-row"><label>公司简称</label><input type="text" class="form-control" name="name" value="${escapeHtml(company.name || '')}"></div>
      <div class="form-row"><label>公司全称</label><input type="text" class="form-control" name="full_name" value="${escapeHtml(company.full_name || '')}"></div>
      <div class="form-row"><label>公司简介</label><textarea class="form-control" name="intro" rows="4">${escapeHtml(company.intro || '')}</textarea></div>
      <div class="form-row"><label>资讯页尾文案（显示在资讯文章详情底部）</label><textarea class="form-control" name="news_footer" rows="2">${escapeHtml(company.news_footer || '')}</textarea></div>
      <div class="form-row"><label>公司地址</label><input type="text" class="form-control" name="address" value="${escapeHtml(company.address || '')}"></div>
      <div class="row"><div class="col-6"><div class="form-row"><label>联系电话</label><input type="text" class="form-control" name="phone" value="${escapeHtml(company.phone || '')}"></div></div>
      <div class="col-6"><div class="form-row"><label>电子邮箱</label><input type="text" class="form-control" name="email" value="${escapeHtml(company.email || '')}"></div></div></div>`;
    document.getElementById("modalSave").onclick = async () => {
      const data = {};
      ["name", "full_name", "intro", "news_footer", "address", "phone", "email"].forEach(k => {
        data[k] = document.querySelector(`#modalBody [name="${k}"]`).value;
      });
      try {
        await api("PUT", "/api/company", data);
        showToast("保存成功"); editModal.hide();
        renderCompanyInfo();
      } catch (e) { showToast("失败: " + e.message, true); }
    };
    editModal.show();
  });
}

// ============================================================
// Toast
// ============================================================
function showToast(msg, isError) {
  const el = document.getElementById("toast");
  document.getElementById("toastMsg").textContent = msg;
  el.className = "toast align-items-center text-white" + (isError ? " error" : "");
  toastEl.show();
}

// ============================================================
// 初始化
// ============================================================
document.addEventListener("DOMContentLoaded", async () => {
  editModal = new bootstrap.Modal(document.getElementById("editModal"));
  deleteModal = new bootstrap.Modal(document.getElementById("deleteModal"));
  toastEl = new bootstrap.Toast(document.getElementById("toast"), { delay: 2000 });

  // 弹窗关闭时销毁 Dropzone / Quill 实例，避免重复绑定
  document.getElementById("editModal").addEventListener("hidden.bs.modal", () => {
    if (productDropzone) { productDropzone.destroy(); productDropzone = null; }
    state.richTextInstances = {};
    state.pendingRichText = {};
  });

  // 点击空白处收起可搜索下拉
  document.addEventListener("click", e => {
    if (!e.target.closest(".fk-select")) {
      document.querySelectorAll(".fk-select.open").forEach(w => w.classList.remove("open"));
    }
  });

  document.getElementById("loginBtn").onclick = doLogin;
  document.getElementById("loginPass").addEventListener("keypress", e => { if (e.key === "Enter") doLogin(); });
  document.getElementById("logoutBtn").onclick = doLogout;
  document.getElementById("confirmDelete").onclick = async () => {
    if (["page", "page-section", "page-stat"].includes(state.deletingResource)) {
      const endpoint = "/api/" + state.deletingResource;
      try {
        await api("DELETE", `${endpoint}/${state.deletingId}`);
        showToast("删除成功"); deleteModal.hide();
        if (state._afterDelete) { state._afterDelete(); state._afterDelete = null; }
      } catch (e) { showToast("删除失败: " + e.message, true); }
    } else {
      await doDelete();
    }
  };

  if (await checkAuth()) {
    await loadFkData();
    showAdmin();
  } else {
    showLogin();
  }
});

// ============================================================
// 批量上传产品
// ============================================================
function renderBatchUpload() {
  const c = document.getElementById("adminContent");
  c.innerHTML = `
    <div class="batch-upload-wrap">
      <div class="batch-card">
        <h4 class="batch-title">📋 第 1 步：下载 Excel 模板</h4>
        <p class="batch-desc">带 * 列为必填，剂型 / 商标 / 功能分类 不存在将自动新建。图片请按 <code>ZIP 目录 &lt;产品编号&gt;/&lt;图片文件名&gt;</code> 整理；名为 <code>cover.jpg</code> 的图片会作为产品封面。</p>
        <a href="/api/product/batch_template" class="btn btn-primary" download>⬇ 下载 Excel 模板</a>
      </div>

      <div class="batch-card">
        <h4 class="batch-title">📦 第 2 步：选择本地文件</h4>
        <div class="batch-files">
          <div class="batch-file-slot">
            <label>Excel 文件 (.xlsx)</label>
            <input type="file" id="batchExcel" accept=".xlsx,.xls" class="form-control">
            <div class="batch-file-name" id="batchExcelName">未选择</div>
          </div>
          <div class="batch-file-slot">
            <label>图片 ZIP 包</label>
            <input type="file" id="batchZip" accept=".zip" class="form-control">
            <div class="batch-file-name" id="batchZipName">未选择</div>
          </div>
        </div>
      </div>

      <div class="batch-card">
        <h4 class="batch-title">🚀 第 3 步：开始上传</h4>
        <p class="batch-desc">点击下方按钮后会立即处理并将结果显示在下方。<strong>说明</strong>：同名产品编号会更新原产品的信息并追加图片（不会删除原图片）。</p>
        <button class="btn btn-success" id="batchSubmitBtn" onclick="submitBatchUpload()">⬆ 开始批量上传</button>
        <div class="batch-progress" id="batchProgress" style="display:none">
          <div class="batch-progress-bar"><div class="batch-progress-fill" id="batchProgressFill"></div></div>
          <div class="batch-progress-text" id="batchProgressText">处理中...</div>
        </div>
      </div>

      <div class="batch-card" id="batchResultCard" style="display:none">
        <h4 class="batch-title">✅ 上传结果</h4>
        <div id="batchResult"></div>
      </div>
    </div>
  `;

  // 文件名显示
  document.getElementById("batchExcel").addEventListener("change", e => {
    const f = e.target.files[0];
    document.getElementById("batchExcelName").textContent = f ? `${f.name}（${(f.size/1024).toFixed(1)} KB）` : "未选择";
  });
  document.getElementById("batchZip").addEventListener("change", e => {
    const f = e.target.files[0];
    document.getElementById("batchZipName").textContent = f ? `${f.name}（${(f.size/1024/1024).toFixed(2)} MB）` : "未选择";
  });
}

async function submitBatchUpload() {
  const excelFile = document.getElementById("batchExcel").files[0];
  const zipFile = document.getElementById("batchZip").files[0];
  const btn = document.getElementById("batchSubmitBtn");
  const progress = document.getElementById("batchProgress");
  const fill = document.getElementById("batchProgressFill");
  const text = document.getElementById("batchProgressText");
  const resultCard = document.getElementById("batchResultCard");
  const resultBox = document.getElementById("batchResult");

  if (!excelFile || !zipFile) {
    alert("请先选择 Excel 文件和图片 ZIP 包");
    return;
  }

  btn.disabled = true;
  btn.textContent = "上传中...";
  progress.style.display = "block";
  resultCard.style.display = "none";
  fill.style.width = "20%";
  text.textContent = "正在上传文件...";

  try {
    const fd = new FormData();
    fd.append("excel", excelFile);
    fd.append("zip", zipFile);

    // 用 XHR 以便监听上传进度
    const data = await new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open("POST", "/api/product/batch_upload");
      xhr.upload.onprogress = e => {
        if (e.lengthComputable) {
          const pct = Math.min(90, Math.round(e.loaded / e.total * 80) + 20);
          fill.style.width = pct + "%";
          text.textContent = `上传中 ${(e.loaded/1024/1024).toFixed(1)} / ${(e.total/1024/1024).toFixed(1)} MB`;
        }
      };
      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try { resolve(JSON.parse(xhr.responseText)); }
          catch (err) { reject(new Error("响应解析失败")); }
        } else {
          try {
            const errJson = JSON.parse(xhr.responseText);
            reject(new Error(errJson.error || `HTTP ${xhr.status}`));
          } catch { reject(new Error(`HTTP ${xhr.status}`)); }
        }
      };
      xhr.onerror = () => reject(new Error("网络错误"));
      xhr.send(fd);
    });

    fill.style.width = "100%";
    text.textContent = "完成";

    if (data.ok) {
      const s = data.summary || {};
      resultCard.style.display = "block";
      resultBox.innerHTML = `
        <div class="batch-summary">
          <div class="batch-stat ok"><span class="batch-stat-num">${s.products_created || 0}</span><span class="batch-stat-label">新增产品</span></div>
          <div class="batch-stat ok"><span class="batch-stat-num">${s.products_updated || 0}</span><span class="batch-stat-label">更新产品</span></div>
          <div class="batch-stat ok"><span class="batch-stat-num">${s.images_added || 0}</span><span class="batch-stat-label">新增图片</span></div>
          <div class="batch-stat ${s.errors_count ? 'warn' : ''}"><span class="batch-stat-num">${s.errors_count || 0}</span><span class="batch-stat-label">错误行</span></div>
          <div class="batch-stat ${(data.unmatched_zips||[]).length ? 'warn' : ''}"><span class="batch-stat-num">${(data.unmatched_zips||[]).length}</span><span class="batch-stat-label">未匹配ZIP</span></div>
        </div>
        ${(data.errors||[]).length ? `
          <details class="batch-details" open>
            <summary>错误明细（${data.errors.length}）</summary>
            <table class="batch-table">
              <thead><tr><th>行</th><th>产品编号</th><th>说明</th></tr></thead>
              <tbody>${data.errors.map(e => `<tr><td>${e.row}</td><td>${e.code || ''}</td><td>${escapeHtml(e.message || '')}</td></tr>`).join('')}</tbody>
            </table>
          </details>
        ` : ''}
        ${(data.unmatched_zips||[]).length ? `
          <details class="batch-details">
            <summary>ZIP 中未匹配的目录（这些目录名不在 Excel 中）</summary>
            <p class="batch-tip">${data.unmatched_zips.join('、')}</p>
          </details>
        ` : ''}
        <div class="batch-tip">✅ 已自动滚动到 <a href="#" onclick="event.preventDefault();navigate('product')">产品列表</a> 查看最新数据。</div>
      `;
    } else {
      resultCard.style.display = "block";
      resultBox.innerHTML = `<div class="alert alert-danger">${escapeHtml(data.error || '上传失败')}</div>`;
    }
  } catch (err) {
    fill.style.width = "0%";
    text.textContent = "失败";
    resultCard.style.display = "block";
    resultBox.innerHTML = `<div class="alert alert-danger">${escapeHtml(err.message || String(err))}</div>`;
  } finally {
    btn.disabled = false;
    btn.textContent = "⬆ 开始批量上传";
  }
}
