# -*- coding: utf-8 -*-
"""Предложение владельцу: дом в собственность плюс подключение к сети.

Покупатель платит за дом и один раз за подключение, дом остаётся его,
управляем им мы. Считается это так:

    вход      = цена дома + взнос за подключение
    выплата   = TARGET × вход          (цель, а не обещание)
    доля      = выплата / выручка      (подстраивается под цену дома)

Порядок именно такой. Раньше фиксированной была доля в выручке, и тогда
доходность разъезжалась по вилке цены: на дешёвом доме одна, на дорогом
другая. Теперь фиксирована цель по доходности, а доля выводится из неё,
поэтому дом за €120 000 и дом за €170 000 дают владельцу одно и то же
в процентах и разное в деньгах.

Загрузка стоит одна на все сценарии и намеренно: это не прогноз, а
политика. Дом не привязан к площадке, и ферма, которая не выходит на
эту цифру, меняется по ходу сезона.

    python3 club.py
"""

EUR  = lambda v: '€' + format(int(round(v)), ',d').replace(',', ' ')
EUR2 = lambda v: '€' + ('%.2f' % v).replace('.', ',')
PCT  = lambda v, d=1: (('%.' + str(d) + 'f') % (v * 100)).replace('.', ',') + '%'

# ── что продаётся ────────────────────────────────────────────────────────
# (ключ, английское имя, русское имя, цена дома, ставка за ночь)
MODELS = [
    ('residence-21', 'Residence 21ft',       'Residence 21ft',       120_000, 280),
    ('residence-24', 'Grand Residence 24ft', 'Grand Residence 24ft', 170_000, 320),
]
ONBOARDING = 18_000

# ── политика, а не прогноз ───────────────────────────────────────────────
OCC    = 0.75    # круглый год; внутри сезонного окна цель 75–85%
TARGET = 0.17    # цель по доходности на полную сумму входа

# ── расходы ──────────────────────────────────────────────────────────────
# Комиссия канала считается процентом от ставки, а не плоской суммой: на €320 она
# другая, чем на €280. Раньше она стояла в списке числом €33,60, что верно
# ровно для одной ставки из двух.
COMMISSION = 0.12
# Вторым элементом идёт не строка, а перевод по языкам: английский служит
# ключом и подписью английской версии, остальные языки берутся отсюда.
# Тройка (английское, переводы, число) сохранена, чтобы распаковка по всему
# файлу и в gen_invest.py осталась прежней.
VARIABLE = [
    ('Cleaning and linen between guests',
     {'ru': 'Уборка и бельё между гостями',
      'sr': 'Čišćenje i posteljina između gostiju',
      'tr': 'Konuklar arası temizlik ve çarşaf'},                            27.00),
    ('Maintenance, parts, wear',
     {'ru': 'Обслуживание, запчасти, износ',
      'sr': 'Servis, delovi, habanje',
      'tr': 'Bakım, yedek parça, aşınma'},                                   14.00),
    ('Welcome basket from the farm',
     {'ru': 'Приветственный набор с фермы',
      'sr': 'Korpa dobrodošlice sa imanja',
      'tr': 'Çiftlikten karşılama sepeti'},                                  11.00),
    ('Water, waste, consumables',
     {'ru': 'Вода, вывоз, расходники',
      'sr': 'Voda, odvoz, potrošni materijal',
      'tr': 'Su, atık, sarf malzemesi'},                                      9.50),
    ('Moving between zones',
     {'ru': 'Перегон между зонами',
      'sr': 'Premeštanje između zona',
      'tr': 'Bölgeler arası taşıma'},                                         7.50),
    ('Check-in, comms, platform',
     {'ru': 'Приём гостя, связь, платформа',
      'sr': 'Prijem gosta, komunikacija, platforma',
      'tr': 'Karşılama, iletişim, platform'},                                 5.40),
]
FIXED = [
    ('Insurance',
     {'ru': 'Страховка', 'sr': 'Osiguranje', 'tr': 'Sigorta'},            1_500),
    ('Accounting and admin',
     {'ru': 'Бухгалтерия и админ',
      'sr': 'Računovodstvo i administracija',
      'tr': 'Muhasebe ve idare'},                                         2_000),
    ('Platform and telemetry',
     {'ru': 'Платформа и телеметрия',
      'sr': 'Platforma i telemetrija',
      'tr': 'Platform ve telemetri'},                                       800),
]
VAR_NIGHT = sum(v for _, _, v in VARIABLE)      # без комиссии канала
FIX_YEAR  = sum(v for _, _, v in FIXED)         # на один юнит в год

ONBOARDING_USE = [
    ('Tow vehicle: deposit or lease, net of VAT',
     {'ru': 'Тягач: первый взнос или лизинг, за вычетом НДС',
      'sr': 'Vozilo za vuču: prva rata ili lizing, bez PDV-a',
      'tr': 'Çekici araç: peşinat ya da kiralama, KDV hariç'},            11_400),
    ('Logistics and siting on the farm',
     {'ru': 'Логистика и установка на ферме',
      'sr': 'Logistika i postavljanje na imanju',
      'tr': 'Lojistik ve çiftliğe yerleştirme'},                           3_600),
    ('PMS, locks, photography, listings',
     {'ru': 'Интеграция в PMS, замки, съёмка, листинги',
      'sr': 'Integracija u PMS, zaključavanje, snimanje, oglasi',
      'tr': 'PMS entegrasyonu, kilitler, çekim, ilanlar'},                 2_000),
    ('Company structure for the first months',
     {'ru': 'Структура компании на первые месяцы',
      'sr': 'Struktura kompanije za prve mesece',
      'tr': 'İlk aylar için şirket yapısı'},                               1_000),
]


