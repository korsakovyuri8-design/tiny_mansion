# -*- coding: utf-8 -*-
"""Пересобирает числовые слайды deck/deck.html из club.py и bars.py.

Колода уже один раз разошлась с сайтом: она продолжала предлагать вход
от €50 000 в пул через полгода после того, как модель стала продажей дома
в собственность, и считала загрузку по другой лестнице. Инвестор, который
читает и то и другое, видит два разных предложения.

Поэтому цифры сюда не пишутся руками. Скрипт заменяет размеченные блоки
целиком, так что его можно гонять сколько угодно раз.

    python3 gen_deck.py
    node deck/mkpdf.mjs
"""
import io, os, sys, contextlib, runpy

ROOT = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.join(ROOT, 'deck', 'deck.html')

with contextlib.redirect_stdout(io.StringIO()):
    C = runpy.run_path(os.path.join(ROOT, 'club.py'))
    B = runpy.run_path(os.path.join(ROOT, 'bars.py'))

ALL        = C['ALL']
ONBOARDING = C['ONBOARDING']
OCC        = C['OCC']
TARGET     = C['TARGET']
NUNITS     = 3                      # столько резиденций в первом размещении
D21, D24   = ALL[0][3], ALL[1][3]
HOUSE_LOW, HOUSE_HIGH = D21['price'], D24['price']
ENTRY_LOW, ENTRY_HIGH = D21['entry'], D24['entry']

# Та же ставка, по которой считает /bars/economics/ и страницы юнитов:
# средняя оценка по Европе. €1610 — факт по Северной Америке, он остаётся
# в тексте как то, на что можно сослаться.
RATE_EU, WAGE_EU, RATE_NA = 1_450, 18, 1_610
outing = B['outing']

EN = ['Conservative', 'Base', 'Optimistic']
NOTE = ['The floor we hold ourselves to',
        'What the model is built on',
        'What a good season looks like']


def E(v):
    return '€' + format(int(round(v)), ',d')


def rows_residences():
    """Раньше здесь стояли три сценария загрузки. Теперь загрузка одна —
    политика, а не прогноз, — и различаются модели, а не сценарии."""
    out = ''
    for i, (_, en, _, d) in enumerate(ALL):
        cls = ' class="tot"' if i == len(ALL) - 1 else ''
        out += ('      <tr%s><td class="lbl">%s</td>'
                '<td class="n">%s</td><td class="n">%.0f%%</td>'
                '<td class="n">%s</td><td class="n">%s</td></tr>\n'
                % (cls, en, E(d['rate']), OCC * 100, E(d['rev']), E(d['payout'])))
    return out


def rows_units():
    b = outing(RATE_EU, WAGE_EU, 'bar')
    c = outing(RATE_EU, WAGE_EU, 'coffee')
    r = [('Charged for the outing', RATE_EU, RATE_EU),
         ('Staff, stock, fuel, running', -(RATE_EU - c), -(RATE_EU - b))]
    out = ''
    for lbl, a, d in r:
        out += ('      <tr><td class="lbl">%s</td><td class="n">%s%s</td>'
                '<td class="n">%s%s</td></tr>\n'
                % (lbl, '−' if a < 0 else '', E(abs(a)),
                   '−' if d < 0 else '', E(abs(d))))
    out += ('      <tr class="tot"><td class="lbl">Left over</td>'
            '<td class="n">%s</td><td class="n">%s</td></tr>\n' % (E(c), E(b)))
    for n in (24, 30):
        out += ('      <tr><td class="lbl">A season of %d outings</td>'
                '<td class="n">%s</td><td class="n">%s</td></tr>\n'
                % (n, E(c * n), E(b * n)))
    return out


def rows_revenue():
    lo = min(d['rev'] for _, _, _, d in ALL)
    hi = max(d['rev'] for _, _, _, d in ALL)
    return ('          <tr><td class="lbl">Rate a night, by model</td>'
            '<td class="n">%s and %s</td></tr>\n'
            '          <tr><td class="lbl">One residence, a full year at %.0f%%</td>'
            '<td class="n">%s–%s</td></tr>\n'
            '          <tr><td class="lbl">Three residences, a full year</td>'
            '<td class="n">%s–%s</td></tr>\n'
            % (E(D21['rate']), E(D24['rate']), OCC * 100,
               E(lo), E(hi), E(lo * NUNITS), E(hi * NUNITS)))


BLOCKS = {
    'REVENUE': rows_revenue(),
    'PRICE': ('      <tr class="tot"><td class="lbl">Price to the owner</td>'
              '<td class="n" colspan="2">%s–%s, plus %s onboarding</td></tr>\n'
              % (E(HOUSE_LOW), E(HOUSE_HIGH), E(ONBOARDING))),
    'INVESTOR': ('      <p><strong>The house itself, %s–%s all in.</strong> Buys the '
                 'residence outright in their own name — movable property with a serial '
                 'number and an invoice, not cadastral real estate — and we run the guests '
                 'under a management contract they can end. Their share of the revenue is '
                 'sized in advance to a %.0f%% a year target on that full sum; when revenue '
                 'falls short, the payment falls with it and we add no money of our own.</p>\n'
                 % (E(ENTRY_LOW), E(ENTRY_HIGH), TARGET * 100)),
    'RESIDENCES': rows_residences(),
    'UNITS': rows_units(),
}

s = io.open(DECK, encoding='utf-8').read()
changed = 0
for name, html in BLOCKS.items():
    a, b = '<!-- GEN:%s -->' % name, '<!-- /GEN:%s -->' % name
    if s.count(a) != 1 or s.count(b) != 1:
        sys.exit('нет маркеров GEN:%s в deck.html — добавьте их вокруг блока' % name)
    i, j = s.index(a) + len(a), s.index(b)
    if s[i:j] != '\n' + html:
        s = s[:i] + '\n' + html + s[j:]
        changed += 1

io.open(DECK, 'w', encoding='utf-8').write(s)
print('колода пересобрана: блоков обновлено %d из %d' % (changed, len(BLOCKS)))
print('дальше: node deck/mkpdf.mjs')
