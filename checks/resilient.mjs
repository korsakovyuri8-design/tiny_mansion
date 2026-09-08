/* Что видит человек, у которого что-то не сработало: выключен JavaScript,
   не доехал /ru.js, нажата кнопка «назад». */
import pw from './pw.mjs';
import { serve } from './srv.mjs';
await serve(8411);                       /* обычный */
await serve(8412, { block: /^\/ru\.js$/ });  /* словарь недоступен */
const b = await pw.chromium.launch({ args: ['--no-proxy-server'] });
const fail = [];
const ok = m => console.log('  ✓ ' + m);
const no = m => { fail.push(m); console.log('  ✗ ' + m); };

/* ── 1. Без JavaScript ── */
console.log('\n═══ JavaScript выключен');
{
  const ctx = await b.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage();
  await page.route('**://fonts.g*.com/**', r => r.abort());
  for (const u of ['/', '/bars/', '/salons/economics/', '/enquiry/', '/residence/residence-21/']) {
    await page.goto('http://127.0.0.1:8411' + u, { waitUntil: 'domcontentloaded' });
    const r = await page.evaluate(() => {
      const v = document.querySelector('.view-section.active');
      const txt = v ? v.innerText.trim() : '';
      const shown = [...document.querySelectorAll('.view-section')]
        .filter(s => getComputedStyle(s).display !== 'none').length;
      return { len: txt.length, shown, head: txt.slice(0, 60).replace(/\n/g, ' '),
               note: (document.querySelector('noscript') ? 'есть' : 'нет') };
    });
    r.len > 300 && r.shown === 1
      ? ok(u + ': видна одна страница, ' + r.len + ' знаков — «' + r.head + '…»')
      : no(u + ': видимых секций ' + r.shown + ', знаков ' + r.len);
  }
  /* Почта без скрипта пишется вручную — она должна быть на странице */
  await page.goto('http://127.0.0.1:8411/', { waitUntil: 'domcontentloaded' });
  /* Их несколько: первый — стиль для reveal, адрес в другом. */
  const ns = (await page.locator('noscript').allInnerTexts().catch(() => []))
    .concat(await page.evaluate(() => [...document.querySelectorAll('noscript')].map(n => n.innerHTML)))
    .join(' ');
  /korsakovgroup/.test(ns) ? ok('без скрипта на странице есть адрес почты')
                           : no('без скрипта адреса почты нет');
  /* И что именно видно на странице резиденции без скрипта. */
  await page.goto('http://127.0.0.1:8411/residence/residence-21/', { waitUntil: 'domcontentloaded' });
  const rt = await page.evaluate(() => {
    const v = document.querySelector('.view-section.active');
    return v.innerText.replace(/\n{2,}/g, ' | ').slice(0, 400);
  });
  console.log('    страница резиденции без скрипта: ' + rt);
  await ctx.close();
}

/* ── 2. /ru.js не отдаётся ── */
console.log('\n═══ словарь /ru.js недоступен');
{
  const page = await b.newPage({ viewport: { width: 390, height: 844 } });
  const errs = [];
  page.on('pageerror', e => errs.push(String(e).slice(0, 100)));
  await page.route('**://fonts.g*.com/**', r => r.abort());
  await page.addInitScript(() => { try { localStorage.setItem('tm-lang', 'ru'); } catch (e) {} });
  await page.goto('http://127.0.0.1:8412/bars/economics/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(600);
  const r = await page.evaluate(() => {
    const v = document.querySelector('.view-section.active');
    return { len: v ? v.innerText.trim().length : 0, cyr: /[А-Яа-я]/.test(v ? v.innerText : ''),
             lang: document.documentElement.lang };
  });
  r.len > 300 ? ok('страница читается: ' + r.len + ' знаков, язык «' + r.lang + '», кириллица: ' + (r.cyr ? 'есть' : 'нет'))
              : no('страница пустая при недоступном словаре');
  errs.length ? no('ошибки: ' + errs.join(' | ')) : ok('без ошибок');
  /* Переключение на английский всё равно должно работать */
  await page.locator('.lang-btn[data-lang="en"]').click(); await page.waitForTimeout(400);
  const en = await page.locator('main').innerText();
  en.length > 300 ? ok('на английский переключается') : no('на английский не переключается');
  await page.close();
}

/* ── 3. Назад / вперёд ── */
console.log('\n═══ кнопки «назад» и «вперёд»');
{
  const page = await b.newPage({ viewport: { width: 390, height: 844 } });
  await page.route('**://fonts.g*.com/**', r => r.abort());
  await page.goto('http://127.0.0.1:8411/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(300);
  const trail = [];
  for (const sel of ['a[href="/bars/"]', 'a[href="/salons/"]', 'a[href="/about/"]']) {
    await page.locator(sel).first().click(); await page.waitForTimeout(450);
    trail.push(await page.evaluate(() => location.pathname));
  }
  const seen = [];
  for (let i = 0; i < 3; i++) {
    await page.goBack(); await page.waitForTimeout(450);
    seen.push(await page.evaluate(() => location.pathname + '|' +
      (document.querySelector('.view-section.active') || {}).id));
  }
  const want = ['/salons/|view-salons', '/bars/|view-units', '/|view-home'];
  seen.every((v, i) => v.split('|')[0] === want[i].split('|')[0])
    ? ok('назад: ' + seen.join(' → '))
    : no('назад ведёт не туда: ' + seen.join(' → ') + '  (ждали ' + want.join(' → ') + ')');
  await page.goForward(); await page.waitForTimeout(450);
  const fwd = await page.evaluate(() => location.pathname + '|' +
    ((document.querySelector('.view-section.active') || {}).id || '?'));
  fwd.startsWith('/bars/') ? ok('вперёд: ' + fwd) : no('вперёд ведёт не туда: ' + fwd);
  await page.close();
}

console.log('\nнеудач: ' + fail.length);
await b.close(); process.exit(0);
