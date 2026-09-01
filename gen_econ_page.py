# -*- coding: utf-8 -*-
"""Generate /bars/economics/ out of model.py, so the page on the site and
the arithmetic that produced it cannot drift apart.

    python3 gen_econ_page.py
"""
import io, sys, contextlib, runpy

SRC = '/home/user/tiny_mansion/src/index.html'

with contextlib.redirect_stdout(io.StringIO()):
    M = runpy.run_path('/home/user/tiny_mansion/model.py')

USD  = M['USD']
SC   = M['SCENARIOS']
FEST = M['FEST']

# ── numbers, and how each one is spelled in Russian ──────────────────────
NUM = {}
def N(a, b):
    NUM[a] = b
    return a
def E(v):
    s = '€' + format(int(round(v)), ',d')
    return N(s, s.replace(',', ' '))
def D(v):
    s = '$' + format(int(round(v)), ',d')
    return N(s, s.replace(',', ' '))

def ER(v):
    """The same amount, spelled for a Russian sentence."""
    return ('€' + format(int(round(v)), ',d')).replace(',', '\u00A0')

def cell(n, v):
    """The walker matches the whole cell, so the whole cell is the key."""
    a = str(n) + ' × €' + ('%.2f' % v)
    return N(a, a.replace('.', ','))

def C(v):
    """A per-serving price keeps its cents; a season total does not."""
    s = '€' + ('%.2f' % v)
    return N(s, s.replace('.', ','))

# ── prose, in pairs ──────────────────────────────────────────────────────
TXT = {}
def unesc(v):
    return v.replace('&amp;', '&').replace('&nbsp;', '\u00A0')
def t(a, b):
    if a != b:
        TXT[unesc(a)] = unesc(b)
    return a

# ── the figures ──────────────────────────────────────────────────────────
COF_FEE = 1750 * USD
BAR_CLA = 1250 * USD
BAR_SIG = 1400 * USD
BAR_PRE = 1750 * USD

cof_staff, cof_stock, cof_fuel, cof_admin = [v for _, v in SC['coffee']['costs']]
bar_staff = SC['bar']['costs'][0][1]
bar_fuel  = SC['bar']['costs'][1][1]
bar_run   = SC['bar']['costs'][2][1] + SC['bar']['costs'][3][1]
bar_total = bar_staff + bar_fuel + bar_run

COF_NET   = SC['coffee']['net']
BAR_NET_C = BAR_CLA - bar_total
BAR_NET_P = BAR_PRE - bar_total

def festival(k):
    f = FEST[k]
    gross  = f['cups'] * f['price']
    cogs   = f['cups'] * f['cogs']
    labour = f['staff'] * f['hours'] * 18
    return f, gross, cogs, labour, gross - cogs - f['pitch'] - labour
FC, FCg, FCc, FCl, FCn = festival('coffee')
FB, FBg, FBc, FBl, FBn = festival('bar')

OUT = [18, 24, 30, 40]
DASH = '—'
MINUS = '−'

# ── table helpers ────────────────────────────────────────────────────────
def row(en, ru, *cells, **kw):
    cls = ' class="tot"' if kw.get('tot') else ''
    tds = ''.join('<td class="n">' + c + '</td>' for c in cells)
    return ('        <tr' + cls + '><td class="lbl">' + t(en, ru) + '</td>'
            + tds + '</tr>\n')

def fig(caption_en, caption_ru, heads, body, note_en, note_ru):
    th = ''.join('<th class="n">' + t(h[0], h[1]) + '</th>' for h in heads[1:])
    return ('''          <figure class="fig">
            <table>
              <caption>''' + t(caption_en, caption_ru) + '''</caption>
              <thead><tr><th>''' + t(heads[0][0], heads[0][1]) + '''</th>''' + th + '''</tr></thead>
              <tbody>
''' + body + '''              </tbody>
            </table>
            <figcaption class="fig-note">''' + t(note_en, note_ru) + '''</figcaption>
          </figure>
''')

def section(eyebrow, head, lede, rest=''):
    return ('''        <div class="section-pad">
          <span class="eyebrow">''' + t(*eyebrow) + '''</span>
          <h2 class="serif" style="font-size:var(--t-section);line-height:1.08;letter-spacing:-0.01em;margin-top:14px;">''' + t(*head) + '''</h2>
          <p class="page-lede" style="margin-top:16px;">''' + t(*lede) + '''</p>
''' + rest + '''        </div>

''')

