# -*- coding: utf-8 -*-
"""Сменить объявленный срок первого развёртывания на всём сайте.

Дата стоит в пятидесяти с лишним местах: в разметке, в ключах словарей и в
переводах на четырёх языках, на главной, в форме, на страницах резиденций, в
подвале и на страницах инвесторам. Ключом словаря служит английская строка,
поэтому менять английский текст, не меняя ключ, нельзя: перевод молча
отвалится. Презентация в deck/ держит ту же дату своим текстом и тоже здесь.
Отсюда скрипт, а не поиск с заменой руками.

    python3 relaunch.py 2 2027     # перенести на II квартал 2027
    python3 relaunch.py --check

Формы на каждом языке скрипт строит сам, по таблице ниже: русский
склоняется в трёх падежах, сербский в трёх плюс короткое «I kv.»,
турецкий берёт два написания номера и два послелога. Проверка требует,
чтобы ни одной формы другой даты на сайте не осталось: отставшая форма это
не косметика, а живая старая дата на странице.

После замены обязательно:

    node build.mjs && python3 gen_invest.py
"""
import glob, io, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# Сейчас объявлено. Скрипт правит эту строку сам, когда перенос прошёл.
CURRENT = (1, 2027)

# Каждый файл, который держит дату собственным текстом. Собранные страницы
# перезаписываются сборкой, поэтому их здесь нет; словари lang/*.js есть,
# потому что перевод живёт в них.
def files():
    out = ['src/index.html', 'gen_invest.py', 'club.py', 'deck/deck.html',
           'drafts/invest-en.html']
    out += sorted(os.path.relpath(p, ROOT)
                  for p in glob.glob(os.path.join(ROOT, 'lang', '*.js')))
    return [f for f in out if os.path.exists(os.path.join(ROOT, f))]

ROMAN = {1: 'I', 2: 'II', 3: 'III', 4: 'IV'}
SR_ORD = {1: ('prvi', 'prvog', 'prvom'), 2: ('drugi', 'drugog', 'drugom'),
          3: ('treći', 'trećeg', 'trećem'), 4: ('četvrti', 'četvrtog', 'četvrtom')}
TR_ORD = {1: 'ilk', 2: 'ikinci', 3: 'üçüncü', 4: 'dördüncü'}


def forms(q, y):
    """Все написания квартала на всех языках, от длинных к коротким.

    Порядок важен: «I квартале 2027» заменяется раньше «I квартал 2027»,
    иначе общая замена съест начало длинной формы и оставит хвост. То же с
    турецкими послелогами: «çeyrekten» раньше «çeyrekte» раньше «çeyrek»."""
    r, n, y = ROMAN[q], SR_ORD[q], str(y)
    t = TR_ORD[q]
    return [
        '%s квартале %s' % (r, y), '%s квартала %s' % (r, y),
        '%s кв. %s' % (r, y), '%s квартал %s' % (r, y),
        '%s kvartalu %s' % (n[2], y), '%s kvartala %s' % (n[1], y),
        '%s kv. %s' % (r, y), '%s kvartal %s' % (n[0], y),
        '%s %d. çeyrekten' % (y, q), '%s %s çeyrekten' % (y, t),
        '%s %d. çeyrekte' % (y, q), '%s %s çeyrekte' % (y, t),
        '%s %d. çeyrek' % (y, q), '%s %s çeyrek' % (y, t),
        'Q%d %s' % (q, y),
    ]


# Любая дата вида «Q3 2026», «III квартала 2026», «I kv. 2027», «2027 ilk
# çeyrekte». Отставшая форма значит, что английский ключ уехал на новый
# квартал, а перевод остался на старом, и он молча отвалился.
STRAY = re.compile(
    r'Q[1-4]\s+20\d\d'
    r'|[IVX]{1,4}\s+(?:квартал\w*|кв\.)\s+20\d\d'
    r'|(?:[IVX]{1,4}\s+kv\.|\b(?:prv|drug|treć|četvrt)\w*\s+kvartal\w*)\s+20\d\d'
    r'|20\d\d\s+(?:[1-4]\.|ilk|ikinci|üçüncü|dördüncü)\s+çeyrek\w*')


def occurrences(good):
    out = {}
    for rel in files():
        s = io.open(os.path.join(ROOT, rel), encoding='utf-8').read()
        n = sum(s.count(f) for f in good)
        if n:
            out[rel] = n
    return out


def strays(good):
    """Даты, не совпадающие ни с одной формой объявленной. Должно быть пусто."""
    keep, out = set(good), []
    for rel in files():
        s = io.open(os.path.join(ROOT, rel), encoding='utf-8').read()
        for m in STRAY.finditer(s):
            if m.group(0) not in keep:
                out.append((rel, s.count('\n', 0, m.start()) + 1, m.group(0)))
    return out


def check():
    good = forms(*CURRENT)
    total = occurrences(good)
    if not total:
        sys.exit('Ни одного вхождения «Q%d %d»: дата уже другая, поправьте CURRENT.'
                 % CURRENT)
    print('Сейчас на сайте объявлено: Q%d %d' % CURRENT)
    for rel, n in sorted(total.items()):
        print('  %-22s %d' % (rel, n))
    print('  всего                  %d' % sum(total.values()))

    left = strays(good)
    if left:
        print('\nОтставшие даты, их надо привести к объявленной:')
        for rel, line, txt in left:
            print('  %s:%d  %s' % (rel, line, txt))
        sys.exit(1)
    print('Отставших дат нет.')


def apply(q, y):
    olds, news = forms(*CURRENT), forms(q, y)
    changed = 0
    for rel in files():
        p = os.path.join(ROOT, rel)
        s = before = io.open(p, encoding='utf-8').read()
        for o, n in zip(olds, news):      # длинные формы раньше коротких
            s = s.replace(o, n)
        if s != before:
            io.open(p, 'w', encoding='utf-8').write(s)
            n = sum(before.count(f) for f in olds)
            print('  %-22s %d' % (rel, n))
            changed += n
    if not changed:
        sys.exit('Ничего не изменилось. Проверьте CURRENT в этом файле.')
    print('\nЗаменено вхождений: %d' % changed)

    # Запомнить новую дату здесь же: забытый CURRENT это ровно тот случай,
    # из-за которого английский ключ уезжал, а перевод оставался.
    me = os.path.abspath(__file__)
    s = io.open(me, encoding='utf-8').read()
    s = re.sub(r'^CURRENT = \(\d, \d{4}\)$', 'CURRENT = (%d, %d)' % (q, y),
               s, count=1, flags=re.M)
    io.open(me, 'w', encoding='utf-8').write(s)
    print('CURRENT в relaunch.py переставлен на (%d, %d)' % (q, y))

    left = strays(forms(q, y))
    if left:
        print('\nОстались даты в других формах, руками:')
        for rel, line, txt in left:
            print('  %s:%d  %s' % (rel, line, txt))
    print('Теперь: node build.mjs && python3 gen_invest.py')


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '--check':
        check()
    elif len(sys.argv) == 3 and sys.argv[1].isdigit() and sys.argv[2].isdigit():
        q, y = int(sys.argv[1]), int(sys.argv[2])
        if q not in ROMAN:
            sys.exit('Квартал бывает от 1 до 4.')
        apply(q, y)
    else:
        sys.exit(__doc__)
