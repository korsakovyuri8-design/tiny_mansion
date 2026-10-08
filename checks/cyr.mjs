import pw from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const ROOT = path.resolve(new URL('..', import.meta.url).pathname);
const TY={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.jpg':'image/jpeg','.png':'image/png','.webp':'image/webp'};
const srv=http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]);
  if(!path.extname(p))p=p.replace(/\/?$/,'/')+'index.html';const f=path.join(ROOT,p);
  if(fs.existsSync(f)&&!fs.statSync(f).isDirectory()){r.writeHead(200,{'content-type':TY[path.extname(f)]||'application/octet-stream'});fs.createReadStream(f).pipe(r);}
  else{r.writeHead(404);r.end('x');}});
await new Promise(r=>srv.listen(8330,r));
const b=await pw.chromium.launch({args:['--no-proxy-server']});
const sm=fs.readFileSync(path.join(ROOT,'sitemap.xml'),'utf8');
const pages=[...sm.matchAll(/<loc>https:\/\/tinymansion\.co([^<]*)<\/loc>/g)].map(m=>m[1]);
/* Кириллица неуместна в трёх версиях из четырёх: английской, сербской
   латиницей и турецкой. Утёкшая русская строка видна сразу по письму. */
const NAMES={en:'английской',sr:'сербской',tr:'турецкой'};
let total=0;
for (const lang of ['en','sr','tr']) {
  const page=await b.newPage({viewport:{width:1280,height:900}});
  await page.route('**://fonts.g*.com/**',r=>r.abort());
  await page.addInitScript(l=>{try{localStorage.setItem('tm-lang',l);}catch(e){}}, lang);
  for (const u of pages) {
    await page.goto('http://127.0.0.1:8330'+u,{waitUntil:'networkidle'});
    await page.waitForTimeout(300);
    const hits=await page.evaluate(()=>{
      const v=document.querySelector('.view-section.active'); const out=[];
      const w=document.createTreeWalker(v,NodeFilter.SHOW_TEXT); let n;
      while((n=w.nextNode())){const t=n.textContent.trim();
        if(t && /[Ѐ-ӿ]/.test(t)) out.push(t.slice(0,80));}
      return [...new Set(out)];});
    if(hits.length){ total+=hits.length;
      console.log('\n'+u+'  кириллица в '+NAMES[lang]+' версии: '+hits.length);
      hits.slice(0,60).forEach(h=>console.log('   '+h));}

    /* Турецкая i. При lang="tr" браузер поднимает i до İ, как и положено
       по-турецки, и английское имя собственное под text-transform
       превращается в «RESİDENCE 21FT» и «TİNY MANSİON». Лечится атрибутом
       lang="en" на самом имени, а ловится здесь. */
    if (lang === 'tr') {
      const dotted = await page.evaluate(() => {
        /* Английские имена, какими они выглядят после турецкого
           uppercase. Список ровно из тех, в которых есть i. */
        const rx = /RESİDENCE|MANSİON|VİCTRON|İNSTAGRAM|RADİSSON|LİNEA|NUKİ|ORBİTAL|BEST WESTERN İ/g;
        return [...new Set((document.body.innerText.match(rx) || []))];
      });
      if (dotted.length) { total += dotted.length;
        console.log('\n'+u+'  турецкая İ в английском имени: '+dotted.join(', ')); }
    }
  }
  await page.close();
}
console.log('\nвсего: '+total);
await b.close(); srv.close();
