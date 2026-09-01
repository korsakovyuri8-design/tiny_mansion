# The NTPCG pitch deck

`deck.html` + `style.css` render to a 16:9 PDF, one page per `.slide`:

```
node deck/mkpdf.mjs
```

It writes `Tiny-Mansion-NTPCG-pitch-deck.pdf` to the repository root. That
PDF is not committed — it is 4 MB and regenerates in seconds.

The deck pulls the site's own photographs out of the repository root, so a
picture that changes there changes here too. `fonts/` holds the same EB
Garamond and Jost subsets the site loads from Google, kept locally because
the build has no outbound network.

Every figure in the deck comes from somewhere else in this repository:
the residence numbers from `invest/en/index.html`, the commercial-unit
economics from `model.py`, the team from the About view in
`src/index.html`. Change the source, then re-render.

`robots.txt` disallows `/deck/` — this is the source of a document, not a
page of the site.
