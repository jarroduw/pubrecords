import argparse
import glob
import os
import csv
import datetime
import logging

import shutil
from pathlib import Path
from docx import Document
from db import DB

logging.logLevel="INFO"
logger = logging.getLogger('~')

class DOCX(object):
    def __init__(self, finame, db):
        self.db = db
        self.finame = finame
        self.readInDoc()
        self.readText()
        self.handleDocInfo()
        self.writeToDB()

    def readInDoc(self):
        logger.info("Reading in %s", self.finame)
        self.obj = Document(self.finame)
    
    def handleDocInfo(self):
        docInfo = self.obj.core_properties
        self.author = docInfo.author
        self.created = docInfo.created
        self.modified = docInfo.modified
        self.last_author = docInfo.last_modified_by
        self.numEdits = docInfo.revision
        self.numpara = len(self.docText)
        self.numwords = len(" ".join(self.docText))

    def readText(self):
        docText = []
        for p, pg in enumerate(self.obj.paragraphs):
            docText.append(pg.text)
        self.docText = docText
        logger.info("Extracted %s paragraphs of text", p)

    def writeToDB(self):
        self.writeToDB_doc()
        self.writeToDB_docx()##Meta
        self.writeToDB_textdata()##Actual text
        self.writeToDB_docxtextdata()##text meta data
        self.db.conn.commit()

    def writeToDB_doc(self):
        query = """INSERT INTO doc (source) VALUES (%s) RETURNING id;"""
        self.db.cur.execute(query, (self.finame,))
        self.doc_id = self.db.cur.fetchone()[0]

    def writeToDB_docx(self):
        query = """INSERT INTO docx (
            doc_id, author, doc_created, doc_modified, last_author, num_edits, num_para, num_words
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
                )
            RETURNING id;"""
        self.db.cur.execute(query, (self.doc_id, self.author, self.created, self.modified, self.last_author, self.numEdits, self.numpara, self.numwords,))
        self.docx_id = self.db.cur.fetchone()[0]

    def writeToDB_textdata(self):
        query = """INSERT INTO textdata (doc_id, loc, raw_txt, txt) VALUES (%s, %s, %s, %s);"""
        dataToLoad = [(self.doc_id, i, data, self.cleanText(data),) for i, data in enumerate(self.docText)]
        self.db.cur.executemany(query, dataToLoad)

    def writeToDB_docxtextdata(self):
        ##Should be a bulk insert
        query = """INSERT INTO docxtextdata (textdata_id, para_num) VALUES (%s, %s);"""
        query_get = """SELECT id FROM textdata WHERE doc_id=%s;"""
        self.db.cur.execute(query_get, (self.doc_id,))
        temp = self.db.cur.fetchall()
        dataToLoad = [(idx, i+1,) for i, idx in enumerate(temp)]
        self.db.cur.executemany(query, dataToLoad)

    def cleanText(self, txt):
        txt = txt.replace("\n", " ")
        return txt

class DocxHandler(object):
    def __init__(self, folder, root):
        self.folder = folder
        self.root = root
        self._iterateFiles()

    def _iterateFiles(self):
        """Iterator for all files in a directory"""
        db = DB()
        for fi in glob.glob(self.folder + self.root + "*.docx"):
            print(fi)
            pth = Path(fi)
            st = os.stat(fi)
            mtime = datetime.datetime.fromtimestamp(st.st_mtime)
            #try:
            DOCX(fi, db)
            shutil.move(fi, self.folder + '/done/' + self.root + pth.name)
            #except:
            #    print("ERROR")
            #    shutil.move(fi, self.folder + '/issues/' + self.root + pth.name)

if __name__=='__main__':
#    d = DOCX('/c/Users/jarro/Documents/MonroePubRecRequest/FromOtherRequests/Closing_Reflection.docx', {})
    parser = argparse.ArgumentParser()
    parser.add_argument('root', help='root of documents after base')
    args = parser.parse_args()
    ph = DocxHandler('/c/Users/jarro/Documents/MonroePubRecRequest/', args.root)
