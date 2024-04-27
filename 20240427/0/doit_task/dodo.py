from zipfile import ZipFile
from pathlib import Path
from glob import iglob


ZIPARCH = "docs.zip"
HTMLINDEX = "docs/build/html/index.html"


def task_html():
    """Generate HTML docs."""
    return {
            'actions': ['sphinx-build -M html "./docs/source" "./docs/build"'],
            'file_dep': ["./docs/source/API.rst", "./docs/source/index.rst"],
            'targets': ["HTMLINDEX"]
    }


def zipp(path, outfile):
    with ZipFile(outfile, 'w') as myzip:
        for p in iglob(path + '/**', recursive=True):
            P = Path(p)
            if P.is_file():
                myzip.write(p)


def task_zip():
    return {
            'actions': [(zipp, ['./docs/build', ZIPARCH]),],
            'task_dep': ('html',),
            'targets': [ZIPARCH],
    }


def task_erase():
    """Erase all uncommited files."""
    return {
            'actions': ['git clean -xdf']
    }
