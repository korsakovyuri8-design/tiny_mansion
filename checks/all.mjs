/* Runs every check in turn. Each one starts its own static server on its own
   port and prints its own summary, so a failure is read from the output rather
   than an exit code. Build first: the checks read the built pages, not src/. */
import { execFileSync } from 'node:child_process';
import path from 'node:path';
const HERE = path.resolve(new URL('.', import.meta.url).pathname);
const ORDER = [
  ['routes',       'addresses, the language round-trip and the reveal'],
  ['links',        'internal links and subresources'],
  ['identity',     'company, city, mailbox and the advertised quarter'],
  ['cyr',          'Cyrillic left in the English version'],
  ['latin',        'Latin left in the Russian version'],
  ['untranslated', 'English prose left in the Russian version'],
  ['money',        'thousands grouped the wrong way round'],
  ['meta',         'titles and descriptions'],
  ['a11y',         'landmarks, focus rings, alt text'],
  ['clip',         'text clipped at 390 and 1280, both languages'],
  ['ovf',          'anything pushing the page sideways'],
];
for (const [name, what] of ORDER) {
  console.log('\n\n═══ ' + name + ' — ' + what + ' ═══');
  try {
    console.log(execFileSync('node', [path.join(HERE, name + '.mjs')],
      { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));
  } catch (e) {
    console.log('FAILED TO RUN: ' + e.message);
  }
}
