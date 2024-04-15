import locale
import os
import gettext

LOCALES = {
        ("ru_RU", "UTF-8"): gettext.translation("prog", "po", ["ru"]),
        ("en_US", "UTF-8"): gettext.NullTranslations(),
}

def _(*text):
    return LOCALES[locale.getlocale()].ngettext(*text)


# locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())

while line := input():
    n = len(line.split())
    for loc in LOCALES:
        locale.setlocale(locale.LC_ALL, loc)
        print(_("Entered {} word", "Entered {} words", n).format(n))
