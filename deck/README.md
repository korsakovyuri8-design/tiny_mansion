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

The team comes from the About view in `src/index.html`. Every money
figure is generated — see below.

`robots.txt` disallows `/deck/` — this is the source of a document, not a
page of the site.

## The numbers are generated

Every figure on the money slides is written by `gen_deck.py` from `club.py`
and `bars.py` — the same two models the site reads. The deck drifted once:
it went on offering entry from €50,000 into a pool months after the model
became an outright sale, and ran a different occupancy ladder. Nobody
noticed, because a slide has no test.

    python3 gen_deck.py     # rewrite the blocks between the GEN markers
    node deck/mkpdf.mjs     # then the PDF

The generated blocks are the price to the owner, the investor segment, the
residence scenarios, the commercial-unit outing table and the revenue lines.
Do not type a number into any of them: edit the model and re-run.
