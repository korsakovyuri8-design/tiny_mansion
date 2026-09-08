# -*- coding: utf-8 -*-
"""Сменить объявленный срок первого развёртывания на всём сайте.

Дата стоит в тридцати с лишним местах: в разметке, в ключах словаря и в
переводах, на главной, в форме, на страницах резиденций, в подвале и на
обеих инвесторских страницах. Ключ словаря — это английская строка, поэтому
менять английский текст, не меняя ключ, нельзя: перевод молча отвалится.
Презентация в deck/ держит её же своим текстом и тоже здесь.
Отсюда скрипт, а не поиск с заменой руками.

    python3 relaunch.py "Q2 2027" "II квартал 2027"
    python3 relaunch.py --check

После него обязательно:

    node build.mjs && python3 gen_invest.py

Русские падежи: скрипт знает про «в I квартале 2027» и меняет предложный
падеж отдельно. Если новая формулировка склоняется иначе — проверьте глазами.
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
# Каждый файл, который держит дату собственным текстом. Собранные страницы
# перезаписываются сборкой, поэтому их здесь нет.
FILES = ['src/index.html', 'gen_invest.py', 'club.py', 'deck/deck.html',
         'drafts/invest-en.html']

EN_OLD = 'Q1 2027'
RU_OLD = 'I квартал 2027'

# Русский склоняется, и по сайту дата стоит в трёх падежах: «I квартал 2027»,
# «в I квартале 2027», «с I квартала 2027». Пропущенный падеж — это не
# опечатка, а живая старая дата на странице; поэтому все три здесь, длинные
# формы заменяются раньше коротких, иначе общая замена их съест.
RU_FORMS = ['квартале', 'квартала', 'кв.']


def decline(ru, form):
    """«II квартал 2027» -> «II квартале 2027», «II кв. 2027» и так далее."""
    return re.sub(r'\bквартал\b', form, ru)


def ru_forms(ru):
    """Все формы, от длинной к короткой: именительный заменяется последним,
    иначе он съест начало «квартале» и «квартала» и оставит хвост."""
    return [decline(ru, f) for f in RU_FORMS] + [ru]


def occurrences():
    out = {}
    for rel in FILES:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        s = io.open(p, encoding='utf-8').read()
        n = s.count(EN_OLD) + sum(s.count(f) for f in ru_forms(RU_OLD))
        if n:
            out[rel] = n
    return out


# Любая дата вида «Q3 2026», «III квартала 2026», «I кв. 2027». Отставшая
# форма — это не косметика: английский ключ уезжает на новый квартал, русское
# значение остаётся на старом, и перевод молча отваливается.
STRAY = re.compile(r'Q[1-4]\s+20\d\d|[IVX]{1,4}\s+(?:квартал\w*|кв\.)\s+20\d\d')


def strays():
    """Даты, не совпадающие ни с одной формой объявленной. Должно быть пусто."""
    good = set([EN_OLD] + ru_forms(RU_OLD))
    out = []
    for rel in FILES:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        s = io.open(p, encoding='utf-8').read()
        for m in STRAY.finditer(s):
            if m.group(0) not in good:
                line = s.count('\n', 0, m.start()) + 1
                out.append((rel, line, m.group(0)))
    return out


def check():
    total = occurrences()
    if not total:
        sys.exit('Ни одного вхождения «%s» — дата уже другая, поправьте EN_OLD.' % EN_OLD)
    print('Сейчас на сайте объявлено: %s / %s' % (EN_OLD, RU_OLD))
    for rel, n in sorted(total.items()):
        print('  %-22s %d' % (rel, n))
    print('  всего                  %d' % sum(total.values()))

    left = strays()
    if left:
        print('\nОтставшие даты — их надо привести к объявленной:')
        for rel, line, txt in left:
            print('  %s:%d  %s' % (rel, line, txt))
        sys.exit(1)
    print('Отставших дат нет.')


def apply(en_new, ru_new):
    olds, news = ru_forms(RU_OLD), ru_forms(ru_new)
    changed = 0
    for rel in FILES:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        s = io.open(p, encoding='utf-8').read()
        before = s
        for o, n in zip(olds, news):   # склонения первыми, потом именительный
            s = s.replace(o, n)
        s = s.replace(EN_OLD, en_new)
        if s != before:
            io.open(p, 'w', encoding='utf-8').write(s)
            n = before.count(EN_OLD) + sum(before.count(f) for f in olds)
            print('  %-22s %d' % (rel, n))
            changed += n
    if not changed:
        sys.exit('Ничего не изменилось. Проверьте EN_OLD и RU_OLD в этом файле.')
    print('\nЗаменено вхождений: %d' % changed)
    left = strays()
    if left:
        print('\nОстались даты в других формах — руками:')
        for rel, line, txt in left:
            print('  %s:%d  %s' % (rel, line, txt))
    print('Теперь: node build.mjs && python3 gen_invest.py')
    print('И поправьте EN_OLD/RU_OLD в этом файле на новые значения.')


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '--check':
        check()
    elif len(sys.argv) == 3:
        apply(sys.argv[1], sys.argv[2])
    else:
        sys.exit(__doc__)
