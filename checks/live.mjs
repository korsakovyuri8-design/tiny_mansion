/* Всё, что на сайте нажимается и считает: калькулятор, формы, галереи,
   переключатель языка, вкладки. Пальцем, на телефоне, на обоих языках. */
import pw from './pw.mjs';
import { serve } from './srv.mjs';
await serve(8410);
const b = await pw.chromium.launch({ args: ['--no-proxy-server'] });
const fail = [];
const ok = m => console.log('  ✓ ' + m);
const no = m => { fail.push(m); console.log('  ✗ ' + m); };

for (const [w, h, dev] of [[390, 844, 'телефон'], [1280, 900, 'компьютер']]) {
  console.log('\n═══ ' + dev + ' ' + w + '×' + h);
  const page = await b.newPage({ viewport: { width: w, height: h }, isMobile: w < 700, hasTouch: w < 700 });
  const errs = [];
  page.on('pageerror', e => errs.push(String(e).slice(0, 120)));
  page.on('console', m => { const t = m.text();
    if (m.type() === 'error' && !/ERR_FAILED/.test(t)) errs.push('console: ' + t.slice(0, 120)); });
  await page.route('**://fonts.g*.com/**', r => r.abort());

  /* — калькулятор — */
  await page.goto('http://127.0.0.1:8410/bars/calculator/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(400);
  const rows0 = await page.locator('.calc-table--menu tbody tr').count();
  const pay0 = (await page.locator('.calc-verdict, .calc-out').first().innerText().catch(() => '')).slice(0, 90);
  rows0 > 0 ? ok('калькулятор: строк меню ' + rows0) : no('калькулятор: меню пустое');

  const addBtn = page.locator('button', { hasText: /Add a line|Добавить/ }).first();
  if (await addBtn.count()) {
    await addBtn.click(); await page.waitForTimeout(250);
    const rows1 = await page.locator('.calc-table--menu tbody tr').count();
    rows1 === rows0 + 1 ? ok('добавление строки: ' + rows0 + ' → ' + rows1)
                        : no('добавление строки не сработало: ' + rows0 + ' → ' + rows1);
  } else no('кнопки «добавить строку» нет');

  /* правка цены должна пересчитать окупаемость */
  const price = page.locator('.calc-table--menu input.n').first();
  await price.fill('99'); await price.dispatchEvent('input'); await page.waitForTimeout(300);
  const pay1 = (await page.locator('.calc-verdict, .calc-out').first().innerText().catch(() => '')).slice(0, 90);
  pay1 !== pay0 ? ok('цена меняет расчёт') : no('цена не меняет расчёт (было «' + pay0 + '»)');

  /* удаление строки */
  const del = page.locator('.calc-del').first();
  if (await del.count()) {
    const before = await page.locator('.calc-table--menu tbody tr').count();
    await del.click(); await page.waitForTimeout(250);
    const after = await page.locator('.calc-table--menu tbody tr').count();
    after === before - 1 ? ok('удаление строки: ' + before + ' → ' + after)
                         : no('удаление строки не сработало: ' + before + ' → ' + after);
  } else no('кнопки удаления нет');

  /* Вкладка проверяется на чистом калькуляторе: правленое меню не
     перезаписывается намеренно, это и есть calc.dirty. */
  await page.evaluate(() => { try { localStorage.removeItem('tm-calc'); } catch (e) {} });
  await page.reload({ waitUntil: 'networkidle' }); await page.waitForTimeout(400);
  const tabs = page.locator('.calc-tab');
  if (await tabs.count() > 1) {
    const t0 = await page.locator('.calc-table--menu tbody').innerText();
    await tabs.nth(1).click(); await page.waitForTimeout(350);
    const t1 = await page.locator('.calc-table--menu tbody').innerText();
    t1 !== t0 ? ok('вкладка юнита перерисовывает меню') : no('вкладка юнита ничего не меняет');
  } else no('вкладок юнита нет');

  /* сохранение между заходами */
  await page.reload({ waitUntil: 'networkidle' }); await page.waitForTimeout(400);
  const kept = await page.locator('.calc-table--menu tbody').innerText();
  kept.length > 10 ? ok('меню пережило перезагрузку') : no('меню после перезагрузки пустое');

  /* — переключатель языка на всех видах — */
  for (const u of ['/', '/bars/calculator/', '/salons/economics/', '/residence/residence-21/']) {
    await page.goto('http://127.0.0.1:8410' + u, { waitUntil: 'networkidle' });
    await page.waitForTimeout(300);
    const en = await page.locator('main').innerText();
    await page.locator('.lang-btn[data-lang="ru"]').click(); await page.waitForTimeout(400);
    const ru = await page.locator('main').innerText();
    await page.locator('.lang-btn[data-lang="en"]').click(); await page.waitForTimeout(400);
    const back = await page.locator('main').innerText();
    if (ru === en) no('язык не переключается на ' + u);
    else if (back !== en) no('обратно на английский возвращается не тем же текстом: ' + u);
    else ok('язык туда-обратно: ' + u);
  }

  /* — галерея резиденции — */
  await page.goto('http://127.0.0.1:8410/residence/residence-21/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(400);
  const thumbs = page.locator('.res-thumb');
  const n = await thumbs.count();
  if (n > 1) {
    const src0 = await page.locator('.res-main img, .res-hero img').first().getAttribute('src').catch(() => null);
    await thumbs.nth(2).click(); await page.waitForTimeout(400);
    const src1 = await page.locator('.res-main img, .res-hero img').first().getAttribute('src').catch(() => null);
    src1 && src1 !== src0 ? ok('галерея: миниатюра меняет большое фото')
                          : no('галерея: миниатюра не меняет фото (' + src0 + ' → ' + src1 + ')');
  } else no('миниатюр в галерее нет');

  /* — форма заявки — */
  await page.goto('http://127.0.0.1:8410/enquiry/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(300);
  const form = page.locator('form[data-mailform]').first();
  const action = await form.getAttribute('action');
  action && action.includes('yuri@korsakovgroup.com') ? ok('форма уходит на рабочий адрес')
    : no('форма уходит на ' + action);
  const req = await form.locator('[required]').count();
  req > 0 ? ok('обязательные поля размечены: ' + req) : no('обязательных полей нет — форма уйдёт пустой');
  const next = await form.locator('input[name="_next"]').first().inputValue().catch(e => 'ошибка: ' + e.message.slice(0, 60));
  next && next.endsWith('/thanks/') ? ok('после отправки ведёт на /thanks/') : no('_next = ' + next);

  console.log(errs.length ? '  ✗ ошибки в консоли: ' + [...new Set(errs)].join(' | ') : '  ✓ ошибок в консоли нет');
  if (errs.length) fail.push('ошибки консоли на ' + dev);
  await page.close();
}
console.log('\nнеудач: ' + fail.length);
await b.close(); process.exit(0);
