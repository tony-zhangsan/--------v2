/* ============================================================
   category.js — 产品分类页交互（category.html 专用）
   ------------------------------------------------------------
   只做交互，不生成任何正文：
     · 一级分类切换（主图 / 标题 / 广告语随分类走）
     · 二级分类筛选（点一次筛选，再点一次取消）
     · 两行横向拖动 + 底部自定义滚动条
     · 头部滚动变实色、CONTACT US 按压动效
   正文（分类名、广告语、全部产品卡）全部写在 HTML 里。
   ============================================================ */
(function () {
  'use strict';

  var page = document.querySelector('.page-category');
  if (!page) return;

  var heroBgBox = document.querySelector('.ct-hero__bgs');
  var titleEl = document.querySelector('[data-hero-title]');
  var adEl = document.querySelector('[data-hero-ad]');
  var countEl = document.querySelector('[data-hero-count]');
  var groups = Array.prototype.slice.call(document.querySelectorAll('.ct-group'));
  var panels = Array.prototype.slice.call(document.querySelectorAll('.ct-panel'));

  /* 每个面板的卡片列重新分栏：两行，横向滚动。
     ⚠️ 卡片节点必须留在 DOM 里（被筛掉的放进 .ct-pool），否则二次筛选就找不回来了。 */
  function pool(panel) {
    var p = panel.querySelector('.ct-pool');
    if (!p) {
      p = document.createElement('div');
      p.className = 'ct-pool';
      p.hidden = true;
      panel.appendChild(p);
    }
    return p;
  }

  function rechunk(panel) {
    var track = panel.querySelector('.ct-track');
    if (!track) return;

    if (!panel._cards) {
      panel._cards = Array.prototype.slice.call(track.querySelectorAll('.ct-card'));
    }
    var cards = panel._cards;

    // 先摘掉旧的分栏容器（卡片会被一并带出，随后重新归位）
    Array.prototype.slice.call(track.querySelectorAll('.ct-col')).forEach(function (col) {
      track.removeChild(col);
    });

    var visible = cards.filter(function (c) { return !c.hasAttribute('data-hidden'); });

    for (var i = 0; i < visible.length; i += 2) {
      var col = document.createElement('div');
      col.className = 'ct-col';
      col.appendChild(visible[i]);
      if (visible[i + 1]) col.appendChild(visible[i + 1]);
      track.appendChild(col);
    }

    // 被筛掉的卡片收进隐藏池，保持在 DOM 中
    var poolEl = pool(panel);
    cards.forEach(function (c) {
      if (c.hasAttribute('data-hidden')) poolEl.appendChild(c);
    });
  }

  /* ---------- 滚动条 ---------- */
  function initScroll(panel) {
    var vp = panel.querySelector('.ct-viewport');
    var bar = panel.querySelector('.ct-scroll');
    if (!vp || !bar) return null;

    var thumb = bar.querySelector('.ct-scroll__thumb');
    var dragging = false;
    var startX = 0;
    var startLeft = 0;

    function sync() {
      var max = vp.scrollWidth - vp.clientWidth;
      if (max <= 4) {
        bar.classList.add('is-hidden');
        return;
      }
      bar.classList.remove('is-hidden');
      var ratio = vp.clientWidth / vp.scrollWidth;
      var w = Math.max(ratio * bar.clientWidth, 40);
      thumb.style.width = w + 'px';
      var travel = bar.clientWidth - w;
      var pos = max > 0 ? (vp.scrollLeft / max) * travel : 0;
      thumb.style.transform = 'translateX(' + pos + 'px)';
    }

    function scrollToX(x) {
      vp.scrollLeft = x;
    }

    bar.addEventListener('pointerdown', function (e) {
      dragging = true;
      bar.classList.add('is-dragging');
      startX = e.clientX;
      startLeft = vp.scrollLeft;
      var max = vp.scrollWidth - vp.clientWidth;
      var travel = bar.clientWidth - thumb.offsetWidth;
      if (e.target !== thumb && travel > 0) {
        var rect = bar.getBoundingClientRect();
        var clickPos = e.clientX - rect.left - thumb.offsetWidth / 2;
        scrollToX((clickPos / travel) * max);
      }
      bar.setPointerCapture && bar.setPointerCapture(e.pointerId);
    });

    bar.addEventListener('pointermove', function (e) {
      if (!dragging) return;
      var max = vp.scrollWidth - vp.clientWidth;
      var travel = bar.clientWidth - thumb.offsetWidth;
      if (travel <= 0) return;
      scrollToX(startLeft + ((e.clientX - startX) / travel) * max);
    });

    function endDrag() {
      dragging = false;
      bar.classList.remove('is-dragging');
    }
    bar.addEventListener('pointerup', endDrag);
    bar.addEventListener('pointercancel', endDrag);
    bar.addEventListener('pointerleave', function () { if (dragging && !bar.hasPointerCapture) endDrag(); });

    /* 鼠标直接拖拽产品区 */
    var down = false, x0 = 0, l0 = 0, moved = false;
    vp.addEventListener('pointerdown', function (e) {
      if (e.pointerType === 'touch') return;
      down = true; moved = false; x0 = e.clientX; l0 = vp.scrollLeft;
    });
    vp.addEventListener('pointermove', function (e) {
      if (!down) return;
      var dx = e.clientX - x0;
      if (Math.abs(dx) > 4) { moved = true; vp.classList.add('is-dragging'); }
      if (moved) vp.scrollLeft = l0 - dx;
    });
    ['pointerup', 'pointercancel', 'pointerleave'].forEach(function (t) {
      vp.addEventListener(t, function () {
        down = false;
        vp.classList.remove('is-dragging');
      });
    });

    vp.addEventListener('scroll', sync, { passive: true });
    window.addEventListener('resize', sync);

    /* 触控板横向滚动 / 滚轮纵向转横向 */
    vp.addEventListener('wheel', function (e) {
      if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) return;
      if (vp.scrollWidth <= vp.clientWidth) return;
      vp.scrollLeft += e.deltaY;
      e.preventDefault();
    }, { passive: false });

    sync();
    return { sync: sync, reset: function () { vp.scrollLeft = 0; sync(); } };
  }

  var scrolls = {};
  panels.forEach(function (p) { scrolls[p.dataset.cat] = initScroll(p); });

  /* ---------- 分类切换 ---------- */
  function activate(cat, sub, opts) {
    opts = opts || {};
    var panel = panels.filter(function (p) { return p.dataset.cat === cat; })[0];
    var group = groups.filter(function (g) { return g.dataset.cat === cat; })[0];
    if (!panel || !group) return;

    groups.forEach(function (g) { g.classList.toggle('is-active', g === group); });
    panels.forEach(function (p) { p.classList.toggle('is-active', p === panel); });

    /* 主图 */
    if (heroBgBox) {
      Array.prototype.forEach.call(heroBgBox.children, function (bg) {
        bg.classList.toggle('is-active', bg.dataset.cat === cat);
      });
    }
    if (titleEl) titleEl.textContent = group.dataset.title || '';
    if (adEl) adEl.textContent = group.dataset.ad || '';
    if (countEl) {
      var n0 = parseInt(group.dataset.count, 10) || 0;
      countEl.textContent = n0 ? group.dataset.count : '';
      countEl.hidden = !n0;
    }

    /* 二级筛选：未指定则清空 */
    setFilter(panel, sub || '');

    if (scrolls[cat]) scrolls[cat].reset();

    if (!opts.silent && window.history && history.replaceState) {
      history.replaceState(null, '', '?cat=' + cat + (sub ? '&sub=' + sub : ''));
    }
  }

  function setFilter(panel, sub) {
    // 卡片全量取自 panel，二级按钮在侧栏的 group 里（不在 panel 内）
    if (!panel._cards) {
      panel._cards = Array.prototype.slice.call(panel.querySelectorAll('.ct-card'));
    }
    var cards = panel._cards;
    var group = groups.filter(function (g) { return g.dataset.cat === panel.dataset.cat; })[0];

    cards.forEach(function (c) {
      var match = !sub || c.dataset.sub === sub;
      if (match) c.removeAttribute('data-hidden');
      else c.setAttribute('data-hidden', '');
    });
    rechunk(panel);

    if (group) {
      Array.prototype.slice.call(group.querySelectorAll('.ct-sub')).forEach(function (s) {
        s.classList.toggle('is-active', !!sub && s.dataset.sub === sub);
      });
    }

    var visible = cards.filter(function (c) { return !c.hasAttribute('data-hidden'); }).length;
    if (group && countEl && visible) {
      countEl.textContent = visible + ' ' + (group.dataset.countLabel || '');
      countEl.hidden = false;
    }
    if (scrolls[panel.dataset.cat]) scrolls[panel.dataset.cat].sync();
  }

  groups.forEach(function (g) {
    var btn = g.querySelector('.ct-group__btn');
    if (btn) {
      btn.addEventListener('click', function () {
        activate(g.dataset.cat, '');
        /* 侧栏在移动端是横向条，切换后滚回可见 */
        g.scrollIntoView({ block: 'nearest', inline: 'nearest' });
      });
    }
  });

  /* 二级分类按钮在左侧目录里（不在产品面板内），所以用文档级事件委托 */
  document.addEventListener('click', function (e) {
    var sub = e.target.closest ? e.target.closest('.ct-sub') : null;
    if (!sub) return;
    var group = sub.closest('.ct-group');
    if (!group) return;

    var panel = panels.filter(function (p) { return p.dataset.cat === group.dataset.cat; })[0];
    if (!panel) return;

    var val = sub.dataset.sub || '';
    var isActive = sub.classList.contains('is-active');
    var next = (isActive && val) ? '' : val;   // 再点一次已选中的二级分类＝取消筛选

    setFilter(panel, next);
    if (window.history && history.replaceState) {
      history.replaceState(null, '', '?cat=' + panel.dataset.cat + (next ? '&sub=' + next : ''));
    }
  });

  /* ---------- CONTACT US 动效 ---------- */
  var contact = document.querySelector('.ct-nav__contact');
  if (contact) {
    contact.addEventListener('pointerdown', function () { contact.classList.add('is-pressed'); });
    ['pointerup', 'pointerleave', 'blur'].forEach(function (t) {
      contact.addEventListener(t, function () { contact.classList.remove('is-pressed'); });
    });
  }

  /* ---------- 头部滚动变实色 ---------- */
  var header = document.querySelector('.site-header');
  var hero = document.querySelector('.ct-hero');
  if (header && hero) {
    var onScroll = function () {
      header.classList.toggle('is-solid', window.scrollY > hero.offsetHeight - 120);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ---------- 初始状态：支持 ?cat= / ?sub= 与 #hash ---------- */
  var params = new URLSearchParams(window.location.search);
  var initCat = params.get('cat') || (window.location.hash || '').replace('#', '');
  var initSub = params.get('sub') || '';
  var valid = panels.map(function (p) { return p.dataset.cat; });
  activate(valid.indexOf(initCat) > -1 ? initCat : valid[0], initSub, { silent: true });
})();

/* ============================================================
   产品规格弹窗
   卡片上带 data-spec / data-size / data-pack / data-qty，内容全部来自 HTML，
   本模块只负责显隐与赋值。
   ============================================================ */
(function () {
  'use strict';

  var modal = document.getElementById('ct-modal');
  if (!modal) return;

  var dialog = modal.querySelector('.ct-modal__dialog');
  var img = modal.querySelector('[data-modal-img]');
  var titleEl = modal.querySelector('[data-modal-title]');
  var subEl = modal.querySelector('[data-modal-sub]');
  var closeBtn = modal.querySelector('[data-modal-close]');
  var figure = modal.querySelector('.ct-modal__figure');
  var EMPTY = modal.getAttribute('data-empty') || '—';
  var lastFocus = null;
  var dragged = false;

  function val(name, extra) {
    var box = modal.querySelector('[data-p="' + name + '"]');
    if (!box) return;
    if (!extra) {
      box.textContent = EMPTY;
      box.classList.add('is-empty');
      return;
    }
    box.classList.remove('is-empty');
    box.textContent = extra.split('|')[0];
    if (extra.indexOf('|') > -1) {
      var s = document.createElement('span');
      s.className = 'ct-param__sub';
      s.textContent = extra.split('|')[1];
      box.appendChild(s);
    }
  }

  function open(card) {
    lastFocus = document.activeElement;
    titleEl.textContent = card.getAttribute('data-code') || card.getAttribute('data-name') || '';
    subEl.textContent = card.getAttribute('data-name') || '';
    if (card.getAttribute('data-code')) subEl.hidden = !card.getAttribute('data-name');
    else subEl.hidden = true;

    var spec = card.getAttribute('data-spec');
    if (spec) {
      img.src = spec;
      img.alt = (card.getAttribute('data-code') || '') + ' ' + (card.getAttribute('data-name') || '') + ' 规格图';
      figure.hidden = false;
    } else {
      // 该型号的规格表只有文字（没有产品图），图片区整个不显示，避免和下方参数重复
      img.removeAttribute('src');
      figure.hidden = true;
    }

    val('size', card.getAttribute('data-size'));
    val('pack', card.getAttribute('data-pack'));
    val('qty', card.getAttribute('data-qty'));

    modal.classList.add('is-open');
    modal.removeAttribute('aria-hidden');
    document.body.classList.add('ct-locked');
    closeBtn.focus();
  }

  function close() {
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('ct-locked');
    img.removeAttribute('src');
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  document.addEventListener('click', function (e) {
    var card = e.target.closest ? e.target.closest('.ct-card') : null;
    if (card && !dragged) {
      open(card);
      return;
    }
    if (e.target === modal || e.target.closest('[data-modal-close]')) close();
  });

  document.addEventListener('keydown', function (e) {
    if (!modal.classList.contains('is-open')) return;
    if (e.key === 'Escape') { close(); return; }
    if (e.key === 'Enter' || e.key === ' ') {
      var card = document.activeElement;
      if (card && card.classList && card.classList.contains('ct-card')) {
        e.preventDefault();
        open(card);
      }
    }
    if (e.key === 'Tab') {
      var f = dialog.querySelectorAll('button, a[href], [tabindex]:not([tabindex="-1"])');
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });

  /* 横向拖动产品区时不要误开弹窗。
     ⚠️ 必须走位移阈值：真实鼠标按下时指针常有 1~2px 抖动，
     以前只要动过就判定为拖动，点击会被整个吞掉（表现为“点了没反应”）。 */
  var downX = 0, downY = 0;
  var DRAG_THRESHOLD = 10;

  document.addEventListener('pointerdown', function (e) {
    dragged = false;
    downX = e.clientX || 0;
    downY = e.clientY || 0;
  }, true);

  document.addEventListener('pointermove', function (e) {
    if (!e.buttons) return;
    if (!e.target.closest || !e.target.closest('.ct-viewport')) return;
    if (Math.abs((e.clientX || 0) - downX) > DRAG_THRESHOLD ||
        Math.abs((e.clientY || 0) - downY) > DRAG_THRESHOLD) {
      dragged = true;
    }
  }, true);

  ['pointerup', 'pointercancel'].forEach(function (t) {
    document.addEventListener(t, function () {
      window.setTimeout(function () { dragged = false; }, 80);
    }, true);
  });
})();
