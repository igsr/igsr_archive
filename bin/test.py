import glob
import os

path="/nfs/1000g-archive/vol1/ftp/dir_test/**/*"

for origin in glob.glob(path,recursive=True):
    if not os.path.isdir(origin):
        print(origin)