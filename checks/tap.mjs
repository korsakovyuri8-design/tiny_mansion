/* Палец — не курсор. Всё, что нажимается, должно быть не меньше 44×44 CSS-px
   и не стоять вплотную к соседу: иначе на телефоне промахиваешься. Ссылки
   внутри абзаца из этого исключены — там мерилом служит строка, а не кнопка. */
import pw from './pw.mjs';
import { serve, pages } from './srv.mjs';
await serve(8406);
const b = await pw.chromium.launch({ args: ['--no-proxy-server'] });
const urls = pages();
const small = new Map(), tight = new Map();
for (const lang of ['en', 'ru']) {
  const page = await b.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  await page.route('**://fonts.g*.com/**', r => r.abort());
  await page.addInitScript(l => { try { localStorage.setItem('tm-lang', l); } catch (e) {} }, lang);
  for (const u of urls) {
    await page.goto('http://127.0.0.1:8406' + u, { waitUntil: 'networkidle' });
    await page.waitForTimeout(150);
    const r = await page.evaluate(() => {
      const sel = 'a, button, [role="button"], input, select, textarea, summary, [tabindex]:not([tabindex="-1"])';
      const inProse = el => !!el.closest('p, li, dd, figcaption, .prose, .fig-note, .form-hint, .breadcrumbs');
      const boxes = [], small = [];
      for (const el of document.querySelectorAll(sel)) {
        const b = el.getBoundingClientRect();
        if (b.width < 1 || b.height < 1) continue;
        if (getComputedStyle(el).visibility === 'hidden') continue;
        const name = el.tagName + '.' + (el.className || '').toString().split(' ')[0]
          + ' «' + (el.textContent || el.getAttribute('aria-label') || '').trim().slice(0, 24) + '»';
        if (!inProse(el) && (b.width < 24 || b.height < 24))
          small.push(name + '  ' + Math.round(b.width) + '×' + Math.round(b.height));
        if (!inProse(el)) boxes.push({ name, b: { x: b.x, y: b.y, w: b.width, h: b.height } });
      }
      /* Соседи ближе 8px по обеим осям — промах гарантирован. */
      const tight = [];
      for (let i = 0; i < boxes.length; i++)
        for (let j = i + 1; j < boxes.length; j++) {
          const a = boxes[i].b, c = boxes[j].b;
          const dx = Math.max(0, Math.max(a.x, c.x) - Math.min(a.x + a.w, c.x + c.w));
          const dy = Math.max(0, Math.max(a.y, c.y) - Math.min(a.y + a.h, c.y + c.h));
          const smallish = m => m.w < 44 || m.h < 44;
          if (dx < 8 && dy < 8 && !(dx === 0 && dy === 0) && (smallish(a) || smallish(c)))
            tight.push(boxes[i].name + '  ↔  ' + boxes[j].name + '  ' + Math.round(dx) + '/' + Math.round(dy) + 'px');
        }
      return { small: [...new Set(small)], tight: [...new Set(tight)] };
    });
    for (const x of r.small) small.set(x, (small.get(x) || 0) + 1);
    for (const x of r.tight) tight.set(x, (tight.get(x) || 0) + 1);
  }
  await page.close();
}
const show = (title, m) => {
  console.log('\n' + title + ': ' + m.size);
  [...m.entries()].sort((a, b) => b[1] - a[1]).slice(0, 25)
    .forEach(([k, n]) => console.log('  ×' + String(n).padStart(3) + '  ' + k));
};
show('меньше 24×24 (WCAG 2.5.8 AA)', small);
show('вплотную к соседу', tight);
await b.close(); process.exit(0);
