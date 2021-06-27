import psycopg2

class DB(object):

    def __init__(self):
        self.connectToDb()
    
    def connectToDb(self):
        with open('__sensitive_dbpw.txt', 'r') as fi:
            pw = fi.read().strip()
        self.conn = psycopg2.connect(
            dbname='pubrec_db',
            user='pubrec',
            host='127.0.0.1',
            password=pw
            )
        
        self.cur = self.conn.cursor()