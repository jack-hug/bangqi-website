/* 邦琪药业官网 - 全局脚本 */
document.addEventListener("DOMContentLoaded", function () {
  /* 数字圆环 + SVG 进度环同步动画 */
  function animateCounter(el) {
    const target = parseInt(el.dataset.target, 10) || 0;
    const duration = 1600;
    const start = performance.now();
    const ring = el.closest(".stat-ring")?.querySelector(".stat-bar");
    /* 进度：取当前 3 个 stat 中最大值做归一化，让进度环视觉对比均匀 */
    let ringMax = 100;
    if (ring && ring.dataset.target) {
      const all = Array.from(document.querySelectorAll(".stat-bar")).map((b) => parseInt(b.dataset.target, 10) || 0);
      ringMax = Math.max(100, ...all);
    }
    function tick(now) {
      const p = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      const val = Math.round(target * eased);
      el.textContent = val.toLocaleString("en-US");
      if (ring && p < 1) {
        const C = 2 * Math.PI * 50;
        const offset = C * (1 - (target * eased) / ringMax);
        ring.style.strokeDashoffset = offset;
      } else if (ring) {
        const C = 2 * Math.PI * 50;
        ring.style.strokeDashoffset = C * (1 - target / ringMax);
      }
      if (p < 1) requestAnimationFrame(tick);
    }
    /* 进度环起始态 */
    if (ring) {
      const C = 2 * Math.PI * 50;
      ring.style.strokeDashoffset = C;
    }
    requestAnimationFrame(tick);
  }

  const counters = document.querySelectorAll(".stat-num[data-target]");
  if ("IntersectionObserver" in window) {
    const co = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) { animateCounter(e.target); co.unobserve(e.target); }
      });
    }, { threshold: 0.4 });
    counters.forEach((el) => co.observe(el));
  } else {
    counters.forEach(animateCounter);
  }

  /* 滚动上浮动画（企业相关四张卡片） - 进入视口触发，离开后再回来重新触发 */
  const risers = document.querySelectorAll(".rise");
  if ("IntersectionObserver" in window && risers.length) {
    const ro = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.remove("rise-in");
            // 强制重排，重新触发动画
            void e.target.offsetWidth;
            e.target.classList.add("rise-in");
          }
        });
      },
      { threshold: 0.18 }
    );
    risers.forEach((el) => ro.observe(el));
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