def unit(price, rate, occ=OCC, target=TARGET):
    """Один дом за год. Доля владельца выводится из цели, а не задана."""
    nights = 365 * occ
    rev    = rate * nights
    var    = nights * (VAR_NIGHT + COMMISSION * rate)
    gop    = rev - var - FIX_YEAR
    entry  = price + ONBOARDING
    payout = target * entry
    return dict(price=price, rate=rate, entry=entry, nights=nights, rev=rev,
                var=var, fix=FIX_YEAR, gop=gop, payout=payout,
                share=payout / rev, left=gop - payout,
                left_pc=(gop - payout) / gop, y=payout / entry)


ALL = [(k, en, ru, unit(p, r)) for k, en, ru, p, r in MODELS]


def rule(n=78):
    print('─' * n)


if __name__ == '__main__':
    print('=' * 78)
    print('ДОМ В СОБСТВЕННОСТЬ + ПОДКЛЮЧЕНИЕ К СЕТИ')
    print('=' * 78)

    print('\n1. ВХОД')
    rule()
    print('  %-34s %12s %12s' % ('', 'дом', 'вход'))
    for _, en, _, d in ALL:
        print('  %-34s %12s %12s' % (en, EUR(d['price']), EUR(d['entry'])))
    print('  %-34s %12s %12s' % ('подключение, разово', '', EUR(ONBOARDING)))

    print('\n2. НА ЧТО ИДЁТ ВЗНОС (на один юнит)')
    rule()
    for en, _, v in ONBOARDING_USE:
        print('    %-52s %10s' % (en, EUR(v)))
    print('    %-52s %10s' % ('итого', EUR(sum(v for _, _, v in ONBOARDING_USE))))
    assert sum(v for _, _, v in ONBOARDING_USE) == ONBOARDING, 'взнос не сходится с расшифровкой'

    print('\n3. РАСХОДЫ')
    rule()
    print('  На одну проданную ночь:')
    for en, _, v in VARIABLE:
        print('    %-52s %10s' % (en, EUR2(v)))
    print('    %-52s %10s' % ('комиссия канала, %s от ставки' % PCT(COMMISSION, 0), 'считается'))
    print('  Постоянные, за год на юнит:')
    for en, _, v in FIXED:
        print('    %-52s %10s' % (en, EUR(v)))
    print('    %-52s %10s' % ('итого', EUR(FIX_YEAR)))

    print('\n4. ГОД, ПРИ ЗАГРУЗКЕ %s' % PCT(OCC, 0))
    rule()
    print('  %-30s %14s %14s' % ('', ALL[0][1], ALL[1][1]))
    row = lambda label, f: print('  %-30s %14s %14s'
                                 % (label, f(ALL[0][3]), f(ALL[1][3])))
    row('Ставка за ночь',      lambda d: EUR(d['rate']))
    row('Проданных ночей',     lambda d: '%d' % round(d['nights']))
    row('Выручка',             lambda d: EUR(d['rev']))
    row('  − эксплуатация',    lambda d: '−' + EUR(d['var'] + d['fix']))
    row('GOP',                 lambda d: EUR(d['gop']))
    rule()
    row('ВЛАДЕЛЬЦУ',           lambda d: EUR(d['payout']))
    row('  это от выручки',    lambda d: PCT(d['share']))
    row('  это от входа',      lambda d: PCT(d['y']))
    row('Остаётся управлению', lambda d: EUR(d['left']))
    row('  это от GOP',        lambda d: PCT(d['left_pc'], 0))

    print('\n5. ПОЧЕМУ ФИКСИРУЕТСЯ ЦЕЛЬ, А НЕ ДОЛЯ')
    rule()
    print('  Доля в выручке одна на оба дома дала бы разную доходность:')
    for _, en, _, d in ALL:
        flat = 0.306 * d['rev'] / d['entry']
        print('    %-24s при доле 30,6%%  →  %s годовых' % (en, PCT(flat)))
    print('  Цель одна на оба дома, и тогда подстраивается доля:')
    for _, en, _, d in ALL:
        print('    %-24s доля %s  →  %s годовых' % (en, PCT(d['share']), PCT(d['y'])))

    print('\n6. ГДЕ ЭТО ЛОМАЕТСЯ')
    rule()
    for _, en, _, d in ALL:
        need = d['payout'] + d['var'] / d['nights'] * 0 + d['fix']
        # загрузка, при которой GOP ровно равен выплате владельцу
        night_margin = d['rate'] * (1 - COMMISSION) - VAR_NIGHT
        occ0 = (d['payout'] + FIX_YEAR) / (night_margin * 365)
        print('    %-24s выплата упирается в GOP при загрузке %s'
              % (en, PCT(occ0)))
    print('  Ниже этой загрузки цель не достигается ничем, кроме уменьшения')
    print('  выплаты: своих денег управляющая сторона не добавляет.')
