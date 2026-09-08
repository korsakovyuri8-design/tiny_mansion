/* Playwright is not a dependency of this repo — it is whatever is installed on
   the machine running the checks. Try the normal resolution first, then the
   global install these checks were written against. */
let mod;
try {
  mod = (await import('playwright')).default ?? (await import('playwright'));
} catch (e) {
  mod = (await import('/opt/node22/lib/node_modules/playwright/index.js')).default;
}
export default mod;
