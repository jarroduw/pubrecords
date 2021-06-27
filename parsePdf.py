import argparse
import glob
import os
import csv
import datetime
import PyPDF2
import logging

import shutil
from pathlib import Path
from db import DB

logging.logLevel="INFO"
logger = logging.getLogger('~')

class PDF(object):
    def __init__(self, finame, db):
        self.db = db
        self.finame = finame
        self.readInDoc()
        self.handleDocInfo()
        self.readText()
        self.writeToDB()

    def readInDoc(self):
        logger.info("Reading in %s", self.finame)
        self.obj = PyPDF2.PdfFileReader(self.finame)
    
    def handleDocInfo(self):
        docInfo = self.obj.documentInfo
        self.author = None
        if '/Author' in docInfo.keys():
            self.author = docInfo['/Author']
        self.created = None
        if '/CreationDate' in docInfo.keys():
            self.created = docInfo['/CreationDate']
        self.modified = None
        if '/ModDate' in docInfo.keys():
            self.modified = docInfo['/ModDate']
        self.title = None
        if '/Title' in docInfo.keys():
            self.title = docInfo['/Title']
        self.numpages = self.obj.getNumPages()

    def readText(self):
        docText = []
        for p in range(0, self.numpages):
            pg = self.obj.getPage(p)
            docText.append(pg.extractText())
        self.docText = docText
        logger.info("Extracted %s pages of text", self.numpages)

    def writeToDB(self):
        self.writeToDB_doc()
        self.writeToDB_pdf()
        self.writeToDB_textdata()
        self.writeToDB_pdftextdata()
        self.db.conn.commit()

    def writeToDB_doc(self):
        query = """INSERT INTO doc (source) VALUES (%s) RETURNING id;"""
        self.db.cur.execute(query, (self.finame,))
        self.doc_id = self.db.cur.fetchone()

    def writeToDB_pdf(self):
        query = """INSERT INTO pdf (
            doc_id, numpages, author, title, doc_created, doc_modified
            ) VALUES (
                %s, %s, %s, %s, %s, %s
                )
            RETURNING id;"""
        self.db.cur.execute(query, (self.doc_id, self.numpages, self.author, self.title, self.created, self.modified,))
        self.pdf_id = self.db.cur.fetchone()

    def writeToDB_textdata(self):
        query = """INSERT INTO textdata (doc_id, loc, raw_txt, txt) VALUES (%s, %s, %s, %s);"""
        dataToLoad = [(self.doc_id, i, data, self.cleanText(data),) for i, data in enumerate(self.docText)]
        self.db.cur.executemany(query, dataToLoad)

    def writeToDB_pdftextdata(self):
        ##Should be a bulk insert
        query = """INSERT INTO pdftextdata (textdata_id, pg) VALUES (%s, %s);"""
        query_get = """SELECT id FROM textdata WHERE doc_id=%s;"""
        self.db.cur.execute(query_get, (self.doc_id[0],))
        temp = self.db.cur.fetchall()
        dataToLoad = [(idx, i+1,) for i, idx in enumerate(temp)]
        self.db.cur.executemany(query, dataToLoad)

    def cleanText(self, txt):
        txt = txt.replace("\n", " ")
        return txt

class PdfHandler(object):
    def __init__(self, folder, root):
        self.folder = folder
        self.root = root
        self._iterateFiles()

    def _iterateFiles(self):
        """Iterator for all files in a directory"""
        db = DB()
        for fi in glob.glob(self.folder + self.root + "*.pdf"):
            print(fi)
            pth = Path(fi)
            st = os.stat(fi)
            mtime = datetime.datetime.fromtimestamp(st.st_mtime)
            
            try:
                PDF(fi, db)
                shutil.move(fi, self.folder + '/done/' + self.root + pth.name)
            except:
                shutil.move(fi, self.folder + '/issues/' + self.root + pth.name)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', help='root of documents after base')
    args = parser.parse_args()
    ph = PdfHandler('/mnt/c/Users/jarro/Documents/MonroePubRecRequest/', args.root)
    # db = DB()
    # pdf = PDF(
    #     '/mnt/c/Users/jarro/Documents/MonroePubRecRequest/Budget Hearing Powerpoint.pdf',
    #     db
    #     )
