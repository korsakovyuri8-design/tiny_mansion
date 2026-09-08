import pw from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';

const ROOT = path.resolve(new URL('..', import.meta.url).pathname);
const TY = { '.html':'text/html; charset=utf-8', '.js':'text/javascript', '.jpg':'image/jpeg',
             '.png':'image/png', '.xml':'application/xml', '.txt':'text/plain' };
const srv = http.createServer((q, r) => {
  let p = decodeURIComponent(q.url.split('?')[0]);
  if (!path.extname(p)) p = p.replace(/\/?$/, '/') + 'index.html';
  const f = path.join(ROOT, p);
  if (fs.existsSync(f) && !fs.statSync(f).isDirectory()) {
    r.writeHead(200, { 'content-type': TY[path.extname(f)] || 'application/octet-stream' });
    fs.createReadStream(f).pipe(r);
  } else { r.writeHead(404); r.end(fs.readFileSync(path.join(ROOT, '404.html'))); }
});
await new Promise(r => srv.listen(8177, r));
const B = 'http://127.0.0.1:8177';

const b = await pw.chromium.launch({ args: ['--no-proxy-server'] });
const page = await b.newPage();
await page.route('**://fonts.g*.com/**', r => r.abort());
const errs = [];
page.on('pageerror', e => errs.push(String(e)));
const broken = new Set();
page.on('response', r => {
  if (r.status() >= 400 && r.url().startsWith(B)) broken.add(r.status() + ' ' + r.url().slice(B.length));
});

/* Every address in the sitemap, plus the two pages kept out of it. */
const sitemap = fs.readFileSync(path.join(ROOT, 'sitemap.xml'), 'utf8');
const pages = [...sitemap.matchAll(/<loc>https:\/\/tinymansion\.co([^<]*)<\/loc>/g)].map(m => m[1]);
pages.push('/thanks/', '/invest/', '/invest/en/');

const linkTargets = new Set();
let checked = 0;
for (const p of pages) {
  const res = await page.goto(B + p, { waitUntil: 'networkidle' });
  if (res.status() !== 200) { console.log('  NOT 200: ' + p + ' -> ' + res.status()); continue; }
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(500);
  const hrefs = await page.evaluate(() => [...document.querySelectorAll('a[href]')]
    .map(a => a.getAttribute('href'))
    .filter(h => h && h[0] === '/'));
  hrefs.forEach(h => linkTargets.add(h.split('#')[0]));
  checked++;
}
console.log(checked + ' pages loaded, ' + linkTargets.size + ' distinct internal link targets');

console.log('\ninternal links that do not resolve:');
let dead = 0;
for (const t of [...linkTargets].sort()) {
  const r = await page.goto(B + t, { waitUntil: 'domcontentloaded' });
  if (r.status() !== 200) { console.log('  ' + r.status() + '  ' + t); dead++; }
}
console.log(dead ? '' : '  none');

console.log('\nbroken subresource requests across all pages:');
console.log(broken.size ? '  ' + [...broken].join('\n  ') : '  none');
console.log('\npage errors: ' + (errs.length ? errs.join('; ') : 'none'));

await b.close(); srv.close();
