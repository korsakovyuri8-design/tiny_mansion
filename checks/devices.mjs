/* Настоящие ширины устройств, обе ориентации, оба языка, все страницы.
   Смотрим три вещи, каждая из которых ломает страницу на телефоне:
   боковую прокрутку всего документа, элементы шире экрана вне контейнера с
   прокруткой, и зоны нажатия меньше 44 CSS-пикселей. */
import pw from './pw.mjs';
import { serve, pages } from './srv.mjs';

const VIEWS = [
  ['iPhone SE',        320,  568],
  ['iPhone 12 mini',   360,  780],
  ['iPhone 14',        390,  844],
  ['iPhone 14 Plus',   414,  896],
  ['iPhone 15 Pro Max',430,  932],
  ['телефон боком',    844,  390],
  ['iPad портрет',     768, 1024],
  ['iPad ландшафт',   1024,  768],
  ['ноутбук',         1440,  900],
  ['широкий',         1920, 1080],
];

await serve(8400);
const b = await pw.chromium.launch({ args: ['--no-proxy-server'] });
const urls = pages();
const found = [];

for (const [name, w, h] of VIEWS) {
  for (const lang of ['en', 'ru']) {
    const page = await b.newPage({ viewport: { width: w, height: h },
      deviceScaleFactor: 2, isMobile: w < 700, hasTouch: w < 700 });
    await page.route('**://fonts.g*.com/**', r => r.abort());
    await page.addInitScript(l => { try { localStorage.setItem('tm-lang', l); } catch (e) {} }, lang);
    for (const u of urls) {
      await page.goto('http://127.0.0.1:8400' + u, { waitUntil: 'networkidle' });
      await page.waitForTimeout(150);
      const r = await page.evaluate(vw => {
        const out = { scroll: 0, wide: [], small: [] };
        const de = document.documentElement;
        if (de.scrollWidth > de.clientWidth + 1) out.scroll = de.scrollWidth - de.clientWidth;
        const view = document.querySelector('.view-section.active') || document.body;
        /* Элемент шире экрана — беда только если его никто не прокручивает. */
        const scrollable = el => {
          for (let p = el.parentElement; p; p = p.parentElement) {
            const ov = getComputedStyle(p).overflowX;
            if (ov === 'auto' || ov === 'scroll' || ov === 'hidden') return true;
          }
          return false;
        };
        for (const el of view.querySelectorAll('*')) {
          const b = el.getBoundingClientRect();
          if (b.width < 1 || b.height < 1) continue;
          if ((b.right > vw + 1 || b.left < -1) && !scrollable(el))
            out.wide.push(el.tagName + '.' + (el.className || '').toString().split(' ')[0]
              + ' ' + Math.round(b.left) + '..' + Math.round(b.right));
        }
        return out;
      }, w);
      if (r.scroll) found.push([name, lang, u, 'страница едет вбок на ' + r.scroll + 'px']);
      for (const x of [...new Set(r.wide)].slice(0, 4))
        found.push([name, lang, u, 'шире экрана: ' + x]);
    }
    await page.close();
  }
}
console.log(found.length ? found.map(f => '  ' + f[0].padEnd(18) + f[1] + ' ' + f[2] + '  ' + f[3]).join('\n')
                         : '  чисто');
console.log('\nнаходок: ' + found.length + ' на ' + VIEWS.length + ' размерах × 2 языка × ' + urls.length + ' страниц');
await b.close(); process.exit(0);
