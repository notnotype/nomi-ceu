import os
import re
from icecream import ic
from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path

allow_dirs = [
    "\.\./overrides.*",
    "\.\./README\.md",
    "\.\./LICENSE\.md",
    "\.\./manifest\.json",
    "\.\./modlist\.html",
]
zfile = ZipFile('nomi-ceu-client.zip', 'w', ZIP_DEFLATED)
for root, dirs, files in os.walk('../'):
    # ic(root, dirs, files)
    del_dir = []
    
    for each in dirs:
        for allow_dir in allow_dirs:
            if re.match(allow_dir, os.path.join(root, each)):
                break
        else:
            del_dir.append(each)
            
    for each in del_dir:
        dirs.remove(each)
    
    fpath = root.replace('../', '')
    fpath = fpath and fpath + os.sep or ''
    for filename in files:
        zfile.write(os.path.join(root, filename), fpath + filename)
        print(os.path.join(root, filename))

zfile.close()