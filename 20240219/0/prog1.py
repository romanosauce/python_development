import glob
import zlib

path = "../../.git/objects"
for file in glob.iglob(path + "/??/*"):
    with open(file, "rb") as f:
        content = f.read()
    content = zlib.decompress(content)
    if (pos := content.find(b"commit")) != -1:
        print(content.partition(b'\x00')[2].decode())