# ── 1. where the rate comes from ─────────────────────────────────────────
b1 = (row('Park &amp; Pour, Classic', 'Park &amp; Pour, Classic', D(1250), E(BAR_CLA))
    + row('Park &amp; Pour, Signature', 'Park &amp; Pour, Signature', D(1400), E(BAR_SIG))
    + row('Park &amp; Pour, Premier', 'Park &amp; Pour, Premier', D(1750), E(BAR_PRE))
    + row('Hayloft, cart: three hours, one barista, 150 drinks',
          'Hayloft, тележка: три часа, один бариста, 150 напитков', D(1750), E(COF_FEE)))

s1 = section(
  ('Where the rate comes from', 'Откуда взялась ставка'),
  ('Two operators who publish their prices', 'Два оператора, которые публикуют свои цены'),
  ('Nothing on this page is a projection of ours. Every figure starts from what two working operators charge their own customers, in public, on their own websites: a towed Irish pub in Columbus, Ohio, and a towed espresso bar in Calgary, Alberta. A number you can go and check is worth more than a number we modelled.',
   'На этой странице нет наших прогнозов. Все цифры отталкиваются от того, что два работающих оператора берут со своих клиентов — публично, на своих же сайтах: буксируемый ирландский паб в Колумбусе, Огайо, и буксируемый эспрессо-бар в Калгари, Альберта. Цифра, которую можно пойти и проверить, стоит больше, чем цифра, которую мы смоделировали.'),
  fig('Their price lists, converted at $1 = €0.92',
      'Их прайсы, пересчитанные по курсу $1 = €0,92',
      [('Package', 'Пакет'), ('Asked', 'Ставка'), ('In euro', 'В евро')], b1,
      'Park &amp; Pour let the pub by the night and the renter brings the beer, which is why nothing they sell has a drinks cost in it. Hayloft sell a booking rather than an hour: three hours on site, one barista, 150 drinks included. The two are different businesses that happen to arrive at the same top rate, and that coincidence is the most useful thing on this page.',
      'Park &amp; Pour сдают паб на вечер, а пиво привозит арендатор — поэтому в том, что они продают, нет себестоимости напитков. Hayloft продают не час, а бронь: три часа на площадке, один бариста, 150 напитков включено. Это два разных бизнеса, которые сошлись в одной верхней ставке, и это совпадение — самое полезное, что есть на этой странице.'))

# ── 2. one outing ────────────────────────────────────────────────────────
b2 = (row('Charged for the outing', 'Ставка за выезд', E(COF_FEE), E(BAR_CLA), E(BAR_PRE))
    + row('Staff', 'Персонал', MINUS + E(cof_staff), MINUS + E(bar_staff), MINUS + E(bar_staff))
    + row('Cost of what is served', 'Себестоимость того, что подаёте', MINUS + E(cof_stock), DASH, DASH)
    + row('Fuel and towing', 'Топливо и буксировка', MINUS + E(cof_fuel), MINUS + E(bar_fuel), MINUS + E(bar_fuel))
    + row('Cleaning, consumables, line service', 'Уборка, расходники, обслуживание линии',
          MINUS + E(cof_admin), MINUS + E(bar_run), MINUS + E(bar_run))
    + row('Left over', 'Остаётся', E(COF_NET), E(BAR_NET_C), E(BAR_NET_P), tot=True))

s2 = section(
  ('One outing', 'Один выезд'),
  ('What a booking leaves, line by line', 'Что остаётся с одной брони, построчно'),
  ('The bar appears twice on purpose. At the cheapest package the same trailer leaves ' + E(BAR_NET_C) + '; at the dearest it leaves ' + E(BAR_NET_P) + '. That gap is the single most consequential number on this page, and it is not equipment — it is how much the unit looks like an occasion when it arrives.',
   'Бар стоит в таблице дважды намеренно. По самому дешёвому пакету тот же прицеп оставляет ' + ER(BAR_NET_C) + ', по самому дорогому — ' + ER(BAR_NET_P) + '. Этот разрыв — самая важная цифра на странице, и дело не в оборудовании, а в том, насколько юнит выглядит событием, когда он приезжает.'),
  fig('One outing, three packages', 'Один выезд, три пакета',
      [('Line', 'Строка'), ('Coffee', 'Кофе'), ('Bar, cheapest', 'Бар, дешёвый'), ('Bar, dearest', 'Бар, дорогой')], b2,
      'Labour is at €18 an hour throughout. Coffee is one barista for six hours — three on site and the travel around them. The bar is two people for four hours, because a pub has to be towed, set up and taken down, and it has no drinks cost because the client brings the kegs.',
      'Труд везде посчитан по €18 в час. Кофе — это один бариста на шесть часов: три на площадке и дорога вокруг них. Бар — двое на четыре часа, потому что паб надо привезти, поставить и забрать; себестоимости напитков у него нет, потому что кегу привозит заказчик.'))

