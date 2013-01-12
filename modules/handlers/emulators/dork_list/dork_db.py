import sqlite3
import datetime
import threading
import logging

logger = logging.getLogger(__name__)


class DorkDB(object):
    sqlite_lock = threading.Lock()

    def __init__(self):
        self.conn = sqlite3.connect("db/dork.db")

    def create(self):
        with DorkDB.sqlite_lock:
            self.cursor = self.conn.cursor()
            tablename = ["intitle", "intext", "inurl", "filetype", "ext", "allinurl"]
            for table in tablename:
                sql = "CREATE TABLE IF NOT EXISTS %s (id INTEGER PRIMARY KEY, content TEXT, count INTEGER, firsttime TEXT, lasttime TEXT)" % table
                self.cursor.execute(sql)
            self.cursor.close()
            self.conn.commit()

    def insert(self, insert_list):
        if len(insert_list) == 0:
            return
        try:
            with DorkDB.sqlite_lock:
                for item in insert_list:
                    self.cursor = self.conn.cursor()
                    sql = "SELECT * FROM %s WHERE content = ?" % item['table']
                    cnt = self.cursor.execute(sql, (item['content'],)).fetchall()
                    if len(cnt) == 0:
                        self.trueInsert(item['table'], item['content'])
                    else:
                        self.update_entry(item['table'], cnt)
                self.conn.commit()
        except sqlite3.ProgrammingError as e:
            logger.exception("Error while selecting in dork_db: {0}".format(e))

    def trueInsert(self, table, content):
        try:
            self.cursor = self.conn.cursor()
            sql = "INSERT INTO %s VALUES( ?, ?, ?, ?, ?)" % table
            self.cursor.execute(sql, (None, content, 1, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            self.cursor.close()
        except sqlite3.OperationalError as e:
            logger.exception("Error while inserting into dork_db: {0}".format(e))
        except sqlite3.ProgrammingError as e:
            #NOTE: Might be better to fail hard here!
            logger.exception("Programming error while inserting into dork_db: {0}".format(e))

    def update_entry(self, table, cnt):
        self.cursor = self.conn.cursor()
        try:
            sql = "UPDATE %s SET lasttime = ? , count = count + 1 WHERE content = ?" % table
            self.cursor.execute(sql, (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), cnt[0][1]))
            self.cursor.close()
        except sqlite3.OperationalError as e:
            logger.exception("Error while updaing column in dork_db: {0}".format(e))

    def get_dork_list(self, table):
        with DorkDB.sqlite_lock:
            self.cursor = self.conn.cursor()
            sql = "SELECT content FROM %s" % table
            self.cursor.execute(sql)
            res = self.cursor.fetchall()
        return res
