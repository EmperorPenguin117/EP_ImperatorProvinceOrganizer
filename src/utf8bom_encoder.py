"""
This script goes through a directory and all subdirectories and converts the txt files to utf-8-bom
"""

import os
import codecs

rootdir = 'C:\\Users\\andre\\Documents\\Paradox Interactive\\Crusader Kings III\\mod\\Crusader-Universalis-2-0'
BLOCKSIZE = 1048576 # or some other, desired size in bytes

for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        if file.endswith('.txt') or file.endswith('.yml'):
            try:
                s = open(os.path.join(subdir, file), mode='r', encoding='utf-8').read()
                open(file, mode='w', encoding='utf-8-sig').write(s)
                print(os.path.join(subdir, file))
            except:
                print("COULD NOT OPEN: " + file)
