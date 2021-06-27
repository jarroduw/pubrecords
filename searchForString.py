import psycopg2
from db import DB

if __name__=="__main__":
    db = DB()
    string = 'blasko'
    db.cur.execute("SELECT d.*, ta.loc, ta.txt FROM textdata ta LEFT JOIN doc d ON d.id = ta.doc_id WHERE ta.txt_index_col @@ plainto_tsquery(%s);", (string,))
    result = db.cur.fetchall()