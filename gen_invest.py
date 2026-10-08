# -*- coding: utf-8 -*-
"""Собирает /invest/ на четырёх языках из club.py.

Все четыре страницы пишутся одним проходом из одной модели, поэтому версии
не могут разойтись между собой, а цифры на странице не могут разойтись с
расчётом. Меняется club.py, запускается это.

    python3 gen_invest.py

Строка задаётся сразу на всех языках: T(ru=..., en=..., sr=..., tr=...).
Пропущенный язык это не пустое место на странице, а KeyError на сборке:
непереведённый абзац лучше поймать здесь, чем увидеть по-английски в
сербской версии.
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

# Языки в том же порядке, что переключатель на самом сайте, и адреса под них.
LANGS = ('en', 'ru', 'sr', 'tr')
PATHS = {'en': '/invest/en/', 'ru': '/invest/', 'sr': '/invest/sr/', 'tr': '/invest/tr/'}
FILES = {'en': 'invest/en/index.html', 'ru': 'invest/index.html',
         'sr': 'invest/sr/index.html', 'tr': 'invest/tr/index.html'}
SITE  = 'https://tinymansion.co'

# Загрузка, при которой выплата владельцу упирается в GOP. Ниже неё цель
# недостижима ничем, кроме уменьшения выплаты, и это надо сказать вслух.
def break_occ(d):
    margin = d['rate'] * (1 - COMMISSION) - VAR_NIGHT
    return (d['payout'] + FIX_YEAR) / (margin * 365)

BREAK_LOW  = min(break_occ(D21), break_occ(D24))
BREAK_HIGH = max(break_occ(D21), break_occ(D24))


# ── форматирование чисел под язык ────────────────────────────────────────
# Разряды и дробная запятая расставлены так же, как в словарях сайта:
# английский «120,000.50», русский «120 000,50», сербский и турецкий
# «120.000,50».
GROUP = {'en': ',', 'ru': ' ', 'sr': '.', 'tr': '.'}
POINT = {'en': '.', 'ru': ',', 'sr': ',', 'tr': ','}

def eur(v, lang):
    return '€' + format(int(round(v)), ',d').replace(',', GROUP[lang])

def eur2(v, lang):
    """Сумма с копейками: расходы на ночь стоят в модели не целыми."""
    s = ('%.2f' % v).replace('.', POINT[lang])
    return '€' + s

def pct(v, lang, d=1):
    # По-турецки знак процента стоит перед числом: %17, а не 17%.
    s = ('%.*f' % (d, v * 100)).replace('.', POINT[lang])
    return '%' + s if lang == 'tr' else s + '%'


# ── строки на всех языках сразу ──────────────────────────────────────────
def T(ru, en, sr, tr):
    return {'ru': ru, 'en': en, 'sr': sr, 'tr': tr}

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

LBL = {'en': 'EN', 'ru': 'RU', 'sr': 'SR', 'tr': 'TR'}

def switcher(cur):
    """Переключатель языка: четыре ссылки, текущая не ссылка."""
    out = []
    for c in LANGS:
        if c == cur:
            out.append('<span aria-current="true">%s</span>' % LBL[c])
        else:
            out.append('<a href="%s" hreflang="%s" lang="%s">%s</a>'
                       % (PATHS[c], c, c, LBL[c]))
    return ''.join(out)

def alternates():
    """hreflang на все четыре версии плюс x-default на английскую."""
    out = ['<link rel="alternate" hreflang="%s" href="%s%s">' % (c, SITE, PATHS[c])
           for c in LANGS]
    out.append('<link rel="alternate" hreflang="x-default" href="%s%s">'
               % (SITE, PATHS['en']))
    return '\n'.join(out)


def page(lang):
    E  = lambda v: eur(v, lang)
    E2 = lambda v: eur2(v, lang)
    P  = lambda v, d=1: pct(v, lang, d)
    t  = lambda pair: pair[lang]
    # Подпись из таблицы club.py: английская строка служит ключом и
    # английской подписью, остальные языки лежат рядом с ней.
    label = lambda en, tr_map: en if lang == 'en' else tr_map[lang]
    out = []
    w = out.append

    # ── шапка документа ──────────────────────────────────────────────────
    title = t(T('Tiny Mansion · Дом в собственность на ферме Адриатики',
                'Tiny Mansion · A house of your own on an Adriatic farm',
                'Tiny Mansion · Kuća u vašem vlasništvu na jadranskom imanju',
                'Tiny Mansion · Adriyatik kıyısında bir çiftlikte kendi eviniz'))
    desc = t(T('Резиденция в вашей собственности на действующей ферме в Черногории. '
               'Вход %s–%s, цель по доходности %s годовых от суммы входа. '
               'Вся арифметика на странице.'
               % (E(ENTRY_LOW), E(ENTRY_HIGH), P(TARGET, 0)),
               'A residence you own outright on a working farm in Montenegro. '
               '%s–%s all in, and a %s a year target on the full entry sum. '
               'Every figure is on the page.'
               % (E(ENTRY_LOW), E(ENTRY_HIGH), P(TARGET, 0)),
               'Rezidencija u vašem vlasništvu, na imanju koje radi u Crnoj Gori. '
               'Ulaz %s–%s, cilj prinosa %s godišnje na punu sumu ulaza. '
               'Sva aritmetika je na stranici.'
               % (E(ENTRY_LOW), E(ENTRY_HIGH), P(TARGET, 0)),
               'Karadağ\'da çalışan bir çiftlikte tamamen size ait bir rezidans. '
               'Giriş %s–%s, tam giriş tutarı üzerinden yıllık %s getiri hedefi. '
               'Bütün aritmetik sayfada.'
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
%s
<meta property="og:type" content="website">
<meta property="og:site_name" content="Tiny Mansion">
<meta property="og:url" content="%s%s">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:image" content="https://tinymansion.co/invest/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="%s">
<meta name="twitter:description" content="%s">
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
      <a href="/" class="wordmark" lang="en">Tiny Mansion</a>
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

<main>''' % (lang, esc(title), esc(desc), alternates(),
              SITE, PATHS[lang],
              esc(title), esc(desc), esc(title), esc(desc),
              t(T('Основное', 'Main', 'Glavno', 'Ana menü')),
              t(T('Резиденции', 'Residences', 'Rezidencije', 'Rezidanslar')),
              t(T('Фермы', 'Farms', 'Imanja', 'Çiftlikler')),
              t(T('Бары', 'Bars', 'Barovi', 'Barlar')),
              t(T('Салоны', 'Salons', 'Saloni', 'Salonlar')),
              t(T('О нас', 'About', 'O nama', 'Hakkımızda')),
              PATHS[lang],
              t(T('Инвестиции', 'Invest', 'Investitorima', 'Yatırım')),
              t(T('Связаться', 'Enquire', 'Upit', 'İletişim')),
              switcher(lang)))

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
        t(T('Черногория · первое размещение: I квартал 2027',
            'Montenegro · first deployment Q1 2027',
            'Crna Gora · prvo postavljanje: I kv. 2027',
            'Karadağ · ilk yerleşim: 2027 1. çeyrek')),
        t(T('Два способа владеть домом,<br>который переезжает за сезоном',
            'Two ways to own a residence<br>that moves to where the season is',
            'Dva načina da imate kuću<br>koja se seli za sezonom',
            'Sezonun ardından taşınan bir eve<br>sahip olmanın iki yolu')),
        t(T('Купить один дом целиком и отдать его нам в управление. Или войти в '
            'размещение целиком. Арифметика опубликована и в том, и в другом случае, '
            'при той же загрузке, которой мы пользуемся сами.',
            'Buy one house outright and let us run it. Or come in on the deployment '
            'as a whole. The arithmetic is published either way, at the same occupancy '
            'we use ourselves.',
            'Kupite jednu kuću celu i date nam je u upravljanje. Ili uđite u celo '
            'postavljanje. Aritmetika je objavljena u oba slučaja, pri istoj '
            'popunjenosti kojom se i sami vodimo.',
            'Bir evi tamamen satın alıp işletmeyi bize bırakın. Ya da yerleşimin '
            'bütününe ortak olun. Aritmetik iki durumda da yayımlanmış, hem de '
            'kendimiz için kullandığımız aynı doluluk üzerinden.')),
        t(T('Вход %s–%s' % (E(ENTRY_LOW), E(ENTRY_HIGH)),
            '%s–%s all in' % (E(ENTRY_LOW), E(ENTRY_HIGH)),
            'Ulaz %s–%s' % (E(ENTRY_LOW), E(ENTRY_HIGH)),
            'Giriş %s–%s' % (E(ENTRY_LOW), E(ENTRY_HIGH)))),
        t(T('Цель %s годовых' % P(TARGET, 0), '%s a year target' % P(TARGET, 0),
            'Cilj %s godišnje' % P(TARGET, 0), 'Hedef yıllık %s' % P(TARGET, 0))),
        t(T('Загрузка %s' % P(OCC, 0), '%s occupancy' % P(OCC, 0),
            'Popunjenost %s' % P(OCC, 0), 'Doluluk %s' % P(OCC, 0))),
        t(T('Доход в евро', 'Income in euro', 'Prihod u evrima',
            'Euro cinsinden gelir'))))

    # ── ТРЕК А: КУПИТЬ ОДИН ДОМ ──────────────────────────────────────────
    # Четвёрка: подпись и значение, каждое на всех языках. Пары T() здесь
    # собираются по месту, чтобы подпись и значение нельзя было перепутать
    # осями, как это один раз уже случилось.
    terms = [
        (T('Цена', 'Price', 'Cena', 'Fiyat'),
         T('%s за Residence 21ft, %s за Grand Residence 24ft: готовый дом, '
           'доставленный на ферму.' % (E(HOUSE_LOW), E(HOUSE_HIGH)),
           '%s for the Residence 21ft, %s for the Grand Residence 24ft, delivered '
           'finished to the farm.' % (E(HOUSE_LOW), E(HOUSE_HIGH)),
           '%s za Residence 21ft, %s za Grand Residence 24ft: gotova kuća, '
           'dostavljena na imanje.' % (E(HOUSE_LOW), E(HOUSE_HIGH)),
           'Residence 21ft için %s, Grand Residence 24ft için %s: bitmiş ev, '
           'çiftliğe teslim edilmiş.' % (E(HOUSE_LOW), E(HOUSE_HIGH)))),
        (T('Подключение, разово', 'Onboarding, once', 'Priključenje, jednokratno',
           'Devreye alma, tek seferlik'),
         T('%s сверх цены дома. Это не доля в чём-либо и не наше вознаграждение: '
           'взнос покупает услугу, и она расписана ниже строкой.' % E(ONBOARD),
           '%s on top of the house. It is not a share of anything and not our fee: '
           'it buys a service, itemised below.' % E(ONBOARD),
           '%s preko cene kuće. To nije udeo u bilo čemu i nije naša naknada: taj '
           'iznos kupuje uslugu, a ona je ispod raspisana stavku po stavku.' % E(ONBOARD),
           'Ev fiyatının üzerine %s. Bu, bir şeyde pay değil ve bizim ücretimiz de '
           'değil: bir hizmet satın alıyor, aşağıda kalem kalem yazılı.' % E(ONBOARD))),
        (T('Итого вход', 'Entry, all in', 'Ukupan ulaz', 'Toplam giriş'),
         T('%s или %s, в зависимости от модели. Доходность на этой странице '
           'считается от этой суммы, а не от одной цены дома.'
           % (E(ENTRY_LOW), E(ENTRY_HIGH)),
           '%s or %s, depending on the model. Every return figure on this page is '
           'taken on that sum, not on the house price alone.'
           % (E(ENTRY_LOW), E(ENTRY_HIGH)),
           '%s ili %s, u zavisnosti od modela. Svaka cifra prinosa na ovoj stranici '
           'računa se od te sume, a ne samo od cene kuće.'
           % (E(ENTRY_LOW), E(ENTRY_HIGH)),
           'Modele göre %s ya da %s. Bu sayfadaki her getiri rakamı, yalnız ev '
           'fiyatı değil bu tutar üzerinden alınıyor.'
           % (E(ENTRY_LOW), E(ENTRY_HIGH)))),
        (T('Что вы получаете в собственность', 'What you own',
           'Šta dobijate u vlasništvo', 'Neye sahip oluyorsunuz'),
         T('Резиденцию целиком, на своё имя, как движимое имущество с серийным '
           'номером и счётом. Не кадастровую недвижимость.',
           'The residence outright, registered in your own name as movable property '
           'with a serial number and an invoice. Not cadastral real estate.',
           'Rezidenciju celu, na svoje ime, kao pokretnu imovinu sa serijskim brojem '
           'i fakturom. Ne kao katastarsku nekretninu.',
           'Rezidansın tamamı, kendi adınıza, seri numarası ve faturası olan taşınır '
           'mal olarak. Kadastroya kayıtlı gayrimenkul değil.')),
        (T('Земля', 'The land', 'Zemlja', 'Arazi'),
         T('Вы её не покупаете и не арендуете. Резиденция стоит на действующей ферме '
           'по договору, который держим мы и продлеваем год за годом. Ни земляных '
           'работ, ни подключений, ни разрешения на строительство с вашей стороны.',
           'Not bought and not rented by you. The residence stands on a working farm '
           'under an agreement we hold with the farm, renewed year by year. No '
           'groundwork, no connections, no building permit on your side.',
           'Ne kupujete je i ne iznajmljujete. Rezidencija stoji na imanju koje radi, '
           'po ugovoru koji držimo mi i obnavljamo iz godine u godinu. Bez zemljanih '
           'radova, bez priključaka, bez građevinske dozvole na vašoj strani.',
           'Onu satın almıyor ve kiralamıyorsunuz. Rezidans, çalışan bir çiftlikte, '
           'bizim tuttuğumuz ve yıl yıl yenilediğimiz bir sözleşmeyle duruyor. Sizin '
           'tarafınızda altyapı kazısı, bağlantı ve yapı ruhsatı yok.')),
        (T('Кто им управляет', 'Who runs it', 'Ko njome upravlja', 'Kim işletiyor'),
         T('Мы, по отдельному договору управления, который вы можете расторгнуть. '
           'Бронирования, гости, уборка, обслуживание и сезонные переезды остаются за нами.',
           'We do, under a separate management agreement you can terminate. Bookings, '
           'guests, cleaning, maintenance and the season’s moves are ours.',
           'Mi, po odvojenom ugovoru o upravljanju koji možete raskinuti. Rezervacije, '
           'gosti, čišćenje, održavanje i sezonska premeštanja ostaju na nama.',
           'Biz, ayrı bir işletme sözleşmesiyle; sözleşmeyi siz sona erdirebilirsiniz. '
           'Rezervasyonlar, konuklar, temizlik, bakım ve sezonluk taşımalar bizde.')),
        (T('Срок', 'Delivery', 'Rok', 'Teslim'),
         T('Три месяца от оплаты, плюс около недели из Стамбула в Бар и несколько '
           'дней до фермы. Строится по одной спецификации и проверяется до отгрузки.',
           'Three months from payment, plus about a week from Istanbul to Bar and a '
           'few days to the farm. Built to one specification, tested before it leaves '
           'the yard.',
           'Tri meseca od plaćanja, plus oko nedelju dana od Istanbula do Bara i još '
           'nekoliko dana do imanja. Gradi se po jednoj specifikaciji i proverava se '
           'pre otpreme.',
           'Ödemeden üç ay, artı İstanbul\'dan Bar\'a yaklaşık bir hafta ve çiftliğe '
           'birkaç gün. Tek bir şartnameye göre üretiliyor ve sahadan çıkmadan önce '
           'test ediliyor.')),
        (T('Если захотите забрать', 'If you want it back',
           'Ako budete želeli da je povučete', 'Geri almak isterseniz'),
         T('Это транспортное средство. Расторгаете договор управления, и дом едет '
           'туда, куда вы скажете.',
           'It is a vehicle. End the management agreement, and the house goes where '
           'you send it.',
           'To je vozilo. Raskinete ugovor o upravljanju i kuća ide tamo gde kažete.',
           'O bir araç. İşletme sözleşmesini bitirirsiniz, ev de sizin söylediğiniz '
           'yere gider.')),
    ]
    rows = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (esc(t(lab)), esc(t(val)))
                   for lab, val in terms)
    onb = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (esc(label(en, m)), E(v))
                  for en, m, v in ONB_USE)
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
        t(T('Трек А', 'Track A', 'Opcija A', 'A seçeneği')),
        t(T('Купить один дом', 'Buy one residence', 'Kupite jednu kuću',
            'Bir ev satın alın')),
        t(T('Дом ваш и записан на вас. Земля в сделку не входит, и именно поэтому '
            'цена такая.',
            'The house is yours, in your name. The land is not part of the deal, '
            'which is what keeps the price where it is.',
            'Kuća je vaša i vodi se na vas. Zemlja ne ulazi u posao, i upravo zato '
            'je cena takva.',
            'Ev sizin ve sizin adınıza kayıtlı. Arazi işin parçası değil, fiyatı bu '
            'seviyede tutan da bu.')),
        rows,
        t(T('На что идёт взнос за подключение', 'What the onboarding fee buys',
            'Šta kupuje naknada za priključenje',
            'Devreye alma bedeli neyi satın alıyor')),
        onb,
        t(T('Сумма расписана до последней строки и сходится с %s. Тягач это самая '
            'крупная позиция и единственная, которой вы пользуетесь, не владея ею: '
            'он общий на парк.' % E(ONBOARD),
            'The lines add up to %s exactly. The tow vehicle is the largest of them '
            'and the only thing here you use without owning: it is shared across the '
            'fleet.' % E(ONBOARD),
            'Stavke se sabiraju u %s tačno. Vozilo za vuču je najveća od njih i jedina '
            'stvar ovde koju koristite, a ne posedujete: deli ga ceo park.' % E(ONBOARD),
            'Kalemler tam olarak %s ediyor. Çekici araç bunların en büyüğü ve burada '
            'sahip olmadan kullandığınız tek şey: tüm filo onu paylaşıyor.' % E(ONBOARD)))))

    # ── АРИФМЕТИКА ───────────────────────────────────────────────────────
    # Порядок расчёта тот же, что в club.py: сначала цель по доходности,
    # потом доля. Обратный порядок разъезжается по вилке цены.
    # Имя модели это английское имя собственное, и заглавные ему нужны
    # английские: по-турецки uppercase превращает i в İ, и «Residence»
    # становится «RESİDENCE».
    hdr = ''.join('<th lang="en">%s</th>' % esc(en) for _, en, _, _ in ALL)
    def line(label, f, cls=''):
        return ('<tr%s><td class="lbl">%s</td>%s</tr>'
                % (cls, esc(t(label)),
                   ''.join('<td class="n">%s</td>' % f(d) for _, _, _, d in ALL)))
    body = (
        line(T('Ставка за ночь', 'Rate a night', 'Cena po noći', 'Gecelik fiyat'),
             lambda d: E(d['rate'])) +
        line(T('Проданных ночей в году', 'Nights sold in a year',
               'Prodatih noći u godini', 'Yılda satılan gece'),
             lambda d: '%d' % round(d['nights'])) +
        line(T('Выручка', 'Revenue', 'Prihod', 'Gelir'), lambda d: E(d['rev'])) +
        line(T('− эксплуатация', 'less running costs', '− troškovi rada',
               '− işletme giderleri'),
             lambda d: '−' + E(d['var'] + d['fix'])) +
        line(T('Осталось до распределения', 'Left before it is split',
               'Ostalo pre deobe', 'Paylaşımdan önce kalan'),
             lambda d: E(d['gop'])) +
        line(T('Владельцу за год', 'To the owner, a year', 'Vlasniku godišnje',
               'Sahibine yıllık'),
             lambda d: E(d['payout']), ' class="tot"') +
        line(T('  доля в выручке', '  share of revenue', '  udeo u prihodu',
               '  gelirdeki pay'), lambda d: P(d['share'])) +
        line(T('  от суммы входа', '  on the entry sum', '  od sume ulaza',
               '  giriş tutarına göre'), lambda d: P(d['y'])))
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
        t(T('Арифметика', 'The arithmetic', 'Aritmetika', 'Aritmetik')),
        t(T('Как считается доля', 'How the share is worked out',
            'Kako se računa udeo', 'Pay nasıl hesaplanıyor')),
        t(T('Владелец получает %s годовых от суммы входа. Его доля в выручке дома '
            'зависит от того, во сколько обошёлся дом: дорогой дом берёт большую '
            'долю, дешёвый меньшую, а в процентах годовых оба дают одно и то же.'
            % P(TARGET, 0),
            'The owner takes %s a year on the entry sum. The share of the house’s '
            'revenue that produces it depends on what the house cost: a dearer house '
            'takes a larger share, a cheaper one a smaller share, and as a percentage '
            'a year the two come out the same.' % P(TARGET, 0),
            'Vlasnik dobija %s godišnje na sumu ulaza. Udeo u prihodu kuće koji to '
            'daje zavisi od toga koliko je kuća koštala: skuplja kuća uzima veći '
            'udeo, jeftinija manji, a u procentima godišnje obe daju isto.'
            % P(TARGET, 0),
            'Sahibi, giriş tutarı üzerinden yıllık %s alıyor. Bunu veren ev '
            'gelirindeki pay, evin kaça geldiğine bağlı: pahalı ev daha büyük pay '
            'alıyor, ucuz olan daha küçük, yıllık yüzde olarak ikisi de aynı çıkıyor.'
            % P(TARGET, 0))),
        t(T('<strong>%s это цель, а не обещание.</strong> Она рассчитана при '
            'загрузке %s и достигается тем, что доля владельца в выручке заранее '
            'подобрана под неё. Меньше выручка, меньше выплата: своих денег '
            'управляющая сторона не добавляет, и ниже мы говорим, где именно этот '
            'механизм упирается в предел.' % (P(TARGET, 0), P(OCC, 0)),
            '<strong>%s is a target, not a promise.</strong> It is computed at %s '
            'occupancy and reached by sizing the owner’s share of revenue to it in '
            'advance. Less revenue, less paid out: the manager adds no money of its '
            'own, and below we say where the mechanism runs out.'
            % (P(TARGET, 0), P(OCC, 0)),
            '<strong>%s je cilj, a ne obećanje.</strong> Izračunat je pri '
            'popunjenosti %s i postiže se tako što je vlasnikov udeo u prihodu '
            'unapred podešen na njega. Manji prihod, manja isplata: upravljačka '
            'strana ne dodaje svoj novac, a ispod kažemo gde se taj mehanizam '
            'zaustavlja.' % (P(TARGET, 0), P(OCC, 0)),
            '<strong>%s bir hedef, vaat değil.</strong> %s doluluk üzerinden '
            'hesaplandı ve sahibinin gelir payı ona göre önceden ayarlanarak '
            'tutuluyor. Gelir azsa ödeme de az: işletme tarafı kendi parasını '
            'eklemiyor, mekanizmanın nerede durduğunu aşağıda söylüyoruz.'
            % (P(TARGET, 0), P(OCC, 0)))),
        hdr, body,
        t(T('Загрузка %s стоит одна на весь год, и это политика, а не прогноз. Дом не '
            'привязан к площадке: ферма, которая на эту цифру не выходит, меняется по '
            'ходу сезона, и резиденция переезжает. Внутри сезонного окна цель 75–85%%.'
            % P(OCC, 0),
            'Occupancy is taken at %s across the year, a policy rather than a '
            'forecast. The house is not tied to a site: any farm that does not reach '
            'that figure is replaced during the season, and the residence moves. '
            'Within each seasonal window the target is 75–85%%.' % P(OCC, 0),
            'Popunjenost %s stoji jedna za celu godinu, i to je politika, a ne '
            'prognoza. Kuća nije vezana za lokaciju: imanje koje ne dostiže tu cifru '
            'menja se tokom sezone i rezidencija se seli. Unutar sezonskog prozora '
            'cilj je 75–85%%.' % P(OCC, 0),
            'Doluluk yıl boyu %s alındı; bu bir politika, tahmin değil. Ev bir yere '
            'bağlı değil: bu rakama ulaşmayan çiftlik sezon içinde değiştiriliyor ve '
            'rezidans taşınıyor. Sezon penceresi içinde hedef %%75–85.' % P(OCC, 0))),
        t(T('<strong>Где механизм упирается в предел.</strong> Выплата владельцу '
            'съедает всё, что остаётся после расходов, при загрузке %s–%s, в '
            'зависимости от модели. Ниже неё цель не достигается ничем, кроме '
            'уменьшения самой выплаты.' % (P(BREAK_LOW), P(BREAK_HIGH)),
            '<strong>Where the mechanism runs out.</strong> The owner’s payment eats '
            'everything left after costs at %s–%s occupancy, depending on the model. '
            'Below that the target is not reached by anything except paying out less.'
            % (P(BREAK_LOW), P(BREAK_HIGH)),
            '<strong>Gde se mehanizam zaustavlja.</strong> Isplata vlasniku pojede '
            'sve što ostane posle troškova, pri popunjenosti %s–%s, u zavisnosti od '
            'modela. Ispod toga cilj se ne dostiže ničim osim manjom isplatom.'
            % (P(BREAK_LOW), P(BREAK_HIGH)),
            '<strong>Mekanizma nerede duruyor.</strong> Sahibine yapılan ödeme, '
            'modele göre %s–%s dolulukta giderlerden sonra kalan her şeyi yiyor. '
            'Bunun altında hedefe, ödemeyi düşürmek dışında hiçbir şeyle ulaşılmıyor.'
            % (P(BREAK_LOW), P(BREAK_HIGH))))))

    # ── ЧТО НЕ ВХОДИТ В РАСЧЁТ ───────────────────────────────────────────
    varrows = ''.join('<div><dt>%s</dt><dd>%s</dd></div>'
                      % (esc(label(en, m)), E(v) if v == int(v) else E2(v))
                      for en, m, v in VARIABLE)
    fixrows = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (esc(label(en, m)), E(v))
                      for en, m, v in FIXED)
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
        t(T('Расходы', 'The costs', 'Troškovi', 'Giderler')),
        t(T('Каждая строка названа', 'Every line is named',
            'Svaka stavka je imenovana', 'Her kalem adıyla yazılı')),
        t(T('На проданную ночь', 'Per night sold', 'Po prodatoj noći',
            'Satılan gece başına')),
        varrows,
        t(T('комиссия канала', 'booking commission', 'provizija kanala',
            'kanal komisyonu')),
        t(T('%s от ставки' % P(COMMISSION, 0), '%s of the rate' % P(COMMISSION, 0),
            '%s od cene' % P(COMMISSION, 0), 'fiyat üzerinden %s' % P(COMMISSION, 0))),
        t(T('За год на дом', 'Per house, per year', 'Godišnje po kući',
            'Ev başına yıllık')),
        fixrows,
        t(T('итого', 'total', 'ukupno', 'toplam')), E(FIX_YEAR),
        t(T('Комиссия канала стоит процентом, а не суммой, потому что на ставке %s '
            'она одна, а на %s другая. Раньше в модели стояло плоское число, верное '
            'ровно для одной из двух ставок.' % (E(D21['rate']), E(D24['rate'])),
            'The booking commission is a percentage rather than a figure, because it '
            'is one thing at %s a night and another at %s. The model used to carry a '
            'flat number, correct for exactly one of the two rates.'
            % (E(D21['rate']), E(D24['rate'])),
            'Provizija kanala stoji kao procenat, a ne kao suma, jer je na ceni %s '
            'jedna, a na %s druga. Model je ranije nosio ravan broj, tačan za tačno '
            'jednu od dve cene.' % (E(D21['rate']), E(D24['rate'])),
            'Kanal komisyonu tutar değil yüzde olarak duruyor, çünkü gecelik %s '
            'fiyatta bir, %s fiyatta başka. Model eskiden sabit bir sayı taşıyordu; '
            'iki fiyattan tam olarak birinde doğruydu.'
            % (E(D21['rate']), E(D24['rate']))))))

    # ── ВИД НА ЖИТЕЛЬСТВО ────────────────────────────────────────────────
    status = [
        (T('Оформление', 'Set-up', 'Osnivanje', 'Kuruluş'),
         T('Регистрация компании и первая отчётность идут через юриста, с которым мы '
           'работаем в Черногории. Стоимость называется вам до того, как вы на '
           'что-либо соглашаетесь.',
           'Company registration and the first filing, handled by the lawyer we work '
           'with in Montenegro. Quoted to you before you commit.',
           'Registracija firme i prva prijava idu preko advokata sa kojim radimo u '
           'Crnoj Gori. Cena vam se kaže pre nego što se na bilo šta obavežete.',
           'Şirket kuruluşu ve ilk beyan, Karadağ\'da birlikte çalıştığımız avukat '
           'üzerinden yürüyor. Bedeli, hiçbir şeye bağlanmadan önce size söylüyoruz.')),
        (T('Каждый год', 'Each year', 'Svake godine', 'Her yıl'),
         T('От %s налогов и взносов плюс бухгалтерия. Это реальные деньги, и они '
           'выходят из того, что зарабатывает дом, поэтому мы показываем их отдельной '
           'строкой, а не прячем внутрь доходности.' % E(5000),
           'From %s in taxes and contributions, plus accounting. This is a real '
           'cost and it comes out of what the house earns, so we show it separately '
           'rather than folding it into a yield figure.' % E(5000),
           'Od %s poreza i doprinosa, plus računovodstvo. To je pravi novac i izlazi '
           'iz onoga što kuća zaradi, pa ga prikazujemo odvojenom stavkom, a ne '
           'krijemo unutar prinosa.' % E(5000),
           '%s\'den başlayan vergi ve primler, artı muhasebe. Bu gerçek bir gider ve '
           'evin kazandığından çıkıyor; bu yüzden onu getiri rakamının içine '
           'saklamıyor, ayrı bir kalem olarak gösteriyoruz.' % E(5000))),
        (T('Не входит', 'Not included', 'Ne ulazi', 'Dahil değil'),
         T('Ваше налоговое положение в стране, где вы налоговый резидент, остаётся вопросом '
           'к вашему советнику.',
           'Your own tax position at home, which is a question for your own adviser.',
           'Vaš poreski položaj u zemlji u kojoj ste poreski rezident ostaje pitanje '
           'za vašeg savetnika.',
           'Vergi mükellefi olduğunuz ülkedeki kendi vergi durumunuz, kendi '
           'danışmanınıza sorulacak bir konu.')),
    ]
    strows = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (esc(t(lab)), esc(t(val)))
                     for lab, val in status)
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
        t(T('Статус', 'Status', 'Status', 'Statü')),
        t(T('Если вам нужен ещё и вид на жительство',
            'If you also want residence in Montenegro',
            'Ako vam treba i boravak u Crnoj Gori',
            'Karadağ\'da oturum da istiyorsanız')),
        t(T('Стоит прочитать до того, как сравнивать нас с квартирой: правила '
            'поменялись в январе 2026 года, и большинство продающих презентаций за '
            'этим не успели.',
            'Worth reading before you compare us with an apartment, because the rules '
            'changed in January 2026 and most sales pitches have not caught up.',
            'Vredi pročitati pre nego što nas uporedite sa stanom: pravila su se '
            'promenila u januaru 2026, a većina prodajnih prezentacija to nije '
            'ispratila.',
            'Bizi bir daireyle karşılaştırmadan önce okumaya değer: kurallar Ocak '
            '2026\'da değişti ve satış sunumlarının çoğu buna yetişemedi.')),
        t(T('Чего дом не даёт', 'What the residence does not do', 'Šta kuća ne daje',
            'Rezidansın vermediği şey')),
        t(T('Вида на жительство он не даёт. Для него нужна кадастровая недвижимость '
            'с оценочной стоимостью не ниже %s, а наш дом зарегистрирован как '
            'движимое имущество. Мы предпочитаем сказать это здесь, а не дать вам '
            'выяснить это потом.' % E(150000),
            'It does not give you a residence permit. That permit requires cadastral '
            'real estate with a tax-assessed value of at least %s, and our house '
            'is registered as movable property. We would rather say so here than let '
            'you find out later.' % E(150000),
            'Boravak ne daje. Za njega je potrebna katastarska nekretnina sa poreskom '
            'procenom od najmanje %s, a naša kuća je registrovana kao pokretna '
            'imovina. Radije to kažemo ovde nego da vi to otkrijete kasnije.' % E(150000),
            'Oturum izni vermiyor. O izin için vergi değeri en az %s olan, kadastroya '
            'kayıtlı bir gayrimenkul gerekiyor; bizim evimiz ise taşınır mal olarak '
            'tescilli. Bunu sonradan öğrenmeniz yerine burada söylemeyi tercih '
            'ediyoruz.' % E(150000))),
        t(T('Про квартиру тоже стоит знать: вид на жительство по недвижимости не даёт '
            'права работать или вести бизнес в Черногории, и эти годы не идут в зачёт '
            'постоянного проживания.',
            'Worth knowing about the apartment route too: a property-based permit does '
            'not allow you to work or run a business in Montenegro, and those years do '
            'not count toward permanent residence.',
            'Vredi znati i o stanu: boravak po osnovu nekretnine ne daje pravo na rad '
            'ni na vođenje biznisa u Crnoj Gori, i te godine se ne računaju u trajni '
            'boravak.',
            'Daire yolu için de bilmeye değer: gayrimenkule dayalı oturum, Karadağ\'da '
            'çalışma ya da iş yürütme hakkı vermiyor ve o yıllar kalıcı oturuma '
            'sayılmıyor.')),
        t(T('Что работает', 'What does work', 'Šta radi', 'İşleyen yol')),
        t(T('Вид на жительство через собственную черногорскую компанию. Компания ваша, '
            'на ней договор управления вашим домом, вы её директор по трудовому '
            'договору. Эти годы идут в зачёт постоянного проживания полностью, и '
            'работать вы вправе.',
            'Residence through your own Montenegrin company. You hold the company, the '
            'company holds the management arrangement for your house, and you are '
            'employed as its director. Those years count in full toward permanent '
            'residence, and you may legally operate.',
            'Boravak preko sopstvene crnogorske firme. Firma je vaša, na njoj je '
            'ugovor o upravljanju vašom kućom, a vi ste njen direktor po ugovoru o '
            'radu. Te godine se u potpunosti računaju u trajni boravak i smete legalno '
            'da radite.',
            'Kendi Karadağ şirketiniz üzerinden oturum. Şirket sizin, evinizin işletme '
            'sözleşmesi şirkette, siz de şirketin müdürü olarak iş sözleşmesiyle '
            'çalışıyorsunuz. O yıllar kalıcı oturuma tam olarak sayılıyor ve yasal '
            'olarak çalışabiliyorsunuz.')),
        t(T('Это стоит денег каждый год. Чтобы продлиться, компания должна была уплатить '
            'за прошедший год не меньше %s налогов и взносов. Граждане ЕС, ЕЭЗ и '
            'Швейцарии от этого требования освобождены.' % E(5000),
            'It has a running cost. To renew, the company must have paid at least '
            '%s in taxes and contributions over the previous year. Citizens of the '
            'EU, EEA and Switzerland are exempt from that requirement.' % E(5000),
            'To košta svake godine. Da bi se obnovio, firma je za proteklu godinu '
            'morala da uplati najmanje %s poreza i doprinosa. Državljani EU, EEP i '
            'Švajcarske izuzeti su od tog uslova.' % E(5000),
            'Bunun yıllık bir maliyeti var. Yenileme için şirketin geçen yıl en az %s '
            'vergi ve prim ödemiş olması gerekiyor. AB, AEA ve İsviçre vatandaşları bu '
            'koşuldan muaf.' % E(5000))),
        strows,
        t(T('<strong>Мы не гарантируем, что вид на жительство выдадут или продлят.</strong> '
            'Миграционные правила Черногории менялись дважды между ноябрём 2025 и '
            'январём 2026 года. Ничто на этой странице не является юридической '
            'консультацией, и мы познакомим вас с юристом до того, как вы на что-либо '
            'подпишетесь.',
            '<strong>We do not guarantee that any permit will be granted or renewed.</strong> '
            'Montenegrin immigration rules were amended twice between November 2025 and '
            'January 2026. Nothing on this page is legal advice, and we will introduce '
            'you to counsel before you commit to anything.',
            '<strong>Ne garantujemo da će boravak biti odobren ili obnovljen.</strong> '
            'Migraciona pravila Crne Gore menjala su se dva puta između novembra 2025 i '
            'januara 2026. Ništa na ovoj stranici nije pravni savet, i upoznaćemo vas '
            'sa advokatom pre nego što bilo šta potpišete.',
            '<strong>Herhangi bir iznin verileceğini ya da yenileneceğini garanti '
            'etmiyoruz.</strong> Karadağ\'ın göç kuralları Kasım 2025 ile Ocak 2026 '
            'arasında iki kez değişti. Bu sayfadaki hiçbir şey hukuki tavsiye değil ve '
            'bir şey imzalamadan önce sizi avukatla tanıştırıyoruz.'))))

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
        t(T('Трек Б', 'Track B', 'Opcija B', 'B seçeneği')),
        t(T('Или войти в размещение целиком', 'Or come in on the deployment',
            'Ili uđite u celo postavljanje', 'Ya da yerleşimin bütününe girin')),
        t(T('Двадцать пять резиденций по Черногории и сеть ферм, на которые их '
            'ставить. Один дом это актив. Размещение это бизнес вокруг него.',
            'Twenty-five residences across Montenegro, and a network of farms to put '
            'them on. One house is an asset. The deployment is the business around it.',
            'Dvadeset pet rezidencija po Crnoj Gori i mreža imanja na koja se '
            'postavljaju. Jedna kuća je sredstvo. Postavljanje je biznis oko njega.',
            'Karadağ\'ın her yanına yirmi beş rezidans ve onları koyacak bir çiftlik '
            'ağı. Bir ev bir varlık. Yerleşim ise onun çevresindeki iş.')),
        t(T('Что строится', 'What is being built', 'Šta se gradi', 'Ne kuruluyor')),
        t(T('Парк, который ходит между горами летом, винным краем в межсезонье и '
            'небольшой полосой побережья в отдельные недели, так что пустым стоит '
            'не один и тот же дом. Рамочные соглашения с фермами подписаны, '
            'производитель подтверждён, первые юниты в сборке.',
            'A fleet that moves between the mountains in summer, the wine country in '
            'the shoulder months and a small stretch of coast in selected weeks, so '
            'the same house is never the one sitting empty. Framework agreements with '
            'farms are signed, the manufacturer is confirmed, and the first units are '
            'in build.',
            'Park koji leti ide između planina, u međusezoni u vinorodni kraj, a u '
            'pojedinim nedeljama na uzak pojas obale, tako da prazna ne stoji uvek '
            'ista kuća. Okvirni ugovori sa imanjima su potpisani, proizvođač je '
            'potvrđen, prve jedinice su u izradi.',
            'Yazın dağlar arasında, ara sezonda şarap bölgesinde, belirli haftalarda '
            'da kıyının küçük bir bölümünde dolaşan bir filo; böylece boş kalan hep '
            'aynı ev olmuyor. Çiftliklerle çerçeve anlaşmaları imzalandı, üretici '
            'kesinleşti, ilk üniteler üretimde.')),
        t(T('Как устроено участие', 'How participation works',
            'Kako funkcioniše učešće', 'Katılım nasıl işliyor')),
        t(T('Частным порядком, разговором, а не формой на сайте. Мы присылаем модель, '
            'допущения под ней и условия, потом разговариваем. Участие оформляется '
            'индивидуально и публично не предлагается.',
            'Privately, by conversation, not through a form on a website. We send the '
            'model, the assumptions behind it and the terms, then talk. Participation '
            'is arranged individually and is not open to the public.',
            'Privatno, kroz razgovor, a ne kroz formu na sajtu. Pošaljemo model, '
            'pretpostavke ispod njega i uslove, pa razgovaramo. Učešće se uređuje '
            'pojedinačno i nije javno ponuđeno.',
            'Özel olarak, konuşarak; sitedeki bir formla değil. Modeli, altındaki '
            'varsayımları ve koşulları gönderiyoruz, sonra konuşuyoruz. Katılım tek '
            'tek düzenleniyor ve kamuya açık olarak sunulmuyor.')),
        t(T('Ничто здесь не является предложением ценных бумаг или приглашением '
            'инвестировать. Мы даём информацию по запросу тем, кто её просит, с '
            'проверками, которых требует наш юрист, и любое участие оформляется '
            'документами до того, как двигаются деньги.',
            'Nothing here is an offer of securities or an invitation to invest. We '
            'provide information on request to people who ask for it, subject to the '
            'checks our counsel requires, and any participation is documented in full '
            'before money moves.',
            'Ništa ovde nije ponuda hartija od vrednosti ni poziv na investiranje. '
            'Informacije dajemo na zahtev onima koji ih traže, uz provere koje naš '
            'advokat zahteva, i svako učešće se dokumentuje pre nego što se novac '
            'pomeri.',
            'Buradaki hiçbir şey menkul kıymet teklifi ya da yatırım daveti değil. '
            'Bilgiyi, isteyenlere talep üzerine, avukatımızın istediği kontrollerle '
            'veriyoruz ve her katılım, para hareket etmeden önce belgeleniyor.')),
        t(T('Запросить материалы', 'Request the materials', 'Zatražite materijale',
            'Materyalleri isteyin'))))

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
        t(T('Где мы на самом деле', 'Where we actually are', 'Gde smo stvarno sada',
            'Gerçekte nerede olduğumuz')),
        t(T('Ни одной проданной ночи', 'Not one night sold', 'Ni jedna prodata noć',
            'Satılmış tek bir gece yok')),
        t(T('Существует один прототип, собранный вручную в 2023 году. Ни одна '
            'резиденция ещё не построена по производственной спецификации, и ни один '
            'гость в ней не жил. Первые юниты встают в Черногории в I квартале 2027.',
            'One prototype exists, built by hand in 2023. No residence has been built '
            'to production specification yet, and no guest has stayed in one. The '
            'first units deploy in Montenegro in Q1 2027.',
            'Postoji jedan prototip, sastavljen rukama 2023. Ni jedna rezidencija još '
            'nije napravljena po proizvodnoj specifikaciji i ni jedan gost u njoj nije '
            'odseo. Prve jedinice staju u Crnoj Gori u prvom kvartalu 2027.',
            '2023\'te elle yapılmış bir prototip var. Henüz üretim şartnamesine göre '
            'yapılmış bir rezidans yok ve hiçbir konuk birinde kalmadı. İlk üniteler '
            '2027 ilk çeyrekte Karadağ\'a yerleşiyor.')),
        t(T('Всё, что на этой странице описывает доход, есть модель. Всё, что описывает '
            'продукт, есть спецификация, по которой мы строим. Отвечаем на письма сами.',
            'Everything on this page that describes earnings is a model, and everything '
            'that describes the product is a specification we are building to. We '
            'answer every message ourselves.',
            'Sve što na ovoj stranici opisuje prihod je model. Sve što opisuje proizvod '
            'je specifikacija po kojoj gradimo. Na pisma odgovaramo sami.',
            'Bu sayfada geliri anlatan her şey bir model. Ürünü anlatan her şey, '
            'üretimde uyduğumuz şartname. Mesajları kendimiz yanıtlıyoruz.')),
        t(T('Написать нам', 'Write to us', 'Pišite nam', 'Bize yazın')),
        t(T('Показанные цифры модельные и ориентировочные. Это не прогноз, не '
            'гарантия и не обещание дохода. Доходность зависит от загрузки, '
            'операционных расходов и сезона и может оказаться ниже расчётной.',
            'Figures shown are modelled and indicative. They are not a forecast, a '
            'guarantee or a promise of return. Yields depend on occupancy, operating '
            'costs and the season, and may be lower than modelled.',
            'Prikazane cifre su modelske i orijentacione. To nije prognoza, garancija '
            'ni obećanje prihoda. Prinos zavisi od popunjenosti, operativnih troškova '
            'i sezone i može biti niži od izračunatog.',
            'Gösterilen rakamlar modellenmiş ve gösterge niteliğinde. Bir tahmin, '
            'garanti ya da getiri vaadi değil. Getiri doluluğa, işletme giderlerine ve '
            'sezona bağlı ve hesaplanandan düşük çıkabilir.')),
        t(T('Страница носит информационный характер. Это не инвестиционная, '
            'юридическая или налоговая консультация, не публичная оферта и не '
            'приглашение приобрести какой-либо инструмент. Изображения резиденций это '
            'рендеры: ни один дом не построен по производственной спецификации.',
            'This page is information only. It is not investment advice, legal advice, '
            'tax advice, a public offer, or an invitation to subscribe for any '
            'instrument. Images of the residences are renders: no house has been built '
            'to the production specification.',
            'Stranica je informativnog karaktera. Nije investiciono, pravno ni poresko '
            'savetovanje, nije javna ponuda i nije poziv na kupovinu bilo kakvog '
            'instrumenta. Prikazi rezidencija su renderi: ni jedna kuća nije '
            'napravljena po proizvodnoj specifikaciji.',
            'Bu sayfa yalnızca bilgi içindir. Yatırım, hukuk ya da vergi danışmanlığı '
            'değil, kamuya açık bir teklif değil ve herhangi bir araca katılma daveti '
            'değil. Rezidans görselleri render: hiçbir ev üretim şartnamesine göre '
            'yapılmadı.')),
        t(T('Условия участия обсуждаются индивидуально и оформляются документами, '
            'подготовленными с юристом. Tiny Mansion это проект Korsakov Group d.o.o., '
            'Тиват, Черногория.',
            'Terms are agreed individually and set out in documents prepared with a '
            'lawyer. Tiny Mansion is a project of Korsakov Group d.o.o., Tivat, '
            'Montenegro.',
            'Uslovi učešća se dogovaraju pojedinačno i uređuju dokumentima '
            'pripremljenim sa advokatom. Tiny Mansion je projekat Korsakov Group '
            'd.o.o., Tivat, Crna Gora.',
            'Katılım koşulları tek tek kararlaştırılıyor ve avukatla hazırlanan '
            'belgelerle düzenleniyor. Tiny Mansion, Korsakov Group d.o.o. (Tivat, '
            'Karadağ) projesidir.'))))

    return ''.join(out)


for lang in LANGS:
    p = os.path.join(ROOT, FILES[lang])
    d = os.path.dirname(p)
    if not os.path.isdir(d):
        os.makedirs(d)
    io.open(p, 'w', encoding='utf-8').write(page(lang))
    print('written %-24s %6.1f KB' % (FILES[lang], os.path.getsize(p) / 1024))
