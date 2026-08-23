/* ==========================================================
   СЧЁТЧИК
   ==========================================================
   Пока обе строки ниже пустые — не грузится ничего и наружу
   не уходит ни одного запроса. Страница работает как работала.

   Чтобы включить, заполните SRC и ID:

     Plausible   SRC = 'https://plausible.io/js/script.js'
                 ID  = 'tinymansion.co'          (домен)

     Umami       SRC = 'https://cloud.umami.is/script.js'
                 ID  = 'xxxxxxxx-xxxx-...'       (website id)

   Оба считают без куки и без сбора персональных данных, поэтому
   баннер согласия не нужен и текст на странице приватности —
   «мы не ставим отслеживающих куки» — остаётся правдой.
   ========================================================== */
(function () {
  var SRC = '';
  var ID  = '';

  /* События, которые шлём: отправка формы и то, дочитали ли
     инвест-страницу. Без счётчика track() просто ничего не делает. */
  window.track = function (name, props) {
    try {
      if (window.plausible) window.plausible(name, props ? { props: props } : undefined);
      else if (window.umami) window.umami.track(name, props);
    } catch (e) { /* счётчик не должен ломать страницу */ }
  };

  if (!SRC || !ID) return;

  var s = document.createElement('script');
  s.defer = true;
  s.src = SRC;
  /* Plausible читает data-domain, Umami — data-website-id. Ставим оба:
     каждый берёт своё и игнорирует чужое. */
  s.setAttribute('data-domain', ID);
  s.setAttribute('data-website-id', ID);
  document.head.appendChild(s);

  /* Заглушка на время загрузки скрипта, чтобы ранние события не потерялись. */
  window.plausible = window.plausible || function () {
    (window.plausible.q = window.plausible.q || []).push(arguments);
  };

  /* Глубина прокрутки — только там, где она что-то значит: длинная
     страница, которую либо дочитывают, либо нет. Каждый рубеж один раз. */
  if (location.pathname.indexOf('/invest') === 0) {
    var marks = [25, 50, 75, 100], seen = {};
    var onScroll = function () {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      if (h <= 0) return;
      var pct = (window.scrollY / h) * 100;
      for (var i = 0; i < marks.length; i++) {
        var m = marks[i];
        if (pct >= m && !seen[m]) { seen[m] = 1; window.track('invest_scroll_' + m); }
      }
      if (seen[100]) window.removeEventListener('scroll', onScroll);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
  }
})();
