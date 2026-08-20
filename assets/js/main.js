/* ==========================================================================
   JSOA LP
   1. CTA の遷移先を index.html の window.JSOA_CTA_URL から一括適用
   2. SP: スクロールに追従する CTA の出し入れ
   ========================================================================== */
(function () {
  'use strict';

  /* ---------- 1. CTA リンクの一括適用 ---------- */
  var url = (window.JSOA_CTA_URL || '').trim();
  var ctas = document.querySelectorAll('[data-cta]');

  Array.prototype.forEach.call(ctas, function (el) {
    if (url) {
      el.setAttribute('href', url);
      // 外部サイトへ飛ばす場合は別タブで開く
      if (/^https?:\/\//i.test(url) && url.indexOf(location.host) === -1) {
        el.setAttribute('target', '_blank');
        el.setAttribute('rel', 'noopener');
      }
    } else {
      // 遷移先が未設定のうちは遷移させない（ページ先頭へ飛ぶのを防ぐ）
      el.setAttribute('href', '#');
      el.addEventListener('click', function (e) { e.preventDefault(); });
    }
  });

  /* ---------- 2. SP 追従CTA ---------- */
  var bar = document.getElementById('stickycta');
  var hero = document.querySelector('.hero');
  var footer = document.querySelector('.footer');
  if (!bar || !hero || !footer) return;

  var isMobile = function () { return window.matchMedia('(max-width: 767px)').matches; };

  var heroPassed = false;
  var footerShown = false;

  function render() {
    if (!isMobile()) {
      bar.hidden = true;
      bar.classList.remove('is-visible');
      document.body.classList.remove('has-stickycta');
      return;
    }
    var show = heroPassed && !footerShown;
    bar.hidden = false;
    bar.classList.toggle('is-visible', show);
    document.body.classList.toggle('has-stickycta', show);
  }

  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      heroPassed = !entries[0].isIntersecting;
      render();
    }, { rootMargin: '-40% 0px 0px 0px' }).observe(hero);

    new IntersectionObserver(function (entries) {
      footerShown = entries[0].isIntersecting;
      render();
    }).observe(footer);
  } else {
    // IntersectionObserver 非対応時のフォールバック
    window.addEventListener('scroll', function () {
      heroPassed = window.pageYOffset > hero.offsetHeight * 0.6;
      footerShown = window.pageYOffset + window.innerHeight >= footer.offsetTop;
      render();
    }, { passive: true });
  }

  window.addEventListener('resize', render);
  render();
})();
