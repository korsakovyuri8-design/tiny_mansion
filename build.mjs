/* ==========================================================
   BUILD
   ==========================================================
   The site is one hand-written document, src/index.html. Every view lives
   in it and the browser swaps between them without a reload — which is
   fast, but leaves one address for the whole site. A crawler, a shared
   link and a reload all need an address that a server can answer on its
   own.

   So: render src/index.html once per address in a real browser, and write
   the result out as a static file at that address. Each file is a real 200
   with its own title, description and canonical, and still boots into the
   same interactive site.

   Edit src/index.html. Everything else here with an index.html in it is
   output — it is overwritten on every run, so changes made to it are lost.

   Run it after editing the source:

       node build.mjs

   It also writes sitemap.xml and robots.txt from the same route list, so
   the three can't drift apart.
   ========================================================== */
import pw from '/opt/node22/lib/node_modules/playwright/index.js';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const { chromium } = pw;
const ROOT = path.dirname(fileURLToPath(import.meta.url));
const SITE = 'https://tinymansion.co';
/* The hand-written document. Kept out of the output tree so a build can
   never overwrite the thing it is built from. */
const SOURCE = path.join(ROOT, 'src', 'index.html');
const PORT = 8123;

/* ---------- a static server just for the build ---------- */
const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css',
  '.jpg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp', '.svg': 'image/svg+xml',
  '.xml': 'application/xml', '.txt': 'text/plain'
};
const server = http.createServer((req, res) => {
  const p = decodeURIComponent(req.url.split('?')[0]);
  /* Assets come off disk. Every other address is answered with the source
     document — which is the point: we are asking it to render that address.
     Never with a file from an earlier build, or each run would re-render
     its own output. */
  const file = path.extname(p) ? path.join(ROOT, p) : SOURCE;
  if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    res.writeHead(404); res.end('not found'); return;
  }
  res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
});
await new Promise(r => server.listen(PORT, r));

/* ---------- what to build ---------- */
const browser = await chromium.launch({ args: ['--no-proxy-server'] });
const page = await browser.newPage();
const errors = [];
page.on('pageerror', e => errors.push(String(e)));

/* Nothing outside this machine is needed to produce the markup, and the
   font request is slow to fail here — which would make the build wait on
   it once per address. The <link> stays in the written file; only this
   run skips fetching it. */
await page.route('**://fonts.googleapis.com/**', r => r.abort());
await page.route('**://fonts.gstatic.com/**', r => r.abort());

await page.goto(`http://127.0.0.1:${PORT}/`, { waitUntil: 'networkidle' });

/* The route list comes out of the page's own data, so adding a farm to
   the source adds its page here without touching this file. */
const routes = await page.evaluate(() => {
  const out = Object.keys(VIEW_PATH).map(v => VIEW_PATH[v]);
  Object.keys(DATA.countries).forEach(id => out.push('/country/' + id + '/'));
  RESIDENCES.forEach(r => out.push('/residence/' + r.id + '/'));
  UNITS.forEach(u => out.push('/bar/' + u.id + '/'));
  Object.values(DATA.countries).forEach(c =>
    (c.farms || []).forEach(f => out.push('/farm/' + f.id + '/')));
  return out;
});

/* /thanks/ only makes sense after sending a form: it needs an address so
   the form has somewhere to land, but not a place in search results. */
const NOINDEX = ['/thanks/'];

console.log(routes.length + ' addresses\n');

/* Clear what the last build wrote, so a farm removed from index.html stops
   having a page rather than lingering as an orphan in search results. */
['residences', 'farms', 'bars', 'enquiry', 'host', 'about', 'terms', 'privacy',
 'thanks', 'country', 'residence', 'farm', 'bar'].forEach(d => {
  fs.rmSync(path.join(ROOT, d), { recursive: true, force: true });
});

/* ---------- render each one ---------- */
let built = 0;
for (const route of routes) {
  await page.goto(`http://127.0.0.1:${PORT}${route}`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(120);

  /* Whatever the page reports is what it rendered: if the address were
     wrong the app would have sent itself home, and we'd write that file
     to the wrong path. */
  const landed = await page.evaluate(() => location.pathname);
  if (landed !== route) {
    console.log('  SKIP ' + route + ' -> the page routed itself to ' + landed);
    continue;
  }

  const html = await page.evaluate((noindex) => {
    const doc = document.documentElement.cloneNode(true);

    /* Reveal-on-scroll is left alone: the class has to survive into the
       written file or the animation is gone from the live site. What the
       build did scroll past is reset, so every page starts the same way. */
    doc.querySelectorAll('.reveal.in, .route.in').forEach(el => el.classList.remove('in'));

    /* initForms() fills the form's action and return address from wherever
       the page is running — which during a build is this machine. Put the
       live values back so nothing local is written into a shipped file. */
    doc.querySelectorAll('form[data-mailform]').forEach(f => {
      f.removeAttribute('action');   /* the address stays out of the markup */
      const n = f.querySelector('input[name="_next"]');
      if (n) n.setAttribute('value', 'https://tinymansion.co/thanks/');
    });

    /* The build ran in English. Drop the round-trip bookkeeping the
       translator leaves behind so the file is plain markup. */
    doc.querySelectorAll('[data-lang-done]').forEach(el => el.removeAttribute('data-lang-done'));
    doc.removeAttribute('data-scroll');

    if (noindex) {
      const m = document.createElement('meta');
      m.setAttribute('name', 'robots');
      m.setAttribute('content', 'noindex, follow');
      doc.querySelector('head').appendChild(m);
    }
    return '<!DOCTYPE html>\n' + doc.outerHTML;
  }, NOINDEX.indexOf(route) !== -1);

  const dir = route === '/' ? ROOT : path.join(ROOT, route);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'index.html'), html);

  const title = await page.title();
  console.log('  ' + route.padEnd(34) + Math.round(html.length / 1024) + ' KB  ' + title);
  built++;
}

