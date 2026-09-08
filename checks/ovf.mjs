import pw from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const ROOT = path.resolve(new URL('..', import.meta.url).pathname);
const TY={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css',
  '.jpg':'image/jpeg','.png':'image/png','.webp':'image/webp'};
const srv=http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]);
  if(!path.extname(p))p=p.replace(/\/?$/,'/')+'index.html';const f=path.join(ROOT,p);
  if(fs.existsSync(f)&&!fs.statSync(f).isDirectory()){r.writeHead(200,{'content-type':TY[path.extname(f)]||'application/octet-stream'});fs.createReadStream(f).pipe(r);}
  else{r.writeHead(404);r.end('x');}});
await new Promise(r=>srv.listen(8284,r));
const b=await pw.chromium.launch({args:['--no-proxy-server']});
const sm=fs.readFileSync(path.join(ROOT,'sitemap.xml'),'utf8');
const pages=[...sm.matchAll(/<loc>https:\/\/tinymansion\.co([^<]*)<\/loc>/g)].map(m=>m[1]);
for (const w of [360,768]) {
  console.log('\n=== '+w+'px');
  let bad=0;
  for (const u of pages) {
    const page=await b.newPage({viewport:{width:w,height:800}});
    await page.route('**://fonts.g*.com/**',r=>r.abort());
    await page.goto('http://127.0.0.1:8284'+u,{waitUntil:'networkidle'});
    await page.waitForTimeout(300);
    const r=await page.evaluate(W=>{
      const out=[];
      if(document.documentElement.scrollWidth>W+1) out.push('doc '+document.documentElement.scrollWidth);
      document.querySelectorAll('.view-section.active *').forEach(e=>{
        const b=e.getBoundingClientRect();
        if(b.width>0&&(b.right>W+1||b.left<-1))
          out.push((e.tagName+'.'+(e.className||'').toString().slice(0,26))+' '+Math.round(b.left)+'..'+Math.round(b.right));
      });
      return [...new Set(out)].slice(0,4);},w);
    if(r.length){bad++;console.log('  '+u+'  '+r.join(' | '));}
    await page.close();
  }
  console.log('  страниц с выносом: '+bad+' из '+pages.length);
}
await b.close(); srv.close();
