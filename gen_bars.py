# -*- coding: utf-8 -*-
"""Пересобирает /bars/economics/ из bars.py.

Страница показывает, из чего складывается цена юнита, почему она
диапазоном, и когда она возвращается — отдельно для бара и отдельно
для кофейни. Заменяет секцию целиком, а не дописывает, поэтому её
можно запускать сколько угодно раз.

    python3 bars.py        # посмотреть модель
    python3 gen_bars.py    # переписать страницу
    node build.mjs
"""
import io, os, sys, contextlib, runpy

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'src', 'index.html')

with contextlib.redirect_stdout(io.StringIO()):
    M = runpy.run_path(os.path.join(ROOT, 'bars.py'))

SHELL, BAR_KIT = M['SHELL'], M['BAR_KIT']
COFFEE_MID, COFFEE_TOP = M['COFFEE_MID'], M['COFFEE_TOP']
BUILDS, retail, outing = M['BUILDS'], M['retail'], M['outing']
MARGIN = M['MARGIN']

RATE, WAGE = 1_450, 18          # Европа, средняя оценка
OUTINGS = 30

def grp(rows):
    return sum(r[1] for r in rows), sum(r[2] for r in rows)

SH = grp(SHELL); BK = grp(BAR_KIT); CM = grp(COFFEE_MID); CT = grp(COFFEE_TOP)
BAR_R  = (retail(BUILDS[0][1]), retail(BUILDS[0][2]))
COFM_R = (retail(BUILDS[1][1]), retail(BUILDS[1][2]))
COFT_R = (retail(BUILDS[2][1]), retail(BUILDS[2][2]))
BAR_MID  = retail((BUILDS[0][1] + BUILDS[0][2]) / 2)
COFM_MID = retail((BUILDS[1][1] + BUILDS[1][2]) / 2)

BAR_NET = outing(RATE, WAGE, 'bar')
COF_NET = outing(RATE, WAGE, 'coffee')

# ── словарь: английский в разметку, русский в RU ─────────────────────────
TXT = {}
def t(en, ru):
    if en != ru:
        TXT[en.replace('&amp;', '&')] = ru.replace('&amp;', '&')
    return en

def E(v):
    return '€' + format(int(round(v)), ',d')

def ERU(v):
    return '€' + format(int(round(v)), ',d').replace(',', ' ')

def money(v):
    """Число в ячейке: у русского пробел вместо запятой."""
    return t(E(v), ERU(v))

def rng(a, b):
    return t(E(a) + ' – ' + E(b), ERU(a) + ' – ' + ERU(b))


def rows(items, ru_names):
    out = ''
    for (en, lo, hi), ru in zip(items, ru_names):
        out += ('        <tr><td class="lbl">' + t(en, ru) + '</td>'
                '<td class="n">' + rng(retail(lo), retail(hi)) + '</td></tr>\n')
    return out


def total_row(en, ru, lo, hi):
    return ('        <tr class="tot"><td class="lbl">' + t(en, ru) + '</td>'
            '<td class="n">' + rng(retail(lo), retail(hi)) + '</td></tr>\n')


