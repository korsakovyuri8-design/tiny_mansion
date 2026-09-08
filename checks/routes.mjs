import pw from './pw.mjs';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(new URL('..', import.meta.url).pathname);
const PORT = 8155;
const TYPES = { '.html':'text/html; charset=utf-8', '.js':'text/javascript', '.css':'text/css',
  '.jpg':'image/jpeg', '.png':'image/png', '.xml':'application/xml', '.txt':'text/plain' };

/* Behaves like GitHub Pages: a real file or a real 404 with 404.html. */
const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (!path.extname(p)) p = p.replace(/\/?$/, '/') + 'index.html';
  const file = path.join(ROOT, p);
  if (file.startsWith(ROOT) && fs.existsSync(file) && !fs.statSync(file).isDirectory()) {
    res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream' });
    fs.createReadStream(file).pipe(res);
  } else {
    res.writeHead(404, { 'content-type': 'text/html; charset=utf-8' });
    res.end(fs.readFileSync(path.join(ROOT, '404.html')));
  }
});
await new Promise(r => server.listen(PORT, r));
const B = 'http://127.0.0.1:' + PORT;

const browser = await pw.chromium.launch({ args: ['--no-proxy-server'] });
const page = await browser.newPage();
const errs = [];
page.on('pageerror', e => errs.push(String(e)));
await page.route('**://fonts.g*.com/**', r => r.abort());

const bad404 = [];
page.on('response', r => {
  if (r.status() >= 400 && new URL(r.url()).origin === B) bad404.push(r.status() + ' ' + r.url());
});

const state = () => page.evaluate(() => ({
  path: location.pathname + location.hash,
  view: (document.querySelector('.view-section.active') || {}).id,
  title: document.title,
  canonical: (document.querySelector('link[rel=canonical]') || {}).href,
  h1: (document.querySelector('.view-section.active h1') || {}).innerText
}));

console.log('--- deep links land on the right view (hard load) ---');
for (const p of ['/', '/residences/', '/farms/', '/about/', '/terms/', '/privacy/',
                 '/enquiry/', '/host/', '/country/montenegro/', '/residence/residence-21/',
                 '/farm/f-pony/']) {
  await page.goto(B + p, { waitUntil: 'networkidle' });
  const s = await state();
  const ok = s.path === p && s.canonical === 'https://tinymansion.co' + p;
  console.log((ok ? '  ok   ' : '  FAIL ') + p.padEnd(26) + (s.view || '-').padEnd(18) + s.title);
}

console.log('\n--- clicking through, no reload ---');
await page.goto(B + '/', { waitUntil: 'networkidle' });
let reloads = 0;
page.on('load', () => reloads++);
for (const [label, sel] of [['Residences', 'header a[href="/residences/"]'],
                            ['Farms', 'header a[href="/farms/"]'],
                            ['About', 'header a[href="/about/"]'],
                            ['Enquire', 'header a[href="/enquiry/"]']]) {
  await page.click(sel);
  await page.waitForTimeout(200);
  const s = await state();
  console.log('  ' + label.padEnd(12) + s.path.padEnd(18) + (s.view || '-').padEnd(18) + s.title);
}
console.log('  full page loads during that: ' + reloads + ' (want 0)');

console.log('\n--- back button walks it back ---');
for (let i = 0; i < 4; i++) {
  await page.goBack();
  await page.waitForTimeout(180);
  const s = await state();
  console.log('  back -> ' + s.path.padEnd(18) + (s.view || '-').padEnd(18) + s.title);
}

console.log('\n--- a card opens a real address ---');
await page.goto(B + '/', { waitUntil: 'networkidle' });
await page.click('.country-panel');
await page.waitForTimeout(250);
console.log('  country panel -> ' + JSON.stringify(await state(), null, 0).slice(0, 160));
await page.click('#tabbtn-farms'); await page.waitForTimeout(150); await page.click('.farm-card');
await page.waitForTimeout(250);
console.log('  farm card     -> ' + JSON.stringify(await state(), null, 0).slice(0, 160));

console.log('\n--- addresses shared while the site used #/ ---');
for (const h of ['/#/about', '/#/all-farms', '/#/country/montenegro', '/#/residence/residence-21', '/#/farm/f-pony']) {
  await page.goto(B + h, { waitUntil: 'networkidle' });
  await page.waitForTimeout(200);
  const s = await state();
  console.log('  ' + h.padEnd(30) + '-> ' + s.path.padEnd(26) + (s.view || '-'));
}

console.log('\n--- nonsense addresses ---');
for (const p of ['/country/atlantis/', '/farm/nope/', '/does-not-exist/']) {
  const r = await page.goto(B + p, { waitUntil: 'networkidle' });
  await page.waitForTimeout(150);
  const s = await state();
  console.log('  ' + p.padEnd(22) + 'HTTP ' + r.status() + '  -> ' + s.path.padEnd(12) + ' ' + s.title);
}

console.log('\n--- in-page anchor ---');
await page.goto(B + '/', { waitUntil: 'networkidle' });
await page.click('a[href="#choose-country"]');
await page.waitForTimeout(400);
console.log('  scrolled to: ' + await page.evaluate(() => Math.round(window.scrollY)) + 'px, path ' + (await state()).path);
await page.goto(B + '/about/', { waitUntil: 'networkidle' });
await page.click('footer a[href="/#choose-country"]');
await page.waitForTimeout(500);
console.log('  from /about/ -> ' + (await state()).path + ', scrollY ' + await page.evaluate(() => Math.round(window.scrollY)));

console.log('\n--- images resolve from a nested address ---');
bad404.length = 0;
await page.goto(B + '/residence/residence-21/', { waitUntil: 'networkidle' });
await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
await page.waitForTimeout(900);
console.log('  broken requests: ' + (bad404.length ? bad404.join('\n    ') : 'none'));

console.log('\n--- language switch still round-trips on a built page ---');
await page.goto(B + '/farm/f-pony/', { waitUntil: 'networkidle' });
const en = await page.evaluate(() => document.querySelector('.view-section.active').innerText);
await page.click('.lang-btn[data-lang="ru"]'); await page.waitForTimeout(250);
const ru = await page.evaluate(() => document.querySelector('.view-section.active').innerText);
await page.click('.lang-btn[data-lang="en"]'); await page.waitForTimeout(250);
const en2 = await page.evaluate(() => document.querySelector('.view-section.active').innerText);
console.log('  ru differs: ' + (ru !== en) + ', en restored exactly: ' + (en === en2));

console.log('\n--- scroll reveal still fires on a built page ---');
await page.goto(B + '/', { waitUntil: 'networkidle' });
const hidden0 = await page.evaluate(() => document.querySelectorAll('.reveal:not(.in)').length);
const H = await page.evaluate(() => document.body.scrollHeight);
for (let y = 0; y * 400 < H + 1200; y++) {
  await page.evaluate(v => window.scrollTo({ top: v, behavior: 'instant' }), y * 400);
  await page.waitForTimeout(200);
}
await page.waitForTimeout(600);
const hidden1 = await page.evaluate(() =>
  [...document.querySelectorAll('.reveal:not(.in)')].filter(e => e.offsetParent !== null).length);
console.log('  hidden before scrolling: ' + hidden0 + ', still hidden after: ' + hidden1 + ' (want 0)');

console.log('\nPAGE ERRORS: '  + (errs.length ? errs.join('; ') : 'none'));
await browser.close();
server.close();
