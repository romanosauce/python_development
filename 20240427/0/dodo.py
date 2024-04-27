def task_html():
    return {
            'actions': ['sphinx-build -M html "./docs/source" "./docs/build"'],
            'file_dep': ["./docs/source/API.rst", "./docs/source/index.rst"]
    }


def task_erase():
    return {
            'actions': ['git clean -xdf']
    }
