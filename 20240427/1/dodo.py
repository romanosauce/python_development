import glob


def task_pot():
    return {
            'actions': ['pybabel extract --keywords=ngettext:2,3 --keywords=_:2 mood -o server.pot'],
            'file_dep': glob.glob('mood/server/*.py'),
            'targets': ['server.pot'],
            'doc': 're-create .pot',
            }


def task_po():
    return {
            'actions': ['pybabel update --ignore-pot-creation-date -D mood -i server.pot -l ru_RU.UTF-8 -d po'],
            'file_dep': ['server.pot'],
            'targets': ['po/ru_RU.UTF-8/LC_MESSAGES/mood.po'],
            'doc': 'update translations',
            }


def task_mo():
    return {
            'actions': ['pybabel compile -D mood -l ru_RU.UTF-8 -d po -i po/ru_RU.UTF-8/LC_MESSAGES/mood.po'],
            'file_dep': ['po/ru_RU.UTF-8/LC_MESSAGES/mood.po'],
            'targets': ['po/ru_RU.UTF-8/LC_MESSAGES/mood.mo'],
            'doc': 'compile translations',
            }


def task_rmdb():
    return {
            'actions': ['rm .*.db'],
            'doc': 'task for removing doit database',
            }


def task_i18n():
    return {
            'actions': None,
            'task_dep': ['pot', 'po', 'mo'],
            'doc': 'task for generating translations',
            }


def task_html():
    return {
            'actions': ['sphinx-build -M html ./docs/source ./docs/build'],
            }
