import mmap
import time
import os

filesize = os.stat('/root/backuproot/data2.tar').st_size

with open('/root/backuproot/data2.tar', 'r+b') as f:
    mm = mmap.mmap(f.fileno(), 0)

    start = time.time()

    a = f.read()
    print("File Read")
    mid = time.time()

    b = mm.read(filesize)
    print("MMap Read")
    end = time.time()


print("File : " + str(mid-start))
print("MMap : " + str(end-mid))

with open('/root/backuproot/text', 'r+b') as f:

    mm = mmap.mmap(f.fileno(), filesize)

    start = time.time()

    f.write(a)
    print("File Write")
    mid = time.time()

    mm.write(b)
    print("MMap Write")
    end = time.time()


print("File : " + str(mid-start))
print("MMap : " + str(end-mid))

