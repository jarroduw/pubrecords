import argparse
import glob
import os
import csv
import datetime
from bs4 import BeautifulSoup
import logging
import psycopg2

import shutil
from pathlib import Path
from db import DB

logging.logLevel="INFO"
logger = logging.getLogger('~')

class Email(object):
    def __init__(self, finame, db):
        self.db = db
        self.finame = finame
        self.readInDoc()
        self.readText()
        self.writeToDB()

    def readInDoc(self):
        logger.info("Reading in %s", self.finame)
        try:
            with open(self.finame) as fi:
                self.obj = fi.read().strip()
        except UnicodeDecodeError:
            with open(self.finame, encoding='windows-1252') as fi:
                self.obj = fi.read().strip()

    def readText(self):
        docText = self.obj.split("\n")
        subjIdx = [i for i, s in enumerate(docText) if "Subject" in s]
        fromIdx = [i for i, s in enumerate(docText) if "From" in s]
        newDocText = []
        base = 0
        for ji, si in enumerate(subjIdx):
            fi = fromIdx[ji]
            try:
                nextFi = fromIdx[ji+1]
            except IndexError:
                nextFi = len(docText)+1
            head = docText[fi:si+1]
            body = docText[si+1:nextFi]
            newDocText.append(["\n".join(head), " ".join(body)])
        self.docText = newDocText

    def writeToDB(self):
        self.writeToDB_doc()
        self.writeToDB_email()
        self.writeToDB_textdata()
        self.writeToDB_emailHead()
        self.db.conn.commit()

    def writeToDB_doc(self):
        query = """INSERT INTO doc (source) VALUES (%s) RETURNING id;"""
        self.db.cur.execute(query, (self.finame,))
        self.doc_id = self.db.cur.fetchone()

    def writeToDB_email(self):
        query = """INSERT INTO email (
            doc_id, num_emails
            ) VALUES (
                %s, %s
                )
            RETURNING id;"""
        self.db.cur.execute(query, (self.doc_id, len(self.docText),))
        self.email_id = self.db.cur.fetchone()

    def writeToDB_textdata(self):
        query = """INSERT INTO textdata (doc_id, loc, raw_txt, txt) VALUES (%s, %s, %s, %s);"""
        dataToLoad = [(self.doc_id, i, data[1], self.cleanText(data[1]),) for i, data in enumerate(self.docText)]
        self.db.cur.executemany(query, dataToLoad)

    def writeToDB_emailHead(self):
        query = """INSERT INTO email_head (doc_id, loc, raw_txt) VALUES (%s, %s, %s);"""
        dataToLoad = [(self.doc_id, i, data[0],) for i, data in enumerate(self.docText)]
        self.db.cur.executemany(query, dataToLoad)

    def cleanText(self, txt):
        txt = txt.replace("\n", " ")
        return txt

class EmailHandler(object):
    def __init__(self, folder, root):
        self.folder = folder
        self.root = root
        self._iterateFiles()

    def _iterateFiles(self):
        """Iterator for all files in a directory"""
        db = DB()
        for fi in glob.glob(self.folder + self.root + "*.txt"):
            print(fi)
            error_encountered = False
            pth = Path(fi)
            st = os.stat(fi)
            mtime = datetime.datetime.fromtimestamp(st.st_mtime)
            try:
                Email(fi, db)
                shutil.move(fi, self.folder + '/done/' + self.root + pth.name)
            except psycopg2.errors.ProgramLimitExceeded:
                print("==> Exceeded tsvector maximum length")
                error_encountered = True
            except IndexError:
                print("==> Index error in read_text")
                error_encountered = True
            if error_encountered:
                shutil.move(fi, self.folder + '/issues/' + self.root + pth.name)


if __name__=='__main__':
    #h = Email('/c/Users/jarro/Documents/MonroePubRecRequest/Request20-60-003/Re Invitation CLE Zoom Staff Meeting! @ Tue Mar 24, 2020 10am - 11am (PDT) (goodj@monroe.wednet.edu).txt', DB())
    parser = argparse.ArgumentParser()
    parser.add_argument('root', help='root of documents after base')
    args = parser.parse_args()
    ph = EmailHandler('/c/Users/jarro/Documents/MonroePubRecRequest/', args.root)
    # db = DB()
    # pdf = PDF(
    #     '/c/Users/jarro/Documents/MonroePubRecRequest/Budget Hearing Powerpoint.pdf',
    #     db
    #     )
