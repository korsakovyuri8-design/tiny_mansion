/* Общий статический сервер для проб: отдаёт репозиторий как GitHub Pages. */
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
export const ROOT = path.resolve(new URL('..', import.meta.url).pathname);
const TY={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css',
  '.jpg':'image/jpeg','.png':'image/png','.webp':'image/webp','.xml':'application/xml',
  '.txt':'text/plain','.woff2':'font/woff2','.svg':'image/svg+xml','.ico':'image/x-icon'};
export function serve(port, opts = {}) {
  const srv = http.createServer((q, r) => {
    let p = decodeURIComponent(q.url.split('?')[0]);
    if (opts.block && opts.block.test(p)) { r.writeHead(500); return r.end('blocked'); }
    if (!path.extname(p)) p = p.replace(/\/?$/, '/') + 'index.html';
    const f = path.join(ROOT, p);
    if (fs.existsSync(f) && !fs.statSync(f).isDirectory()) {
      r.writeHead(200, { 'content-type': TY[path.extname(f)] || 'application/octet-stream' });
      fs.createReadStream(f).pipe(r);
    } else {                                   /* как Pages: свой 404 */
      const nf = path.join(ROOT, '404.html');
      r.writeHead(404, { 'content-type': 'text/html; charset=utf-8' });
      r.end(fs.existsSync(nf) ? fs.readFileSync(nf) : 'nf');
    }
  });
  return new Promise(res => srv.listen(port, () => res(srv)));
}
export function pages() {
  const sm = fs.readFileSync(path.join(ROOT, 'sitemap.xml'), 'utf8');
  return [...sm.matchAll(/<loc>https:\/\/tinymansion\.co([^<]*)<\/loc>/g)].map(m => m[1]);
}
