import glob
import zlib
import sys
import os.path

if len(sys.argv) == 2:
    for store in glob.iglob(
            os.path.normpath(sys.argv[1]) + "/.git/refs/heads/*"):
        print(os.path.basename(store))
        # with open(store, "rb") as f:
            # obj = zlib.decompress(f.read())
            # header, _, body = obj.partition(b'\x00')
            # kind, size = header.split()
        # if kind == "branch":
            # print(kind)
