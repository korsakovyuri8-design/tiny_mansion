import pw from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const ROOT = path.resolve(new URL('..', import.meta.url).pathname);
const TY={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.jpg':'image/jpeg','.png':'image/png','.webp':'image/webp'};
const srv=http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]);
  if(!path.extname(p))p=p.replace(/\/?$/,'/')+'index.html';const f=path.join(ROOT,p);
  if(fs.existsSync(f)&&!fs.statSync(f).isDirectory()){r.writeHead(200,{'content-type':TY[path.extname(f)]||'application/octet-stream'});fs.createReadStream(f).pipe(r);}
  else{r.writeHead(404);r.end('x');}});
await new Promise(r=>srv.listen(8360,r));
const B='http://127.0.0.1:8360';
const b=await pw.chromium.launch({args:['--no-proxy-server']});
const sm=fs.readFileSync(path.join(ROOT,'sitemap.xml'),'utf8');
const pages=[...sm.matchAll(/<loc>https:\/\/tinymansion\.co([^<]*)<\/loc>/g)].map(m=>m[1]);

const SCAN = `(() => {
  const out = [];
  const v = document.querySelector('.view-section.active') || document.body;
  const scope = [v, document.querySelector('header'), document.querySelector('footer')].filter(Boolean);
  for (const root of scope) {
    root.querySelectorAll('*').forEach(el => {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') return;
      const r = el.getBoundingClientRect();
      if (r.width < 2 || r.height < 2) return;
      // текст, обрезанный собственным контейнером
      const hidden = cs.overflowX === 'hidden' || cs.overflow === 'hidden';
      if (hidden && el.scrollWidth > el.clientWidth + 2 && el.children.length === 0)
        out.push('обрезано по ширине: <' + el.tagName.toLowerCase() + ' class="' +
                 (el.className||'').toString().slice(0,26) + '"> "' +
                 el.textContent.trim().slice(0, 40) + '"');
      const hiddenY = cs.overflowY === 'hidden' || cs.overflow === 'hidden';
      if (hiddenY && el.scrollHeight > el.clientHeight + 3 && el.children.length === 0)
        out.push('обрезано по высоте: <' + el.tagName.toLowerCase() + ' class="' +
                 (el.className||'').toString().slice(0,26) + '"> "' +
                 el.textContent.trim().slice(0, 40) + '"');
      // вылезает за родителя
      const p = el.parentElement;
      if (p && p !== document.body) {
        const pr = p.getBoundingClientRect();
        const po = getComputedStyle(p);
        if ((po.overflow === 'visible') && pr.width > 4 &&
            (r.right > pr.right + 12 || r.left < pr.left - 12) &&
            po.position === 'static' && getComputedStyle(el).position === 'static')
          out.push('шире родителя: <' + el.tagName.toLowerCase() + ' class="' +
                   (el.className||'').toString().slice(0,22) + '"> "' +
                   el.textContent.trim().slice(0, 30) + '"');
      }
    });
  }
  return [...new Set(out)];
})()`;

for (const w of [390, 1280]) {
  for (const lang of ['en','ru']) {
    const page = await b.newPage({viewport:{width:w,height:900}});
    await page.route('**://fonts.g*.com/**', r=>r.abort());
    await page.goto(B+'/',{waitUntil:'networkidle'});
    await page.click('.lang-btn[data-lang="'+lang+'"]'); await page.waitForTimeout(350);
    let bad = 0;
    for (const u of pages) {
      await page.goto(B+u,{waitUntil:'networkidle'});
      await page.waitForTimeout(220);
      const r = await page.evaluate(SCAN);
      if (r.length) { bad++; console.log('\n' + w + 'px ' + lang + '  ' + u);
        r.slice(0,6).forEach(x=>console.log('    ' + x)); }
    }
    console.log(w + 'px ' + lang + ': страниц с находками ' + bad + ' из ' + pages.length);
    await page.close();
  }
}
await b.close(); srv.close();
