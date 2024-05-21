"""Module for starting client and print received data in parallel."""
from . import start_client
import sys


if len(sys.argv) == 1:
    print("Please provide your login name")
    quit(1)
login_name = sys.argv[1]
file_name = None
if '--file' in sys.argv[2:]:
    i = sys.argv.index('--file', 2)
    try:
        file_name = sys.argv[i+1]
    except Exception as e:
        print('Please provide a file name')
        quit(1)

start_client(login_name, file_name)
