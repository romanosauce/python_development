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
    base_path = os.path.normpath(sys.argv[1])
    branch_path = base_path + "/.git/refs/heads/" +\
            sys.argv[2]
    with open(branch_path, "rb") as f:
        branch_head = f.read().decode().strip()
    commit_path = base_path +\
            f"/.git/objects/{branch_head[:2]}/{branch_head[2:]}"
    commit_id = branch_head
    while commit_id:
        with open(commit_path, "rb") as f:
            obj = zlib.decompress(f.read())
            header, _, body = obj.partition(b'\x00')

        body_fields = body.split()
        tree_id = body_fields[1].decode()
        print(f"TREE for commit {commit_id}")

        if body_fields[2] != b"parent":
            commit_id = ""
        else:
            commit_id = body_fields[3].decode()
            commit_path = base_path +\
                    f"/.git/objects/{commit_id[:2]}/{commit_id[2:]}"

        tree_path = base_path +\
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
            obj_path = base_path +\
                    f"/.git/objects/{num[:2]}/{num[2:]}"
            with open(obj_path, "rb") as f:
                obj = zlib.decompress(f.read())
                kind = obj.partition(b"\x00")[0].split()[0]
            print(f"{kind.decode()} {num}    {tname.decode()}")
