def task_html():
    return {
            'actions': ['sphinx-build -M html "./docs/source" "./docs/build"'],
    }


def task_erase():
    return {
            'actions': ['git clean -xdf']
    }
