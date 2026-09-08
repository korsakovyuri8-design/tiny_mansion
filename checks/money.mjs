/* Russian groups thousands with a space and English with a comma. Anything
   still comma-grouped in the Russian rendering is a cell nobody translated. */
import pw from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const ROOT = path.resolve(new URL('..', import.meta.url).pathname);
const TY={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.jpg':'image/jpeg','.png':'image/png','.webp':'image/webp'};
const srv=http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]);
  if(!path.extname(p))p=p.replace(/\/?$/,'/')+'index.html';const f=path.join(ROOT,p);
  if(fs.existsSync(f)&&!fs.statSync(f).isDirectory()){r.writeHead(200,{'content-type':TY[path.extname(f)]||'application/octet-stream'});fs.createReadStream(f).pipe(r);}
  else{r.writeHead(404);r.end('x');}});
await new Promise(r=>srv.listen(8334,r));
const b=await pw.chromium.launch({args:['--no-proxy-server']});
const sm=fs.readFileSync(path.join(ROOT,'sitemap.xml'),'utf8');
const pages=[...sm.matchAll(/<loc>https:\/\/tinymansion\.co([^<]*)<\/loc>/g)].map(m=>m[1]);
for (const [lang, bad, want] of [['ru', /€\s?\d{1,3},\d{3}/, 'запятая в русском'],
                                 ['en', /€\s?\d{1,3} \d{3}/, 'пробел в английском']]) {
  const page=await b.newPage({viewport:{width:1280,height:2000}});
  await page.route('**://fonts.g*.com/**',r=>r.abort());
  await page.addInitScript(l=>{try{localStorage.setItem('tm-lang',l);}catch(e){}}, lang);
  let total=0;
  for (const u of pages) {
    if (lang==='ru' && u.startsWith('/invest/en')) continue;
    if (lang==='en' && u==='/invest/') continue;
    await page.goto('http://127.0.0.1:8334'+u,{waitUntil:'networkidle'});
    await page.waitForTimeout(200);
    const hits=await page.evaluate(re=>{
      const rx=new RegExp(re); const v=document.querySelector('.view-section.active'); const out=[];
      const w=document.createTreeWalker(v,NodeFilter.SHOW_TEXT); let n;
      while((n=w.nextNode())){const t=n.textContent.trim(); if(t&&rx.test(t)) out.push(t.slice(0,70));}
      return [...new Set(out)];}, bad.source);
    if(hits.length){total+=hits.length; console.log('\n'+lang+' '+u); hits.forEach(h=>console.log('   '+h));}
  }
  console.log('\n'+want+': '+total);
  await page.close();
}
await b.close(); srv.close();