/* ---------- sitemap and robots ---------- */
const indexed = routes.filter(r => NOINDEX.indexOf(r) === -1);
const today = new Date().toISOString().slice(0, 10);
const urls = indexed.map(r =>
  '  <url>\n' +
  '    <loc>' + SITE + r + '</loc>\n' +
  '    <lastmod>' + today + '</lastmod>\n' +
  '    <priority>' + (r === '/' ? '1.0' : r.split('/').length > 3 ? '0.6' : '0.8') + '</priority>\n' +
  '  </url>').join('\n');

fs.writeFileSync(path.join(ROOT, 'sitemap.xml'),
  '<?xml version="1.0" encoding="UTF-8"?>\n' +
  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '\n</urlset>\n');

fs.writeFileSync(path.join(ROOT, 'robots.txt'),
  '# The investor deck is by invitation, not for search.\n' +
  '# /src/ is the document every page here is built from, not a page.\n' +
  '# /deck/ is the source of a PDF presentation, not a page of the site.\n' +
  '# /drafts/ is work not yet approved for publication.\n' +
  'User-agent: *\n' +
  'Disallow: /invest/\n' +
  'Disallow: /thanks/\n' +
  'Disallow: /src/\n' +
  'Disallow: /deck/\n' +
  'Disallow: /drafts/\n' +
  '\n' +
  '# The deck is sent as a link in a message, and a link in a message needs\n' +
  '# a card. These fetch a page to build that card and do not index it; the\n' +
  '# noindex on the page itself is what keeps it out of search. A crawler\n' +
  '# obeys only the most specific group that names it and ignores the one\n' +
  '# above, so this group repeats every rule it still keeps.\n' +
  'User-agent: TelegramBot\n' +
  'User-agent: WhatsApp\n' +
  'User-agent: Twitterbot\n' +
  'User-agent: facebookexternalhit\n' +
  'User-agent: LinkedInBot\n' +
  'User-agent: Slackbot\n' +
  'User-agent: Slackbot-LinkExpanding\n' +
  'User-agent: Discordbot\n' +
  'User-agent: SkypeUriPreview\n' +
  'User-agent: vkShare\n' +
  'Disallow: /thanks/\n' +
  'Disallow: /src/\n' +
  'Disallow: /deck/\n' +
  'Disallow: /drafts/\n' +
  '\n' +
  'Sitemap: ' + SITE + '/sitemap.xml\n');

console.log('\n' + built + ' files, ' + indexed.length + ' in sitemap.xml');
console.log('page errors: ' + (errors.length ? errors.join('; ') : 'none'));

/* ---------- the advertised launch date ----------
   The whole site turns on one promise — "first residences deploy Q3 2026" —
   repeated in about forty places. A date like that rots silently: nothing
   breaks, no test fails, and one day the site is advertising a quarter that
   has already ended to somebody reading it. So the build says so.
   python3 relaunch.py "Q4 2026" "IV квартал 2026" changes it everywhere. */
const source = fs.readFileSync(SOURCE, 'utf8');
const quarters = [...source.matchAll(/\bQ([1-4]) (20\d\d)\b/g)]
  .map(m => ({ q: +m[1], y: +m[2] }));
if (quarters.length) {
  const seen = new Map();
  quarters.forEach(x => seen.set(x.q + '/' + x.y, x));
  const now = new Date();
  for (const x of seen.values()) {
    const ends = new Date(Date.UTC(x.y, x.q * 3, 0, 23, 59, 59));
    const days = Math.round((ends - now) / 86400000);
    const label = 'Q' + x.q + ' ' + x.y;
    if (days < 0)
      console.log('\n  ВНИМАНИЕ: сайт обещает ' + label + ', а этот квартал кончился ' +
                  (-days) + ' дн. назад. python3 relaunch.py --check');
    else if (days <= 60)
      console.log('\n  ВНИМАНИЕ: сайт обещает ' + label + ', до конца квартала ' +
                  days + ' дн. python3 relaunch.py --check');
  }
}

await browser.close();
server.close();
