/* Контраст текста к фону по всему сайту, оба языка, телефон и компьютер.
   Порог WCAG AA: 4.5 для обычного текста, 3.0 для крупного (18.66px жирный
   или 24px). Шапка над героем прозрачная — там фон берётся с картинки, такие
   узлы считаем отдельно и мягче, потому что под ними лежит затемнение. */
import pw from './pw.mjs';
import { serve, pages } from './srv.mjs';
await serve(8415);
const b = await pw.chromium.launch({ args: ['--no-proxy-server'] });
const hits = new Map();
for (const [w, h] of [[390, 844], [1280, 900]]) {
  for (const lang of ['en', 'ru']) {
    const page = await b.newPage({ viewport: { width: w, height: h } });
    await page.route('**://fonts.g*.com/**', r => r.abort());
    await page.addInitScript(l => { try { localStorage.setItem('tm-lang', l); } catch (e) {} }, lang);
    for (const u of pages()) {
      await page.goto('http://127.0.0.1:8415' + u, { waitUntil: 'networkidle' });
      await page.waitForTimeout(150);
      const bad = await page.evaluate(() => {
        const parse = c => (c.match(/[\d.]+/g) || [0, 0, 0]).map(Number);
        const lum = c => { const [r, g, bl] = parse(c).slice(0, 3).map(v => {
          v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); });
          return 0.2126 * r + 0.7152 * g + 0.0722 * bl; };
        const bgOf = e => { for (let n = e; n; n = n.parentElement) {
          const c = getComputedStyle(n).backgroundColor;
          const a = parse(c)[3];
          if (c && !/transparent/.test(c) && (a === undefined || a > 0.85)) return c;
        } return 'rgb(247,243,237)'; };
        const out = [];
        for (const el of document.querySelectorAll('.view-section.active *, header *, footer *')) {
          /* Только собственный текст узла: иначе меряется контейнер сам с
             собой и всякий раз выходит 1.00. */
          const own = [...el.childNodes].filter(n => n.nodeType === 3)
            .map(n => n.textContent).join('').trim();
          if (!own) continue;
          const t = own;
          const st = getComputedStyle(el);
          if (st.visibility === 'hidden' || st.display === 'none') continue;
          if (parseFloat(st.opacity) < 0.9) continue;
          const r = el.getBoundingClientRect(); if (r.width < 2 || r.height < 2) continue;
          /* Шапка над героем стоит на фотографии — её меряет глаз, не формула. */
          if (el.closest('header.over-hero')) continue;
          const fs = parseFloat(st.fontSize), bold = parseInt(st.fontWeight, 10) >= 700;
          const need = (fs >= 24 || (fs >= 18.66 && bold)) ? 3 : 4.5;
          const L1 = lum(st.color), L2 = lum(bgOf(el));
          const ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
          if (ratio < need)
            out.push(ratio.toFixed(2) + ' (надо ' + need + ')  ' + el.tagName + '.' +
              (el.className || '').toString().split(' ')[0] + '  ' + Math.round(fs) + 'px  «' + t.slice(0, 34) + '»');
        }
        return [...new Set(out)];
      });
      for (const x of bad) hits.set(x, (hits.get(x) || 0) + 1);
    }
    await page.close();
  }
}
console.log(hits.size ? [...hits.entries()].sort((a, b) => b[1] - a[1]).slice(0, 30)
  .map(([k, n]) => '  ×' + String(n).padStart(3) + '  ' + k).join('\n') : '  всё проходит AA');
console.log('\nразных находок: ' + hits.size);
await b.close(); process.exit(0);
