/* Слово, которое не влезает в ширину экрана, вылезает за рамку своего блока и
   тащит вбок весь документ. Рамка при этом остаётся на месте, поэтому обход по
   элементам такого не видит — нужен Range по текстовым узлам. */
import pw from './pw.mjs';
import { serve, pages } from './srv.mjs';
await serve(8403);
const b = await pw.chromium.launch({ args: ['--no-proxy-server'] });
const urls = pages();
let total = 0;
for (const w of [320, 360, 390]) {
  for (const lang of ['en', 'ru']) {
    const page = await b.newPage({ viewport: { width: w, height: 780 }, isMobile: true, hasTouch: true });
    await page.route('**://fonts.g*.com/**', r => r.abort());
    await page.addInitScript(l => { try { localStorage.setItem('tm-lang', l); } catch (e) {} }, lang);
    for (const u of urls) {
      await page.goto('http://127.0.0.1:8403' + u, { waitUntil: 'networkidle' });
      await page.waitForTimeout(120);
      const hits = await page.evaluate(vw => {
        const out = [];
        const view = document.querySelector('.view-section.active') || document.body;
        /* Обход останавливается на <body>: overflow на body и html не режет,
           а передаётся вьюпорту, поэтому страница всё равно едет вбок. */
        const clipped = el => {
          for (let p = el; p && p !== document.body; p = p.parentElement) {
            const ov = getComputedStyle(p).overflowX;
            if (ov === 'auto' || ov === 'scroll' || ov === 'hidden' || ov === 'clip') return true;
          }
          return false;
        };
        const tw = document.createTreeWalker(view, NodeFilter.SHOW_TEXT);
        let n;
        while ((n = tw.nextNode())) {
          if (!n.textContent.trim()) continue;
          if (clipped(n.parentElement)) continue;
          const r = document.createRange(); r.selectNodeContents(n);
          for (const box of r.getClientRects())
            if (box.right > vw + 1 || box.left < -1) {
              out.push(n.textContent.trim().slice(0, 40) + '  [' + n.parentElement.tagName +
                '] ' + Math.round(box.left) + '..' + Math.round(box.right));
              break;
            }
        }
        return [...new Set(out)];
      }, w);
      if (hits.length) { total += hits.length; console.log(w + 'px ' + lang + ' ' + u);
        hits.forEach(h => console.log('   ' + h)); }
    }
    await page.close();
  }
}
console.log('\nстрок, вылезающих за экран: ' + total);
await b.close(); process.exit(0);
