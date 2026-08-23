"""Derivative images.

Photography is shot and kept as JPEG at 2048px on the long side. That is the
right file to hand a desktop, and the wrong one to hand a phone twice over:
wrong format, and four times the pixels it can show.

For every .jpg in the repository root this writes:

    name-1024.webp    cards, thumbnails, a phone at ordinary density
    name-1440.webp    a full-width image on a phone with a 3x screen
    name-2048.webp    everything else

The .jpg stays as it is. It is what a browser without WebP falls back to,
and it is the file to re-run this from if the sizes ever change.

    python3 images.py

Safe to re-run: a derivative is only rewritten when it is missing or older
than its source.

Scaling is by width, not by the long side, because that is what a srcset
width descriptor means. A source narrower than 1024 therefore lands in both
slots identically — three portraits do, for about 230 KB in the repository
and nothing on the wire, since a browser fetches one of them.
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
WIDTHS = [1024, 1440, 2048]
QUALITY = 82          # WebP at 82 sits where JPEG needs about 90

def derivatives(name):
    stem = name[:-4]
    src = os.path.join(ROOT, name)
    im = None
    for w in WIDTHS:
        out = os.path.join(ROOT, '%s-%d.webp' % (stem, w))
        if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(src):
            continue
        if im is None:
            im = Image.open(src).convert('RGB')
        # Never upscale: a 1200px source stays 1200px in its "2048" slot,
        # and srcset still picks it correctly by the width we declare.
        scale = min(1.0, w / im.width)
        size = (round(im.width * scale), round(im.height * scale))
        im.resize(size, Image.LANCZOS).save(out, 'WEBP', quality=QUALITY, method=6)
        yield out, size

def main():
    names = sorted(f for f in os.listdir(ROOT) if f.endswith('.jpg'))
    before = after = 0
    written = 0
    for name in names:
        jpg = os.path.getsize(os.path.join(ROOT, name))
        before += jpg
        for out, size in derivatives(name):
            written += 1
            print('  %-28s %4dx%-4d %5d KB' %
                  (os.path.basename(out), size[0], size[1], os.path.getsize(out) // 1024))
        big = os.path.join(ROOT, '%s-%d.webp' % (name[:-4], WIDTHS[-1]))
        if os.path.exists(big):
            after += os.path.getsize(big)

    print('\n%d files written, %d sources' % (written, len(names)))
    if before and after:
        print('at full size: %d KB of JPEG -> %d KB of WebP (%+d%%)'
              % (before // 1024, after // 1024, round((after - before) / before * 100)))

if __name__ == '__main__':
    main()