def fig(cap_en, cap_ru, head_en, head_ru, body, note_en, note_ru,
        val_en='Price', val_ru='Цена'):
    return ('''          <figure class="fig">
            <table>
              <caption>''' + t(cap_en, cap_ru) + '''</caption>
              <thead><tr><th>''' + t(head_en, head_ru) + '''</th>'''
            '<th class="n">' + t(val_en, val_ru) + '</th></tr></thead>\n'
            '              <tbody>\n' + body + '''              </tbody>
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


# ── 1. почему диапазон ───────────────────────────────────────────────────
s1 = section(
  ('Why the price moves', 'Почему цена не одна'),
  ('The shell is ours. The equipment is your choice.',
   'Корпус наш. Оборудование — ваш выбор.'),
  ('Two units off the same drawing can differ by twenty thousand euro, and all of that '
   'difference sits in the equipment. Some buyers already own machines. Some have a supplier '
   'they have worked with for years. Some want one particular espresso machine and nothing '
   'else. We build the trailer around whatever you decide, and the price follows that decision '
   'rather than a price list of ours.',
   'Два юнита по одному чертежу могут отличаться на двадцать тысяч евро, и вся эта разница — '
   'в оборудовании. У кого-то машины уже есть. У кого-то поставщик, с которым работают годами. '
   'Кто-то хочет одну конкретную кофемашину и никакую другую. Мы строим прицеп вокруг вашего '
   'решения, и цена идёт за этим решением, а не за нашим прайсом.'),
  '          <p class="fineprint" style="margin-top:26px;">' + t(
   'If you bring your own equipment, its line simply comes out of the quotation. What stays is '
   'the shell, the services and the fitting — and we will say plainly whether what you have '
   'will work in a trailer that moves.',
   'Если оборудование у вас своё, его строка просто уходит из расчёта. Остаётся корпус, '
   'инженерия и монтаж — и мы прямо скажем, будет ли то, что у вас есть, работать в прицепе, '
   'который ездит.') + '</p>\n')

# ── 2. корпус ────────────────────────────────────────────────────────────
b2 = rows(SHELL, [
    'Шасси двухосное с тормозами, 6,4 м, допуск ЕС',
    'Каркас и утеплённые сэндвич-панели, корпус',
    'Окно выдачи, роллета, маркиза',
    'Дверь, остекление, замок',
    'Внутренняя отделка: нержавейка, пищевой пол',
    'Электрика: щит, ввод CEE, розетки, свет',
    'Вода: баки, насос, бойлер, две мойки',
    'Буфер 5 кВт·ч и инвертор',
    'Покраска и ливрея заказчика',
    'Сборка, работа',
    'Омологация, регистрация, документы',
]) + total_row('The shell, complete', 'Корпус целиком', SH[0], SH[1])

s2 = section(
  ('What we build', 'Что делаем мы'),
  ('The shell, and everything that makes it road-legal',
   'Корпус и всё, что делает его дорожным'),
  ('This part does not change with the fit-out. It is the same trailer under a draft bar and '
   'under an espresso counter: the chassis, the body, the services, the paint and the papers.',
   'Эта часть не зависит от начинки. Под разливным баром и под эспрессо-стойкой один и тот же '
   'прицеп: шасси, корпус, инженерия, покраска и документы.'),
  fig('The shell, line by line', 'Корпус по строкам',
      'Component', 'Узел', b2,
      'A buffer battery, not autonomy. A bar at an event stands on shore power; it does not '
      'need the week of independence a residence is built for, and it is not paying for it.',
      'Буферная батарея, а не автономность. Бар на мероприятии стоит у розетки: недельная '
      'независимость, ради которой строится резиденция, ему не нужна — и он за неё не платит.'))

# ── 3. барное оборудование ───────────────────────────────────────────────
b3 = rows(BAR_KIT, [
    'Гликолевый чиллер',
    'Питон и фитинги на шесть кранов',
    'Башня-колонна, шесть кранов',
    'Холодильный агрегат кегового отсека',
    'Два подстоечных холодильника',
    'Ванна для льда и спидрейл',
    'Мойка для посуды, раковина, водонагреватель',
    'Стойка розлива, каплесборник, ополаскиватель',
    'Бэк-бар: полки, свет',
    'CO₂ и азот: баллоны, редукторы, обвязка',
]) + total_row('The bar fit-out', 'Барная начинка', BK[0], BK[1])

s3 = section(
  ('The draft bar', 'Разливной бар'),
  ('What goes into pouring', 'Из чего собирается розлив'),
  ('Built around the glycol line, because that is what decides whether the last pour at '
   'midnight is the same temperature as the first one at noon.',
   'Собирается вокруг гликолевой линии — именно она решает, будет ли последняя кружка в '
   'полночь той же температуры, что первая в полдень.'),
  fig('The bar fit-out, line by line', 'Барная начинка по строкам',
      'Component', 'Узел', b3,
      'Six taps is the common configuration; four and twelve are both possible and both move '
      'the chiller, the python and the tower.',
      'Шесть кранов — обычная конфигурация. Четыре и двенадцать тоже возможны, и оба варианта '
      'двигают чиллер, питон и колонну.'))

# ── 4. кофейное оборудование ─────────────────────────────────────────────
b4 = rows(COFFEE_MID, [
    'Эспрессо-машина двухгруппная, средний класс',
    'Две кофемолки on-demand, средний класс',
    'Водоподготовка, умягчение, помпа',
    'Холодильник для молока подстоечный',
    'Темпер, нок-бокс, инструмент',
    'Барная станция: спидрейл, ванна, гастроёмкости',
    'Блендер и станция шейкера',
    'Мойка для посуды, раковина, водонагреватель',
    'Бэк, полки, свет, POS-стойка',
]) + total_row('The coffee fit-out', 'Кофейная начинка', CM[0], CM[1])
b4 += total_row('The same, with top-tier machine and grinders',
                'То же, с машиной и кофемолками верхнего класса', CT[0], CT[1])

s4 = section(
  ('The espresso bar', 'Кофейня'),
  ('Where the choice of machine changes everything',
   'Здесь выбор машины меняет всё'),
  ('The espresso machine and the grinders are the single largest variable in the whole '
   'quotation. A mid-range two-group and a La Marzocco Linea are eight thousand euro apart, '
   'and the trailer around them is identical.',
   'Эспрессо-машина и кофемолки — самая большая переменная во всём расчёте. Между двухгруппной '
   'машиной среднего класса и La Marzocco Linea восемь тысяч евро разницы, а прицеп вокруг них '
   'одинаковый.'),
  fig('The coffee fit-out, line by line', 'Кофейная начинка по строкам',
      'Component', 'Узел', b4,
      'The top-tier line replaces the machine and the grinders and leaves the rest untouched. '
      'That is the whole difference between the two figures.',
      'Верхний класс меняет только машину и кофемолки, всё остальное остаётся тем же. В этом и '
      'вся разница между двумя цифрами.'))

# ── 5. цена целиком ──────────────────────────────────────────────────────
b5 = (
  '        <tr><td class="lbl">' + t('Draft bar', 'Разливной бар') + '</td>'
  '<td class="n">' + rng(*BAR_R) + '</td></tr>\n'
  '        <tr><td class="lbl">' + t('Espresso bar, mid-range equipment',
                                     'Кофейня, оборудование среднего класса') + '</td>'
  '<td class="n">' + rng(*COFM_R) + '</td></tr>\n'
  '        <tr><td class="lbl">' + t('Espresso bar, top-tier equipment',
                                     'Кофейня, оборудование верхнего класса') + '</td>'
  '<td class="n">' + rng(*COFT_R) + '</td></tr>\n')

s5 = section(
  ('The price', 'Цена'),
  ('What a unit comes to', 'Во что обходится юнит'),
  ('Delivered to your gate, in your own livery, with the papers. The spread inside each line '
   'is the equipment, not our margin — that stays the same across the whole range.',
   'До ваших ворот, в вашей ливрее, с документами. Разброс внутри каждой строки — это '
   'оборудование, а не наша маржа: она одинакова по всему диапазону.'),
  fig('Delivered price', 'Цена с доставкой',
      'Unit', 'Юнит', b5,
      'Quoted per order against the specification you approve. Bring your own equipment and '
      'those lines come out; specify something we have not costed and we will price it before '
      'you commit.',
      'Считается под заказ по спецификации, которую вы утверждаете. Своё оборудование — строки '
      'уходят из расчёта; что-то, чего мы не считали, — посчитаем до того, как вы на что-то '
      'подпишетесь.'))

print('sections 1-5 built, %d phrases so far' % len(TXT))

# ── 6 и 7. бизнес-модель, отдельно под каждый юнит ───────────────────────
def money_row(en, ru, v, minus=False, tot=False):
    cls = ' class="tot"' if tot else ''
    val = ('−' if minus else '') + money(v)
    return ('        <tr' + cls + '><td class="lbl">' + t(en, ru) + '</td>'
            '<td class="n">' + val + '</td></tr>\n')


def model_section(kind, eyebrow, head, lede, price, net, cost_rows, note):
    body = money_row('Charged for the outing', 'Ставка за выезд', RATE)
    for en, ru, v in cost_rows:
        body += money_row(en, ru, v, minus=True)
    body += money_row('Left over', 'Остаётся', net, tot=True)

    season = ''
    for n in (18, 24, 30, 40):
        season += ('        <tr><td class="lbl">'
                   + t(str(n) + ' outings', str(n) + ' выездов') + '</td>'
                   '<td class="n">' + money(net * n) + '</td>'
                   '<td class="n">' + t('%.1f' % (price / (net * n)),
                                        ('%.1f' % (price / (net * n))).replace('.', ','))
                   + '</td></tr>\n')

    return section(eyebrow, head, lede,
      fig('One outing', 'Один выезд', 'Line', 'Строка', body,
          'At €1,450 an outing and €18 an hour for labour — a middle estimate for western '
          'Europe. The one rate we can point at is North American: the Ohio and Alberta '
          'operators who publish theirs.',
          'При ставке €1 450 за выезд и €18 в час за труд — это средняя оценка по Западной '
          'Европе. Единственная ставка, на которую мы можем показать пальцем, '
          'североамериканская: операторы в Огайо и Альберте публикуют свою.',
          'Amount', 'Сумма')
      + '''          <figure class="fig">
            <table>
              <caption>''' + t('A season, and when the unit is paid off at ' + E(price),
                               'Сезон и окупаемость при цене ' + ERU(price)) + '''</caption>
              <thead><tr><th>''' + t('Season', 'Сезон') + '</th>'
      '<th class="n">' + t('Left over', 'Остаётся') + '</th>'
      '<th class="n">' + t('Seasons to pay off', 'Сезонов до возврата') + '</th></tr></thead>\n'
      '              <tbody>\n' + season + '''              </tbody>
            </table>
            <figcaption class="fig-note">''' + t(*note) + '''</figcaption>
          </figure>
''')


s6 = model_section('bar',
  ('The bar, in numbers', 'Бар в цифрах'),
  ('What a draft bar earns', 'Что зарабатывает разливной бар'),
  ('The client brings the kegs, so there is no drinks cost on our side. In exchange the outing '
   'costs more to run: a pub has to be towed, set up and taken down by two people.',
   'Кегу привозит заказчик, поэтому себестоимости напитков здесь нет. Зато дороже сам выезд: '
   'паб надо привезти, поставить и забрать вдвоём.'),
  BAR_MID, BAR_NET,
  [('Staff, two people for four hours', 'Персонал, двое по четыре часа', 2 * 4 * WAGE),
   ('Fuel and towing', 'Топливо и буксировка', 60),
   ('Cleaning, consumables, line service', 'Уборка, расходники, обслуживание линии', 100)],
  ('Taken at ' + E(BAR_MID) + ', the middle of the range. A cheaper build pays back sooner, a '
   'dearer one later, and the arithmetic is the same either way.',
   'Считано по ' + ERU(BAR_MID) + ' — середине диапазона. Сборка дешевле окупается быстрее, '
   'дороже — медленнее, арифметика та же.'))

s7 = model_section('coffee',
  ('The coffee bar, in numbers', 'Кофейня в цифрах'),
  ('What an espresso bar earns', 'Что зарабатывает кофейня'),
  ('One barista, three hours on site, a hundred and fifty drinks — the package the Alberta '
   'operator sells. Here the drinks do cost something, because you are the one supplying them.',
   'Один бариста, три часа на площадке, полтораста напитков — тот пакет, который продаёт '
   'оператор в Альберте. Здесь напитки уже чего-то стоят, потому что поставляете их вы.'),
  COFM_MID, COF_NET,
  [('Barista, six hours including travel', 'Бариста, шесть часов с дорогой', 6 * WAGE),
   ('Beans, milk, cups: 150 drinks', 'Зерно, молоко, стаканы: 150 напитков', 165),
   ('Fuel and towing', 'Топливо и буксировка', 60),
   ('Cleaning and consumables', 'Уборка и расходники', 40)],
  ('Taken at ' + E(COFM_MID) + ', the mid-range build. The top-tier machine adds about twelve '
   'thousand to the price and nothing to the revenue — it buys queue speed and the look of the '
   'counter, not a higher rate.',
   'Считано по ' + ERU(COFM_MID) + ' — сборке среднего класса. Машина верхнего класса '
   'добавляет к цене около двенадцати тысяч и ничего к выручке: она покупает скорость очереди '
   'и вид стойки, а не ставку.'))

# ── 8. оговорки ──────────────────────────────────────────────────────────
s8 = section(
  ('The edges', 'Границы'),
  ('What these numbers rest on', 'На чём эти цифры стоят'),
  ('Component prices here are market estimates, not quotations we have been given. The rate of '
   '€1,450 an outing is an estimate for western Europe; the only rates we can point at are the '
   'two North American operators who publish theirs. Both will move when we have invoices and '
   'European operators to compare against, and we will publish what changes.',
   'Цены узлов здесь — рыночные оценки, а не выставленные нам счета. Ставка €1 450 за выезд — '
   'оценка по Западной Европе; единственные ставки, на которые можно показать пальцем, — у двух '
   'североамериканских операторов, публикующих свои прайсы. И то и другое сдвинется, когда '
   'появятся счета и европейские операторы для сравнения, и мы опубликуем, что изменилось.'),
  '          <p class="fineprint" style="margin-top:26px;">' + t(
   'Not in the price: VAT, the vehicle that tows it, your insurance, and whatever your own '
   'municipality asks of a business serving food or drink.',
   'Не входит в цену: НДС, тягач, ваша страховка и всё, что ваш муниципалитет спрашивает с '
   'бизнеса, который наливает и кормит.') + '</p>\n')

# ── страница целиком ─────────────────────────────────────────────────────
PAGE = '''    <!-- ======================================================
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
          <span class="eyebrow">''' + t('Price and economics', 'Цена и экономика') + '''</span>
          <h1 class="page-title serif">''' + t('What the price is made of, and when it comes back',
                                               'Из чего складывается цена и когда она возвращается') + '''</h1>
          <p class="page-lede">''' + t(
  'Every component we costed, what each one adds, and the arithmetic of a season — separately '
  'for the bar and for the coffee bar. Disagree with a line rather than with the conclusion.',
  'Каждый узел, который мы посчитали, что он добавляет, и арифметика сезона — отдельно для бара '
  'и отдельно для кофейни. Спорьте со строкой, а не с выводом.') + '''</p>
        </div>

''' + s1 + s2 + s3 + s4 + s5 + s6 + s7 + s8 + '''        <div class="section-pad">
          <a class="btn btn-solid" href="/enquiry/">Ask for a quotation</a>
          <p style="margin-top:26px;"><a class="btn btn-line" href="/bars/">''' + t(
  'Back to the units', 'Назад к юнитам') + '''</a></p>
        </div>
      </div>
    </section>
'''

# ── подстановка в src/index.html ─────────────────────────────────────────
s = io.open(SRC, encoding='utf-8').read()

A = '''    <!-- ======================================================
         MOBILE BARS — the working behind the numbers'''
B = '''    <!-- ======================================================
         ALL FARMS'''
if s.count(A) != 1 or s.count(B) != 1:
    sys.exit('якорь секции: %d / %d' % (s.count(A), s.count(B)))
s = s[:s.index(A)] + PAGE + '\n' + s[s.index(B):]

C = '  /* ── Финмодель: /bars/economics/ ── */'
D = '  /* ── Мобильные бары и кухни ── */'
if s.count(C) != 1 or s.count(D) != 1:
    sys.exit('якорь словаря: %d / %d' % (s.count(C), s.count(D)))

def js(v):
    return "'" + v.replace('\\', '\\\\').replace("'", "\\'") + "'"

lines = [C]
for k in sorted(TXT):
    pair = '  ' + js(k) + ': ' + js(TXT[k]) + ','
    if len(pair) > 96:
        pair = '  ' + js(k) + ':\n    ' + js(TXT[k]) + ','
    lines.append(pair)
lines.append('')
s = s[:s.index(C)] + '\n'.join(lines) + '\n' + s[s.index(D):]

io.open(SRC, 'w', encoding='utf-8').write(s)
print('страница пересобрана: %d фраз в словаре' % len(TXT))
