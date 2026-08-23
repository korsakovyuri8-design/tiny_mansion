# Tiny Mansion

The site at [tinymansion.co](https://tinymansion.co). Served by GitHub Pages
from `main`, on the domain named in `CNAME`.

## Where to edit

**`src/index.html`** — the whole site: markup, styles, data, script, and the
Russian dictionary. This is the only file to edit by hand.

Everything else with an `index.html` in it (`/`, `about/`, `farm/f-pony/`, …)
is **generated**. Editing those files is wasted work — the next build
overwrites them.

Also hand-written:

| File | What it is |
| --- | --- |
| `invest/index.html` | The investor deck. A separate page, Russian only, kept out of search. |
| `404.html` | What GitHub Pages serves for an address that does not exist. |
| `analytics.js` | Inert until `SRC` and `ID` are filled in. See the comment at the top of it. |
| `build.mjs` | The build described below. |

## Building

After any edit to `src/index.html`:

```
node build.mjs
```

This opens `src/index.html` in a real browser once per address, and writes
what it renders to a static file at that address. It also writes
`sitemap.xml` and `robots.txt` from the same list of addresses.

Commit the generated files along with the source — GitHub Pages serves what
is in the repository, there is no build step on their side.

## Why the build exists

Every view lives in one document and the browser swaps between them without
a reload, which is fast. On its own that leaves the whole site sharing one
address: a shared link, a reload and a search engine all get the home page.

The build gives each view a real address that a server answers by itself —
its own file, its own title, description and canonical — while the site
still moves between them in the browser without a reload. Addresses shared
back when the site used `#/` still work; they rewrite themselves to the real
one.

## Adding a farm, a country or a residence

Add the record to `DATA` in `src/index.html` and run the build. Its page,
its entry in `sitemap.xml`, and its title and description all follow from
the record — there is no second place to update.

## Translation

`applyLang()` walks the document and swaps text against the `RU` dictionary,
keyed by the English source string. So **changing an English string means
changing its dictionary key too**, or that string stops being translated.

Page titles and descriptions live in `HEAD_META` and go through the same
dictionary. The build runs in English, which is what a crawler reads; a
visitor who switches language gets the translation of the same strings.

## Still to do

- `analytics.js` needs an account: fill in `SRC` and `ID`.
- FormSubmit needs its one-time activation — send the form once from the
  live site and confirm the email it sends back, or submissions are not
  forwarded.
- Terms still has no registration number or postal address, and the
  cancellation terms have to be decided before booking opens.
