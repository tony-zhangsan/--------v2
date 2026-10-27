/* ============================================================
   site.js — 极简交互，无依赖
   只做三件事：移动端菜单、年份、询盘表单前端校验
   内容渲染全部在 HTML 里完成，本文件不生成任何正文
   ============================================================ */
(function () {
  'use strict';

  /* ---------- 移动端菜单 ---------- */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');

  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      nav.classList.toggle('is-open', !open);
    });

    // 点了导航项就收起
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) {
        toggle.setAttribute('aria-expanded', 'false');
        nav.classList.remove('is-open');
      }
    });

    // Esc 收起
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) {
        toggle.setAttribute('aria-expanded', 'false');
        nav.classList.remove('is-open');
        toggle.focus();
      }
    });
  }

  /* ---------- 页脚年份 ---------- */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = String(new Date().getFullYear());
  });

  /* ---------- 询盘表单校验 ----------
     注意：这里只做前端校验，不负责发送。
     后端接口接上后，把 form 的 action 填好即可。 */
  document.querySelectorAll('form[data-validate]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      var invalid = null;

      form.querySelectorAll('[required]').forEach(function (field) {
        var ok = field.value.trim() !== '';
        if (ok && field.type === 'email') {
          ok = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(field.value.trim());
        }
        field.setAttribute('aria-invalid', ok ? 'false' : 'true');
        if (!ok && !invalid) invalid = field;
      });

      if (invalid) {
        e.preventDefault();
        invalid.focus();
        return;
      }

      // 未配置 action 时阻止真实提交，避免跳到空白页
      if (!form.getAttribute('action')) {
        e.preventDefault();
        var note = form.querySelector('[data-form-note]');
        if (note) {
          note.hidden = false;
          note.textContent = form.getAttribute('data-pending-message') || '';
        }
      }
    });
  });

  /* ---------- 首页头部：下滑超过 60px 由透明转实色 ---------- */
  var header = document.querySelector('.site-header');

  if (header && (document.body.classList.contains('page-home') ||
                 document.body.classList.contains('page-products'))) {
    var onScroll = function () {
      header.classList.toggle('is-solid', window.pageYOffset > 60);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ---------- 关于我们：上下滑动切换双屏 ----------
     只处理切屏与指示点，不改 DOM 结构里已有的文案。
     ≤900px 交由原生滚动（about.css 已取消 scroll-snap）。 */
  var aboutSlides = Array.prototype.slice.call(document.querySelectorAll('.about-slide'));

  if (aboutSlides.length) {
    var aboutDotsBox = document.getElementById('about-dots');
    var aboutIndex = 0;
    var aboutLocked = false;
    var aboutDots = [];

    var aboutTop = function (el) {
      return el.getBoundingClientRect().top + window.pageYOffset;
    };

    var aboutSetActive = function (i) {
      aboutIndex = i;
      aboutDots.forEach(function (d, k) {
        d.classList.toggle('is-active', k === i);
      });
    };

    var aboutGo = function (i) {
      i = Math.max(0, Math.min(aboutSlides.length - 1, i));
      if (i === aboutIndex) return;
      aboutSetActive(i);
      aboutLocked = true;
      window.scrollTo({ top: aboutTop(aboutSlides[i]), behavior: 'smooth' });
      window.setTimeout(function () { aboutLocked = false; }, 850);
    };

    if (aboutDotsBox) {
      aboutSlides.forEach(function (_, i) {
        var b = document.createElement('button');
        b.type = 'button';
        b.setAttribute('aria-label', (i + 1) + ' / ' + aboutSlides.length);
        b.addEventListener('click', function () { aboutGo(i); });
        aboutDotsBox.appendChild(b);
        aboutDots.push(b);
      });
    }

    /* 滚轮：一次手势只切一屏 */
    window.addEventListener('wheel', function (e) {
      if (window.innerWidth <= 900 || e.ctrlKey) return;
      if (aboutLocked) { e.preventDefault(); return; }
      if (Math.abs(e.deltaY) < 8) return;
      e.preventDefault();
      aboutGo(aboutIndex + (e.deltaY > 0 ? 1 : -1));
    }, { passive: false });

    /* 键盘 */
    document.addEventListener('keydown', function (e) {
      var k = e.key;
      if (k === 'ArrowDown' || k === 'PageDown' || k === ' ') {
        e.preventDefault(); aboutGo(aboutIndex + 1);
      } else if (k === 'ArrowUp' || k === 'PageUp') {
        e.preventDefault(); aboutGo(aboutIndex - 1);
      } else if (k === 'Home') {
        e.preventDefault(); aboutGo(0);
      } else if (k === 'End') {
        e.preventDefault(); aboutGo(aboutSlides.length - 1);
      }
    });

    /* 触屏：原生滚动 + 一次滑动一屏 */
    var aboutTouchY = null;
    window.addEventListener('touchstart', function (e) {
      if (e.touches.length === 1) aboutTouchY = e.touches[0].clientY;
    }, { passive: true });

    window.addEventListener('touchend', function (e) {
      if (aboutTouchY === null || window.innerWidth > 900) { aboutTouchY = null; return; }
      var dy = aboutTouchY - e.changedTouches[0].clientY;
      aboutTouchY = null;
      if (Math.abs(dy) < 60) return;
      var next = Math.max(0, Math.min(aboutSlides.length - 1, aboutIndex + (dy > 0 ? 1 : -1)));
      window.scrollTo({ top: aboutTop(aboutSlides[next]), behavior: 'smooth' });
      aboutSetActive(next);
    }, { passive: true });

    /* 滚动同步指示点 */
    if ('IntersectionObserver' in window) {
      var aboutIO = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting && en.intersectionRatio > 0.55) {
            aboutSetActive(aboutSlides.indexOf(en.target));
          }
        });
      }, { threshold: [0.55] });
      aboutSlides.forEach(function (s) { aboutIO.observe(s); });
    }

    aboutSetActive(0);

    /* 支持 about.html#cambodia 直达第二屏 */
    if (location.hash) {
      var targetSlide = document.querySelector(location.hash);
      var hashIndex = aboutSlides.indexOf(targetSlide);
      if (hashIndex > 0) {
        aboutSetActive(hashIndex);
        var rootEl = document.documentElement;
        var prevBehavior = rootEl.style.scrollBehavior;
        rootEl.style.scrollBehavior = 'auto';
        window.scrollTo(0, aboutTop(aboutSlides[hashIndex]));
        window.requestAnimationFrame(function () { rootEl.style.scrollBehavior = prevBehavior; });
      }
    }
  }

  /* ---------- 产品中心：分类橱窗 ----------
     只切换卡片的 .is-active（放大）与滑动条位置。
     背景是固定一张图，不随分类切换。 */
  var pcRail = document.getElementById('pc-rail');

  if (pcRail) {
    var pcCards = Array.prototype.slice.call(pcRail.querySelectorAll('.pc-card'));
    var pcTrack = document.getElementById('pc-track');
    var pcThumb = document.getElementById('pc-track-thumb');
    var pcActive = -1;

    var pcSetActive = function (i) {
      if (i === pcActive) return;
      pcActive = i;
      pcCards.forEach(function (c, k) { c.classList.toggle('is-active', k === i); });
    };

    /* 卡片放大后把它滚进可视范围，且不牵动整页 */
    var pcKeepVisible = function (card) {
      var rail = pcRail.getBoundingClientRect();
      var box = card.getBoundingClientRect();
      if (box.right > rail.right) {
        pcRail.scrollTo({ left: pcRail.scrollLeft + (box.right - rail.right) + 8, behavior: 'smooth' });
      } else if (box.left < rail.left) {
        pcRail.scrollTo({ left: pcRail.scrollLeft - (rail.left - box.left) - 8, behavior: 'smooth' });
      }
    };

    pcCards.forEach(function (card, i) {
      card.addEventListener('mouseenter', function () {
        pcSetActive(i);
        window.setTimeout(function () { pcKeepVisible(card); }, 300);
      });
      card.addEventListener('focus', function () { pcSetActive(i); });
    });

    /* 底部滑动条：跟随 + 可拖动 */
    var pcSyncTrack = function () {
      if (!pcTrack || !pcThumb) return;
      var max = pcRail.scrollWidth - pcRail.clientWidth;
      /* 一屏放得下就不显示滑动条，别留个拖不动的死控件 */
      pcTrack.parentNode.classList.toggle('is-idle', max <= 1);
      var visible = Math.min(1, pcRail.clientWidth / pcRail.scrollWidth);
      var w = Math.max(visible, 0.14);
      var p = max > 0 ? pcRail.scrollLeft / max : 0;
      pcThumb.style.width = (w * 100) + '%';
      pcThumb.style.left = (p * (1 - w) * 100) + '%';
      pcTrack.setAttribute('aria-valuenow', String(Math.round(p * 100)));
    };

    if (pcTrack && pcThumb) {
      var pcDragging = false;
      var pcStartX = 0;
      var pcStartLeft = 0;

      pcTrack.addEventListener('pointerdown', function (e) {
        pcDragging = true;
        pcStartX = e.clientX;
        pcStartLeft = pcRail.scrollLeft;
        pcTrack.classList.add('is-dragging');
        try { pcTrack.setPointerCapture(e.pointerId); } catch (err) {}
      });

      pcTrack.addEventListener('pointermove', function (e) {
        if (!pcDragging) return;
        var thumbW = pcThumb.offsetWidth || 1;
        pcRail.scrollLeft = pcStartLeft + (e.clientX - pcStartX) * (pcRail.clientWidth / thumbW);
      });

      var pcEndDrag = function (e) {
        if (!pcDragging) return;
        pcDragging = false;
        pcTrack.classList.remove('is-dragging');
        try { pcTrack.releasePointerCapture(e.pointerId); } catch (err) {}
      };

      pcTrack.addEventListener('pointerup', pcEndDrag);
      pcTrack.addEventListener('pointercancel', pcEndDrag);

      pcTrack.addEventListener('keydown', function (e) {
        if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
        e.preventDefault();
        pcRail.scrollBy({ left: (e.key === 'ArrowRight' ? 1 : -1) * 200, behavior: 'smooth' });
      });

      pcRail.addEventListener('scroll', pcSyncTrack, { passive: true });
      window.addEventListener('resize', pcSyncTrack);
      pcSyncTrack();
    }

    /* 默认高亮第一个分类（与 HTML 里的 is-active 一致） */
    pcSetActive(0);
  }
})();
