/* untranslated.mjs only flags Latin prose of two words and twelve characters or
   more, so "11 m²" sat untranslated on a Russian page for a while, along with
   three aria-labels. This flags any Latin letter left in the Russian rendering
   once the vocabulary that is *meant* to stay Latin has been struck out — brand
   names, chemistry, licence classes, standards. Target is zero: a new hit is
   either a missing dictionary key or a term that belongs on this list. */
import pw from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const ROOT = path.resolve(new URL('..', import.meta.url).pathname);

/* Stays Latin in Russian on purpose. */
const KEEP = [
  /TINY MANSION/g, /TinyArc Group(\s+d\.o\.o\.)?/g, /Best Western/g,
  /\bI{1,3}V?\b/g,   /* Roman quarters: I, II, III, IV */ /\bEN\b/g, /\bRU\b/g,
  /Grand Residence 24ft/g, /Residence 2\dft/g, /Trailer Made/g,
  /Đedov(ina|\s+Do)?/g, /Ravni/g, /Eko Oaza/g, /Karadžić/g, /Pavićević/g, /Pešić/g, /Medojević/g,
  /Victron/g, /Cerbo GX/g, /Nuki/g, /Orbital/g, /LiFePO[₄4]?/g, /Wyndham/g,
  /Instagram/g, /FormSubmit/g, /Google( Fonts)?/g, /La Marzocco( Linea)?/g,
  /Radisson( Individuals)?/g, /CO[₂2]/g, /\bIP\b/g, /Tiny Mansion/g, /Farm Store/g, /full-stack/gi, /white label/gi,
  /on-demand/gi, /Morsko dobro/g, /konoba/gi, /\bPIR\b/g, /\bCEE\b/g, /\bCE\b/g,
  /\bPOS\b/g, /\bR-\d+\b/g, /\bB96\b/g, /\bBE\b/g, /\bAV\b/g, /\bLED\b/g,
  /°C/g, /\bGX\b/g, /[\w.+-]+@[\w.-]+/g, /e-?mail/gi,
];
const strip = t => KEEP.reduce((s, r) => s.replace(r, ''), t);

const TY={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.jpg':'image/jpeg','.png':'image/png','.webp':'image/webp'};
const srv=http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]);
  if(!path.extname(p))p=p.replace(/\/?$/,'/')+'index.html';const f=path.join(ROOT,p);
  if(fs.existsSync(f)&&!fs.statSync(f).isDirectory()){r.writeHead(200,{'content-type':TY[path.extname(f)]||'application/octet-stream'});fs.createReadStream(f).pipe(r);}
  else{r.writeHead(404);r.end('x');}});
await new Promise(r=>srv.listen(8332,r));

const b=await pw.chromium.launch({args:['--no-proxy-server']});
const page=await b.newPage({viewport:{width:1280,height:900}});
await page.route('**://fonts.g*.com/**',r=>r.abort());
await page.addInitScript(()=>{try{localStorage.setItem('tm-lang','ru');}catch(e){}});
const sm=fs.readFileSync(path.join(ROOT,'sitemap.xml'),'utf8');
const pages=[...sm.matchAll(/<loc>https:\/\/tinymansion\.co([^<]*)<\/loc>/g)].map(m=>m[1]);
let total=0;
for (const u of pages) {
  if (u.startsWith('/invest/en')) continue;                 // English by design
  await page.goto('http://127.0.0.1:8332'+u,{waitUntil:'networkidle'});
  await page.waitForTimeout(250);
  const raw=await page.evaluate(()=>{
    const v=document.querySelector('.view-section.active'); const out=[];
    const w=document.createTreeWalker(v,NodeFilter.SHOW_TEXT); let n;
    while((n=w.nextNode())){
      if(n.parentElement.closest('script,style')) continue;
      const t=n.textContent.trim();
      if(t && /[A-Za-z]/.test(t)) out.push(['text', t]);
    }
    for (const el of v.querySelectorAll('[data-label],[alt],[placeholder],[aria-label],[title]'))
      for (const a of ['data-label','alt','placeholder','aria-label','title']) {
        const val=el.getAttribute(a);
        if(val && /[A-Za-z]/.test(val)) out.push([a, val]);
      }
    return [...new Map(out.map(p=>[p[0]+'\u0000'+p[1], p])).values()];});
  /* The attribute name is Latin itself, so only the value is tested. */
  const bad=raw.filter(([, v])=>/[A-Za-z]/.test(strip(v)))
               .map(([a, v])=>(a==='text' ? '' : a+'=') + v.slice(0, 120));
  if(bad.length){ total+=bad.length; console.log('\n'+u); bad.forEach(h=>console.log('   '+h)); }
}
console.log('\nлатиница в русской версии: '+total);
await b.close(); srv.close();
