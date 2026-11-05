/* ---------------------------------------------------------------
   询盘表单 → 云数据库（WorkBuddy Cloud Service）
   - 依赖页面先引入 CDN 版 SDK，全局 WorkBuddyCloud 可用
   - 匿名访客可直接写入，表上只授了 INSERT，不回传数据
   - 前端校验在此重复一遍，不依赖 site.js 的监听顺序
   --------------------------------------------------------------- */
(function () {
  'use strict';

  var CONFIG = {
    endpoint: 'https://xindadi-hardware.app.workbuddy.host',
    oauthRelayBaseUrl: 'https://www.workbuddy.cn/v2/as/genie-baas/oauth',
    publishableKey: 'wbpk_XWz9xWCwHj42idzMuNNyLz_sNfb5UHPTjzih0X9DE2Q9fs5J0IY2lyM'
  };

  var COPY = {
    zh: {
      sending: '正在提交…',
      success: '已收到您的询盘，我们会在两个工作日内回复。',
      failed: '提交失败，请稍后重试，或直接发邮件至 info@xindadi.com。',
      unavailable: '表单服务暂时不可用，请发邮件至 info@xindadi.com。'
    },
    en: {
      sending: 'Sending…',
      success: 'Thanks — we have received your enquiry and will reply within two business days.',
      failed: 'Submission failed. Please try again, or email info@xindadi.com directly.',
      unavailable: 'The form service is temporarily unavailable. Please email info@xindadi.com.'
    }
  };

  var forms = document.querySelectorAll('form[data-cloud-form]');
  if (!forms.length) return;

  function copyFor(form) {
    var lang = (form.getAttribute('data-lang') || document.documentElement.lang || 'en').toLowerCase();
    return lang.indexOf('zh') === 0 ? COPY.zh : COPY.en;
  }

  function showNote(form, text, state) {
    var note = form.querySelector('[data-form-note]');
    if (!note) return;
    note.textContent = text;
    note.className = 'contact-form__note is-' + state;
    note.hidden = false;
  }

  function clearNote(form) {
    var note = form.querySelector('[data-form-note]');
    if (!note) return;
    note.hidden = true;
    note.textContent = '';
  }

  function setBusy(form, busy, label) {
    var btn = form.querySelector('button[type="submit"]');
    if (!btn) return;
    if (busy) {
      if (!btn.dataset.idleLabel) btn.dataset.idleLabel = btn.innerHTML;
      btn.disabled = true;
      btn.textContent = label;
    } else {
      btn.disabled = false;
      if (btn.dataset.idleLabel) btn.innerHTML = btn.dataset.idleLabel;
    }
  }

  function validate(form) {
    var invalid = null;
    Array.prototype.forEach.call(form.querySelectorAll('[required]'), function (field) {
      var ok = field.value.trim() !== '';
      if (ok && field.type === 'email') {
        ok = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(field.value.trim());
      }
      field.setAttribute('aria-invalid', ok ? 'false' : 'true');
      if (!ok && !invalid) invalid = field;
    });
    return invalid;
  }

  function collect(form) {
    var data = new FormData(form);
    function pick(key) {
      var v = data.get(key);
      if (v === null) return null;
      v = String(v).trim();
      return v === '' ? null : v;
    }
    var zh = (document.documentElement.lang || '').toLowerCase().indexOf('zh') === 0;
    return {
      name: pick('name') || '',
      company: pick('company'),
      email: pick('email') || '',
      phone: pick('phone'),
      country: pick('country'),
      product_series: pick('series'),
      message: pick('message') || '',
      locale: zh ? 'zh' : 'en',
      source_page: location.pathname
    };
  }

  // SDK 没加载成功（离线 / CDN 被拦）时给出明确提示，不留空白
  if (!window.WorkBuddyCloud || typeof window.WorkBuddyCloud.createWorkBuddyCloud !== 'function') {
    Array.prototype.forEach.call(forms, function (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        showNote(form, copyFor(form).unavailable, 'error');
      });
    });
    return;
  }

  var cloud = window.WorkBuddyCloud.createWorkBuddyCloud({
    endpoint: CONFIG.endpoint,
    oauthRelayBaseUrl: CONFIG.oauthRelayBaseUrl,
    publishableKey: CONFIG.publishableKey
  });

  Array.prototype.forEach.call(forms, function (form) {
    form.addEventListener('input', function () { clearNote(form); });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var copy = copyFor(form);

      var invalid = validate(form);
      if (invalid) {
        clearNote(form);
        invalid.focus();
        return;
      }

      var payload = collect(form);
      setBusy(form, true, copy.sending);
      showNote(form, copy.sending, 'info');

      // 不链 .select()：匿名角色只有 INSERT 权限，RETURNING 会被拒
      cloud.database
        .from('inquiries')
        .insert(payload)
        .then(function (res) {
          if (res && res.error) throw res.error;
          showNote(form, copy.success, 'success');
          form.reset();
        })
        .catch(function (err) {
          showNote(form, copy.failed, 'error');
          if (window.console && console.error) {
            console.error('[inquiry] submit failed:', err && (err.message || err));
          }
        })
        .then(function () {
          setBusy(form, false);
        });
    });
  });
})();
