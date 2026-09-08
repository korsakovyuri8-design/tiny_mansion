/* Шапка липкая, значит якорь может увести цель под неё. Проверка кликает
   каждую внутристраничную ссылку и смотрит, где оказался заголовок цели
   относительно нижнего края шапки. */
import pw from './pw.mjs';
import { serve, pages } from './srv.mjs';
await serve(8409);
const b = await pw.chromium.launch({ args: ['--no-proxy-server'] });
const bad = [];
for (const [w, h, tag] of [[390, 844, 'телефон'], [1280, 900, 'компьютер']]) {
  for (const lang of ['en', 'ru']) {
    const page = await b.newPage({ viewport: { width: w, height: h } });
    await page.route('**://fonts.g*.com/**', r => r.abort());
    await page.addInitScript(l => { try { localStorage.setItem('tm-lang', l); } catch (e) {} }, lang);
    for (const u of pages()) {
      await page.goto('http://127.0.0.1:8409' + u, { waitUntil: 'networkidle' });
      await page.waitForTimeout(150);
      const hrefs = await page.evaluate(() => [...document.querySelectorAll('.view-section.active a[href*="#"]')]
        .map(a => a.getAttribute('href')).filter(h => /#\w/.test(h)));
      for (const href of [...new Set(hrefs)]) {
        const id = href.split('#')[1];
        await page.goto('http://127.0.0.1:8409' + u, { waitUntil: 'networkidle' });
        await page.waitForTimeout(120);
        const ok = await page.evaluate(async ([href, id]) => {
          const a = [...document.querySelectorAll('a[href$="#' + id + '"]')][0];
          if (!a) return { skip: true };
          a.click();
          await new Promise(r => setTimeout(r, 700));
          const t = document.getElementById(id);
          if (!t) return { missing: true };
          const hd = document.querySelector('header').getBoundingClientRect();
          return { top: Math.round(t.getBoundingClientRect().top), header: Math.round(hd.bottom) };
        }, [href, id]);
        if (ok.skip) continue;
        if (ok.missing) { bad.push(tag + ' ' + lang + ' ' + u + ' → #' + id + ': такого id на странице нет'); continue; }
        if (ok.top < ok.header - 2)
          bad.push(tag + ' ' + lang + ' ' + u + ' → #' + id + ': цель на ' + ok.top +
                   'px, шапка кончается на ' + ok.header + 'px — ушла под неё на ' + (ok.header - ok.top) + 'px');
      }
    }
    await page.close();
  }
}
console.log(bad.length ? bad.join('\n') : 'все внутристраничные якоря встают под шапкой, не за ней');
console.log('\nнаходок: ' + bad.length);
await b.close(); process.exit(0);
