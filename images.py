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
width descriptor means. Nothing is ever upscaled: a source narrower than a
slot just lands in it at its own size. A source narrower than every slot gets
a single file named by its real width instead of three copies of itself, and
the run prints which those are so their markup can name it.
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
WIDTHS = [1024, 1440, 2048]
QUALITY = 82          # WebP at 82 sits where JPEG needs about 90

def slots_for(width):
    """Which files to write for a source this wide.

    A source at least as wide as the smallest slot gets the full set, named
    by slot. media() in the page names all three without being able to look
    at the disk, so for anything it renders the three files have to exist —
    a narrower source simply lands in the larger slots at its own size.

    A source narrower than even the smallest slot gets one file, named by
    its real width. Nothing renders those through media(): their markup is
    written by hand and can name the width that exists.
    """
    return list(WIDTHS) if width >= WIDTHS[0] else [width]

def derivatives(name):
    stem = name[:-4]
    src = os.path.join(ROOT, name)
    im = None
    for w in slots_for(Image.open(src).width):
        out = os.path.join(ROOT, '%s-%d.webp' % (stem, w))
        if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(src):
            continue
        if im is None:
            im = Image.open(src).convert('RGB')
        scale = min(1.0, w / im.width)
        size = (round(im.width * scale), round(im.height * scale))
        im.resize(size, Image.LANCZOS).save(out, 'WEBP', quality=QUALITY, method=6)
        yield out, size

def main():
    names = sorted(f for f in os.listdir(ROOT) if f.endswith('.jpg'))
    before = after = 0
    written = 0
    narrow = []
    for name in names:
        jpg = os.path.getsize(os.path.join(ROOT, name))
        before += jpg
        for out, size in derivatives(name):
            written += 1
            print('  %-28s %4dx%-4d %5d KB' %
                  (os.path.basename(out), size[0], size[1], os.path.getsize(out) // 1024))
        widths = slots_for(Image.open(os.path.join(ROOT, name)).width)
        big = os.path.join(ROOT, '%s-%d.webp' % (name[:-4], widths[-1]))
        if os.path.exists(big):
            after += os.path.getsize(big)
        if widths != list(WIDTHS):
            narrow.append((name, widths))

    print('\n%d files written, %d sources' % (written, len(names)))
    if narrow:
        print('\nwritten as a single file — markup for these names the width shown:')
        for name, widths in narrow:
            print('  %-26s %s' % (name, ', '.join(str(w) for w in widths)))
    if before and after:
        print('at full size: %d KB of JPEG -> %d KB of WebP (%+d%%)'
              % (before // 1024, after // 1024, round((after - before) / before * 100)))

if __name__ == '__main__':
    main()
