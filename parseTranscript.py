"""Takes transcript from transcriber and loads it into database"""

import csv
from db import DB

class Transcript(object):
    def __init__(self, finame, db):
        self.finame = finame
        self.readIn()
        self.db = db

    def readIn(self):
        output = []
        with open(self.finame) as fi:
            reader = csv.reader(fi, delimiter='\t')
            for row in reader:
                data = {
                    'time': self.processTime(row[0]),
                    'conf': float(row[1]),
                    'text': row[2]
                    }
                output.append(data)
        self.data = output

    def processTime(self, time_str):
        strLi = time_str.split(":")
        hr = int(strLi[0])*60*60
        mi = int(strLi[1])*60
        total_sec = hr + mi + int(strLi[2])
        return total_sec

    def writeToDB_doc(self):
        query = """INSERT INTO doc (source) VALUES (%s) returning id;"""
        self.db.cur.execute(query, (self.finame,))

    def writeToDB_textdata(self):
        query = """INSERT INTO textdata (doc_id, loc, raw_txt, txt) VALUES (%s, %s, %s, %s)"""
        temp = [(self.doc_id, i, x['text'], x['text'],) for i, x in enumerate(self.data)]
        self.db.cur.execute(query, temp)

    def writeToDb_transcriptdata(self):
        query = """
            INSERT INTO transcriptdata (
                textdata_id, chunktime, confidence
                ) VALUES (
                    %s, %s, %s
                    );
            """
        query_get = """SELECT id FROM textdata WHERE doc_id=%s;"""
        self.db.cur.execute(query_get, (self.doc_id[0],))
        temp = self.db.cur.fetchall()
        dataToLoad = [
            (
                idx,
                self.data[i]['time'],
                self.data[i]['conf']
            ) for i, idx in enumerate(temp)
        ]
        self.db.cur.executemany(query, dataToLoad)

if __name__ == '__main__':
    pth = '/home/olsonjr/SchoolBoard_20200616_0.txt'
    db = DB()
    t = Transcript(pth, db)