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

HOUSE_LOW, HOUSE_HIGH = C['HOUSE_LOW'], C['HOUSE_HIGH']
ONBOARDING, NUNITS = C['ONBOARDING'], C['UNITS']
HURDLE = C['HURDLE']
unit, SCENARIOS = C['unit'], C['SCENARIOS']

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
    out = ''
    for i, (_, occ) in enumerate(SCENARIOS):
        d = unit(occ)
        cls = ' class="tot"' if i == len(SCENARIOS) - 1 else ''
        out += ('      <tr%s><td class="lbl">%s</td>'
                '<td class="n">%.0f%%</td><td class="n">%s</td>'
                '<td class="n">%s</td><td>%s</td></tr>\n'
                % (cls, EN[i], d['occ'] * 100, E(d['adr']),
                   E(d['rev'] * NUNITS), NOTE[i]))
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
    lo = min(unit(o)['rev'] for _, o in SCENARIOS) * NUNITS
    hi = max(unit(o)['rev'] for _, o in SCENARIOS) * NUNITS
    adr_lo = min(unit(o)['adr'] for _, o in SCENARIOS)
    adr_hi = max(unit(o)['adr'] for _, o in SCENARIOS)
    return ('          <tr><td class="lbl">Guest nights, average sold</td>'
            '<td class="n">%s–%s a night</td></tr>\n'
            '          <tr><td class="lbl">Three residences, a full season</td>'
            '<td class="n">%s–%s</td></tr>\n'
            % (E(adr_lo), E(adr_hi), E(lo), E(hi)))


BLOCKS = {
    'REVENUE': rows_revenue(),
    'PRICE': ('      <tr class="tot"><td class="lbl">Price to the owner</td>'
              '<td class="n" colspan="2">%s–%s, plus %s onboarding</td></tr>\n'
              % (E(HOUSE_LOW), E(HOUSE_HIGH), E(ONBOARDING))),
    'INVESTOR': ('      <p><strong>The house itself, %s–%s all in.</strong> Buys the '
                 'residence outright in their own name — movable property with a serial '
                 'number and an invoice, not cadastral real estate — and we run the guests '
                 'under a management contract they can end. Our fee is subordinated to a %.0f%% '
                 'preferred return: below it we are cut first.</p>\n'
                 % (E(HOUSE_LOW + ONBOARDING), E(HOUSE_HIGH + ONBOARDING), HURDLE * 100)),
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
