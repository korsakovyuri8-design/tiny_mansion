/* ==========================================================
   Render deck.html to a 16:9 PDF, one page per .slide.

     node deck/mkpdf.mjs

   Chromium is driven over a local server rather than file://
   so the deck can pull the site's own photographs out of the
   repository root and the fonts out of deck/fonts.
   ========================================================== */
import pw from '/opt/node22/lib/node_modules/playwright/index.js';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DECK = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.dirname(DECK);
const OUT  = path.join(ROOT, 'Tiny-Mansion-NTPCG-pitch-deck.pdf');

const TYPES = { '.html':'text/html', '.css':'text/css', '.woff2':'font/woff2',
                '.jpg':'image/jpeg', '.png':'image/png' };

const server = http.createServer((rq, rs) => {
  const u = decodeURIComponent(rq.url.split('?')[0]);
  const f = u.startsWith('/__f/') ? path.join(DECK, 'fonts', path.basename(u))
          : u.startsWith('/img/') ? path.join(ROOT, path.basename(u))
          : path.join(DECK, u === '/' ? 'deck.html' : path.basename(u));
  if (!fs.existsSync(f)) { console.log('  missing ' + u); rs.writeHead(404); return rs.end('nf'); }
  rs.writeHead(200, { 'content-type': TYPES[path.extname(f)] || 'application/octet-stream' });
  rs.end(fs.readFileSync(f));
});
await new Promise(r => server.listen(8160, r));

const browser = await pw.chromium.launch({ args: ['--no-proxy-server'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });

const failed = [];
page.on('requestfailed', r => failed.push(r.url()));
page.on('response', r => { if (r.status() >= 400) failed.push(r.status() + ' ' + r.url()); });

await page.goto('http://127.0.0.1:8160/deck.html', { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(600);

/* A slide taller than its page silently loses its bottom edge in the PDF,
   so check before printing rather than after someone opens the file. */
const info = await page.evaluate(() => {
  const s = [...document.querySelectorAll('.slide')];
  return { slides: s.length,
           over: s.map((e, i) => ({ i: i + 1, h: e.scrollHeight, w: e.scrollWidth }))
                  .filter(o => o.h > 720 || o.w > 1280) };
});
console.log('slides: ' + info.slides + '  overflowing: ' +
            (info.over.length ? JSON.stringify(info.over) : 'none'));
console.log('failed requests: ' + (failed.length ? failed.join(', ') : 'none'));

await page.pdf({ path: OUT, width: '1280px', height: '720px', printBackground: true });
console.log('written ' + OUT + '  ' + (fs.statSync(OUT).size / 1048576).toFixed(2) + ' MB');

await browser.close();
server.close();
