import locale
import os
import gettext

# locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())
_podir = os.path.join(os.path.dirname(__file__), "po")
translation = gettext.translation("prog", _podir, fallback=True)
_, ngettext = translation.gettext, translation.ngettext

while line := input():
    n = len(line.split())
    print(ngettext("Entered {} word", "Entered {} words", n).format(n))
