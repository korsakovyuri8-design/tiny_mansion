import pw from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const ROOT = path.resolve(new URL('..', import.meta.url).pathname);
const TY={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.jpg':'image/jpeg','.png':'image/png','.webp':'image/webp'};
const srv=http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]);
  if(!path.extname(p))p=p.replace(/\/?$/,'/')+'index.html';const f=path.join(ROOT,p);
  if(fs.existsSync(f)&&!fs.statSync(f).isDirectory()){r.writeHead(200,{'content-type':TY[path.extname(f)]||'application/octet-stream'});fs.createReadStream(f).pipe(r);}
  else{r.writeHead(404);r.end('x');}});
await new Promise(r=>srv.listen(8320,r));
const b=await pw.chromium.launch({args:['--no-proxy-server']});
const page=await b.newPage({viewport:{width:1280,height:900}});
await page.route('**://fonts.g*.com/**',r=>r.abort());
const sm=fs.readFileSync(path.join(ROOT,'sitemap.xml'),'utf8');
const pages=[...sm.matchAll(/<loc>https:\/\/tinymansion\.co([^<]*)<\/loc>/g)].map(m=>m[1]);
for (const lang of ['ru']) {
  await page.goto('http://127.0.0.1:8320/',{waitUntil:'networkidle'});
  await page.click('.lang-btn[data-lang="'+lang+'"]'); await page.waitForTimeout(300);
  console.log('=== '+lang);
  let short=0, latin=0;
  for (const u of pages) {
    await page.goto('http://127.0.0.1:8320'+u,{waitUntil:'networkidle'});
    await page.waitForTimeout(200);
    const d=await page.evaluate(()=>document.querySelector('meta[name="description"]').content);
    const bad=[];
    if(d.length<70) {short++; bad.push('коротко');}
    if(!/[Ѐ-ӿ]/.test(d)) {latin++; bad.push('НЕ ПЕРЕВЕДЕНО');}
    if(bad.length) console.log('  '+u.padEnd(26)+String(d.length).padStart(3)+'  '+bad.join(', ')+'  '+d.slice(0,70));
  }
  console.log('  короче 70 знаков: '+short+', без кириллицы: '+latin+' из '+pages.length);
}
await b.close(); srv.close();
