/* Непереведённая строка в русской версии видна по письму, а в сербской и
   турецкой нет: там латиница это и есть язык. Поэтому проверка сравнивает
   не письмо, а сами строки. Страница снимается по-английски, потом на
   каждом языке, узел за узлом в одном и том же порядке; совпавший с
   английским узел, в котором есть связная латинская речь, это строка,
   которой нет в словаре. Имена, бренды и стандарты исключены списком из
   keep.mjs: они совпадают с английскими по делу. */
import pw from './pw.mjs';
import { strip } from './keep.mjs';
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

/* Узлы активной секции в порядке документа, плюс переводимые атрибуты:
   список снимается одинаково на всех языках, поэтому его можно сравнивать
   поэлементно. */
const SNAP = `(() => {
  const view = document.querySelector('.view-section.active');
  if (!view) return null;
  const out = [];
  const w = document.createTreeWalker(view, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = w.nextNode())) {
    /* Заголовки с разметкой переводятся целиком, вместе с <em>, поэтому
       узлов внутри них на разных языках разное число: по-английски
       «A house that moves to where the <em>season</em> is» это три узла,
       по-русски два. Сравнивать их поэлементно нечем, и перевод им
       обеспечивает html-часть словаря. */
    if (n.parentElement.closest('script,style,[data-i18n-html]')) continue;
    out.push(['text', n.textContent.trim()]);
  }
  const ATTRS = ['data-label','alt','placeholder','aria-label','title'];
  for (const el of view.querySelectorAll('[data-label],[alt],[placeholder],[aria-label],[title]'))
    for (const a of ATTRS) {
      const v = el.getAttribute(a);
      if (v !== null) out.push([a, v.trim()]);
    }
  return out;
})()`;

/* Связная латинская речь: два слова и больше, двенадцать знаков и больше,
   и после вычёркивания имён латиница ещё осталась. Одно слово ловит
   latin.mjs, который смотрит русскую версию по письму. */
const prose = s => s.length >= 12 && /[A-Za-z]{3}\s+[A-Za-z]{3}/.test(s)
                 && /[A-Za-z]{3}\s+[A-Za-z]{3}/.test(strip(s));

const b=await pw.chromium.launch({args:['--no-proxy-server']});
const sitemap = fs.readFileSync(path.join(ROOT,'sitemap.xml'),'utf8');
const pages = [...sitemap.matchAll(/<loc>https:\/\/tinymansion\.co([^<]*)<\/loc>/g)].map(m=>m[1]);

async function snapshots(lang) {
  const page = await b.newPage({ viewport: { width: 1280, height: 900 } });
  await page.route('**://fonts.g*.com/**', r => r.abort());
  await page.addInitScript(l => { try { localStorage.setItem('tm-lang', l); } catch (e) {} }, lang);
  const out = {};
  for (const u of pages) {
    await page.goto(B + u, { waitUntil: 'networkidle' });
    await page.waitForTimeout(300);
    out[u] = await page.evaluate(SNAP);
  }
  await page.close();
  return out;
}

const en = await snapshots('en');
let total = 0;
for (const lang of ['ru','sr','tr']) {
  const got = await snapshots(lang);
  let n = 0;
  for (const u of pages) {
    const a = en[u], c = got[u];
    if (!a || !c) { console.log('  ' + lang + ' ' + u + ': активной секции нет'); n++; continue; }
    if (a.length !== c.length) {
      console.log('  ' + lang + ' ' + u + ': узлов ' + c.length + ', по-английски ' + a.length);
      n++;
      continue;
    }
    const left = [...new Set(a.filter((p, i) => p[1] && p[1] === c[i][1] && prose(p[1]))
                              .map(p => (p[0] === 'text' ? '' : p[0] + '=') + p[1].slice(0, 90)))];
    if (left.length) {
      n += left.length;
      console.log('\n' + lang + ' ' + u);
      left.forEach(t => console.log('   ' + t));
    }
  }
  console.log('\n' + lang + ': осталось английским ' + n);
  total += n;
}
console.log('\nвсего непереведённого: ' + total);
await b.close(); srv.close();