# ── 3. trading yourself ──────────────────────────────────────────────────
b3 = (row('Sold over the day', 'Продано за день',
          cell(FC['cups'], FC['price']), cell(FB['cups'], FB['price']))
    + row('Taken', 'Выручка', E(FCg), E(FBg))
    + row('Cost of what is served', 'Себестоимость того, что подаёте', MINUS + E(FCc), MINUS + E(FBc))
    + row('Pitch fee', 'Место на площадке', MINUS + E(FC['pitch']), MINUS + E(FB['pitch']))
    + row('Staff, two people for nine hours', 'Персонал, двое по девять часов', MINUS + E(FCl), MINUS + E(FBl))
    + row('Left over', 'Остаётся', E(FCn), E(FBn), tot=True))

s3 = section(
  ('The other way to earn', 'Второй способ заработать'),
  ('Trading for yourself at a festival', 'Торговля за свой счёт на фестивале'),
  ('A private booking is a fee. A festival is not: you pay for the pitch and you keep what you sell. It is the mode every operator asks about, so here it is at honest volumes — a hard nine-hour day with two people on the counter.',
   'Частная бронь — это гонорар. Фестиваль устроен иначе: вы платите за место и оставляете себе то, что продали. Про этот режим спрашивают все, поэтому вот он в честных объёмах — тяжёлый девятичасовой день, двое за стойкой.'),
  fig('One festival day', 'Один фестивальный день',
      [('Line', 'Строка'), ('Coffee', 'Кофе'), ('Bar', 'Бар')], b3,
      'This is the finding worth arguing with. On these volumes a festival day leaves the coffee unit ' + E(FCn) + ' against ' + E(COF_NET) + ' for a private booking — a fifth of it, for three times the hours. The bar fares better but still comes second. Festivals fill the gaps in a diary; they do not build the payback. If your own numbers say otherwise, the ones to change are the cups and the pitch fee.',
      'Вот вывод, с которым стоит поспорить. При этих объёмах фестивальный день оставляет кофейному юниту ' + ER(FCn) + ' против ' + ER(COF_NET) + ' с частной брони — пятую часть, за втрое большее время. У бара лучше, но всё равно второе место. Фестивали затыкают дыры в календаре, а не окупают юнит. Если ваши цифры говорят иначе — менять надо число порций и цену места.'))

# ── 4. a season ──────────────────────────────────────────────────────────
b4 = ''.join(row(str(n) + ' outings', str(n) + ' выездов', E(COF_NET * n), E(BAR_NET_P * n))
             for n in OUT)
b4 += row('20 private outings and 10 festival days', '20 частных выездов и 10 фестивальных дней',
          E(COF_NET * 20 + FCn * 10), E(BAR_NET_P * 20 + FBn * 10))

s4 = section(
  ('A season', 'Сезон'),
  ('What a full year of it comes to', 'Во что складывается год'),
  ('A European season of private events is roughly twenty weekends, and a weekend can hold more than one outing. Eighteen is a slow first year while the diary fills; forty is an operator who is properly booked.',
   'Европейский сезон частных мероприятий — это примерно двадцать выходных, и в выходные помещается не один выезд. Восемнадцать — это медленный первый год, пока набирается календарь; сорок — это оператор, у которого действительно всё занято.'),
  fig('Left over across a season', 'Остаётся за сезон',
      [('Season', 'Сезон'), ('Coffee', 'Кофе'), ('Bar', 'Бар')], b4,
      'The bar is taken at the dearest package throughout. At the cheapest one it earns roughly a third less, which moves every line in this table by the same third.',
      'Бар везде посчитан по дорогому пакету. По дешёвому он зарабатывает примерно на треть меньше, и на эту же треть смещается каждая строка таблицы.'))

