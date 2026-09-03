# -*- coding: utf-8 -*-
"""Сменить объявленный срок первого развёртывания на всём сайте.

Дата стоит в тридцати с лишним местах: в разметке, в ключах словаря и в
переводах, на главной, в форме, на страницах резиденций, в подвале и на
обеих инвесторских страницах. Ключ словаря — это английская строка, поэтому
менять английский текст, не меняя ключ, нельзя: перевод молча отвалится.
Отсюда скрипт, а не поиск с заменой руками.

    python3 relaunch.py "Q4 2026" "IV квартал 2026"
    python3 relaunch.py --check

После него обязательно:

    node build.mjs && python3 gen_invest.py

Русские падежи: скрипт знает про «в III квартале 2026» и меняет предложный
падеж отдельно. Если новая формулировка склоняется иначе — проверьте глазами.
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
# Каждый файл, который держит дату собственным текстом. Собранные страницы
# перезаписываются сборкой, поэтому их здесь нет.
FILES = ['src/index.html', 'gen_invest.py', 'club.py']

EN_OLD = 'Q3 2026'
RU_OLD = 'III квартал 2026'
RU_OLD_PREP = 'III квартале 2026'


def prepositional(ru_new):
    """«IV квартал 2026» -> «IV квартале 2026». Только для этой формы."""
    return re.sub(r'\bквартал\b', 'квартале', ru_new)


def occurrences():
    out = {}
    for rel in FILES:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        s = io.open(p, encoding='utf-8').read()
        n = s.count(EN_OLD) + s.count(RU_OLD) + s.count(RU_OLD_PREP)
        if n:
            out[rel] = n
    return out


def check():
    total = occurrences()
    if not total:
        sys.exit('Ни одного вхождения «%s» — дата уже другая, поправьте EN_OLD.' % EN_OLD)
    print('Сейчас на сайте объявлено: %s / %s' % (EN_OLD, RU_OLD))
    for rel, n in sorted(total.items()):
        print('  %-22s %d' % (rel, n))
    print('  всего                  %d' % sum(total.values()))


def apply(en_new, ru_new):
    ru_new_prep = prepositional(ru_new)
    changed = 0
    for rel in FILES:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        s = io.open(p, encoding='utf-8').read()
        before = s
        # предложный падеж первым, иначе его съест общая замена
        s = s.replace(RU_OLD_PREP, ru_new_prep)
        s = s.replace(RU_OLD, ru_new)
        s = s.replace(EN_OLD, en_new)
        if s != before:
            io.open(p, 'w', encoding='utf-8').write(s)
            n = before.count(EN_OLD) + before.count(RU_OLD) + before.count(RU_OLD_PREP)
            print('  %-22s %d' % (rel, n))
            changed += n
    if not changed:
        sys.exit('Ничего не изменилось. Проверьте EN_OLD и RU_OLD в этом файле.')
    print('\nЗаменено вхождений: %d' % changed)
    print('Теперь: node build.mjs && python3 gen_invest.py')
    print('И поправьте EN_OLD/RU_OLD в этом файле на новые значения.')


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '--check':
        check()
    elif len(sys.argv) == 3:
        apply(sys.argv[1], sys.argv[2])
    else:
        sys.exit(__doc__)
