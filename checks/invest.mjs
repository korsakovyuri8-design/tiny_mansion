/* Страницы инвесторам закрыты noindex и потому не попадают в sitemap, а
   значит и в остальные проверки, которые идут по нему. На них при этом стоят
   все деньги проекта. Здесь то же, что остальной набор делает для сайта:
   язык не течёт из одного в другой, ссылки ведут куда-то, заголовок и
   описание на месте, страница не едет вбок и не роняет скрипт. */
import pw from './pw.mjs';
import { serve } from './srv.mjs';

const PAGES = [
  ['/invest/en/', 'en', /[Ѐ-ӿ]/,  'кириллица в английской версии'],
  ['/invest/',    'ru', null,               null],
];
/* Латиница, которой на русской странице место. */
/* Метки на этой странице набраны через text-transform, поэтому innerText
   отдаёт их прописными — сравнение без учёта регистра, иначе «RESIDENCE 21FT»
   не совпадёт с записанным здесь именем модели. */
/* Длинное имя стирается раньше короткого: иначе «Grand Residence 24ft»
   теряет свой хвост на правиле для «Residence 24ft» и оставляет «Grand». */
const KEEP = [/Tiny Mansion/gi, /Korsakov Group(\s+d\.o\.o\.)?/gi,
  /Grand Residence 24ft/gi, /Residence 2\dft/gi, /\bRU\b|\bEN\b/g, /d\.o\.o\./gi, /[\w.+-]+@[\w.-]+/g,
  /\bPMS\b/gi, /\bI{1,3}V?\b/g];

await serve(8440);
const b = await pw.chromium.launch({ args: ['--no-proxy-server'] });
let bad = 0;
const no = m => { bad++; console.log('  ✗ ' + m); };
const ok = m => console.log('  ✓ ' + m);

for (const [u, lang, wrong, label] of PAGES) {
  console.log('\n' + u);
  for (const [w, h] of [[1280, 900], [390, 844]]) {
    const page = await b.newPage({ viewport: { width: w, height: h }, isMobile: w < 700 });
    const errs = [];
    page.on('pageerror', e => errs.push(String(e).slice(0, 120)));
    await page.route('**://fonts.g*.com/**', r => r.abort());
    const res = await page.goto('http://127.0.0.1:8440' + u, { waitUntil: 'networkidle' });
    if (!res || res.status() !== 200) no(w + 'px: HTTP ' + (res && res.status()));
    await page.waitForTimeout(250);

    const r = await page.evaluate(() => ({
      title: document.title,
      desc: (document.querySelector('meta[name=description]') || {}).content || '',
      lang: document.documentElement.lang,
      robots: (document.querySelector('meta[name=robots]') || {}).content || '',
      text: document.body.innerText,
      links: [...document.querySelectorAll('a[href^="/"]')].map(a => a.getAttribute('href')),
      over: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      tbl: [...document.querySelectorAll('table')].length,
    }));

    if (w === 1280) {
      r.title.length > 20 ? ok('заголовок: ' + r.title.slice(0, 60)) : no('заголовка нет');
      r.desc.length > 70 ? ok('описание, ' + r.desc.length + ' знаков') : no('описание короткое');
      r.lang === lang ? ok('lang="' + r.lang + '"') : no('lang="' + r.lang + '", ждали ' + lang);
      /noindex/.test(r.robots) ? ok('noindex на месте') : no('noindex нет: «' + r.robots + '»');
      r.tbl > 0 ? ok('таблиц: ' + r.tbl) : no('таблиц нет');

      if (wrong) {
        const hits = r.text.split('\n').filter(l => wrong.test(l)).slice(0, 5);
        hits.length ? hits.forEach(x => no(label + ': ' + x.slice(0, 60)))
                    : ok(label + ': нет');
      } else {
        const strip = t => KEEP.reduce((s, x) => s.replace(x, ''), t);
        const hits = r.text.split('\n').map(l => l.trim())
          .filter(l => l && /[A-Za-z]/.test(strip(l))).slice(0, 6);
        hits.length ? hits.forEach(x => no('латиница в русской версии: ' + x.slice(0, 60)))
                    : ok('латиница в русской версии: нет');
      }

      /* Ссылки должны вести на существующие адреса. */
      for (const href of [...new Set(r.links)]) {
        const h = await page.request.get('http://127.0.0.1:8440' + href.split('#')[0]);
        if (h.status() !== 200) no('ссылка ' + href + ' → HTTP ' + h.status());
      }
      ok('внутренних ссылок проверено: ' + new Set(r.links).size);
    }
    r.over > 1 ? no(w + 'px: едет вбок на ' + r.over) : ok(w + 'px: вбок не едет');
    errs.length ? no('ошибки скрипта: ' + errs.join(' | ')) : null;
    await page.close();
  }
}
console.log('\nнеудач: ' + bad);
await b.close(); process.exit(0);