# ── 5. what the model supports ───────────────────────────────────────────
b5 = ''
for label_en, label_ru, net in [('Coffee', 'Кофе', COF_NET), ('Bar', 'Бар', BAR_NET_P)]:
    for n in (24, 30, 40):
        b5 += row(label_en + ', ' + str(n) + ' outings', label_ru + ', ' + str(n) + ' выездов',
                  E(net * n * 2), E(net * n * 3))

s5 = section(
  ('The test', 'Проверка'),
  ('What price the model actually supports', 'Какую цену модель выдерживает'),
  ('Read backwards, the arithmetic answers the only question that matters before a price is quoted: what can a unit cost and still pay for itself in the time a buyer will accept? Two seasons is where an owner decides alone, without a lender and without being talked into it. Three is where the decision needs a reason.',
   'Прочитанная в обратную сторону, арифметика отвечает на единственный вопрос, который важен до всякой цены: сколько может стоить юнит, чтобы окупиться в срок, который покупатель примет? Два сезона — это когда владелец решает сам, без банка и без уговоров. Три — это когда решению нужен повод.'),
  fig('The most a unit can cost and still pay for itself',
      'Максимальная цена, при которой юнит ещё окупается',
      [('Use', 'Режим'), ('In two seasons', 'За два сезона'), ('In three', 'За три')], b5,
      'This is the number we hold ourselves to, and it is why there is no price on this page yet. A price is worth quoting when it sits inside this table for a diary a buyer can actually fill — not when it merely looks right beside a house.',
      'Это та цифра, по которой мы проверяем себя, и именно поэтому на этой странице пока нет цены. Цену имеет смысл называть тогда, когда она попадает внутрь этой таблицы при календаре, который покупатель реально заполнит, — а не тогда, когда она просто красиво смотрится рядом с ценой дома.'))

# ── 6. what is not counted ───────────────────────────────────────────────
s6 = section(
  ('The edges', 'Границы'),
  ('What is not in any of these numbers', 'Чего в этих цифрах нет'),
  ('Counted: what you charge, less staff, stock, fuel and the running of the unit. Not counted: VAT, insurance, the cost of borrowing, the vehicle that tows it, storage over the winter, and what the unit is still worth on the day it is paid off. The first five lengthen the payback. The last one shortens it, and on a trailer that has been maintained it is not a small number.',
   'Учтено: ваша ставка минус персонал, продукт, топливо и обслуживание юнита. Не учтено: НДС, страховка, стоимость денег, тягач, зимнее хранение и остаточная стоимость юнита в день, когда он окупился. Первые пять удлиняют срок. Последняя укорачивает, и на ухоженном прицепе это не маленькая цифра.'),
  '''          <p class="fineprint" style="margin-top:26px;">''' + t(
   'Three things would change these figures and none of them are ours to assert yet: the rates verified against European operators rather than North American ones, the real cost of the build once the specification is fixed, and whether a season where you work is twenty weekends or eight. Tell us your own three and we will run the same sheet against them.',
   'Три вещи изменили бы эти цифры, и ни одну из них мы пока не вправе утверждать: ставки, проверенные у европейских операторов, а не у североамериканских; реальная себестоимость сборки, когда зафиксирована спецификация; и то, сколько выходных в сезоне именно там, где вы работаете, — двадцать или восемь. Назовите свои три, и мы прогоним по ним ту же таблицу.') + '''</p>
''')

# ── the page ─────────────────────────────────────────────────────────────
PAGE = '''
    <!-- ======================================================
         MOBILE BARS — the working behind the numbers
         ====================================================== -->
    <section id="view-unit-economics" class="view-section">
      <div class="container page-top">
        <div class="breadcrumbs">
          <a class="breadcrumb-item" href="/">Home</a>
          <span>/</span>
          <a class="breadcrumb-item" href="/bars/">Mobile bars</a>
          <span>/</span><span class="breadcrumb-current">''' + t('The working', 'Расчёт') + '''</span>
        </div>

        <div class="section-pad">
          <span class="eyebrow">''' + t('The financial model', 'Финансовая модель') + '''</span>
          <h1 class="page-title serif">''' + t('How the numbers were worked out', 'Как посчитаны цифры') + '''</h1>
          <p class="page-lede">''' + t(
  'The short version is on the bars page. This is the long one: every rate, every cost line and every assumption behind it, in the order they were worked out, so you can disagree with a specific number rather than with the conclusion.',
  'Короткая версия — на странице баров. Здесь длинная: каждая ставка, каждая статья расходов и каждое допущение за ними, в том порядке, в каком считалось, — чтобы можно было спорить с конкретной цифрой, а не с выводом.') + '''</p>
        </div>

''' + s1 + s2 + s3 + s4 + s5 + s6 + '''        <div class="section-pad">
          <a class="btn btn-solid" href="/enquiry/">Ask for a quotation</a>
          <p style="margin-top:26px;"><a class="btn btn-line" href="/bars/">''' + t('Back to the units', 'Назад к юнитам') + '''</a></p>
        </div>
      </div>
    </section>
'''

