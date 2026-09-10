/* 邦琪药业官网 - 全局脚本 */
document.addEventListener("DOMContentLoaded", function () {
  /* 数字递增动画 + 朱红 SVG 进度环同步（pathLength=100，描边偏移 100→0）
     v1.1 主页会用 IntersectionObserver（其他页通用）。v1.1 主页改用 Swiper，
     因此把 animateCounter 暴露到 window.bqAnimateCounter 供主页脚本在 slideChange 时手动调用。 */
  function animateCounter(el) {
    const target = parseInt(el.dataset.target, 10) || 0;
    const duration = 1600;
    const start = performance.now();
    const card = el.closest(".stat-card");
    const ring = card ? card.querySelector(".stat-ring-fg") : null;
    function tick(now) {
      const p = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      const val = Math.round(target * eased);
      el.textContent = val.toLocaleString("en-US");
      if (ring) ring.style.strokeDashoffset = (100 * (1 - eased)).toFixed(2);
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }
  // 暴露给 v1.1 主页脚本在 slideChange 时手动调用（避免与 Swiper 冲突）
  window.bqAnimateCounter = animateCounter;

  const counters = document.querySelectorAll(".stat-num[data-target]");
  if ("IntersectionObserver" in window) {
    const co = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) { animateCounter(e.target); co.unobserve(e.target); }
      });
    }, { threshold: 0.4 });
    counters.forEach((el) => co.observe(el));
    // 暴露到 window，v1.1 主页可在 Swiper init 时 disconnect（避免与 Swiper 动画时序冲突）
    window.bqCountersObserver = co;
  } else {
    counters.forEach(animateCounter);
  }

  /* 滚动上浮动画：监听 section（不是单张卡片），section 进入视口 ≥55% 时
     统一触发该 section 内所有 .rise 元素错峰弹出，动画仅触发一次。
     避免单卡片 18% 可见就早早触发，用户滚到位时动画已播完。 */
  const risers = document.querySelectorAll(".rise");
  if ("IntersectionObserver" in window && risers.length) {
    // 按所属 section 分组
    const groups = new Map();
    risers.forEach((el) => {
      const sec = el.closest("section") || document.body;
      if (!groups.has(sec)) groups.set(sec, []);
      groups.get(sec).push(el);
    });

    const ro = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting && e.intersectionRatio >= 0.55) {
            const list = groups.get(e.target) || [];
            list.forEach((el, idx) => {
              // 给每张卡片 inline 错峰延迟（CSS :nth-child 在多 col 布局中失效）
              el.style.transitionDelay = (idx * 0.14) + "s";
              el.classList.remove("rise-in");
              // 强制重排，重新触发动画
              void el.offsetWidth;
              el.classList.add("rise-in");
            });
            ro.unobserve(e.target); // 只触发一次
          }
        });
      },
      { threshold: [0, 0.25, 0.5, 0.55, 0.6, 0.75, 1] }
    );
    groups.forEach((_, sec) => ro.observe(sec));
  } else {
    risers.forEach((el) => el.classList.add("rise-in"));
  }

  /* 主页新闻中心自动轮播（垂直滚动展示最新5条） */
  const newsTicker = document.querySelector(".news-ticker");
  if (newsTicker) {
    let idx = 0;
    const items = newsTicker.querySelectorAll(".news-ticker-item");
    if (items.length > 1) {
      setInterval(() => {
        items[idx].classList.remove("on");
        idx = (idx + 1) % items.length;
        items[idx].classList.add("on");
        newsTicker.style.transform = `translateY(-${idx * 100}%)`;
      }, 3800);
    }
  }

  /* 导航高亮当前页 */
  const path = location.pathname;
  document.querySelectorAll(".site-nav .nav-link").forEach((a) => {
    const href = a.getAttribute("href");
    if (href === "/" ? path === "/" : path.startsWith(href)) a.classList.add("active");
  });

  /* 顶部「产品查询」下拉：实时搜索产品（公共 API） */
  (function setupNavSearch() {
    const input = document.getElementById("navSearchInput");
    const results = document.getElementById("navSearchResults");
    const clearBtn = document.getElementById("navSearchClear");
    const dropdown = document.getElementById("navSearchToggle");
    if (!input || !results || !dropdown) return;

    // 打开下拉时自动聚焦输入框
    const wrapper = dropdown.closest(".dropdown");
    if (wrapper) {
      wrapper.addEventListener("shown.bs.dropdown", () => {
        setTimeout(() => input.focus(), 60);
      });
      wrapper.addEventListener("hidden.bs.dropdown", () => {
        input.value = "";
        results.innerHTML = '<div class="search-hint">输入产品名称、产品编号或功能主治关键字</div>';
        clearBtn.hidden = true;
      });
    }

    const HINT_HTML = '<div class="search-hint">输入产品名称、产品编号或功能主治关键字</div>';
    const LOADING_HTML = '<div class="search-loading">搜索中…</div>';

    function escapeHtml(s) {
      return String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
      })[c]);
    }

    function renderResults(items, q) {
      if (!items || !items.length) {
        results.innerHTML = '<div class="search-empty">未找到匹配 "<strong>' + escapeHtml(q) + '</strong>" 的产品</div>';
        return;
      }
      const html = items.map((p) => {
        const form = p.form ? '<span class="tag">' + escapeHtml(p.form) + "</span>" : "";
        const ind = p.indications ? " · " + escapeHtml(p.indications) : "";
        const initial = (p.name || "产").slice(0, 1);
        const thumbInner = p.image
          ? '<img src="' + escapeHtml(p.image) + '" alt="">'
          : escapeHtml(initial);
        return (
          '<a class="search-item" href="/products/' + p.id + '">' +
            '<div class="search-thumb">' + thumbInner + '</div>' +
            '<div class="search-body">' +
              '<span class="search-name">' + escapeHtml(p.name || "(未命名)") + "</span>" +
              '<span class="search-meta">' + form + ind + "</span>" +
            "</div>" +
          "</a>"
        );
      }).join("");
      results.innerHTML = html;
    }

    let timer = null;
    let lastReq = 0;

    function doSearch() {
      const q = input.value.trim();
      clearBtn.hidden = q.length === 0;
      if (!q) { results.innerHTML = HINT_HTML; return; }
      if (q.length < 1) return;
      const reqId = ++lastReq;
      results.innerHTML = LOADING_HTML;
      fetch("/api/search/product?q=" + encodeURIComponent(q), { headers: { "Accept": "application/json" } })
        .then((r) => r.json())
        .then((data) => {
          if (reqId !== lastReq) return; // 过期请求，忽略
          renderResults(data.items || [], q);
        })
        .catch(() => {
          if (reqId !== lastReq) return;
          results.innerHTML = '<div class="search-empty">搜索服务暂时不可用，请稍后再试</div>';
        });
    }

    input.addEventListener("input", () => {
      if (timer) clearTimeout(timer);
      timer = setTimeout(doSearch, 180);
    });
    input.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        input.value = "";
        results.innerHTML = HINT_HTML;
        clearBtn.hidden = true;
        input.blur();
      }
    });
    clearBtn.addEventListener("click", () => {
      input.value = "";
      results.innerHTML = HINT_HTML;
      clearBtn.hidden = true;
      input.focus();
    });
  })();
});
