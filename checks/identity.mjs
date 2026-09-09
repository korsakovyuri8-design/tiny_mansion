/* Четыре вещи стоят на сайте десятками мест и разъезжаются по одной: юрлицо,
   город регистрации, почта и объявленный квартал. Проверка читает собранные
   страницы и требует, чтобы каждая из них имела ровно одно значение — и чтобы
   ссылка mailto, её текст и запасной адрес в <noscript> совпадали между собой. */
import pw from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const ROOT = path.resolve(new URL('..', import.meta.url).pathname);

/* Что сайт должен говорить о себе. Меняется здесь и больше нигде. */
const WANT = {
  entity:  'Korsakov Group',
  city:    'Tivat',
  cityRu:  'Тиват',
  mail:    'yuri@korsakovgroup.com',
  quarter: 'Q1 2027',
  quarterRu: 'I квартал',
};
/* То, чем это было. Ни одного вхождения остаться не должно. */
const GONE = ['TinyArc', 'korsakovyuri8', 'gmail.com', 'Q3 2026', 'III квартал', 'III кв.'];

const TY={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.jpg':'image/jpeg','.png':'image/png','.webp':'image/webp'};
const srv=http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]);
  if(!path.extname(p))p=p.replace(/\/?$/,'/')+'index.html';const f=path.join(ROOT,p);
  if(fs.existsSync(f)&&!fs.statSync(f).isDirectory()){r.writeHead(200,{'content-type':TY[path.extname(f)]||'application/octet-stream'});fs.createReadStream(f).pipe(r);}
  else{r.writeHead(404);r.end('x');}});
await new Promise(r=>srv.listen(8335,r));

/* Не только страницы из sitemap: 404, презентация, черновик и обе страницы
   инвесторам тоже отдаются. Последние закрыты noindex и потому в sitemap не
   попадают — а на них стоят и юрлицо, и квартал, и почта. */
const sm=fs.readFileSync(path.join(ROOT,'sitemap.xml'),'utf8');
const pages=[...sm.matchAll(/<loc>https:\/\/tinymansion\.co([^<]*)<\/loc>/g)].map(m=>m[1])
  .concat(['/404.html','/deck/deck.html','/drafts/invest-en.html',
           '/invest/','/invest/en/']);

const b=await pw.chromium.launch({args:['--no-proxy-server']});
let problems=0;
for (const lang of ['en','ru']) {
  const page=await b.newPage({viewport:{width:1280,height:900}});
  await page.route('**://fonts.g*.com/**',r=>r.abort());
  await page.addInitScript(l=>{try{localStorage.setItem('tm-lang',l);}catch(e){}}, lang);
  for (const u of pages) {
    await page.goto('http://127.0.0.1:8335'+u,{waitUntil:'networkidle'});
    await page.waitForTimeout(200);
    const r=await page.evaluate(() => ({
      html: document.documentElement.innerHTML,
      mails: [...document.querySelectorAll('a[href^="mailto:"]')]
        .map(a => [a.getAttribute('href').replace(/^mailto:/,''), a.textContent.trim()]),
      forms: [...document.querySelectorAll('form[action]')].map(f => f.getAttribute('action')),
    }));
    const say = m => { problems++; console.log('  ' + lang + ' ' + u + ': ' + m); };
    for (const g of GONE) if (r.html.includes(g)) say('осталось «' + g + '»');
    /* Текст ссылки и её href — разные строки в коде, поэтому и сверяются. */
    for (const [href, text] of r.mails) {
      if (href !== WANT.mail) say('mailto ведёт на ' + href);
      if (text !== WANT.mail) say('подпись ссылки ' + text);
    }
    for (const a of r.forms)
      if (!a.includes(WANT.mail) && !/formsubmit\.co\/[a-f0-9]{8,}/.test(a))
        say('форма уходит на ' + a);
  }
  await page.close();
}
console.log(problems ? '\nрасхождений: ' + problems
                     : '\nюрлицо, город, почта и квартал совпадают везде: 0 расхождений');
await b.close(); srv.close();