# ── patch the source ─────────────────────────────────────────────────────
s = io.open(SRC, encoding='utf-8').read()

def once(old, new, label):
    global s
    if s.count(old) != 1:
        sys.exit('anchor %s matched %d' % (label, s.count(old)))
    s = s.replace(old, new)

once('''    <!-- ======================================================
         ALL FARMS
         ====================================================== -->''',
     PAGE.rstrip() + '''

    <!-- ======================================================
         ALL FARMS
         ====================================================== -->''', 'page')

once("""  'all-units':       '/bars/',""",
     """  'all-units':       '/bars/',\n  'unit-economics':  '/bars/economics/',""", 'view-path')

once("""  'all-units': '/bars/',
  'enquiry': '/enquiry/',""",
     """  'all-units': '/bars/', 'unit-economics': '/bars/economics/',
  'enquiry': '/enquiry/',""", 'legacy')

once("""  '/enquiry/': {
    title: 'Register your interest — Tiny Mansion',""",
     """  '/bars/economics/': {
    title: 'The financial model — Tiny Mansion',
    desc:  'Every rate, cost line and assumption behind the mobile bar numbers: two published operator price lists, one outing, a festival day, a season, and the price the model supports.'
  },
  '/enquiry/': {
    title: 'Register your interest — Tiny Mansion',""", 'head-meta')

# the two ways in
once('''          <p style="margin-top:26px;"><a class="btn btn-line" href="/bars/">See how that is worked out</a></p>''',
     '''          <p style="margin-top:26px;"><a class="btn btn-line" href="/bars/economics/">See how that is worked out</a></p>''', 'unit-link')

once('''          <p class="fineprint" style="margin-top:34px;">Counted: what you charge, less staff''',
     '''          <p style="margin-top:34px;"><a class="btn btn-line" href="/bars/economics/">''' + t('See the whole working', 'Смотреть весь расчёт') + '''</a></p>

          <p class="fineprint" style="margin-top:34px;">Counted: what you charge, less staff''', 'bars-link')

once('''              <li><a href="/bars/" class="footer-link">Mobile bars</a></li>''',
     '''              <li><a href="/bars/" class="footer-link">Mobile bars</a></li>
              <li><a href="/bars/economics/" class="footer-link">''' + t('The financial model', 'Финансовая модель') + '''</a></li>''', 'footer')

# ── the dictionary ───────────────────────────────────────────────────────
def js(v):
    return "'" + v.replace('\\', '\\\\').replace("'", "\\'") + "'"

lines = ['  /* ── Финмодель: /bars/economics/ ── */']
for k in sorted(TXT):
    pair = '  ' + js(k) + ': ' + js(TXT[k]) + ','
    if len(pair) > 96:
        pair = '  ' + js(k) + ':\n    ' + js(TXT[k]) + ','
    lines.append(pair)
lines.append('')
lines.append('  /* Числа: разделитель тысяч в русском — пробел, не запятая. */')
for k in sorted(NUM):
    if NUM[k] != k:
        lines.append('  ' + js(k) + ': ' + js(NUM[k]) + ',')

anchor = "  /* ── Мобильные бары и кухни ── */\n"
if s.count(anchor) != 1:
    sys.exit('dictionary anchor %d' % s.count(anchor))
s = s.replace(anchor, '\n'.join(lines) + '\n\n' + anchor)

io.open(SRC, 'w', encoding='utf-8').write(s)
print('page written: %d phrases, %d numbers' % (len(TXT), len([k for k in NUM if NUM[k] != k])))
