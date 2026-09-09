# -*- coding: utf-8 -*-
"""Собирает /invest/ и /invest/en/ из club.py.

Обе страницы пишутся одним проходом из одной модели, поэтому русская и
английская версии не могут разойтись, а цифры на странице не могут
разойтись с расчётом. Меняется club.py — запускается это.

    python3 gen_invest.py
"""
import io, os, contextlib, runpy

ROOT = os.path.dirname(os.path.abspath(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    M = runpy.run_path(os.path.join(ROOT, 'club.py'))

ONBOARD   = M['ONBOARDING']
OCC       = M['OCC']
TARGET    = M['TARGET']
COMMISSION= M['COMMISSION']
VARIABLE  = M['VARIABLE']
FIXED     = M['FIXED']
ONB_USE   = M['ONBOARDING_USE']
VAR_NIGHT = M['VAR_NIGHT']
FIX_YEAR  = M['FIX_YEAR']
ALL       = M['ALL']

D21 = ALL[0][3]
D24 = ALL[1][3]
ENTRY_LOW, ENTRY_HIGH = D21['entry'], D24['entry']
HOUSE_LOW, HOUSE_HIGH = D21['price'], D24['price']

# Загрузка, при которой выплата владельцу упирается в GOP. Ниже неё цель
# недостижима ничем, кроме уменьшения выплаты, и это надо сказать вслух.
def break_occ(d):
    margin = d['rate'] * (1 - COMMISSION) - VAR_NIGHT
    return (d['payout'] + FIX_YEAR) / (margin * 365)

BREAK_LOW  = min(break_occ(D21), break_occ(D24))
BREAK_HIGH = max(break_occ(D21), break_occ(D24))


# ── форматирование чисел под язык ────────────────────────────────────────
def eur(v, ru):
    s = format(int(round(v)), ',d')
    return '€' + (s.replace(',', ' ') if ru else s)

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
               'Вход %s–%s, цель по доходности %s годовых от суммы входа. '
               'Вся арифметика на странице.'
               % (E(ENTRY_LOW), E(ENTRY_HIGH), P(TARGET, 0)),
               'A residence you own outright on a working farm in Montenegro. '
               '%s–%s all in, and a %s a year target on the full entry sum. '
               'Every figure is on the page.'
               % (E(ENTRY_LOW), E(ENTRY_HIGH), P(TARGET, 0))))
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
        <a href="/bars/">%s</a>
        <a href="/salons/">%s</a>
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
              t(T('Бары', 'Bars')), t(T('Салоны', 'Salons')),
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
        t(T('Черногория · первое размещение — I квартал 2027',
            'Montenegro · first deployment Q1 2027')),
        t(T('Два способа владеть домом,<br>который переезжает за сезоном',
            'Two ways to own a residence<br>that moves to where the season is')),
        t(T('Купить один дом целиком и отдать его нам в управление. Или войти в '
            'размещение целиком. Арифметика опубликована и в том, и в другом случае, '
            'при той же загрузке, которой мы пользуемся сами.',
            'Buy one house outright and let us run it. Or come in on the deployment '
            'as a whole. The arithmetic is published either way, at the same occupancy '
            'we use ourselves.')),
        t(T('Вход %s–%s' % (E(ENTRY_LOW), E(ENTRY_HIGH)),
            '%s–%s all in' % (E(ENTRY_LOW), E(ENTRY_HIGH)))),
        t(T('Цель %s годовых' % P(TARGET, 0), '%s a year target' % P(TARGET, 0))),
        t(T('Загрузка %s' % P(OCC, 0), '%s occupancy' % P(OCC, 0))),
        t(T('Доход в евро', 'Income in euro'))))

    # ── ТРЕК А: КУПИТЬ ОДИН ДОМ ──────────────────────────────────────────
    terms = [
        ('Цена', 'Price',
         '%s за Residence 21ft, %s за Grand Residence 24ft — готовый дом, '
         'доставленный на ферму.' % (E(HOUSE_LOW), E(HOUSE_HIGH)),
         '%s for the Residence 21ft, %s for the Grand Residence 24ft, delivered '
         'finished to the farm.' % (E(HOUSE_LOW), E(HOUSE_HIGH))),
        ('Подключение, разово', 'Onboarding, once',
         '%s сверх цены дома. Это не доля в чём-либо и не наше вознаграждение: '
         'взнос покупает услугу, и она расписана ниже строкой.' % E(ONBOARD),
         '%s on top of the house. It is not a share of anything and not our fee: '
         'it buys a service, itemised below.' % E(ONBOARD)),
        ('Итого вход', 'Entry, all in',
         '%s или %s, в зависимости от модели. Доходность на этой странице '
         'считается от этой суммы, а не от одной цены дома.'
         % (E(ENTRY_LOW), E(ENTRY_HIGH)),
         '%s or %s, depending on the model. Every return figure on this page is '
         'taken on that sum, not on the house price alone.'
         % (E(ENTRY_LOW), E(ENTRY_HIGH))),
        ('Что вы получаете в собственность', 'What you own',
         'Резиденцию целиком, на своё имя, как движимое имущество с серийным '
         'номером и счётом. Не кадастровую недвижимость.',
         'The residence outright, registered in your own name as movable property '
         'with a serial number and an invoice. Not cadastral real estate.'),
        ('Земля', 'The land',
         'Вы её не покупаете и не арендуете. Резиденция стоит на действующей ферме '
         'по договору, который держим мы и продлеваем год за годом. Ни земляных '
         'работ, ни подключений, ни разрешения на строительство с вашей стороны.',
         'Not bought and not rented by you. The residence stands on a working farm '
         'under an agreement we hold with the farm, renewed year by year. No '
         'groundwork, no connections, no building permit on your side.'),
        ('Кто им управляет', 'Who runs it',
         'Мы, по отдельному договору управления, который вы можете расторгнуть. '
         'Бронирования, гости, уборка, обслуживание и сезонные переезды — наши.',
         'We do, under a separate management agreement you can terminate. Bookings, '
         'guests, cleaning, maintenance and the season\u2019s moves are ours.'),
        ('Срок', 'Delivery',
         'Три месяца от оплаты, плюс около недели из Стамбула в Бар и несколько '
         'дней до фермы. Строится по одной спецификации и проверяется до отгрузки.',
         'Three months from payment, plus about a week from Istanbul to Bar and a '
         'few days to the farm. Built to one specification, tested before it leaves '
         'the yard.'),
        ('Если захотите забрать', 'If you want it back',
         'Это транспортное средство. Расторгаете договор управления — и дом едет '
         'туда, куда вы скажете.',
         'It is a vehicle. End the management agreement, and the house goes where '
         'you send it.'),
    ]
    rows = ''.join('<div><dt>%s</dt><dd>%s</dd></div>'
                   % (esc(t(T(lr, le))), esc(t(T(vr, ve))))
                   for lr, le, vr, ve in terms)
    onb = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (esc(ru and r or en), E(v))
                  for en, r, v in ONB_USE)
    w('''
<section id="buy">
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h2>%s</h2>
    <p class="lede">%s</p>
    <dl class="terms">%s</dl>
    <h3 style="margin-top:44px">%s</h3>
    <dl class="spec">%s</dl>
    <p class="note">%s</p>
  </div>
</section>''' % (
        t(T('Трек А', 'Track A')),
        t(T('Купить один дом', 'Buy one residence')),
        t(T('Дом ваш и записан на вас. Земля в сделку не входит — именно поэтому '
            'цена такая.',
            'The house is yours, in your name. The land is not part of the deal, '
            'which is what keeps the price where it is.')),
        rows,
        t(T('На что идёт взнос за подключение', 'What the onboarding fee buys')),
        onb,
        t(T('Сумма расписана до последней строки и сходится с %s. Тягач — самая '
            'крупная позиция и единственная, которой вы пользуетесь, не владея ею: '
            'он общий на парк.' % E(ONBOARD),
            'The lines add up to %s exactly. The tow vehicle is the largest of them '
            'and the only thing here you use without owning: it is shared across the '
            'fleet.' % E(ONBOARD)))))

    # ── АРИФМЕТИКА ───────────────────────────────────────────────────────
    # Порядок расчёта — тот же, что в club.py: сначала цель по доходности,
    # потом доля. Обратный порядок разъезжается по вилке цены.
    def col(d, k, en, rune):
        return d
    hdr = ''.join('<th>%s</th>' % esc(ru and rn or en) for _, en, rn, _ in ALL)
    def line(label, f, cls=''):
        return ('<tr%s><td class="lbl">%s</td>%s</tr>'
                % (cls, esc(t(label)),
                   ''.join('<td class="n">%s</td>' % f(d) for _, _, _, d in ALL)))
    body = (
        line(T('Ставка за ночь', 'Rate a night'), lambda d: E(d['rate'])) +
        line(T('Проданных ночей в году', 'Nights sold in a year'),
             lambda d: '%d' % round(d['nights'])) +
        line(T('Выручка', 'Revenue'), lambda d: E(d['rev'])) +
        line(T('− эксплуатация', 'less running costs'),
             lambda d: '−' + E(d['var'] + d['fix'])) +
        line(T('Осталось до распределения', 'Left before it is split'),
             lambda d: E(d['gop'])) +
        line(T('Владельцу за год', 'To the owner, a year'),
             lambda d: E(d['payout']), ' class="tot"') +
        line(T('  доля в выручке', '  share of revenue'), lambda d: P(d['share'])) +
        line(T('  от суммы входа', '  on the entry sum'), lambda d: P(d['y'])))
    w('''
<section>
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h2>%s</h2>
    <p class="lede">%s</p>
    <div class="callout">%s</div>
    <div class="tblwrap">
      <table>
        <thead><tr><th></th>%s</tr></thead>
        <tbody>%s</tbody>
      </table>
    </div>
    <p class="note">%s</p>
    <div class="callout">%s</div>
  </div>
</section>''' % (
        t(T('Арифметика', 'The arithmetic')),
        t(T('Как считается доля', 'How the share is worked out')),
        t(T('Владелец получает %s годовых от суммы входа. Его доля в выручке дома '
            'зависит от того, во сколько обошёлся дом: дорогой дом берёт большую '
            'долю, дешёвый — меньшую, а в процентах годовых оба дают одно и то же.'
            % P(TARGET, 0),
            'The owner takes %s a year on the entry sum. The share of the house’s '
            'revenue that produces it depends on what the house cost: a dearer house '
            'takes a larger share, a cheaper one a smaller share, and as a percentage '
            'a year the two come out the same.' % P(TARGET, 0))),
        t(T('<strong>%s — это цель, а не обещание.</strong> Она рассчитана при '
            'загрузке %s и достигается тем, что доля владельца в выручке заранее '
            'подобрана под неё. Меньше выручка — меньше выплата: своих денег '
            'управляющая сторона не добавляет, и ниже мы говорим, где именно этот '
            'механизм упирается в предел.' % (P(TARGET, 0), P(OCC, 0)),
            '<strong>%s is a target, not a promise.</strong> It is computed at %s '
            'occupancy and reached by sizing the owner’s share of revenue to it in '
            'advance. Less revenue, less paid out: the manager adds no money of its '
            'own, and below we say where the mechanism runs out.'
            % (P(TARGET, 0), P(OCC, 0)))),
        hdr, body,
        t(T('Загрузка %s стоит одна на весь год — это политика, а не прогноз. Дом не '
            'привязан к площадке: ферма, которая на эту цифру не выходит, меняется по '
            'ходу сезона, и резиденция переезжает. Внутри сезонного окна цель — 75–85%%.'
            % P(OCC, 0),
            'Occupancy is taken at %s across the year — a policy rather than a '
            'forecast. The house is not tied to a site: any farm that does not reach '
            'that figure is replaced during the season, and the residence moves. '
            'Within each seasonal window the target is 75–85%%.' % P(OCC, 0))),
        t(T('<strong>Где механизм упирается в предел.</strong> Выплата владельцу '
            'съедает всё, что остаётся после расходов, при загрузке %s–%s — в '
            'зависимости от модели. Ниже неё цель не достигается ничем, кроме '
            'уменьшения самой выплаты.' % (P(BREAK_LOW), P(BREAK_HIGH)),
            '<strong>Where the mechanism runs out.</strong> The owner’s payment eats '
            'everything left after costs at %s–%s occupancy, depending on the model. '
            'Below that the target is not reached by anything except paying out less.'
            % (P(BREAK_LOW), P(BREAK_HIGH))))))

    # ── ЧТО НЕ ВХОДИТ В РАСЧЁТ ───────────────────────────────────────────
    varrows = ''.join('<div><dt>%s</dt><dd>%s</dd></div>'
                      % (esc(ru and r or en), eur(v, ru).replace('€', '€') if v == int(v)
                         else ('€' + ('%.2f' % v).replace('.', ',' if ru else '.')))
                      for en, r, v in VARIABLE)
    fixrows = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (esc(ru and r or en), E(v))
                      for en, r, v in FIXED)
    w('''
<section>
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h2>%s</h2>
    <div class="duo">
      <div>
        <h3>%s</h3>
        <dl class="spec">%s<div><dt>%s</dt><dd>%s</dd></div></dl>
      </div>
      <div>
        <h3>%s</h3>
        <dl class="spec">%s<div><dt>%s</dt><dd>%s</dd></div></dl>
      </div>
    </div>
    <p class="note">%s</p>
  </div>
</section>''' % (
        t(T('Расходы', 'The costs')),
        t(T('Каждая строка названа', 'Every line is named')),
        t(T('На проданную ночь', 'Per night sold')),
        varrows,
        t(T('комиссия канала', 'booking commission')),
        t(T('%s от ставки' % P(COMMISSION, 0), '%s of the rate' % P(COMMISSION, 0))),
        t(T('За год на дом', 'Per house, per year')),
        fixrows,
        t(T('итого', 'total')), E(FIX_YEAR),
        t(T('Комиссия канала стоит процентом, а не суммой, потому что на ставке %s '
            'она одна, а на %s другая. Раньше в модели стояло плоское число, верное '
            'ровно для одной из двух ставок.' % (E(D21['rate']), E(D24['rate'])),
            'The booking commission is a percentage rather than a figure, because it '
            'is one thing at %s a night and another at %s. The model used to carry a '
            'flat number, correct for exactly one of the two rates.'
            % (E(D21['rate']), E(D24['rate']))))))

    # ── ВИД НА ЖИТЕЛЬСТВО ────────────────────────────────────────────────
    status = [
        ('Оформление', 'Set-up',
         'Регистрация компании и первая отчётность — через юриста, с которым мы '
         'работаем в Черногории. Стоимость называется вам до того, как вы на '
         'что-либо соглашаетесь.',
         'Company registration and the first filing, handled by the lawyer we work '
         'with in Montenegro. Quoted to you before you commit.'),
        ('Каждый год', 'Each year',
         'От \u20ac5 000 налогов и взносов плюс бухгалтерия. Это реальные деньги, и они '
         'выходят из того, что зарабатывает дом, поэтому мы показываем их отдельной '
         'строкой, а не прячем внутрь доходности.',
         'From \u20ac5,000 in taxes and contributions, plus accounting. This is a real '
         'cost and it comes out of what the house earns, so we show it separately '
         'rather than folding it into a yield figure.'),
        ('Не входит', 'Not included',
         'Ваше налоговое положение в стране, где вы налоговый резидент, — это вопрос '
         'к вашему советнику.',
         'Your own tax position at home, which is a question for your own adviser.'),
    ]
    strows = ''.join('<div><dt>%s</dt><dd>%s</dd></div>'
                     % (esc(t(T(lr, le))), esc(t(T(vr, ve))))
                     for lr, le, vr, ve in status)
    w('''
<section id="status">
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h2>%s</h2>
    <p class="lede">%s</p>
    <div class="duo">
      <div>
        <h3>%s</h3>
        <p>%s</p>
        <p>%s</p>
      </div>
      <div class="alt">
        <h3>%s</h3>
        <p>%s</p>
        <p>%s</p>
      </div>
    </div>
    <dl class="terms">%s</dl>
    <div class="callout">%s</div>
  </div>
</section>''' % (
        t(T('Статус', 'Status')),
        t(T('Если вам нужен ещё и вид на жительство',
            'If you also want residence in Montenegro')),
        t(T('Стоит прочитать до того, как сравнивать нас с квартирой: правила '
            'поменялись в январе 2026 года, и большинство продающих презентаций за '
            'этим не успели.',
            'Worth reading before you compare us with an apartment, because the rules '
            'changed in January 2026 and most sales pitches have not caught up.')),
        t(T('Чего дом не даёт', 'What the residence does not do')),
        t(T('Вида на жительство он не даёт. Для него нужна кадастровая недвижимость '
            'с оценочной стоимостью не ниже €150 000, а наш дом зарегистрирован как '
            'движимое имущество. Мы предпочитаем сказать это здесь, а не дать вам '
            'выяснить это потом.',
            'It does not give you a residence permit. That permit requires cadastral '
            'real estate with a tax-assessed value of at least €150,000, and our house '
            'is registered as movable property. We would rather say so here than let '
            'you find out later.')),
        t(T('Про квартиру тоже стоит знать: вид на жительство по недвижимости не даёт '
            'права работать или вести бизнес в Черногории, и эти годы не идут в зачёт '
            'постоянного проживания.',
            'Worth knowing about the apartment route too: a property-based permit does '
            'not allow you to work or run a business in Montenegro, and those years do '
            'not count toward permanent residence.')),
        t(T('Что работает', 'What does work')),
        t(T('Вид на жительство через собственную черногорскую компанию. Компания ваша, '
            'на ней договор управления вашим домом, вы — её директор по трудовому '
            'договору. Эти годы идут в зачёт постоянного проживания полностью, и '
            'работать вы вправе.',
            'Residence through your own Montenegrin company. You hold the company, the '
            'company holds the management arrangement for your house, and you are '
            'employed as its director. Those years count in full toward permanent '
            'residence, and you may legally operate.')),
        t(T('Это стоит денег каждый год. Чтобы продлиться, компания должна была уплатить '
            'за прошедший год не меньше €5 000 налогов и взносов. Граждане ЕС, ЕЭЗ и '
            'Швейцарии от этого требования освобождены.',
            'It has a running cost. To renew, the company must have paid at least '
            '€5,000 in taxes and contributions over the previous year. Citizens of the '
            'EU, EEA and Switzerland are exempt from that requirement.')),
        strows,
        t(T('<strong>Мы не гарантируем, что вид на жительство выдадут или продлят.</strong> '
            'Миграционные правила Черногории менялись дважды между ноябрём 2025 и '
            'январём 2026 года. Ничто на этой странице не является юридической '
            'консультацией, и мы познакомим вас с юристом до того, как вы на что-либо '
            'подпишетесь.',
            '<strong>We do not guarantee that any permit will be granted or renewed.</strong> '
            'Montenegrin immigration rules were amended twice between November 2025 and '
            'January 2026. Nothing on this page is legal advice, and we will introduce '
            'you to counsel before you commit to anything.'))))

    # ── ТРЕК Б: РАЗМЕЩЕНИЕ ЦЕЛИКОМ ───────────────────────────────────────
    w('''
<section id="project">
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h2>%s</h2>
    <p class="lede">%s</p>
    <div class="duo">
      <div>
        <h3>%s</h3>
        <p>%s</p>
      </div>
      <div>
        <h3>%s</h3>
        <p>%s</p>
      </div>
    </div>
    <div class="callout">%s</div>
    <a class="cta" href="/enquiry/">%s</a>
  </div>
</section>''' % (
        t(T('Трек Б', 'Track B')),
        t(T('Или войти в размещение целиком', 'Or come in on the deployment')),
        t(T('Двадцать пять резиденций по Черногории и сеть ферм, на которые их '
            'ставить. Один дом — это актив. Размещение — бизнес вокруг него.',
            'Twenty-five residences across Montenegro, and a network of farms to put '
            'them on. One house is an asset. The deployment is the business around it.')),
        t(T('Что строится', 'What is being built')),
        t(T('Парк, который ходит между горами летом, винным краем в межсезонье и '
            'небольшой полосой побережья в отдельные недели, так что пустым стоит '
            'не один и тот же дом. Рамочные соглашения с фермами подписаны, '
            'производитель подтверждён, первые юниты в сборке.',
            'A fleet that moves between the mountains in summer, the wine country in '
            'the shoulder months and a small stretch of coast in selected weeks, so '
            'the same house is never the one sitting empty. Framework agreements with '
            'farms are signed, the manufacturer is confirmed, and the first units are '
            'in build.')),
        t(T('Как устроено участие', 'How participation works')),
        t(T('Частным порядком, разговором, а не формой на сайте. Мы присылаем модель, '
            'допущения под ней и условия, потом разговариваем. Участие оформляется '
            'индивидуально и публично не предлагается.',
            'Privately, by conversation, not through a form on a website. We send the '
            'model, the assumptions behind it and the terms, then talk. Participation '
            'is arranged individually and is not open to the public.')),
        t(T('Ничто здесь не является предложением ценных бумаг или приглашением '
            'инвестировать. Мы даём информацию по запросу тем, кто её просит, с '
            'проверками, которых требует наш юрист, и любое участие оформляется '
            'документами до того, как двигаются деньги.',
            'Nothing here is an offer of securities or an invitation to invest. We '
            'provide information on request to people who ask for it, subject to the '
            'checks our counsel requires, and any participation is documented in full '
            'before money moves.')),
        t(T('Запросить материалы', 'Request the materials'))))

    # ── ГДЕ МЫ НА САМОМ ДЕЛЕ ─────────────────────────────────────────────
    w('''
<section id="enquire" class="dark">
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h2>%s</h2>
    <p class="lede">%s</p>
    <p class="lede" style="margin-top:18px">%s</p>
    <a class="cta" href="/enquiry/">%s</a>
  </div>
</section>
</main>

<footer>
  <div class="wrap">
    <p class="note">%s</p>
    <p class="note">%s</p>
    <p class="note">%s</p>
  </div>
</footer>

</body>
</html>
''' % (
        t(T('Где мы на самом деле', 'Where we actually are')),
        t(T('Ни одной проданной ночи', 'Not one night sold')),
        t(T('Существует один прототип, собранный вручную в 2023 году. Ни одна '
            'резиденция ещё не построена по производственной спецификации, и ни один '
            'гость в ней не жил. Первые юниты встают в Черногории в I квартале 2027.',
            'One prototype exists, built by hand in 2023. No residence has been built '
            'to production specification yet, and no guest has stayed in one. The '
            'first units deploy in Montenegro in Q1 2027.')),
        t(T('Всё, что на этой странице описывает доход, — модель. Всё, что описывает '
            'продукт, — спецификация, по которой мы строим. Отвечаем на письма сами.',
            'Everything on this page that describes earnings is a model, and everything '
            'that describes the product is a specification we are building to. We '
            'answer every message ourselves.')),
        t(T('Написать нам', 'Write to us')),
        t(T('Показанные цифры — модельные и ориентировочные. Это не прогноз, не '
            'гарантия и не обещание дохода. Доходность зависит от загрузки, '
            'операционных расходов и сезона и может оказаться ниже расчётной.',
            'Figures shown are modelled and indicative. They are not a forecast, a '
            'guarantee or a promise of return. Yields depend on occupancy, operating '
            'costs and the season, and may be lower than modelled.')),
        t(T('Страница носит информационный характер. Это не инвестиционная, '
            'юридическая или налоговая консультация, не публичная оферта и не '
            'приглашение приобрести какой-либо инструмент. Изображения резиденций — '
            'рендеры: ни один дом не построен по производственной спецификации.',
            'This page is information only. It is not investment advice, legal advice, '
            'tax advice, a public offer, or an invitation to subscribe for any '
            'instrument. Images of the residences are renders: no house has been built '
            'to the production specification.')),
        t(T('Условия участия обсуждаются индивидуально и оформляются документами, '
            'подготовленными с юристом. Tiny Mansion — проект Korsakov Group d.o.o., '
            'Тиват, Черногория.',
            'Terms are agreed individually and set out in documents prepared with a '
            'lawyer. Tiny Mansion is a project of Korsakov Group d.o.o., Tivat, '
            'Montenegro.'))))

    return ''.join(out)


for lang, path in (('ru', 'invest/index.html'), ('en', 'invest/en/index.html')):
    p = os.path.join(ROOT, path)
    io.open(p, 'w', encoding='utf-8').write(page(lang))
    print('written %-24s %6.1f KB' % (path, os.path.getsize(p) / 1024))
