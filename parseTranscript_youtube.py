"""Takes transcript from transcriber and loads it into database"""

import argparse
import glob
import os
import datetime
import csv
import shutil

from pathlib import Path

from db import DB

class Transcript(object):
    def __init__(self, finame, db):
        self.finame = finame
        self.readIn()
        self.db = db
        self.writeToDB_doc()
        self.writeToDB_textdata()
        self.writeToDB_transcriptdata()

    def readIn(self):
        output = []
        with open(self.finame) as fi:
            text = fi.read().strip().split("\n")
        data = {}
        for r, row in enumerate(text):
            if r == 0 or r % 2 == 0:
                data['time'] = self.processTime(row)
                data['conf'] = 1
            else:
                data['text'] = row
                output.append(data)
                data = {}
        self.data = output

    def processTime(self, time_str):
        strLi = time_str.split(":")
        hr = int(strLi[0])*60*60
        mi = int(strLi[1])*60
        return hr + mi

    def writeToDB_doc(self):
        query = """INSERT INTO doc (source) VALUES (%s) returning id;"""
        self.db.cur.execute(query, (self.finame,))
        self.doc_id = self.db.cur.fetchone()[0]

    def writeToDB_textdata(self):
        query = """INSERT INTO textdata (doc_id, loc, raw_txt, txt) VALUES (%s, %s, %s, %s)"""
        temp = [(self.doc_id, i, x['text'], x['text'],) for i, x in enumerate(self.data)]
        self.db.cur.executemany(query, temp)

    def writeToDB_transcriptdata(self):
        query = """
            INSERT INTO transcriptdata (
                textdata_id, chunktime, confidence
                ) VALUES (
                    %s, %s, %s
                    );
            """
        query_get = """SELECT id FROM textdata WHERE doc_id=%s;"""
        self.db.cur.execute(query_get, (self.doc_id,))
        temp = self.db.cur.fetchall()
        dataToLoad = [
            (
                idx,
                self.data[i]['time'],
                self.data[i]['conf']
            ) for i, idx in enumerate(temp)
        ]
        self.db.cur.executemany(query, dataToLoad)

class TranscriptHandler(object):
    def __init__(self, folder, root):
        self.folder = folder
        self.root = root
        self._iterateFiles()

    def _iterateFiles(self):
        """Iterator for all files in a directory"""
        db = DB()
        for fi in glob.glob(self.folder + self.root + "*.transcript"):
            print(fi)
            pth = Path(fi)
            st = os.stat(fi)
            mtime = datetime.datetime.fromtimestamp(st.st_mtime)
            try:
                Transcript(fi, db)
                shutil.move(fi, self.folder + '/done/' + self.root + pth.name)
            except:
                print("ERROR!")
                shutil.move(fi, self.folder + '/issues/' + self.root + pth.name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', help='root of documents after base')
    args = parser.parse_args()
    th = TranscriptHandler('/c/Users/jarro/Documents/MonroePubRecRequest/', args.root)
    # pth = '/home/olsonjr/SchoolBoard_20200616_0.txt'
    # db = DB()
    # t = Transcript(pth, db)