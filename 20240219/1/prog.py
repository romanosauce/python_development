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
else:
    branch_path = os.path.normpath(sys.argv[1]) + "/.git/refs/heads/" +\
            sys.argv[2]
    with open(branch_path, "rb") as f:
        branch_head = f.read().decode().strip()
    commit_path = os.path.normpath(sys.argv[1]) +\
            f"/.git/objects/{branch_head[:2]}/{branch_head[2:]}"
    with open(commit_path, "rb") as f:
        obj = zlib.decompress(f.read())
        header, _, body = obj.partition(b'\x00')
        print(body.decode().strip())
