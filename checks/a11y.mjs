import pw from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const ROOT = path.resolve(new URL('..', import.meta.url).pathname);
const TYPES={'.html':'text/html','.js':'text/javascript','.css':'text/css','.jpg':'image/jpeg','.webp':'image/webp','.svg':'image/svg+xml','.xml':'application/xml','.txt':'text/plain','.woff2':'font/woff2'};
const server=http.createServer((rq,rs)=>{let f=path.join(ROOT,decodeURIComponent(rq.url.split('?')[0]));
  if(fs.existsSync(f)&&fs.statSync(f).isDirectory())f=path.join(f,'index.html');
  if(!fs.existsSync(f)){rs.writeHead(404);return rs.end('nf');}
  rs.writeHead(200,{'content-type':TYPES[path.extname(f)]||'application/octet-stream'});rs.end(fs.readFileSync(f));});
await new Promise(r=>server.listen(8140,r));
const sitemap=fs.readFileSync(path.join(ROOT,'sitemap.xml'),'utf8');
const pages=[...sitemap.matchAll(/<loc>https:\/\/tinymansion\.co([^<]*)<\/loc>/g)].map(m=>m[1]);
const b=await pw.chromium.launch({args:['--no-proxy-server']});
const p=await b.newPage({viewport:{width:1280,height:900}});
await p.route('**://fonts.googleapis.com/**',r=>r.abort());
await p.route('**://fonts.gstatic.com/**',r=>r.abort());

const report={};
for(const u of pages){
  await p.goto('http://127.0.0.1:8140'+u,{waitUntil:'networkidle'});
  const r=await p.evaluate(()=>{
    const vis=e=>e.offsetParent!==null||e===document.body;
    const active=document.querySelector('.view-section.active')||document.body;
    const out={};
    // headings, in the view actually on screen
    const hs=[...active.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(vis);
    out.h1=hs.filter(h=>h.tagName==='H1').length;
    const skips=[]; let prev=0;
    hs.forEach(h=>{const l=+h.tagName[1]; if(prev&&l>prev+1)skips.push(prev+'->'+l+' "'+h.textContent.trim().slice(0,40)+'"'); prev=l;});
    out.headingSkips=skips;
    // landmarks
    out.landmarks={main:document.querySelectorAll('main').length,
                   nav:document.querySelectorAll('nav').length,
                   header:document.querySelectorAll('header').length,
                   footer:document.querySelectorAll('footer').length};
    out.skipLink=!!document.querySelector('a[href^="#"][class*="skip"], .skip-link');
    // images without alt
    out.imgNoAlt=[...active.querySelectorAll('img')].filter(vis).filter(i=>i.getAttribute('alt')===null).length;
    // controls with no accessible name
    // A link whose only content is an image is named by that image's alt.
    const name=e=>(e.getAttribute('aria-label')||e.getAttribute('title')||e.textContent
                   ||[...e.querySelectorAll('img')].map(i=>i.getAttribute('alt')||'').join(' ')||'').trim();
    out.namelessControls=[...active.querySelectorAll('a,button,[role="button"]')].filter(vis)
      .filter(e=>!name(e)).map(e=>e.tagName+'.'+(e.className||'').toString().slice(0,30));
    // inputs with no label
    out.unlabelled=[...document.querySelectorAll('input:not([type=hidden]),textarea,select')]
      .filter(vis).filter(e=>!(e.id&&document.querySelector('label[for="'+e.id+'"]'))&&!e.getAttribute('aria-label')).length;
    return out;
  });
  report[u]=r;
}
// focus visibility on the first few tab stops of the home page
await p.goto('http://127.0.0.1:8140/',{waitUntil:'networkidle'});
const focus=[];
for(let i=0;i<8;i++){
  await p.keyboard.press('Tab');
  focus.push(await p.evaluate(()=>{
    const e=document.activeElement; if(!e||e===document.body)return 'body';
    const cs=getComputedStyle(e);
    const ring=cs.outlineStyle!=='none'&&parseFloat(cs.outlineWidth)>0;
    return (e.tagName+'.'+(e.className||'').toString().slice(0,24)).padEnd(38)+(ring?'ring':'NO RING');
  }));
}
const problems=[];
for(const [u,r] of Object.entries(report)){
  const bad=[];
  if(r.h1!==1) bad.push('h1 count '+r.h1);
  if(r.headingSkips.length) bad.push('heading skip '+r.headingSkips.join('; '));
  if(r.imgNoAlt) bad.push(r.imgNoAlt+' img without alt');
  if(r.namelessControls.length) bad.push('nameless: '+r.namelessControls.join(', '));
  if(r.unlabelled) bad.push(r.unlabelled+' unlabelled fields');
  if(bad.length) problems.push('  '+u.padEnd(30)+bad.join(' | '));
}
const first=report['/'];
console.log('landmarks:', JSON.stringify(first.landmarks), ' skip link:', first.skipLink);
console.log('\nfocus ring on the first eight tab stops of /:');
focus.forEach(f=>console.log('  '+f));
console.log('\nper-page problems ('+pages.length+' pages):');
console.log(problems.length?problems.join('\n'):'  none');
await b.close(); server.close();
