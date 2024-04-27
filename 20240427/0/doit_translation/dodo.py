import glob


def task_pot():
    return {
            'actions': ["pybabel extract --keyword=_:1 . -o server.pot",
                        "pybabel extract --keywords=ngettext:2,3 . -o server.pot"],
            'file_dep': glob.glob('mood/*.py'),
            'targets': ['mood.pot']
            }


def task_po():
    return {
            'actions': ["pybabel update -D mood -i server.pot -l ru_RU.UTF-8 -d po"],
            'file_dep': ['server.pot'],
            'targets': ['po/ru_RU.UTF-8/LC_MESSAGES/mood.po']
            }


def task_mo():
    return {
            'actions': ["pybabel compile -D mood -l ru_RU.UTF-8 -d po -i po/ru_RU.UTF-8/LC_MESSAGES/mood.po"],
            'file_dep': ['po/ru_RU.UTF-8/LC_MESSAGES/mood.po'],
            'targets': ['po/ru_RU.UTF-8/LC_MESSAGES/mood.mo'],
            }
