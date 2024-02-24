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

    tree_id = body.split()[1].decode()
    tree_path = os.path.normpath(sys.argv[1]) +\
            f"/.git/objects/{tree_id[:2]}/{tree_id[2:]}"
    with open(tree_path, "rb") as f:
        obj = zlib.decompress(f.read())
        header, _, body = obj.partition(b'\x00')
    tail = body
    while tail:
        treeobj, _, tail = tail.partition(b'\x00')
        tmode, tname = treeobj.split()
        num, tail = tail[:20], tail[20:]
        num = num.hex()
        obj_path = os.path.normpath(sys.argv[1]) +\
                f"/.git/objects/{num[:2]}/{num[2:]}"
        with open(obj_path, "rb") as f:
            obj = zlib.decompress(f.read())
            kind = obj.partition(b"\x00")[0].split()[0]
        print(f"{kind.decode()} {num}    {tname.decode()}")
