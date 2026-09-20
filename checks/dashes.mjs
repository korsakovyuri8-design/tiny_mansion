/* Длинного тире на сайте быть не должно: ни в тексте, ни в разметке, ни в
   комментариях, ни escape-последовательностью, ни HTML-сущностью.

   Проверка читает файлы, а не отрисованные страницы: escape и сущность в
   браузере уже превратятся в символ и станут неотличимы от него, а поймать
   надо именно источник.

   Сам знак здесь нигде не написан, он собирается из кода, иначе проверка
   находила бы себя. Короткое тире в диапазонах (€120 000–€170 000, 75–85%)
   это другой символ и обычная типографика: оно остаётся. */
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(new URL('..', import.meta.url).pathname);
const SKIP = new Set(['.git', 'node_modules', 'fonts']);
const TEXT = /\.(html|css|js|mjs|py|md|json|xml|txt|svg)$/i;

const CH = String.fromCharCode(0x2014);
const FORMS = [[CH, 'символ'], ['\\u' + '2014', 'escape'],
               ['&' + 'mdash;', 'сущность'], ['&#' + '8212;', 'сущность'],
               ['&#' + 'x2014;', 'сущность']];

const found = [];
(function walk(dir) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (SKIP.has(e.name)) continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) { walk(p); continue; }
    if (!TEXT.test(e.name)) continue;
    const rel = path.relative(ROOT, p);
    if (rel === path.join('checks', 'dashes.mjs')) continue;
    fs.readFileSync(p, 'utf8').split('\n').forEach((l, i) => {
      for (const [form, kind] of FORMS)
        if (l.includes(form))
          found.push(rel + ':' + (i + 1) + '  (' + kind + ')  ' + l.trim().slice(0, 90));
    });
  }
})(ROOT);

found.slice(0, 40).forEach(f => console.log('  ' + f));
if (found.length > 40) console.log('  ... и ещё ' + (found.length - 40));
console.log('\nдлинных тире в файлах: ' + found.length);
