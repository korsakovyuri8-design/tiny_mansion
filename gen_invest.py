# -*- coding: utf-8 -*-
"""Собирает /invest/ и /invest/en/ из club.py.

Обе страницы пишутся одним проходом из одной модели, поэтому русская и
английская версии не могут разойтись, а цифры на странице не могут
разойтись с расчётом. Меняется club.py — запускается это.

    python3 gen_invest.py
"""
import io, os, sys, contextlib, runpy

ROOT = os.path.dirname(os.path.abspath(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    M = runpy.run_path(os.path.join(ROOT, 'club.py'))

UNITS      = M['UNITS']
HOUSE_LOW  = M['HOUSE_LOW']
HOUSE_HIGH = M['HOUSE_HIGH']
ONBOARD    = M['ONBOARDING']
SEASONS    = M['SEASONS']
SCEN       = M['SCENARIOS']
GROSS      = M['MGMT_GROSS']
GOPSH      = M['MGMT_GOP']
HURDLE     = M['HURDLE']
VARIABLE   = M['VARIABLE']
FIXED      = M['FIXED_NETWORK']
unit       = M['unit']
scaled     = M['scaled']
with_floor = M['with_floor']
breaks_at  = M['floor_breaks_at']

CHEQUE_LOW, CHEQUE_HIGH = HOUSE_LOW + ONBOARD, HOUSE_HIGH + ONBOARD
MOVE = 6_000                       # переезд в соседнюю страну, на юнит

R = {n: unit(o) for n, o in SCEN}
COLS = [n for n, _ in SCEN]
YL = [R[n]['inv'] / CHEQUE_HIGH for n in COLS]      # дороже дом — ниже %
YH = [R[n]['inv'] / CHEQUE_LOW for n in COLS]


# ── форматирование чисел под язык ────────────────────────────────────────
def eur(v, ru):
    s = format(int(round(v)), ',d')
    return '€' + (s.replace(',', ' ') if ru else s)

def pct(v, ru, d=1):
    s = ('%.' + str(d) + 'f') % (v * 100)
    return (s.replace('.', ',') if ru else s) + '%'


# ── строки парами ────────────────────────────────────────────────────────
def T(ru, en):
    return {'ru': ru, 'en': en}

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def page(lang):
    ru = lang == 'ru'
    E  = lambda v: eur(v, ru)
    P  = lambda v, d=1: pct(v, ru, d)
    t  = lambda pair: pair['ru'] if ru else pair['en']
    out = []
    w = out.append

    # ── шапка документа ──────────────────────────────────────────────────
    title = t(T('Tiny Mansion · Дом в собственность на ферме Адриатики',
                'Tiny Mansion · A house of your own on an Adriatic farm'))
    desc = t(T('Резиденция в вашей собственности на действующей ферме в Черногории. '
               'Чек %s–%s, доходность %s–%s, приоритетный доход %s. Вся арифметика на странице.'
               % (E(CHEQUE_LOW), E(CHEQUE_HIGH), P(min(YL), 0), P(max(YH), 0), P(HURDLE, 0)),
               'A residence you own outright on a working farm in Montenegro. '
               '%s–%s all in, a modelled %s–%s return, and a %s preferred return. '
               'Every figure is on the page.'
               % (E(CHEQUE_LOW), E(CHEQUE_HIGH), P(min(YL), 0), P(max(YH), 0), P(HURDLE, 0))))
    other = '/invest/en/' if ru else '/invest/'
    w('''<!DOCTYPE html>
<html lang="%s">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>%s</title>
<meta name="description" content="%s">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="alternate" hreflang="ru" href="https://tinymansion.co/invest/">
<link rel="alternate" hreflang="en" href="https://tinymansion.co/invest/en/">
<link rel="alternate" hreflang="x-default" href="https://tinymansion.co/invest/en/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Tiny Mansion">
<meta property="og:url" content="https://tinymansion.co%s">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:image" content="https://tinymansion.co/invest/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="%s">
<meta name="twitter:description" content="%s">
<meta name="twitter:image" content="https://tinymansion.co/invest/og.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400&amp;family=IBM+Plex+Mono:wght@400;500&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="/invest/invest.css">
<script src="/photo-fallback.js" defer></script>
<script src="/analytics.js" defer></script>
</head>
<body>

<header id="site-header">
  <div class="wrap">
    <div class="header-inner">
      <a href="/" class="wordmark">Tiny Mansion</a>
      <nav class="nav" aria-label="%s">
        <a href="/residences/">%s</a>
        <a href="/farms/">%s</a>
        <a href="/about/">%s</a>
        <a href="%s" aria-current="page">%s</a>
        <a href="/enquiry/">%s</a>
      </nav>
      <div class="lang" role="group" aria-label="Language">%s</div>
    </div>
  </div>
</header>

<main>''' % (lang, esc(title), esc(desc),
              '/invest/' if ru else '/invest/en/',
              esc(title), esc(desc), esc(title), esc(desc),
              t(T('Основное', 'Main')),
              t(T('Резиденции', 'Residences')), t(T('Фермы', 'Farms')),
              t(T('О нас', 'About')),
              '/invest/' if ru else '/invest/en/',
              t(T('Инвестиции', 'Invest')), t(T('Связаться', 'Enquire')),
              ('<span aria-current="true">RU</span><span class="sep" aria-hidden="true"></span>'
               '<a href="/invest/en/" hreflang="en" lang="en">EN</a>') if ru else
              ('<a href="/invest/" hreflang="ru" lang="ru">RU</a>'
               '<span class="sep" aria-hidden="true"></span><span aria-current="true">EN</span>')))

    # ── ГЕРОЙ ────────────────────────────────────────────────────────────
    w('''
<section style="padding-top:72px">
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h1>%s</h1>
    <p class="lede" style="margin-top:24px">%s</p>
    <div class="keyline">
      <span>%s</span><span>%s</span><span>%s</span><span>%s</span>
    </div>
  </div>
</section>''' % (
        t(T('Черногория · первое размещение — III квартал 2026',
            'Montenegro · first deployment Q3 2026')),
        t(T('Дом в вашей собственности,<br>который переезжает за сезоном',
            'A house you own outright,<br>that moves to where the season is')),
        t(T('Вы покупаете резиденцию на своё имя и ставите её на действующую ферму. '
            'Землю вы не покупаете и не арендуете — именно поэтому цена такая. '
            'Гостями занимаемся мы, по отдельному расторжимому договору.',
            'You buy the residence in your own name and place it on a working farm. '
            'You do not buy or rent the land, which is what keeps the price where it is. '
            'We run the guests, under a separate contract you can end.')),
        t(T('Чек %s–%s' % (E(CHEQUE_LOW), E(CHEQUE_HIGH)),
            '%s–%s all in' % (E(CHEQUE_LOW), E(CHEQUE_HIGH)))),
        t(T('Доходность %s–%s' % (P(min(YL), 0), P(max(YH), 0)),
            'Modelled %s–%s' % (P(min(YL), 0), P(max(YH), 0)))),
        t(T('Приоритетный доход %s' % P(HURDLE, 0),
            '%s preferred return' % P(HURDLE, 0))),
        t(T('Доход в евро', 'Income in euro'))))

    # ── ЧТО ЗА СДЕЛКА ────────────────────────────────────────────────────
    w('''
<section>
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h2>%s</h2>
    <p class="lede">%s</p>
    <dl class="terms">
      <div><dt>%s</dt><dd>%s</dd></div>
      <div><dt>%s</dt><dd>%s</dd></div>
      <div><dt>%s</dt><dd>%s</dd></div>
      <div><dt>%s</dt><dd>%s</dd></div>
      <div><dt>%s</dt><dd>%s</dd></div>
    </dl>
    <p class="note">%s</p>
  </div>
</section>''' % (
        t(T('Предложение', 'The offer')),
        t(T('Три договора, и ни одного скрытого', 'Three contracts, none of them hidden')),
        t(T('Купля-продажа делает дом вашим. Подключение ставит его на площадку и '
            'заводит в систему бронирования. Управление — это то, за что мы получаем, '
            'и только сверх вашего приоритетного дохода.',
            'The sale makes the house yours. The onboarding puts it on a site and into '
            'the booking system. Management is what we are paid for, and only above your '
            'preferred return.')),
        t(T('Дом', 'The house')),
        t(T('%s–%s, в вашу собственность, движимое имущество с серийным номером и счётом. '
            'Не кадастровая недвижимость.' % (E(HOUSE_LOW), E(HOUSE_HIGH)),
            '%s–%s, yours outright, movable property with a serial number and an invoice. '
            'Not cadastral real estate.' % (E(HOUSE_LOW), E(HOUSE_HIGH)))),
        t(T('Подключение', 'Onboarding')),
        t(T('%s разово: перегон, установка на ферме, интеграция в систему бронирования, '
            'замки, съёмка, листинги.' % E(ONBOARD),
            '%s once: towing, installation on the farm, booking-system integration, locks, '
            'photography, listings.' % E(ONBOARD))),
        t(T('Земля', 'The land')),
        t(T('Не покупается и не арендуется вами. Договор с фермой заключаем мы. '
            'Ни земляных работ, ни подключений, ни разрешения на строительство.',
            'Neither bought nor rented by you. The farm agreement is ours to hold. '
            'No groundwork, no connections, no building permit.')),
        t(T('Управление', 'Management')),
        t(T('%s с валовой выручки плюс %s с операционной прибыли. Договор расторжимый.'
            % (P(GROSS), P(GOPSH)),
            '%s of gross revenue plus %s of operating profit. The contract can be ended.'
            % (P(GROSS), P(GOPSH)))),
        t(T('Если захотите забрать', 'If you want it back')),
        t(T('Это транспортное средство. Расторгаете договор управления — дом едет туда, '
            'куда вы скажете.',
            'It is a vehicle. End the management contract and the house goes where you send it.')),
        t(T('Тягач, платформа, листинги и договоры с фермами принадлежат сети. Взнос за '
            'подключение — плата за услугу, а не доля в этом имуществе.',
            'The tractor, the platform, the listings and the farm agreements belong to the '
            'network. The onboarding fee buys a service, not a share of any of it.'))))

    w('<div class="plate plate--interior"><p class="plate-cap">'
      + t(T('Интерьер резиденции · рендер', 'Inside the residence · render'))
      + '</p></div>')

    # ── РЫНОК ────────────────────────────────────────────────────────────
    w('''
<section class="tint">
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h2>%s</h2>
    <p class="lede">%s</p>
    <div class="stats">
      <div class="stat"><div><span class="stat-l">%s</span><span class="stat-v">%s</span></div><p class="stat-n">%s</p></div>
      <div class="stat"><div><span class="stat-l">%s</span><span class="stat-v">%s</span></div><p class="stat-n">%s</p></div>
      <div class="stat"><div><span class="stat-l">%s</span><span class="stat-v">%s</span></div><p class="stat-n">%s</p></div>
    </div>
  </div>
</section>
<div class="plate plate--country"><p class="plate-cap">%s</p></div>''' % (
        t(T('Рынок', 'The market')),
        t(T('Побережье переполнено. Север пустой.', 'The coast is full. The north is empty.')),
        t(T('Черногория собирает больше миллиарда евро туристической выручки в год, и почти '
            'вся она приходится на четыре месяца на одной полосе у моря.',
            'Montenegro takes over a billion euro in tourism revenue a year, and almost all of '
            'it lands in four months on one strip by the sea.')),
        t(T('Ночёвок на побережье', 'Nights on the coast')), P(0.897),
        t(T('Сентябрь 2025. Страна фактически работает одной полосой берега.',
            'September 2025. The country effectively runs on a single strip of shoreline.')),
        t(T('Ночёвок в горах', 'Nights in the mountains')), P(0.029),
        t(T('Дурмитор, Биоградска Гора, Комови. Природа мирового уровня, гостей почти нет.',
            'Durmitor, Biogradska Gora, Komovi. World-class landscape, almost no guests.')),
        t(T('Туристическая выручка, 2025', 'Tourism revenue, 2025')),
        t(T('€1,3 млрд', '€1.3bn+')),
        t(T('Рекордный год: более 2,7 млн приездов и свыше 15 млн ночёвок.',
            'A record year: over 2.7m arrivals and more than 15m overnight stays.')),
        t(T('Север Черногории · 2,9% ночёвок страны',
            "Northern Montenegro · 2.9% of the country's nights"))))

    # ── СТАВКА ПО СЕЗОНАМ ────────────────────────────────────────────────
    rows = ''.join('<tr><td>%s</td><td>%d</td><td class="us">%s</td></tr>'
                   % (esc(t(T(n, en))), d, E(r))
                   for (n, d, r), en in zip(SEASONS, [
                       'Peak — the sea in summer, the mountains in their season',
                       'Shoulder — wine country, the lake, the in-between months',
                       'Low — deep winter']))
    w('''
<section>
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h2>%s</h2>
    <p class="lede">%s</p>
    <div class="tblwrap"><table>
      <thead><tr><th>%s</th><th>%s</th><th class="us">%s</th></tr></thead>
      <tbody>%s</tbody>
    </table></div>
    <p class="note">%s</p>
  </div>
</section>''' % (
        t(T('Ставка', 'The rate')),
        t(T('От %s до %s за ночь, по сезону' % (E(SEASONS[2][2]), E(SEASONS[0][2])),
            '%s to %s a night, by season' % (E(SEASONS[2][2]), E(SEASONS[0][2])))),
        t(T('Одна цифра за ночь — это удобно в презентации и бесполезно в расчёте. '
            'Резиденция продаётся по-разному в августе на побережье и в феврале в горах.',
            'A single nightly figure is convenient in a deck and useless in a model. '
            'The residence sells for one price on the coast in August and another in the '
            'mountains in February.')),
        t(T('Сезон', 'Season')), t(T('Ночей в году', 'Nights')), t(T('Ставка', 'Rate')),
        rows,
        t(T('Средневзвешенная по фактически проданным ночам выходит %s–%s — она ниже пика, '
            'потому что зимние ночи дешевле. В расчёте ниже используется именно она, а не '
            'верхняя граница.' % (E(min(R[n]['adr'] for n in COLS)),
                                  E(max(R[n]['adr'] for n in COLS))),
            'Weighted by the nights actually sold it averages %s–%s — below the peak, because '
            'winter nights are cheaper. The model below uses that average, not the top of the '
            'band.' % (E(min(R[n]['adr'] for n in COLS)),
                       E(max(R[n]['adr'] for n in COLS)))))))

    # ── ЭКОНОМИКА ────────────────────────────────────────────────────────
    def r3(label, f, us=False):
        c = ' class="us"' if us else ''
        return ('<tr><td>%s</td>' % esc(label)) + ''.join(
            '<td%s>%s</td>' % (c, f(R[n])) for n in COLS) + '</tr>'

    body = (r3(t(T('Загрузка', 'Occupancy')), lambda d: P(d['occ']))
            + r3(t(T('Проданных ночей', 'Nights sold')), lambda d: str(int(round(d['sold']))))
            + r3(t(T('Средняя ставка', 'Average rate')), lambda d: E(d['adr']))
            + r3(t(T('Выручка', 'Revenue')), lambda d: E(d['rev']))
            + r3(t(T('Эксплуатация', 'Operating costs')), lambda d: '−' + E(d['rev'] - d['gop']))
            + r3(t(T('Операционная прибыль', 'Operating profit')), lambda d: E(d['gop']))
            + r3(t(T('Управление', 'Management')), lambda d: '−' + E(d['fee']))
            + r3(t(T('Вам', 'To you')), lambda d: E(d['inv']), us=True))
    varlist = ''.join('<div><dt>%s</dt><dd>%s</dd></div>'
                      % (esc(t(T(n, en))), ('€' + ('%.2f' % v).replace('.', ',')) if ru
                         else ('€%.2f' % v))
                      for (n, v), en in zip(VARIABLE, [
                          'Booking channel commission, ~12%', 'Cleaning and linen between guests',
                          'Servicing, parts, wear', 'Welcome basket from the farm',
                          'Water, waste, consumables', 'Moving between zones',
                          'Guest handling, comms, platform']))
    w('''
<section class="tint">
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h2>%s</h2>
    <p class="lede">%s</p>
    <dl class="terms">%s</dl>
    <p class="note">%s</p>
    <div class="tblwrap" style="margin-top:38px"><table>
      <thead><tr><th>%s</th><th>%s</th><th>%s</th><th class="us">%s</th></tr></thead>
      <tbody>%s</tbody>
    </table></div>
  </div>
</section>''' % (
        t(T('Экономика', 'The economics')),
        t(T('Каждая статья расходов названа', 'Every cost line is named')),
        t(T('Считается на проданную ночь, потому что почти каждый расход возникает только '
            'тогда, когда в доме кто-то ночевал.',
            'Costed per sold night, because almost every line only happens when somebody '
            'actually slept in the house.')),
        varlist,
        t(T('Плюс постоянные на всю сеть: %s в год — страховка, бухгалтерия, платформа и '
            'телеметрия.' % E(sum(v for _, v in FIXED)),
            'Plus fixed costs across the network: %s a year — insurance, accounting, the '
            'platform and telemetry.' % E(sum(v for _, v in FIXED)))),
        t(T('Один юнит за год', 'One unit, one year')),
        t(T('Консервативный', 'Conservative')), t(T('Базовый', 'Base')),
        t(T('Оптимистичный', 'Optimistic')),
        body))

    # ── ДОХОДНОСТЬ ───────────────────────────────────────────────────────
    yrows = ''
    for house in range(HOUSE_LOW, HOUSE_HIGH + 1, 10_000):
        C = house + ONBOARD
        yrows += ('<tr><td>%s + %s</td>' % (E(house), E(ONBOARD))
                  + ''.join('<td>%s</td>' % P(R[n]['inv'] / C) for n in COLS) + '</tr>')
    w('''
<section>
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h2>%s</h2>
    <p class="lede">%s</p>
    <div class="tblwrap"><table>
      <thead><tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr></thead>
      <tbody>%s</tbody>
    </table></div>
    <p class="note">%s</p>
  </div>
</section>''' % (
        t(T('Доходность', 'The return')),
        t(T('От %s до %s, и вот от чего это зависит'
            % (P(min(YL), 0), P(max(YH), 0)),
            'From %s to %s, and here is what moves it'
            % (P(min(YL), 0), P(max(YH), 0)))),
        t(T('Два диапазона на входе — цена дома и ставка за ночь — дают диапазон и на выходе. '
            'Мы не выбираем из него одну красивую цифру.',
            'Two ranges going in — the price of the house and the nightly rate — make a range '
            'coming out. We are not going to pick the flattering number out of it.')),
        t(T('Чек', 'Cheque')), t(T('Консервативный', 'Conservative')),
        t(T('Базовый', 'Base')), t(T('Оптимистичный', 'Optimistic')),
        yrows,
        t(T('Это операционные допущения, а не обещанная доходность. Прирост стоимости актива '
            'в расчёт не заложен: если рынок не вырастет, модель не рассыпается.',
            'These are operating assumptions, not a promised return. Appreciation is not in the '
            'model: if the market does not rise, nothing here collapses.'))))

    # ── ПРИОРИТЕТНЫЙ ДОХОД ───────────────────────────────────────────────
    frows = ''
    for scale in (1.0, 0.9, 0.75, 0.667):
        d = scaled(scale); f = with_floor(d, CHEQUE_HIGH)
        frows += ('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class="us">%s</td></tr>'
                  % (P(d['occ']), E(d['rev']), E(f['fee']),
                     E(f['topup']) if f['topup'] >= 1 else '—', P(f['y'])))
    w('''
<section class="dark">
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h2>%s</h2>
    <p class="lede" style="color:rgba(247,243,237,.72)">%s</p>
    <div class="tblwrap"><table>
      <thead><tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th class="us">%s</th></tr></thead>
      <tbody>%s</tbody>
    </table></div>
    <p class="note">%s</p>
  </div>
</section>''' % (
        t(T('Приоритетный доход', 'Preferred return')),
        t(T('Сначала режем себя, а не вас', 'We cut ourselves first, not you')),
        t(T('Пока вы не получили %s годовых, наше вознаграждение урезается — вплоть до нуля. '
            'Своих денег мы не доплачиваем: предел механизма — размер самого вознаграждения, '
            'и мы говорим это прямо, а не мелким шрифтом.' % P(HURDLE, 0),
            'Until you have had %s a year, our fee is cut — to zero if that is what it takes. '
            'We do not top it up from our own pocket: the fee is the limit of the mechanism, '
            'and we say so here rather than in a footnote.' % P(HURDLE, 0))),
        t(T('Загрузка', 'Occupancy')), t(T('Выручка', 'Revenue')),
        t(T('Наше вознаграждение', 'Our fee')), t(T('Отдаём вам', 'Given up')),
        t(T('Ваша доходность', 'Your return')),
        frows,
        t(T('Механизм держится до загрузки %s при чеке %s и до %s при %s. Ниже этого мы не '
            'сидим и не надеемся на следующий сезон — смотри следующий раздел.'
            % (P(breaks_at(CHEQUE_HIGH)), E(CHEQUE_HIGH),
               P(breaks_at(CHEQUE_LOW)), E(CHEQUE_LOW)),
            'It holds down to %s occupancy on a %s cheque and %s on a %s one. Below that we do '
            'not sit and hope for next season — see the next section.'
            % (P(breaks_at(CHEQUE_HIGH)), E(CHEQUE_HIGH),
               P(breaks_at(CHEQUE_LOW)), E(CHEQUE_LOW))))))

    w('<div class="plate plate--farm"><p class="plate-cap">'
      + t(T('Ферма-партнёр · три резиденции на площадке',
            'A partner farm · three residences on site'))
      + '</p></div>')

    # ── ПЛАН Б ───────────────────────────────────────────────────────────
    apt_rows = ''
    for disc in (0.15, 0.25, 0.33):
        loss = HOUSE_HIGH * disc + HOUSE_HIGH * (1 - disc) * 0.07
        apt_rows += ('<tr><td>%s</td><td>%s</td><td class="us">%s</td></tr>'
                     % (t(T('скидка %d%%' % (disc * 100), '%d%% discount' % (disc * 100))),
                        E(loss), t(T('в %.0f раз дороже' % (loss / MOVE),
                                     '%.0f× more' % (loss / MOVE)))))
    w('''
<section>
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h2>%s</h2>
    <p class="lede">%s</p>
    <div class="duo">
      <div><h3>%s</h3><p>%s</p></div>
      <div class="alt"><h3>%s</h3><p>%s</p></div>
    </div>
    <div class="tblwrap" style="margin-top:38px"><table>
      <thead><tr><th>%s</th><th>%s</th><th class="us">%s</th></tr></thead>
      <tbody>%s</tbody>
    </table></div>
    <p class="note">%s</p>
  </div>
</section>''' % (
        t(T('План Б', 'Plan B')),
        t(T('Если не работает страна — уезжает страна',
            'If the country stops working, the house leaves the country')),
        t(T('У слабой локации есть второй выход, и он стоит около %s на юнит. У квартиры '
            'такого выхода нет: её можно только продать, и в слабом рынке это скидка плюс '
            'агент плюс налоги.' % E(MOVE),
            'A weak location has a second exit, and it costs about %s a unit. An apartment has '
            'no such exit: it can only be sold, and in a weak market that means a discount plus '
            'the agent plus the taxes.' % E(MOVE))),
        t(T('Соседи вне ЕС', 'The non-EU neighbours')),
        t(T('Сербия, Босния, Албания, Македония. Буксировка, таможня по CEFTA, новая площадка, '
            'листинги — около %s на юнит, считанные дни. Первый кандидат — албанское '
            'побережье: вне ЕС и с растущим премиум-сегментом.' % E(MOVE),
            'Serbia, Bosnia, Albania, North Macedonia. Towing, CEFTA customs, a new site and '
            'fresh listings — about %s a unit, and a matter of days. The first candidate is the '
            'Albanian coast: outside the EU, with a growing premium segment.' % E(MOVE))),
        t(T('В ЕС — честно и дороже', 'Into the EU — honestly, and dearer')),
        t(T('Хорватия, Словения, Греция, Италия. Здесь добавляется ввозной НДС страны '
            'назначения, если не применим режим временного ввоза. Это единственная развилка, '
            'решающая, есть ли план Б в ЕС, и мы её сейчас проверяем с таможенным '
            'консультантом.',
            'Croatia, Slovenia, Greece, Italy. Here the destination country adds import VAT '
            'unless a temporary-admission regime applies. That is the single question deciding '
            'whether Plan B extends into the EU, and we are checking it with a customs adviser '
            'now.')),
        t(T('Выход из квартиры того же чека', 'Exiting an apartment of the same price')),
        t(T('Потеря', 'Loss')), t(T('Против переезда', 'Against a move')),
        apt_rows,
        t(T('Скидка плюс агент и налоги, по %s. И это месяцы ожидания с пустым объектом, '
            'а не дни.' % E(HOUSE_HIGH),
            'Discount plus agent and taxes, on %s. And it is months of waiting with an empty '
            'unit, not days.' % E(HOUSE_HIGH)))))

    # ── ГДЕ МЫ СЛАБЕЕ ────────────────────────────────────────────────────
    weak = [
        T('Ни одной проданной ночи, ни одного гостя, ни одного евро выручки. Вы будете первым.',
          'Not one night sold, not one guest, not one euro of revenue. You would be the first.'),
        T('Ни один дом не построен по производственной спецификации. Есть прототип 2023 года, '
          'собранный вручную по другой.',
          'No house has been built to the production specification. There is a 2023 prototype, '
          'made by hand to a different one.'),
        T('Дом — движимое имущество. У него нет вторичного рынка квартиры и нет земли под ним. '
          'Он амортизируется.',
          'The house is movable property. It has neither an apartment resale market nor land '
          'beneath it, and it depreciates.'),
        T('Загрузка 50% в глубокую зиму — самое смелое допущение в этой модели. Если выйдет '
          '30%, консервативный сценарий уедет вниз.',
          'Fifty per cent occupancy in deep winter is the boldest assumption here. At thirty, '
          'the conservative case moves down.'),
    ]
    strong = [
        T('Доходность не опирается на рост цены актива. Не вырастет рынок — расчёт всё равно стоит.',
          'The return does not lean on the asset appreciating. If the market does not rise, the '
          'arithmetic still stands.'),
        T('Слабая локация не держит ваш капитал. Дом уезжает за дни, а не продаётся месяцами.',
          'A weak location does not hold your capital. The house leaves in days instead of '
          'selling over months.'),
        T('Наше вознаграждение подчинено вашему приоритетному доходу. Мы теряем раньше вас.',
          'Our fee is subordinated to your preferred return. We lose before you do.'),
        T('Каждая статья расходов на этой странице названа. Проверьте любую.',
          'Every cost line on this page is named. Check any of them.'),
    ]
    led = ''.join('<div class="lrow lrow--no"><span class="lmark">%s</span><p>%s</p></div>'
                  % (t(T('Слабее', 'Weaker')), esc(t(x))) for x in weak)
    led += ''.join('<div class="lrow"><span class="lmark">%s</span><p>%s</p></div>'
                   % (t(T('Сильнее', 'Stronger')), esc(t(x))) for x in strong)
    w('''
<section class="dark">
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h2>%s</h2>
    <div class="ledger">%s</div>
    <p class="note">%s</p>
  </div>
</section>''' % (
        t(T('Где мы слабее', 'Where we are weaker')),
        t(T('Что честнее сказать самим', 'What is fairer to say ourselves')),
        led,
        t(T('Вы всё равно найдёте эти пункты. Вопрос только в том, найдёте вы их здесь или '
            'после разговора со своим юристом.',
            'You will find these anyway. The only question is whether you find them here or '
            'after a conversation with your lawyer.'))))

    # ── ЗАКРЫТИЕ ─────────────────────────────────────────────────────────
    w('''
<section class="dark">
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h2>%s</h2>
    <p class="lede">%s</p>
    <a class="cta" href="/enquiry/">%s</a>
  </div>
</section>
</main>

<footer>
  <div class="wrap">
    <p class="note">%s</p>
    <p class="note">%s</p>
  </div>
</footer>

</body>
</html>
''' % (
        t(T('Дальше', 'Next')),
        t(T('Начните с вопросов, а не с бумаг', 'Start with questions, not with paperwork')),
        t(T('Назовите сумму, которую рассматриваете, и получите расчёт именно под неё — по трём '
            'сценариям, с допущениями. Двадцать минут разговора, без давления и без сроков. '
            'Или приезжайте: посмотрите площадки, познакомьтесь с хозяевами ферм, поужинайте '
            'там. Это честнее любой презентации.',
            'Name the sum you are considering and get the calculation for that figure, across '
            'three scenarios, with the assumptions shown. Twenty minutes, no pressure and no '
            'deadline. Or come out: see the sites, meet the farm owners, have dinner there. '
            'That is more honest than any presentation.')),
        t(T('Написать нам', 'Write to us')),
        t(T('Страница носит информационный характер. Это не оферта, не инвестиционная '
            'рекомендация и не предложение ценных бумаг. Все финансовые показатели — '
            'модельные допущения, а не гарантированный результат. Изображения резиденций — '
            'рендеры: ни один дом не построен по производственной спецификации.',
            'This page is information only. It is not an offer, investment advice, or an offer '
            'of securities. Every financial figure is a modelling assumption, not a guaranteed '
            'outcome. Images of the residences are renders: no house has been built to the '
            'production specification.')),
        t(T('Условия участия обсуждаются индивидуально и оформляются документами, '
            'подготовленными с юристом. Tiny Mansion — проект TinyArc Group d.o.o., Бар, '
            'Черногория.',
            'Terms are agreed individually and set out in documents prepared with a lawyer. '
            'Tiny Mansion is a project of TinyArc Group d.o.o., Bar, Montenegro.'))))

    return ''.join(out)


for lang, path in (('ru', 'invest/index.html'), ('en', 'invest/en/index.html')):
    p = os.path.join(ROOT, path)
    io.open(p, 'w', encoding='utf-8').write(page(lang))
    print('written %-24s %6.1f KB' % (path, os.path.getsize(p) / 1024))
