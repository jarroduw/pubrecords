import glob
import os
import csv
import datetime
from pathlib import Path

with ope
    for fi in glob.glob("/c/Users/jarro/Documents/MonroePubRecRequest/*"):
        pth = Path(fi)
        st = os.stat(fi)
        mtime = datetime.datetime.fromtimestamp(st.st_mtime)
        csv.writerow([fi, pth.name, mtime])
