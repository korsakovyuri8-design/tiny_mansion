import pw from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';

const ROOT = path.resolve(new URL('..', import.meta.url).pathname);
const TY={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css',
  '.jpg':'image/jpeg','.png':'image/png','.webp':'image/webp'};
const srv=http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]);
  if(!path.extname(p))p=p.replace(/\/?$/,'/')+'index.html';const f=path.join(ROOT,p);
  if(fs.existsSync(f)&&!fs.statSync(f).isDirectory()){r.writeHead(200,{'content-type':TY[path.extname(f)]||'application/octet-stream'});fs.createReadStream(f).pipe(r);}
  else{r.writeHead(404);r.end('x');}});
await new Promise(r=>srv.listen(8260,r));
const B='http://127.0.0.1:8260';

const b=await pw.chromium.launch({args:['--no-proxy-server']});
const page=await b.newPage();
await page.route('**://fonts.g*.com/**',r=>r.abort());

/* Latin letters in a run of words, with no Cyrillic anywhere in the node —
   proper names like "Residence 21ft" or "Đedovina" are expected, so this
   only flags nodes that are wholly Latin prose. */
const SCAN = `(() => {
  const out = [];
  const view = document.querySelector('.view-section.active');
  if (!view) return ['NO ACTIVE VIEW'];
  const w = document.createTreeWalker(view, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = w.nextNode())) {
    const t = n.textContent.trim();
    if (t.length < 12) continue;
    if (/[\\u0400-\\u04FF]/.test(t)) continue;          // has Cyrillic: translated
    if (!/[A-Za-z]{3}\\s+[A-Za-z]{3}/.test(t)) continue; // needs 2+ Latin words
    if (n.parentElement.closest('script,style')) continue;
    out.push(t.slice(0, 90));
  }
  return [...new Set(out)];
})()`;

const sitemap = fs.readFileSync(path.join(ROOT,'sitemap.xml'),'utf8');
const pages = [...sitemap.matchAll(/<loc>https:\/\/tinymansion\.co([^<]*)<\/loc>/g)].map(m=>m[1]);

// Save the Russian preference first, the way a returning visitor would have it.
await page.goto(B+'/',{waitUntil:'networkidle'});
await page.click('.lang-btn[data-lang="ru"]');
await page.waitForTimeout(250);

let total = 0;
for (const u of pages) {
  await page.goto(B+u,{waitUntil:'networkidle'});
  await page.waitForTimeout(300);
  const left = await page.evaluate(SCAN);
  if (left.length) {
    total += left.length;
    console.log('\n' + u);
    left.forEach(t => console.log('   ' + t));
  }
}
console.log('\n' + (total ? total + ' untranslated strings on a direct load in Russian'
                          : 'nothing untranslated'));
await b.close(); srv.close();
